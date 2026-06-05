"""
Keywords and reserved words in TurboLang.
"""

from lexer.token import TokenType


# Mapping of keywords to their token types
KEYWORDS = {
    'func': TokenType.FUNC,
    'if': TokenType.IF,
    'then': TokenType.THEN,
    'entao': TokenType.THEN,
    'então': TokenType.THEN,
    'else': TokenType.ELSE,
    'senao': TokenType.ELSE,
    'senão': TokenType.ELSE,
    'while': TokenType.WHILE,
    'return': TokenType.RETURN,
    'int': TokenType.INT,
    'float': TokenType.FLOAT_TYPE,
    'char': TokenType.CHAR_TYPE,
    'bool': TokenType.BOOL,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'print': TokenType.PRINT,
}


def is_keyword(word: str) -> bool:
    """Check if a word is a reserved keyword."""
    return word in KEYWORDS


def get_keyword_token_type(word: str) -> TokenType:
    """Get the token type for a keyword."""
    return KEYWORDS.get(word, TokenType.IDENTIFIER)
