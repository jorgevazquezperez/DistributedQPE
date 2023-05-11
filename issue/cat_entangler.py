from typing import Optional
import warnings
import numpy as np

from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library.blueprintcircuit import BlueprintCircuit


class CatEntangler(BlueprintCircuit):

    def __init__(self,
                 num_qubits: Optional[int] = None,
                 name: Optional[str] = None) -> None:
        if name is None:
            name = "CatEntangler"

        super().__init__(name=name)
        self.num_qubits = num_qubits
    
    @property
    def num_qubits(self) -> int:
        return super().num_qubits

    @num_qubits.setter
    def num_qubits(self, num_qubits: int) -> None:
        """Set the number of qubits.
        Note that this changes the registers of the circuit.
        Args:
            num_qubits: The new number of qubits.
        """
        if num_qubits != self.num_qubits:
            self._invalidate()

            self.qregs = []
            if num_qubits is not None and num_qubits > 0:
                self.qregs = [QuantumRegister(num_qubits, name="q")]
    
    def _check_configuration(self, raise_on_failure: bool = True) -> bool:
        """Check if the current configuration is valid."""
        valid = True
        if self.num_qubits is None:
            valid = False
            if raise_on_failure:
                raise AttributeError("The number of qubits has not been set.")
        return valid
    
    def _build(self) -> None:
        """If not already built, build the circuit."""
        if self._is_built:
            return

        super()._build()

        num_qubits = self.num_qubits

        if num_qubits < 3:
            return

        circuit = QuantumCircuit(*self.qregs, name=self.name)
        circuit.add_register(ClassicalRegister(1))
        
        self._create_cat_state(circuit)
        circuit.barrier()

        circuit.cx(0, 1)
        circuit.measure(1, 0)

        for i_qubit in range(1,num_qubits):
            circuit.x(i_qubit).c_if(0, 1)

        self.compose(circuit, qubits=self.qubits, clbits=self.clbits, inplace=True, wrap=True)
    
    def _create_cat_state(self, circuit: QuantumCircuit) -> None:

        num_qubits = self.num_qubits
        circuit.h(1)
        for i_qubit in range(1,num_qubits-1):
            circuit.cx(i_qubit, i_qubit+1)

