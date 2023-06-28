import math

# Getting the distribution tools
from cat_disentangler import CatDisentangler
from cat_entangler import CatEntangler

# Importing Qiskit
from qiskit import IBMQ, Aer, transpile
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library import QFT
from qiskit.circuit.library import PhaseGate

def _process_answer(counts: dict) -> dict:
    """Auxiliar funtion to process the counts and erase the intermediate measures from the result.
    Args:
        counts: Result from the measurements of the quantum circuit.
    Returns:
        dict: Dictionary with the significant measures.
    """
    new_dict = {}
    for key, count in counts.items():
        keys = key.split()
        if len(keys) < 2:
            return
        new_key = keys[1]
        if new_key in new_dict:
            new_dict[new_key] = new_dict[new_key] + count
        else:
            new_dict[new_key] = count
    return new_dict


phase_input = float(input('Enter the phase: '))
n_eval = int(input('Enter the number of evaluation qubits (precision): '))
distributed = input('Distributed? (y/n): ')

if distributed == "y":
    """Distributed implementation using cat entangler and cat disantangler."""
    
    # Definition of the registers and the circuit (3n + 1 qubits)
    qr_eval = QuantumRegister(n_eval, "eval")
    qr_aux = QuantumRegister(2*n_eval, "aux")
    qr_state = QuantumRegister(1, "q")
    cl_eval = ClassicalRegister(n_eval, "cl_eval")
    cl_aux = ClassicalRegister(2*n_eval, "cl_aux")

    qr_list = [qr_eval, qr_aux, qr_state]
    cl_list = [cl_eval, cl_aux]
    qpe = QuantumCircuit(*qr_list, *cl_list, name="QPE")

    # Declaration of the gates
    qpe.x(qr_state[0])
    qpe.h(qr_eval)
    for j in range(n_eval):
        qubits_list = [qr_eval[j], qr_aux[2*j], qr_aux[2*j + 1]]
        qpe.compose(CatEntangler(3), qubits=qubits_list, clbits=[cl_aux[2*j]], inplace=True)
        qpe.append(PhaseGate(theta = 2*math.pi*phase_input).power(2**(n_eval-j-1)).control(), qargs=[qr_aux[2*j + 1]] + qr_state[:])
        qpe.compose(CatDisentangler(3), qubits=qubits_list, clbits=[cl_aux[2*j+1]], inplace=True)
        
else:
    """Usual implementation of QPE algorithm."""

    # Definition of the registers and the circuit (n + 1 qubits)
    qr_eval = QuantumRegister(n_eval, "eval")
    qr_state = QuantumRegister(1, "q")
    cl_eval = ClassicalRegister(n_eval, "cl_eval")

    qr_list = [qr_eval, qr_state]
    qpe = QuantumCircuit(*qr_list, cl_eval, name="QPE")

    # Declaration of the gates
    qpe.x(qr_state[0])
    qpe.h(qr_eval)
    for j in range(n_eval):
        qpe.append(PhaseGate(theta = 2*math.pi*phase_input).power(2**(n_eval-j-1)).control(), qargs=[j] + qr_state[:])

# Add the inverse QFT in both cases and measure the eval qubits  
iqft = QFT(n_eval, inverse=True, do_swaps=False)  
qpe.append(iqft, qargs=qr_eval)
qpe.barrier()
for n in range(n_eval):
    qpe.measure(qr_eval[n],cl_eval[n])

print(qpe)

# Simulation of the circuit
aer_sim = Aer.get_backend('aer_simulator')
t_qpe = transpile(qpe, aer_sim)
intermediate = aer_sim.run(t_qpe)
results = intermediate.result()
counts = results.get_counts()

if distributed == "y":
    results = _process_answer(counts)
    print(results)
else:
    print(counts)

""" Code for getting the statevector (remember to erase measures)    
# Run quantum circuit
backend = Aer.get_backend('statevector_simulator')
job = execute(qpe, backend)
result = job.result()
statevector = result.get_statevector()

# Print statevector
print("Vector de estado:")
print(statevector)
"""
