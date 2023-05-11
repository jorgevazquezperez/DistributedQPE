import math

from cat_disentangler import CatDisentangler
from cat_entangler import CatEntangler
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import PhaseGate

from qiskit import IBMQ, Aer, transpile, assemble

num_qubits = 2

phase_input = 1/4
distributed = True

if distributed:
    qr_host1 = QuantumRegister(num_qubits)
    qr_host2 = QuantumRegister(num_qubits)
    cl_eval = ClassicalRegister(1, name="cl_eval")
    cl_aux = ClassicalRegister(num_qubits, name="cl_aux")

    qr_list = [qr_host1, qr_host2]
    cl_list = [cl_eval, cl_aux]

    qc = QuantumCircuit(*qr_list, *cl_list, name="Distributed")
    qc.x(3)
    qc.h(0)
    qc.compose(CatEntangler(3), qubits=[*qr_host1, qr_host2[0]], clbits=[cl_aux[0]], inplace=True)
    qc.append(PhaseGate(theta = 2*math.pi*phase_input).control(), qargs=qr_host2)
    qc.compose(CatDisentangler(3), qubits=[*qr_host1, qr_host2[0]], clbits=[cl_aux[1]], inplace=True)
    qc.barrier()

    qc.p(-math.pi/2, 0)
    qc.h(0)
    qc.measure(qr_host1[0], cl_eval[0])
    print(qc)
else:
    qr_eval = QuantumRegister(1, "eval")
    qr_state = QuantumRegister(1, "q")
    cl_eval = ClassicalRegister(1, "cl_eval")

    qr_list = [qr_eval, qr_state]
    qc = QuantumCircuit(*qr_list, cl_eval, name="PhaseGate")

    qc.x(qr_state[0])
    qc.h(qr_eval)  # hadamards on evaluation qubits

    qc.append(PhaseGate(theta = 2*math.pi*phase_input).control(), qargs=qr_list)
    
    qc.p(-math.pi/2, 0)
    qc.h(0)
    qc.measure(qr_eval[0], cl_eval[0])
    print(qc)


backend_sim = Aer.get_backend('aer_simulator')
qc_reset = transpile(qc, backend_sim)
reset_sim_job = backend_sim.run(qc_reset)
reset_sim_result = reset_sim_job.result()
answer = reset_sim_result.get_counts(0)

def process_answer(answer):
    new_dict = {}
    for key, count in answer.items():
        keys = key.split()
        if len(keys) < 2:
            return
        new_key = keys[1]
        if new_key in new_dict:
            new_dict[new_key] += count
        else:
            new_dict[new_key] = count
    return new_dict

results = process_answer(answer)

if results is None:
    print(answer)
else:
    print(results)