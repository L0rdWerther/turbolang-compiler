from typing import List, Optional, Any
from dataclasses import dataclass, field

@dataclass
class ASTNode:
    line: int = 0
    column: int = 0

@dataclass
class Program(ASTNode):
    functions: List['FunctionDecl'] = field(default_factory=list)

@dataclass
class FunctionDecl(ASTNode):
    name: str = ''
    parameters: List['Parameter'] = field(default_factory=list)
    return_type: Optional[str] = None
    body: Optional['Block'] = None

@dataclass
class Parameter(ASTNode):
    type_name: str = ''
    name: str = ''

@dataclass
class Block(ASTNode):
    statements: List['Statement'] = field(default_factory=list)

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class VariableDecl(Statement):
    type_name: str = ''
    name: str = ''
    initial_value: Optional['Expression'] = None

@dataclass
class Assignment(Statement):
    target: str = ''
    value: Optional['Expression'] = None
    index: Optional['Expression'] = None

@dataclass
class ExpressionStatement(Statement):
    expression: Optional['Expression'] = None

@dataclass
class IfStatement(Statement):
    condition: Optional['Expression'] = None
    then_block: Optional['Block'] = None
    else_block: Optional['Block'] = None

@dataclass
class WhileStatement(Statement):
    condition: Optional['Expression'] = None
    body: Optional['Block'] = None

@dataclass
class DoWhileStatement(Statement):
    body: Optional['Block'] = None
    condition: Optional['Expression'] = None

@dataclass
class ForStatement(Statement):
    variable: str = ''
    start: Optional['Expression'] = None
    end: Optional['Expression'] = None
    body: Optional['Block'] = None

@dataclass
class ReturnStatement(Statement):
    value: Optional['Expression'] = None

@dataclass
class PrintStatement(Statement):
    argument: Optional['Expression'] = None

@dataclass
class Expression(ASTNode):
    pass

@dataclass
class BinaryExpression(Expression):
    left: Optional[Expression] = None
    operator: str = ''
    right: Optional[Expression] = None

@dataclass
class UnaryExpression(Expression):
    operator: str = ''
    operand: Optional[Expression] = None

@dataclass
class FunctionCall(Expression):
    name: str = ''
    arguments: List[Expression] = field(default_factory=list)

@dataclass
class ArrayAccess(Expression):
    array_name: str = ''
    index: Optional[Expression] = None

@dataclass
class Literal(Expression):
    type_name: str = ''
    value: Any = None

@dataclass
class Identifier(Expression):
    name: str = ''
