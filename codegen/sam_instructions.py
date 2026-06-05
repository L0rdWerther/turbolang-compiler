"""
SaM (Simple Abstract Machine) instruction definitions and generation.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Any


class OpCode(Enum):
    """SaM operation codes."""
    # Stack operations
    PUSH = auto()          # Push constant onto stack
    POP = auto()           # Pop from stack
    DUP = auto()           # Duplicate top of stack
    
    # Load/Store
    LOAD = auto()          # Load variable onto stack
    STORE = auto()         # Store stack top into variable
    LOAD_INDEXED = auto()  # Load value from index
    
    # Arithmetic
    ADD = auto()           # Add top two stack values
    SUB = auto()           # Subtract
    MUL = auto()           # Multiply
    DIV = auto()           # Divide
    MOD = auto()           # Modulo
    NEG = auto()           # Negate
    
    # Comparison
    EQ = auto()            # Equal
    NE = auto()            # Not equal
    LT = auto()            # Less than
    GT = auto()            # Greater than
    LE = auto()            # Less than or equal
    GE = auto()            # Greater than or equal
    
    # Logical
    AND = auto()           # Logical AND
    OR = auto()            # Logical OR
    NOT = auto()           # Logical NOT
    
    # Control flow
    JMP = auto()           # Unconditional jump
    JZ = auto()            # Jump if zero
    JNZ = auto()           # Jump if not zero
    
    # Functions
    CALL = auto()          # Call function
    RET = auto()           # Return from function
    
    # I/O
    PRINT = auto()         # Print stack top
    
    # Special
    LABEL = auto()         # Label (not an instruction)
    HALT = auto()          # Stop execution


@dataclass
class Instruction:
    """Represents a SaM instruction."""
    opcode: OpCode
    operand: Optional[Any] = None
    label: Optional[str] = None
    
    def __str__(self) -> str:
        if self.label:
            return f"{self.label}:"
        
        if self.operand is not None:
            return f"{self.opcode.name} {self.operand}"
        else:
            return self.opcode.name


class InstructionBuffer:
    """Buffer for accumulating instructions."""
    
    def __init__(self):
        """Initialize instruction buffer."""
        self.instructions: List[Instruction] = []
        self.label_counter = 0
    
    def emit(self, opcode: OpCode, operand: Optional[Any] = None) -> None:
        """Emit an instruction."""
        self.instructions.append(Instruction(opcode, operand))
    
    def emit_label(self, label: str) -> None:
        """Emit a label."""
        self.instructions.append(Instruction(OpCode.LABEL, label=label))
    
    def generate_label(self) -> str:
        """Generate a unique label."""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def get_current_address(self) -> int:
        """Get current instruction address."""
        return len(self.instructions)
    
    def get_instructions(self) -> List[Instruction]:
        """Get all instructions."""
        return self.instructions.copy()
    
    def get_code(self) -> str:
        """Get assembly code as string."""
        lines = []
        for instr in self.instructions:
            lines.append(str(instr))
        return "\n".join(lines)