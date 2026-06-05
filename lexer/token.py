"""
Token class for lexical analysis.
Represents atomic units identified by the lexer.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(Enum):
    """Enumeration of all token types in TurboLang."""
    
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    CHAR = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Identifiers and keywords
    IDENTIFIER = auto()
    FUNC = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    INT = auto()
    FLOAT_TYPE = auto()
    CHAR_TYPE = auto()
    BOOL = auto()
    PRINT = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    
    # Comparison operators
    EQ = auto()          # ==
    NE = auto()          # !=
    LT = auto()          # <
    GT = auto()          # >
    LE = auto()          # <=
    GE = auto()          # >=
    
    # Logical operators
    AND = auto()         # &&
    OR = auto()          # ||
    NOT = auto()         # !
    
    # Delimiters
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    SEMICOLON = auto()   # ;
    COMMA = auto()       # ,
    ARROW = auto()       # ->
    COLON = auto()       # :
    
    # Special
    EOF = auto()
    NEWLINE = auto()


@dataclass
class Token:
    """
    Represents a token identified by the lexer.
    
    Attributes:
        type: The TokenType of this token
        value: The actual value/content of the token
        line: Line number where the token appears
        column: Column number where the token appears
        length: Length of the token in characters
    """
    type: TokenType
    value: Any
    line: int
    column: int
    length: int
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}, {self.column})"
    
    def __str__(self) -> str:
        return f"{self.type.name}:{self.value}"