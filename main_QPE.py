#initialization
import math

from cat_disentangler import CatDisentangler
from cat_entangler import CatEntangler

# importing Qiskit
from qiskit import IBMQ, Aer, transpile, assemble
from qiskit.execute_function import execute
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library import QFT
from qiskit.circuit.library import PhaseGate
from qiskit.visualization import circuit_drawer

# import basic plot tools
from qiskit.visualization import plot_histogram

phase_input = 1/4
n_eval = 3

distributed = False

iqft = QFT(n_eval, inverse=True, do_swaps=False)

if distributed:
    qr_eval = QuantumRegister(n_eval, "eval")
    qr_aux = QuantumRegister(2*n_eval, "aux")
    qr_state = QuantumRegister(1, "q")
    cl_eval = ClassicalRegister(n_eval, "cl_eval")
    cl_aux = ClassicalRegister(2*n_eval, "cl_aux")

    qr_list = [qr_eval, qr_aux, qr_state]
    cl_list = [cl_eval, cl_aux]
    qpe = QuantumCircuit(*qr_list, *cl_list, name="QPE")

    qpe.x(qr_state[0])
    qpe.h(qr_eval)  # hadamards on evaluation qubits

    for j in range(n_eval):  # controlled powers
        qubits_list = [qr_eval[j], qr_aux[2*j], qr_aux[2*j + 1]]
        qpe.compose(CatEntangler(3), qubits=qubits_list, clbits=[cl_aux[2*j]], inplace=True)
        qpe.append(PhaseGate(theta = 2*math.pi*phase_input).power(2**(n_eval-j-1)).control(), qargs=[qr_aux[2*j + 1]] + qr_state[:])
        qpe.compose(CatDisentangler(3), qubits=qubits_list, clbits=[cl_aux[2*j+1]], inplace=True)
        
else:
    qr_eval = QuantumRegister(n_eval, "eval")
    qr_state = QuantumRegister(1, "q")
    cl_eval = ClassicalRegister(n_eval, "cl_eval")

    qr_list = [qr_eval, qr_state]
    qpe = QuantumCircuit(*qr_list, cl_eval, name="QPE")

    qpe.x(qr_state[0])
    qpe.h(qr_eval)  # hadamards on evaluation qubits

    for j in range(n_eval):  # controlled powers
        qpe.append(PhaseGate(theta = 2*math.pi*phase_input).power(2**(n_eval-j-1)).control(), qargs=[j] + qr_state[:])
        fase = 2*math.pi*phase_input*(2**(n_eval-j-1))
        print(fase, math.cos(fase))
    
qpe.append(iqft, qargs=qr_eval)
print(qpe)
# Measure
qpe.barrier()
#qpe.h(qr_eval)
"""
for n in range(n_eval):
    qpe.measure(qr_eval[n],cl_eval[n])

#qpe.measure(qr_state[0], cl_eval[0])

aer_sim = Aer.get_backend('aer_simulator')
t_qpe = transpile(qpe, aer_sim)
intermediate = aer_sim.run(t_qpe)
results = intermediate.result()
answer = results.get_counts()

def process_answer(answer):
    new_dict = {}
    for key, count in answer.items():
        keys = key.split()
        if len(keys) < 2:
            return
        new_key = keys[1]
        if new_key in new_dict:
            new_dict[new_key] = new_dict[new_key] + count
        else:
            new_dict[new_key] = count
    return new_dict

results = process_answer(answer)

if results is None:
    print(answer)
else:
    print(results)
"""
# Ejecutar el circuito cuántico
backend = Aer.get_backend('statevector_simulator')
job = execute(qpe, backend)
result = job.result()

# Obtener el vector de estado resultante
statevector = result.get_statevector()

# Imprimir el vector de estado
print("Vector de estado:")
print(statevector)

