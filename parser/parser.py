from typing import List, Optional
from lexer.token import Token, TokenType
from parser.ast_nodes import *

class ParseError(Exception):
    pass

class Parser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    def current_token(self) -> Token:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]

    def peek_token(self, offset: int=1) -> Token:
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self) -> Token:
        current = self.current_token()
        if current.type != TokenType.EOF:
            self.position += 1
        return current

    def expect(self, *token_types: TokenType) -> Token:
        current = self.current_token()
        if current.type not in token_types:
            expected_names = ', '.join((t.name for t in token_types))
            raise ParseError(f'Expected {expected_names}, got {current.type.name} at line {current.line}, column {current.column}')
        return self.advance()

    def match(self, *token_types: TokenType) -> bool:
        return self.current_token().type in token_types

    def parse(self) -> Program:
        functions = []
        while not self.match(TokenType.EOF):
            if self.match(TokenType.FUNC):
                functions.append(self.parse_function_decl())
            else:
                raise ParseError(f'Unexpected token {self.current_token().type.name} at line {self.current_token().line}')
        return Program(functions=functions)

    def parse_function_decl(self) -> FunctionDecl:
        token = self.expect(TokenType.FUNC)
        line, column = (token.line, token.column)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        self.expect(TokenType.LPAREN)
        parameters = self.parse_parameters()
        self.expect(TokenType.RPAREN)
        return_type = None
        if self.match(TokenType.ARROW):
            self.advance()
            type_token = self.expect(TokenType.INT, TokenType.FLOAT_TYPE, TokenType.CHAR_TYPE, TokenType.BOOL)
            return_type = type_token.value
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        return FunctionDecl(name=name, parameters=parameters, return_type=return_type, body=body, line=line, column=column)

    def parse_parameters(self) -> List[Parameter]:
        parameters = []
        if not self.match(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            while self.match(TokenType.COMMA):
                self.advance()
                parameters.append(self.parse_parameter())
        return parameters

    def parse_parameter(self) -> Parameter:
        type_token = self.expect(TokenType.INT, TokenType.FLOAT_TYPE, TokenType.CHAR_TYPE, TokenType.BOOL)
        type_name = type_token.value
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        return Parameter(type_name=type_name, name=name, line=type_token.line)

    def parse_block(self) -> Block:
        statements = []
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            statements.append(self.parse_statement())
        return Block(statements=statements)

    def parse_statement(self) -> Statement:
        if self.match(TokenType.INT, TokenType.FLOAT_TYPE, TokenType.CHAR_TYPE, TokenType.BOOL):
            return self.parse_variable_decl()
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()
        if self.match(TokenType.DO):
            return self.parse_do_while_statement()
        if self.match(TokenType.FOR):
            return self.parse_for_statement()
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()
        if self.match(TokenType.PRINT):
            return self.parse_print_statement()
        if self.match(TokenType.LBRACE):
            self.advance()
            block = self.parse_block()
            self.expect(TokenType.RBRACE)
            return block
        return self.parse_assignment_or_expression()

    def parse_variable_decl(self) -> VariableDecl:
        type_token = self.expect(TokenType.INT, TokenType.FLOAT_TYPE, TokenType.CHAR_TYPE, TokenType.BOOL)
        type_name = type_token.value
        line, column = (type_token.line, type_token.column)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        initial_value = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initial_value = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return VariableDecl(type_name=type_name, name=name, initial_value=initial_value, line=line, column=column)

    def parse_if_statement(self) -> IfStatement:
        token = self.expect(TokenType.IF)
        line, column = (token.line, token.column)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        if self.match(TokenType.THEN):
            self.advance()
        self.expect(TokenType.LBRACE)
        then_block = self.parse_block()
        self.expect(TokenType.RBRACE)
        else_block = None
        if self.match(TokenType.ELSE):
            self.advance()
            self.expect(TokenType.LBRACE)
            else_block = self.parse_block()
            self.expect(TokenType.RBRACE)
        return IfStatement(condition=condition, then_block=then_block, else_block=else_block, line=line, column=column)

    def parse_while_statement(self) -> WhileStatement:
        token = self.expect(TokenType.WHILE)
        line, column = (token.line, token.column)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        return WhileStatement(condition=condition, body=body, line=line, column=column)

    def parse_do_while_statement(self) -> DoWhileStatement:
        token = self.expect(TokenType.DO)
        line, column = (token.line, token.column)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        self.expect(TokenType.WHILE)
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return DoWhileStatement(body=body, condition=condition, line=line, column=column)

    def parse_for_statement(self) -> ForStatement:
        token = self.expect(TokenType.FOR)
        line, column = (token.line, token.column)
        has_parens = self.match(TokenType.LPAREN)
        if has_parens:
            self.advance()
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        start = self.parse_expression()
        self.expect(TokenType.TO)
        end = self.parse_expression()
        if has_parens:
            self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        return ForStatement(variable=name_token.value, start=start, end=end, body=body, line=line, column=column)

    def parse_return_statement(self) -> ReturnStatement:
        token = self.expect(TokenType.RETURN)
        line, column = (token.line, token.column)
        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ReturnStatement(value=value, line=line, column=column)

    def parse_print_statement(self) -> PrintStatement:
        token = self.expect(TokenType.PRINT)
        line, column = (token.line, token.column)
        self.expect(TokenType.LPAREN)
        argument = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return PrintStatement(argument=argument, line=line, column=column)

    def parse_assignment_or_expression(self) -> Statement:
        expr = self.parse_expression()
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
        return self.parse_logical_or()

    def parse_logical_or(self) -> Expression:
        left = self.parse_logical_and()
        while self.match(TokenType.OR):
            op_token = self.advance()
            right = self.parse_logical_and()
            left = BinaryExpression(left=left, operator=op_token.value, right=right, line=op_token.line, column=op_token.column)
        return left

    def parse_logical_and(self) -> Expression:
        left = self.parse_equality()
        while self.match(TokenType.AND):
            op_token = self.advance()
            right = self.parse_equality()
            left = BinaryExpression(left=left, operator=op_token.value, right=right, line=op_token.line, column=op_token.column)
        return left

    def parse_equality(self) -> Expression:
        left = self.parse_comparison()
        while self.match(TokenType.EQ, TokenType.NE):
            op_token = self.advance()
            right = self.parse_comparison()
            left = BinaryExpression(left=left, operator=op_token.value, right=right, line=op_token.line, column=op_token.column)
        return left

    def parse_comparison(self) -> Expression:
        left = self.parse_additive()
        while self.match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op_token = self.advance()
            right = self.parse_additive()
            left = BinaryExpression(left=left, operator=op_token.value, right=right, line=op_token.line, column=op_token.column)
        return left

    def parse_additive(self) -> Expression:
        left = self.parse_multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self.parse_multiplicative()
            left = BinaryExpression(left=left, operator=op_token.value, right=right, line=op_token.line, column=op_token.column)
        return left

    def parse_multiplicative(self) -> Expression:
        left = self.parse_unary()
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_token = self.advance()
            right = self.parse_unary()
            left = BinaryExpression(left=left, operator=op_token.value, right=right, line=op_token.line, column=op_token.column)
        return left

    def parse_unary(self) -> Expression:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op_token = self.advance()
            operand = self.parse_unary()
            return UnaryExpression(operator=op_token.value, operand=operand, line=op_token.line, column=op_token.column)
        return self.parse_postfix()

    def parse_postfix(self) -> Expression:
        expr = self.parse_primary()
        while self.match(TokenType.LBRACKET):
            self.advance()
            index = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            if isinstance(expr, Identifier):
                expr = ArrayAccess(array_name=expr.name, index=index, line=expr.line, column=expr.column)
        return expr

    def parse_primary(self) -> Expression:
        if self.match(TokenType.INTEGER):
            token = self.advance()
            return Literal(type_name='int', value=token.value, line=token.line, column=token.column)
        if self.match(TokenType.FLOAT):
            token = self.advance()
            return Literal(type_name='float', value=token.value, line=token.line, column=token.column)
        if self.match(TokenType.STRING):
            token = self.advance()
            return Literal(type_name='string', value=token.value, line=token.line, column=token.column)
        if self.match(TokenType.CHAR):
            token = self.advance()
            return Literal(type_name='char', value=token.value, line=token.line, column=token.column)
        if self.match(TokenType.TRUE, TokenType.FALSE):
            token = self.advance()
            return Literal(type_name='bool', value=token.value, line=token.line, column=token.column)
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        if self.match(TokenType.IDENTIFIER):
            token = self.advance()
            name = token.value
            if self.match(TokenType.LPAREN):
                self.advance()
                arguments = self.parse_arguments()
                self.expect(TokenType.RPAREN)
                return FunctionCall(name=name, arguments=arguments, line=token.line, column=token.column)
            return Identifier(name=name, line=token.line, column=token.column)
        raise ParseError(f'Unexpected token {self.current_token().type.name} at line {self.current_token().line}')

    def parse_arguments(self) -> List[Expression]:
        arguments = []
        if not self.match(TokenType.RPAREN):
            arguments.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                arguments.append(self.parse_expression())
        return arguments
