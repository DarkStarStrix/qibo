"""
Test functions for gate fusion.
"""
import numpy as np
import pytest
from qibo.models import Circuit
from qibo import gates
from qibo.tensorflow import fusion


@pytest.mark.parametrize("backend", ["custom", "matmuleinsum"])
def test_one_qubit_gate_multiplication(backend):
    """Check gate multiplication for one-qubit gates."""
    import qibo
    qibo.set_backend(backend)
    gate1 = gates.X(0)
    gate2 = gates.H(0)
    final_gate = gate1 @ gate2
    target_matrix = (np.array([[0, 1], [1, 0]]) @
                     np.array([[1, 1], [1, -1]]) / np.sqrt(2))
    np.testing.assert_allclose(final_gate.unitary, target_matrix)

    final_gate = gate2 @ gate1
    target_matrix = (np.array([[1, 1], [1, -1]]) / np.sqrt(2) @
                     np.array([[0, 1], [1, 0]]))
    np.testing.assert_allclose(final_gate.unitary, target_matrix)


@pytest.mark.parametrize("backend", ["custom", "matmuleinsum"])
def test_two_qubit_gate_multiplication(backend):
    """Check gate multiplication for two-qubit gates."""
    import qibo
    qibo.set_backend(backend)
    theta, phi = 0.1234, 0.5432
    gate1 = gates.fSim(0, 1, theta=theta, phi=phi)
    gate2 = gates.SWAP(0, 1)
    final_gate = gate1 @ gate2
    target_matrix = (np.array([[1, 0, 0, 0],
                               [0, np.cos(theta), -1j * np.sin(theta), 0],
                               [0, -1j * np.sin(theta), np.cos(theta), 0],
                               [0, 0, 0, np.exp(-1j * phi)]]) @
                     np.array([[1, 0, 0, 0], [0, 0, 1, 0],
                               [0, 1, 0, 0], [0, 0, 0, 1]]))
    np.testing.assert_allclose(final_gate.unitary, target_matrix)

    # Check that error is raised when target qubits do not agree
    with pytest.raises(NotImplementedError):
        final_gate = gate1 @ gates.SWAP(0, 2)
    # Reset backend for other tests
    qibo.set_backend("custom")


def test_from_queue_single_group():
    """Check fusion that creates a single ``FusionGroup``."""
    queue = [gates.H(0), gates.X(1), gates.CZ(0, 1)]
    fused_groups = fusion.FusionGroup.from_queue(queue)
    assert len(fused_groups) == 1
    group = fused_groups[0]
    assert group.gates0 == [[queue[0]], []]
    assert group.gates1 == [[queue[1]], []]
    assert group.two_qubit_gates == [queue[2]]


def test_from_queue_two_groups():
    """Check fusion that creates two ``FusionGroup``s."""
    queue = [gates.X(0), gates.H(1),
             gates.RX(2, theta=0.1234).controlled_by(1),
             gates.H(2), gates.Y(1),
             gates.H(0)]
    fused_groups = fusion.FusionGroup.from_queue(queue)
    assert len(fused_groups) == 2
    group1, group2 = fused_groups
    assert group1.gates0 == [[queue[0], queue[5]]]
    assert group1.gates1 == [[queue[1]]]
    assert group1.two_qubit_gates == []
    assert group2.gates0 == [[], [queue[4]]]
    assert group2.gates1 == [[], [queue[3]]]
    assert group2.two_qubit_gates == [queue[2]]


def test_fused_gate_calculation():
    queue = [gates.H(0), gates.H(1), gates.CNOT(0, 1),
             gates.X(0), gates.X(1)]
    group = fusion.FusionGroup.from_queue(queue)
    assert len(group) == 1
    group = group[0]

    assert len(group.gates) == 1
    gate = group.gates[0]

    x = np.array([[0, 1], [1, 0]])
    h = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    cnot = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1],
                     [0, 0, 1, 0]])
    target_matrix = np.kron(x, x) @ cnot @ np.kron(h, h)

    np.testing.assert_allclose(gate.unitary, target_matrix)


@pytest.mark.parametrize("nqubits", [4, 5, 10, 11])
@pytest.mark.parametrize("nlayers", [1, 4])
@pytest.mark.parametrize("accelerators", [None, {"/GPU:0": 1, "/GPU:1": 1}])
def test_circuit_fuse_variational_layer(nqubits, nlayers, accelerators):
    """Check fused variational layer execution."""
    theta = 2 * np.pi * np.random.random((2 * nlayers * nqubits,))
    theta_iter = iter(theta)

    c = Circuit(nqubits, accelerators=accelerators)
    for _ in range(nlayers):
        c.add((gates.RY(i, next(theta_iter)) for i in range(nqubits)))
        c.add((gates.CZ(i, i + 1) for i in range(0, nqubits - 1, 2)))
        c.add((gates.RY(i, next(theta_iter)) for i in range(nqubits)))
        c.add((gates.CZ(i, i + 1) for i in range(1, nqubits - 2, 2)))
        c.add(gates.CZ(0, nqubits - 1))

    fused_c = c.fuse()
    target_state = c()
    final_state = fused_c()
    np.testing.assert_allclose(final_state, target_state)


@pytest.mark.parametrize("accelerators", [None, {"/GPU:0": 2}])
def test_fuse_with_callback(accelerators):
    """Check entropy calculation in fused circuit."""
    from qibo import callbacks
    entropy = callbacks.EntanglementEntropy([0])
    c = Circuit(2, accelerators)
    c.add(gates.H(0))
    c.add(gates.X(1))
    c.add(gates.CallbackGate(entropy))
    c.add(gates.CNOT(0, 1))
    c.add(gates.CallbackGate(entropy))

    fused_c = c.fuse()
    target_state = c()
    final_state = fused_c()
    np.testing.assert_allclose(final_state, target_state)
    target_entropy = [0.0, 1.0, 0.0, 1.0]
    np.testing.assert_allclose(entropy[:].numpy(), target_entropy, atol=1e-7)


@pytest.mark.parametrize("nqubits", [3, 4])
@pytest.mark.parametrize("ngates", [10, 20, 40])
@pytest.mark.parametrize("accelerators", [None, {"/GPU:0": 1, "/GPU:1": 1}])
def test_fuse_random_circuits(nqubits, ngates, accelerators):
    """Check gate fusion in randomly generated circuits."""
    one_qubit_gates = [gates.RX, gates.RY, gates.RZ]
    two_qubit_gates = [gates.CNOT, gates.CZ, gates.SWAP]

    for _ in range(10):
        thetas = np.pi * np.random.random((ngates,))
        c = Circuit(nqubits, accelerators)
        for i in range(ngates):
            gate = one_qubit_gates[np.random.randint(0, 3)]
            q0 = np.random.randint(0, nqubits)
            c.add(gate(q0, thetas[i]))
            gate = two_qubit_gates[np.random.randint(0, 3)]
            q0, q1 = np.random.randint(0, nqubits, (2,))
            while q0 == q1:
                q0, q1 = np.random.randint(0, nqubits, (2,))
            c.add(gate(q0, q1))

        fused_c = c.fuse()
        target_state = c()
        final_state = fused_c()
        np.testing.assert_allclose(final_state, target_state)
