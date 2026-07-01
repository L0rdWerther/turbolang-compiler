from lexer.token import TokenType
KEYWORDS = {'func': TokenType.FUNC, 'if': TokenType.IF, 'then': TokenType.THEN, 'else': TokenType.ELSE, 'while': TokenType.WHILE, 'do': TokenType.DO, 'for': TokenType.FOR, 'to': TokenType.TO, 'return': TokenType.RETURN, 'int': TokenType.INT, 'float': TokenType.FLOAT_TYPE, 'char': TokenType.CHAR_TYPE, 'bool': TokenType.BOOL, 'true': TokenType.TRUE, 'false': TokenType.FALSE, 'print': TokenType.PRINT}

def is_keyword(word: str) -> bool:
    return word in KEYWORDS

def get_keyword_token_type(word: str) -> TokenType:
    return KEYWORDS.get(word, TokenType.IDENTIFIER)
