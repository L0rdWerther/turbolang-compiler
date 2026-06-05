"""
Recursive Descent Parser for TurboLang.
Converts tokens into an Abstract Syntax Tree (AST).
"""

from typing import List, Optional
from lexer.token import Token, TokenType
from parser.ast_nodes import *


class ParseError(Exception):
    """Exception raised for parsing errors."""
    pass


class Parser:
    """
    Recursive Descent Parser for TurboLang.
    
    Implements the grammar:
    - program → (function_decl)*
    - function_decl → 'func' identifier '(' parameters? ')' ('->' type)? '{' block '}'
    - parameters → parameter (',' parameter)*
    - parameter → type identifier
    - block → statement*
    - statement → var_decl | assignment | if_stmt | while_stmt | return_stmt | expr_stmt | print_stmt | block
    - var_decl → type identifier ('=' expression)? ';'
    - assignment → identifier ('['expression']')? '=' expression ';'
    - if_stmt → 'if' '(' expression ')' block ('else' block)?
    - while_stmt → 'while' '(' expression ')' block
    - return_stmt → 'return' expression? ';'
    - print_stmt → 'print' '(' expression ')' ';'
    - expression → logical_or
    - logical_or → logical_and ('||' logical_and)*
    - logical_and → equality ('&&' equality)*
    - equality → comparison (('==' | '!=') comparison)*
    - comparison → additive (('<' | '>' | '<=' | '>=') additive)*
    - additive → multiplicative (('+' | '-') multiplicative)*
    - multiplicative → unary (('*' | '/' | '%') unary)*
    - unary → ('!' | '-') unary | postfix
    - postfix → primary ('[' expression ']')*
    - primary → literal | identifier | '(' expression ')' | function_call
    """
    
    def __init__(self, tokens: List[Token]):
        """
        Initialize the parser with tokens.
        
        Args:
            tokens: List of tokens from the lexer
        """
        self.tokens = tokens
        self.position = 0
    
    def current_token(self) -> Token:
        """Get the current token without advancing."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]  # Return EOF if past end
    
    def peek_token(self, offset: int = 1) -> Token:
        """Look ahead at the next token(s)."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF
    
    def advance(self) -> Token:
        """Move to the next token and return the current one."""
        current = self.current_token()
        if current.type != TokenType.EOF:
            self.position += 1
        return current
    
    def expect(self, *token_types: TokenType) -> Token:
        """
        Expect specific token type(s) and advance.

        Args:
            *token_types: One or more TokenType values to match

        Raises:
            ParseError: If the current token doesn't match any of the expected types
        """
        current = self.current_token()

        if current.type not in token_types:
            expected_names = ", ".join(t.name for t in token_types)
            raise ParseError(
                f"Expected {expected_names}, got {current.type.name} "
                f"at line {current.line}, column {current.column}"
            )

        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if the current token matches any of the given types."""
        return self.current_token().type in token_types
    
    def parse(self) -> Program:
        """
        Parse the entire program.
        
        Returns:
            Program AST node
        """
        functions = []
        
        while not self.match(TokenType.EOF):
            if self.match(TokenType.FUNC):
                functions.append(self.parse_function_decl())
            else:
                raise ParseError(
                    f"Unexpected token {self.current_token().type.name} "
                    f"at line {self.current_token().line}"
                )
        
        return Program(functions=functions)
    
    def parse_function_decl(self) -> FunctionDecl:
        """Parse a function declaration."""
        token = self.expect(TokenType.FUNC)
        line, column = token.line, token.column
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.expect(TokenType.LPAREN)
        parameters = self.parse_parameters()
        self.expect(TokenType.RPAREN)
        
        return_type = None
        if self.match(TokenType.ARROW):
            self.advance()
            type_token = self.expect(TokenType.INT, TokenType.FLOAT_TYPE, 
                                     TokenType.CHAR_TYPE, TokenType.BOOL)
            return_type = type_token.value
        
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        
        return FunctionDecl(
            name=name,
            parameters=parameters,
            return_type=return_type,
            body=body,
            line=line,
            column=column
        )
    
    def parse_parameters(self) -> List[Parameter]:
        """Parse function parameters."""
        parameters = []
        
        if not self.match(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            
            while self.match(TokenType.COMMA):
                self.advance()
                parameters.append(self.parse_parameter())
        
        return parameters
    
    def parse_parameter(self) -> Parameter:
        """Parse a single parameter."""
        type_token = self.expect(TokenType.INT, TokenType.FLOAT_TYPE, 
                                 TokenType.CHAR_TYPE, TokenType.BOOL)
        type_name = type_token.value
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        return Parameter(type_name=type_name, name=name, line=type_token.line)
    
    def parse_block(self) -> Block:
        """Parse a block of statements."""
        statements = []
        
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            statements.append(self.parse_statement())
        
        return Block(statements=statements)
    
    def parse_statement(self) -> Statement:
        """Parse a single statement."""
        # Variable declaration
        if self.match(TokenType.INT, TokenType.FLOAT_TYPE, 
                     TokenType.CHAR_TYPE, TokenType.BOOL):
            return self.parse_variable_decl()
        
        # If statement
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        
        # While loop
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()
        
        # Return statement
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()
        
        # Print statement
        if self.match(TokenType.PRINT):
            return self.parse_print_statement()
        
        # Block
        if self.match(TokenType.LBRACE):
            self.advance()
            block = self.parse_block()
            self.expect(TokenType.RBRACE)
            return block
        
        # Assignment or expression statement
        return self.parse_assignment_or_expression()
    
    def parse_variable_decl(self) -> VariableDecl:
        """Parse variable declaration."""
        type_token = self.expect(TokenType.INT, TokenType.FLOAT_TYPE, 
                                 TokenType.CHAR_TYPE, TokenType.BOOL)
        type_name = type_token.value
        line, column = type_token.line, type_token.column
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        initial_value = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initial_value = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        
        return VariableDecl(
            type_name=type_name,
            name=name,
            initial_value=initial_value,
            line=line,
            column=column
        )
    
    def parse_if_statement(self) -> IfStatement:
        """Parse if statement."""
        token = self.expect(TokenType.IF)
        line, column = token.line, token.column
        
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.LBRACE)
        then_block = self.parse_block()
        self.expect(TokenType.RBRACE)
        
        else_block = None
        if self.match(TokenType.ELSE):
            self.advance()
            self.expect(TokenType.LBRACE)
            else_block = self.parse_block()
            self.expect(TokenType.RBRACE)
        
        return IfStatement(
            condition=condition,
            then_block=then_block,
            else_block=else_block,
            line=line,
            column=column
        )
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse while loop."""
        token = self.expect(TokenType.WHILE)
        line, column = token.line, token.column
        
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        
        return WhileStatement(
            condition=condition,
            body=body,
            line=line,
            column=column
        )
    
    def parse_return_statement(self) -> ReturnStatement:
        """Parse return statement."""
        token = self.expect(TokenType.RETURN)
        line, column = token.line, token.column
        
        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.parse_expression()
        
        self.expect(TokenType.SEMICOLON)
        
        return ReturnStatement(value=value, line=line, column=column)
    
    def parse_print_statement(self) -> PrintStatement:
        """Parse print statement."""
        token = self.expect(TokenType.PRINT)
        line, column = token.line, token.column
        
        self.expect(TokenType.LPAREN)
        argument = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        
        return PrintStatement(argument=argument, line=line, column=column)
    
    def parse_assignment_or_expression(self) -> Statement:
        """Parse assignment or expression statement."""
        expr = self.parse_expression()
        
        # Check for assignment
        if isinstance(expr, Identifier):
            if self.match(TokenType.ASSIGN):
                self.advance()
                value = self.parse_expression()
                self.expect(TokenType.SEMICOLON)
                return Assignment(target=expr.name, value=value)
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                self.expect(TokenType.SEMICOLON)
                return Assignment(target=expr.name, value=value, index=index)
        
        self.expect(TokenType.SEMICOLON)
        return ExpressionStatement(expression=expr)
    
    def parse_expression(self) -> Expression:
        """Parse expression (logical OR level)."""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        """Parse logical OR expression."""
        left = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            op_token = self.advance()
            right = self.parse_logical_and()
            left = BinaryExpression(left=left, operator=op_token.value, right=right,
                                   line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_logical_and(self) -> Expression:
        """Parse logical AND expression."""
        left = self.parse_equality()
        
        while self.match(TokenType.AND):
            op_token = self.advance()
            right = self.parse_equality()
            left = BinaryExpression(left=left, operator=op_token.value, right=right,
                                   line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_equality(self) -> Expression:
        """Parse equality expression."""
        left = self.parse_comparison()
        
        while self.match(TokenType.EQ, TokenType.NE):
            op_token = self.advance()
            right = self.parse_comparison()
            left = BinaryExpression(left=left, operator=op_token.value, right=right,
                                   line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_comparison(self) -> Expression:
        """Parse comparison expression."""
        left = self.parse_additive()
        
        while self.match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op_token = self.advance()
            right = self.parse_additive()
            left = BinaryExpression(left=left, operator=op_token.value, right=right,
                                   line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_additive(self) -> Expression:
        """Parse addition/subtraction expression."""
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self.parse_multiplicative()
            left = BinaryExpression(left=left, operator=op_token.value, right=right,
                                   line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_multiplicative(self) -> Expression:
        """Parse multiplication/division expression."""
        left = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_token = self.advance()
            right = self.parse_unary()
            left = BinaryExpression(left=left, operator=op_token.value, right=right,
                                   line=op_token.line, column=op_token.column)
        
        return left
    
    def parse_unary(self) -> Expression:
        """Parse unary expression."""
        if self.match(TokenType.NOT, TokenType.MINUS):
            op_token = self.advance()
            operand = self.parse_unary()
            return UnaryExpression(operator=op_token.value, operand=operand,
                                  line=op_token.line, column=op_token.column)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> Expression:
        """Parse postfix expression (array access, function calls)."""
        expr = self.parse_primary()
        
        while self.match(TokenType.LBRACKET):
            self.advance()
            index = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            
            if isinstance(expr, Identifier):
                expr = ArrayAccess(array_name=expr.name, index=index,
                                  line=expr.line, column=expr.column)
        
        return expr
    
    def parse_primary(self) -> Expression:
        """Parse primary expression."""
        # Literals
        if self.match(TokenType.INTEGER):
            token = self.advance()
            return Literal(type_name='int', value=token.value,
                         line=token.line, column=token.column)
        
        if self.match(TokenType.FLOAT):
            token = self.advance()
            return Literal(type_name='float', value=token.value,
                         line=token.line, column=token.column)
        
        if self.match(TokenType.STRING):
            token = self.advance()
            return Literal(type_name='string', value=token.value,
                         line=token.line, column=token.column)
        
        if self.match(TokenType.CHAR):
            token = self.advance()
            return Literal(type_name='char', value=token.value,
                         line=token.line, column=token.column)
        
        if self.match(TokenType.TRUE, TokenType.FALSE):
            token = self.advance()
            return Literal(type_name='bool', value=token.value,
                         line=token.line, column=token.column)
        
        # Parenthesized expression
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Identifier or function call
        if self.match(TokenType.IDENTIFIER):
            token = self.advance()
            name = token.value
            
            # Function call
            if self.match(TokenType.LPAREN):
                self.advance()
                arguments = self.parse_arguments()
                self.expect(TokenType.RPAREN)
                return FunctionCall(name=name, arguments=arguments,
                                   line=token.line, column=token.column)
            
            # Identifier
            return Identifier(name=name, line=token.line, column=token.column)
        
        raise ParseError(
            f"Unexpected token {self.current_token().type.name} "
            f"at line {self.current_token().line}"
        )
    
    def parse_arguments(self) -> List[Expression]:
        """Parse function call arguments."""
        arguments = []
        
        if not self.match(TokenType.RPAREN):
            arguments.append(self.parse_expression())
            
            while self.match(TokenType.COMMA):
                self.advance()
                arguments.append(self.parse_expression())
        
        return arguments