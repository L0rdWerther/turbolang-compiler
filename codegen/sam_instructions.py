"""
Reference SaM textual instruction helpers.

The compiler backend emits text directly, but these definitions keep the
instruction vocabulary documented in code for tests and tooling.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List, Optional


class OpCode(Enum):
    """Operation names used by the reference Portugol SaM variant."""

    # Stack and frame operations
    ADDSP = auto()
    LINK = auto()
    POPFBR = auto()

    # Constants
    PUSHIMM = auto()
    PUSHIMMF = auto()
    PUSHIMMCH = auto()
    PUSHS = auto()

    # Load/store
    PUSHOFF = auto()
    STOREOFF = auto()
    PUSHIND = auto()
    ITOF = auto()

    # Arithmetic
    ADD = auto()
    SUB = auto()
    TIMES = auto()
    DIV = auto()
    MOD = auto()
    ADDF = auto()
    SUBF = auto()
    TIMESF = auto()
    DIVF = auto()

    # Comparison and logic
    GREATER = auto()
    LESS = auto()
    EQUAL = auto()
    CMPF = auto()
    ISPOS = auto()
    ISNEG = auto()
    ISNIL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Control flow and calls
    JUMP = auto()
    JUMPC = auto()
    JSR = auto()
    JUMPIND = auto()

    # I/O
    WRITE = auto()
    WRITEF = auto()
    WRITECH = auto()
    WRITES = auto()

    # Special
    LABEL = auto()
    STOP = auto()


@dataclass
class Instruction:
    """Represents one textual SaM instruction."""

    opcode: OpCode
    operand: Optional[Any] = None
    label: Optional[str] = None

    def __str__(self) -> str:
        if self.label:
            return f"{self.label}:"

        if self.operand is not None:
            return f"{self.opcode.name} {self.operand}"
        return self.opcode.name


class InstructionBuffer:
    """Small buffer for tests or tools that need to assemble SaM lines."""

    def __init__(self):
        self.instructions: List[Instruction] = []
        self.label_counter = 0

    def emit(self, opcode: OpCode, operand: Optional[Any] = None) -> None:
        self.instructions.append(Instruction(opcode, operand))

    def emit_label(self, label: str) -> None:
        self.instructions.append(Instruction(OpCode.LABEL, label=label))

    def generate_label(self, prefix: str = "LABEL") -> str:
        self.label_counter += 1
        return f"{prefix}_{self.label_counter}"

    def get_current_address(self) -> int:
        return len(self.instructions)

    def get_instructions(self) -> List[Instruction]:
        return self.instructions.copy()

    def get_code(self) -> str:
        return "\n".join(str(instr) for instr in self.instructions)
