"""
Abstract Syntax Tree (AST) node definitions for TurboLang.
Each node represents a syntactic construct in the language.
"""

from typing import List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = 0
    column: int = 0


@dataclass
class Program(ASTNode):
    """Root node representing the entire program."""
    functions: List['FunctionDecl'] = field(default_factory=list)


@dataclass
class FunctionDecl(ASTNode):
    """Function declaration."""
    name: str = ""
    parameters: List['Parameter'] = field(default_factory=list)
    return_type: Optional[str] = None  # Type name: int, float, char, bool
    body: Optional['Block'] = None


@dataclass
class Parameter(ASTNode):
    """Function parameter."""
    type_name: str = ""  # Type: int, float, char, bool
    name: str = ""


@dataclass
class Block(ASTNode):
    """Block of statements."""
    statements: List['Statement'] = field(default_factory=list)


@dataclass
class Statement(ASTNode):
    """Base class for all statements."""
    pass


@dataclass
class VariableDecl(Statement):
    """Variable declaration and optional initialization."""
    type_name: str = ""  # Type: int, float, char, bool
    name: str = ""
    initial_value: Optional['Expression'] = None


@dataclass
class Assignment(Statement):
    """Variable assignment."""
    target: str = ""  # Variable name
    value: Optional['Expression'] = None
    index: Optional['Expression'] = None  # For array assignments


@dataclass
class ExpressionStatement(Statement):
    """Expression used as a statement."""
    expression: Optional['Expression'] = None


@dataclass
class IfStatement(Statement):
    """If statement."""
    condition: Optional['Expression'] = None
    then_block: Optional['Block'] = None
    else_block: Optional['Block'] = None


@dataclass
class WhileStatement(Statement):
    """While loop."""
    condition: Optional['Expression'] = None
    body: Optional['Block'] = None


@dataclass
class ReturnStatement(Statement):
    """Return statement."""
    value: Optional['Expression'] = None


@dataclass
class PrintStatement(Statement):
    """Print statement (built-in)."""
    argument: Optional['Expression'] = None


@dataclass
class Expression(ASTNode):
    """Base class for expressions."""
    pass


@dataclass
class BinaryExpression(Expression):
    """Binary operation (e.g., a + b)."""
    left: Optional[Expression] = None
    operator: str = ""  # +, -, *, /, %, ==, !=, <, >, <=, >=, &&, ||
    right: Optional[Expression] = None


@dataclass
class UnaryExpression(Expression):
    """Unary operation (e.g., -x, !x)."""
    operator: str = ""  # -, !
    operand: Optional[Expression] = None


@dataclass
class FunctionCall(Expression):
    """Function call."""
    name: str = ""
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class ArrayAccess(Expression):
    """Array element access (e.g., arr[i])."""
    array_name: str = ""
    index: Optional[Expression] = None


@dataclass
class Literal(Expression):
    """Literal value."""
    type_name: str = ""  # int, float, char, bool, string
    value: Any = None


@dataclass
class Identifier(Expression):
    """Variable identifier."""
    name: str = ""