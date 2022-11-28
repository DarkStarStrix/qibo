import math

import numpy as np
import pytest

from qibo import gates, matrices
from qibo.models import Circuit
from qibo.models.qcnn import QuantumCNN

num_angles = 21
angles0 = [i * math.pi / num_angles for i in range(num_angles)]


def test_classifier_circuit2():
    """ """
    nqubits = 2
    nlayers = int(nqubits / 2)
    init_state = np.ones(2**nqubits) / np.sqrt(2**nqubits)  #

    qcnn = QuantumCNN(nqubits, nlayers, nclasses=2, RY=True)  # , params=angles0)

    angles = [0] + angles0

    circuit = qcnn.Classifier_circuit(angles)
    # circuit = qcnn._circuit
    statevector = circuit(init_state).state()
    real_vector = get_real_vector2()

    # to compare statevector and real_vector
    np.testing.assert_allclose(statevector.real, real_vector.real, atol=1e-5)
    np.testing.assert_allclose(statevector.imag, real_vector.imag, atol=1e-5)


def get_real_vector2():
    nqubits = 2
    bits = range(nqubits)
    init_state = np.ones(2**nqubits) / np.sqrt(2**nqubits)  #
    angles = angles0

    # convolution
    k = 0
    a = np.dot(
        one_qubit_unitary(nqubits, bits[0], angles[k : k + 3]).unitary(), init_state
    )
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[1], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(RZZ_unitary(nqubits, bits[0], bits[1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RYY_unitary(nqubits, bits[0], bits[1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RXX_unitary(nqubits, bits[0], bits[1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(one_qubit_unitary(nqubits, bits[0], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[1], angles[k : k + 3]).unitary(), a)
    k += 3
    # pooling
    ksink = k
    a = np.dot(one_qubit_unitary(nqubits, bits[1], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[0], angles[k : k + 3]).unitary(), a)
    a = np.dot(CNOT_unitary(nqubits, bits[0], bits[1]).unitary(), a)
    a = np.dot(
        one_qubit_unitary(nqubits, bits[1], angles[ksink : ksink + 3])
        .invert()
        .unitary(),
        a,
    )

    return a


def test_classifier_circuit4():
    """ """
    nqubits = 4
    nlayers = int(nqubits / 2)
    init_state = np.ones(2**nqubits) / np.sqrt(2**nqubits)  #

    qcnn = QuantumCNN(nqubits, nlayers, nclasses=2, RY=True)
    angles = [0] + angles0 + angles0

    circuit = qcnn.Classifier_circuit(angles)
    statevector = circuit(init_state).state()
    real_vector = get_real_vector4()

    # to compare statevector and real_vector
    np.testing.assert_allclose(statevector.real, real_vector.real, atol=1e-5)
    np.testing.assert_allclose(statevector.imag, real_vector.imag, atol=1e-5)


def get_real_vector4():
    nqubits = 4
    init_state = np.ones(2**nqubits) / np.sqrt(2**nqubits)  #
    angles = angles0
    bits = range(nqubits)
    # convolution - layer 1
    # to declare matrix array a

    b0 = 0
    b1 = 1
    k = 0
    a = np.dot(
        one_qubit_unitary(nqubits, bits[b0], angles[k : k + 3]).unitary(), init_state
    )
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[b1], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(RZZ_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RYY_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RXX_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(one_qubit_unitary(nqubits, bits[b0], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[b1], angles[k : k + 3]).unitary(), a)

    b0 = 2
    b1 = 3
    k = 0
    a = np.dot(one_qubit_unitary(nqubits, bits[b0], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[b1], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(RZZ_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RYY_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RXX_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(one_qubit_unitary(nqubits, bits[b0], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[b1], angles[k : k + 3]).unitary(), a)

    b0 = 1
    b1 = 2
    k = 0
    a = np.dot(one_qubit_unitary(nqubits, bits[b0], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[b1], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(RZZ_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RYY_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RXX_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(one_qubit_unitary(nqubits, bits[b0], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[b1], angles[k : k + 3]).unitary(), a)

    b0 = 3
    b1 = 0
    k = 0
    a = np.dot(one_qubit_unitary(nqubits, bits[b0], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[b1], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(RZZ_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RYY_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RXX_unitary(nqubits, bits[b0], bits[b1], angles[k]).unitary(), a)
    k += 1
    a = np.dot(one_qubit_unitary(nqubits, bits[b0], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[b1], angles[k : k + 3]).unitary(), a)

    # pooling - layer 1
    k = 15  # k+=3
    ksink = k
    a = np.dot(one_qubit_unitary(nqubits, bits[2], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[0], angles[k : k + 3]).unitary(), a)
    a = np.dot(CNOT_unitary(nqubits, bits[0], bits[2]).unitary(), a)
    a = np.dot(
        one_qubit_unitary(nqubits, bits[2], angles[ksink : ksink + 3])
        .invert()
        .unitary(),
        a,
    )

    k = 15  # k+=3
    ksink = k
    a = np.dot(one_qubit_unitary(nqubits, bits[3], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[1], angles[k : k + 3]).unitary(), a)
    a = np.dot(CNOT_unitary(nqubits, bits[1], bits[3]).unitary(), a)
    a = np.dot(
        one_qubit_unitary(nqubits, bits[3], angles[ksink : ksink + 3])
        .invert()
        .unitary(),
        a,
    )

    # convolution - layer 2
    k = 0
    a = np.dot(one_qubit_unitary(nqubits, bits[2], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[3], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(RZZ_unitary(nqubits, bits[2], bits[3], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RYY_unitary(nqubits, bits[2], bits[3], angles[k]).unitary(), a)
    k += 1
    a = np.dot(RXX_unitary(nqubits, bits[2], bits[3], angles[k]).unitary(), a)
    k += 1
    a = np.dot(one_qubit_unitary(nqubits, bits[2], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[3], angles[k : k + 3]).unitary(), a)
    k += 3

    # pooling - layer 2
    ksink = k
    a = np.dot(one_qubit_unitary(nqubits, bits[3], angles[k : k + 3]).unitary(), a)
    k += 3
    a = np.dot(one_qubit_unitary(nqubits, bits[2], angles[k : k + 3]).unitary(), a)
    a = np.dot(CNOT_unitary(nqubits, bits[2], bits[3]).unitary(), a)
    a = np.dot(
        one_qubit_unitary(nqubits, bits[3], angles[ksink : ksink + 3])
        .invert()
        .unitary(),
        a,
    )

    return a


def one_qubit_unitary(nqubits, bit, symbols):
    c = Circuit(nqubits)
    c.add(gates.RX(bit, symbols[0]))
    c.add(gates.RY(bit, symbols[1]))
    c.add(gates.RZ(bit, symbols[2]))

    return c


def RXX_unitary(nqubits, bit0, bit1, angle):
    c = Circuit(nqubits)
    c.add(gates.RXX(bit0, bit1, angle))

    return c


def RYY_unitary(nqubits, bit0, bit1, angle):
    c = Circuit(nqubits)
    c.add(gates.RYY(bit0, bit1, angle))

    return c


def RZZ_unitary(nqubits, bit0, bit1, angle):
    c = Circuit(nqubits)
    c.add(gates.RZZ(bit0, bit1, angle))

    return c


def CNOT_unitary(nqubits, bit0, bit1):
    c = Circuit(nqubits)
    c.add(gates.CNOT(bit0, bit1))

    return c
