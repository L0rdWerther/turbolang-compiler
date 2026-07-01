from typing import Optional, List, Dict
from parser.ast_nodes import *
from semantic.symbol_table import SymbolTable, FunctionTable
from semantic.type_checker import TypeChecker, TypeCheckError

class SemanticError(Exception):
    pass

class SemanticAnalyzer:

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.function_table = FunctionTable()
        self.current_function: Optional[str] = None
        self.current_function_return_type: Optional[str] = None
        self.errors: List[str] = []

    def analyze(self, program: Program) -> None:
        for func in program.functions:
            self.register_function(func)
        for func in program.functions:
            self.analyze_function(func)
        if not self.function_table.exists('main'):
            raise SemanticError('No main function defined')
        if self.errors:
            raise SemanticError('Semantic errors found:\n' + '\n'.join(self.errors))

    def register_function(self, func: FunctionDecl) -> None:
        parameters = []
        for param in func.parameters:
            parameters.append((param.type_name, param.name))
        try:
            self.function_table.define(func.name, func.return_type, parameters)
        except ValueError as e:
            raise SemanticError(str(e))

    def analyze_function(self, func: FunctionDecl) -> None:
        self.symbol_table.push_scope()
        self.current_function = func.name
        self.current_function_return_type = func.return_type
        for param in func.parameters:
            try:
                self.symbol_table.define(param.name, param.type_name, is_parameter=True)
            except ValueError as e:
                self.errors.append(f'In function {func.name}: {str(e)}')
        if func.body:
            self.analyze_block(func.body)
            if func.return_type and (not self.block_guarantees_return(func.body)):
                raise SemanticError(f'Function {func.name} must return {func.return_type} on all paths')
        elif func.return_type:
            raise SemanticError(f'Function {func.name} must return {func.return_type}')
        self.symbol_table.pop_scope()
        self.current_function = None
        self.current_function_return_type = None

    def analyze_block(self, block: Block) -> None:
        for statement in block.statements:
            self.analyze_statement(statement)

    def analyze_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, Block):
            self.symbol_table.push_scope()
            self.analyze_block(stmt)
            self.symbol_table.pop_scope()
        elif isinstance(stmt, VariableDecl):
            self.analyze_variable_decl(stmt)
        elif isinstance(stmt, Assignment):
            self.analyze_assignment(stmt)
        elif isinstance(stmt, ExpressionStatement):
            if stmt.expression:
                self.analyze_expression(stmt.expression)
        elif isinstance(stmt, IfStatement):
            self.analyze_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self.analyze_while_statement(stmt)
        elif isinstance(stmt, DoWhileStatement):
            self.analyze_do_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self.analyze_for_statement(stmt)
        elif isinstance(stmt, ReturnStatement):
            self.analyze_return_statement(stmt)
        elif isinstance(stmt, PrintStatement):
            if stmt.argument:
                self.analyze_expression(stmt.argument)

    def analyze_variable_decl(self, decl: VariableDecl) -> None:
        if not TypeChecker.is_valid_type(decl.type_name):
            raise SemanticError(f'Invalid type: {decl.type_name}')
        if self.symbol_table.exists_in_current_scope(decl.name):
            raise SemanticError(f"Variable '{decl.name}' already declared in current scope")
        try:
            self.symbol_table.define(decl.name, decl.type_name)
        except ValueError as e:
            raise SemanticError(str(e))
        if decl.initial_value:
            expr_type = self.analyze_expression(decl.initial_value)
            if not TypeChecker.is_compatible_assignment(expr_type, decl.type_name):
                raise SemanticError(f'Cannot assign {expr_type} to {decl.type_name}')

    def analyze_assignment(self, assign: Assignment) -> None:
        symbol = self.symbol_table.lookup(assign.target)
        if not symbol:
            raise SemanticError(f'Undefined variable: {assign.target}')
        value_type = self.analyze_expression(assign.value)
        if not TypeChecker.is_compatible_assignment(value_type, symbol.type_name):
            raise SemanticError(f'Cannot assign {value_type} to {symbol.type_name}')
        if assign.index:
            if not symbol.is_array and (not symbol.is_parameter):
                raise SemanticError(f'{assign.target} is not an array')
            index_type = self.analyze_expression(assign.index)
            if index_type != 'int':
                raise SemanticError('Array index must be int')

    def analyze_if_statement(self, if_stmt: IfStatement) -> None:
        cond_type = self.analyze_expression(if_stmt.condition)
        if cond_type != 'bool':
            raise SemanticError(f'If condition must be bool, got {cond_type}')
        self.symbol_table.push_scope()
        if if_stmt.then_block:
            self.analyze_block(if_stmt.then_block)
        self.symbol_table.pop_scope()
        if if_stmt.else_block:
            self.symbol_table.push_scope()
            self.analyze_block(if_stmt.else_block)
            self.symbol_table.pop_scope()

    def analyze_while_statement(self, while_stmt: WhileStatement) -> None:
        cond_type = self.analyze_expression(while_stmt.condition)
        if cond_type != 'bool':
            raise SemanticError(f'While condition must be bool, got {cond_type}')
        self.symbol_table.push_scope()
        if while_stmt.body:
            self.analyze_block(while_stmt.body)
        self.symbol_table.pop_scope()

    def analyze_do_while_statement(self, do_stmt: DoWhileStatement) -> None:
        self.symbol_table.push_scope()
        if do_stmt.body:
            self.analyze_block(do_stmt.body)
        self.symbol_table.pop_scope()
        cond_type = self.analyze_expression(do_stmt.condition)
        if cond_type != 'bool':
            raise SemanticError(f'Do-while condition must be bool, got {cond_type}')

    def analyze_for_statement(self, for_stmt: ForStatement) -> None:
        symbol = self.symbol_table.lookup(for_stmt.variable)
        if not symbol:
            raise SemanticError(f'Undefined variable: {for_stmt.variable}')
        if symbol.type_name != 'int':
            raise SemanticError('For loop control variable must be int')
        start_type = self.analyze_expression(for_stmt.start)
        end_type = self.analyze_expression(for_stmt.end)
        if start_type != 'int' or end_type != 'int':
            raise SemanticError('For loop bounds must be int')
        self.symbol_table.push_scope()
        if for_stmt.body:
            self.analyze_block(for_stmt.body)
        self.symbol_table.pop_scope()

    def analyze_return_statement(self, ret_stmt: ReturnStatement) -> None:
        if not self.current_function:
            raise SemanticError('Return statement outside function')
        if ret_stmt.value:
            if not self.current_function_return_type:
                raise SemanticError(f'Procedure {self.current_function} cannot return a value')
            ret_type = self.analyze_expression(ret_stmt.value)
            if not TypeChecker.is_compatible_assignment(ret_type, self.current_function_return_type):
                raise SemanticError(f'Cannot return {ret_type} from function returning {self.current_function_return_type}')
        elif self.current_function_return_type:
            raise SemanticError(f'Function must return {self.current_function_return_type}')

    def block_guarantees_return(self, block: Block) -> bool:
        for statement in block.statements:
            if self.statement_guarantees_return(statement):
                return True
        return False

    def statement_guarantees_return(self, stmt: Statement) -> bool:
        if isinstance(stmt, ReturnStatement):
            return True
        if isinstance(stmt, Block):
            return self.block_guarantees_return(stmt)
        if isinstance(stmt, IfStatement):
            if not stmt.then_block or not stmt.else_block:
                return False
            return self.block_guarantees_return(stmt.then_block) and self.block_guarantees_return(stmt.else_block)
        if isinstance(stmt, DoWhileStatement):
            return stmt.body is not None and self.block_guarantees_return(stmt.body)
        return False

    def analyze_expression(self, expr: Expression) -> str:
        if isinstance(expr, Literal):
            return expr.type_name
        elif isinstance(expr, Identifier):
            symbol = self.symbol_table.lookup(expr.name)
            if not symbol:
                raise SemanticError(f'Undefined variable: {expr.name}')
            return symbol.type_name
        elif isinstance(expr, BinaryExpression):
            left_type = self.analyze_expression(expr.left)
            right_type = self.analyze_expression(expr.right)
            try:
                return TypeChecker.binary_operation_type(left_type, expr.operator, right_type)
            except TypeCheckError as e:
                raise SemanticError(str(e))
        elif isinstance(expr, UnaryExpression):
            operand_type = self.analyze_expression(expr.operand)
            try:
                return TypeChecker.unary_operation_type(expr.operator, operand_type)
            except TypeCheckError as e:
                raise SemanticError(str(e))
        elif isinstance(expr, FunctionCall):
            return self.analyze_function_call(expr)
        elif isinstance(expr, ArrayAccess):
            symbol = self.symbol_table.lookup(expr.array_name)
            if not symbol:
                raise SemanticError(f'Undefined variable: {expr.array_name}')
            if not symbol.is_array and (not symbol.is_parameter):
                raise SemanticError(f'{expr.array_name} is not an array')
            index_type = self.analyze_expression(expr.index)
            if index_type != 'int':
                raise SemanticError('Array index must be int')
            return symbol.type_name
        else:
            raise SemanticError(f'Unknown expression type: {type(expr)}')

    def analyze_function_call(self, call: FunctionCall) -> str:
        func_info = self.function_table.lookup(call.name)
        if not func_info:
            raise SemanticError(f'Undefined function: {call.name}')
        if len(call.arguments) != func_info.parameters_count:
            raise SemanticError(f'Function {call.name} expects {func_info.parameters_count} arguments, got {len(call.arguments)}')
        for i, (arg, (param_type, _)) in enumerate(zip(call.arguments, func_info.parameters)):
            arg_type = self.analyze_expression(arg)
            if not TypeChecker.is_compatible_assignment(arg_type, param_type):
                raise SemanticError(f'Argument {i + 1} of {call.name}: expected {param_type}, got {arg_type}')
        return func_info.return_type if func_info.return_type else 'void'
