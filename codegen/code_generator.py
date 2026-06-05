"""
Code generator for TurboLang.
Generates SaM assembly code from the AST.
"""

import struct
from typing import Dict, Optional, List, Tuple

from parser.ast_nodes import *
from semantic.symbol_table import SymbolTable
from semantic.type_checker import TypeChecker
from codegen.sam_instructions import InstructionBuffer, OpCode


class CodeGenError(Exception):
    """Exception for code generation errors."""
    pass


class CodeGenerator:
    """
    Code generator for TurboLang.
    Converts AST to the documented TurboLang SaM variant.
    """

    def __init__(self):
        self.buffer = InstructionBuffer()
        self.symbol_table = SymbolTable()
        self.function_table: Dict[str, Tuple[Optional[str], List[str]]] = {}
        self.function_param_types: Dict[str, List[str]] = {}
        self.current_function: Optional[str] = None
        self.current_return_type: Optional[str] = None
        self.function_labels: Dict[str, str] = {}

    def generate(self, program: Program) -> str:
        for func in program.functions:
            label = self.buffer.generate_label()
            self.function_labels[func.name] = label
            self.function_table[func.name] = (
                func.return_type,
                [p.name for p in func.parameters],
            )
            self.function_param_types[func.name] = [p.type_name for p in func.parameters]

        if 'main' not in self.function_labels:
            raise CodeGenError("No main function defined")

        self.buffer.emit(OpCode.JMP, self.function_labels['main'])

        for func in program.functions:
            self.generate_function(func)

        return self.buffer.get_code()

    def generate_function(self, func: FunctionDecl) -> None:
        self.current_function = func.name
        self.current_return_type = func.return_type
        self.symbol_table.push_scope()
        self.symbol_table.reset_offset()

        self.buffer.emit_label(self.function_labels[func.name])

        argc = len(func.parameters)
        for index, param in enumerate(func.parameters):
            symbol = self.symbol_table.define(param.name, param.type_name, is_parameter=True)
            symbol.offset = index - argc

        self.symbol_table.reset_offset()
        self.buffer.emit(OpCode.ENTER, self.count_locals(func.body) if func.body else 0)

        if func.body:
            self.generate_block(func.body)

        if func.name == 'main':
            self.buffer.emit(OpCode.HALT)
        elif not func.return_type:
            self.buffer.emit(OpCode.RET, 0)

        self.symbol_table.pop_scope()
        self.current_function = None
        self.current_return_type = None

    def generate_block(self, block: Block) -> None:
        for stmt in block.statements:
            self.generate_statement(stmt)

    def generate_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, Block):
            self.symbol_table.push_scope()
            self.generate_block(stmt)
            self.symbol_table.pop_scope()
        elif isinstance(stmt, VariableDecl):
            self.generate_variable_decl(stmt)
        elif isinstance(stmt, Assignment):
            self.generate_assignment(stmt)
        elif isinstance(stmt, ExpressionStatement):
            if stmt.expression:
                self.generate_expression(stmt.expression)
                if self.expression_type(stmt.expression) != 'void':
                    self.buffer.emit(OpCode.POP)
        elif isinstance(stmt, IfStatement):
            self.generate_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self.generate_while_statement(stmt)
        elif isinstance(stmt, ReturnStatement):
            self.generate_return_statement(stmt)
        elif isinstance(stmt, PrintStatement):
            self.generate_print_statement(stmt)

    def generate_variable_decl(self, decl: VariableDecl) -> None:
        self.symbol_table.define(decl.name, decl.type_name)

        if decl.initial_value:
            self.generate_expression(decl.initial_value)
            self.emit_assignment_conversion(self.expression_type(decl.initial_value), decl.type_name)
            symbol = self.symbol_table.lookup(decl.name)
            self.buffer.emit(OpCode.STORE, symbol.offset)

    def generate_assignment(self, assign: Assignment) -> None:
        self.generate_expression(assign.value)

        symbol = self.symbol_table.lookup(assign.target)
        if not symbol:
            raise CodeGenError(f"Undefined variable: {assign.target}")

        self.emit_assignment_conversion(self.expression_type(assign.value), symbol.type_name)
        self.buffer.emit(OpCode.STORE, symbol.offset)

    def generate_if_statement(self, if_stmt: IfStatement) -> None:
        if if_stmt.else_block:
            else_label = self.buffer.generate_label()
            end_label = self.buffer.generate_label()

            self.generate_expression(if_stmt.condition)
            self.buffer.emit(OpCode.JZ, else_label)

            if if_stmt.then_block:
                self.symbol_table.push_scope()
                self.generate_block(if_stmt.then_block)
                self.symbol_table.pop_scope()

            self.buffer.emit(OpCode.JMP, end_label)
            self.buffer.emit_label(else_label)
            self.symbol_table.push_scope()
            self.generate_block(if_stmt.else_block)
            self.symbol_table.pop_scope()
            self.buffer.emit_label(end_label)
        else:
            end_label = self.buffer.generate_label()

            self.generate_expression(if_stmt.condition)
            self.buffer.emit(OpCode.JZ, end_label)

            if if_stmt.then_block:
                self.symbol_table.push_scope()
                self.generate_block(if_stmt.then_block)
                self.symbol_table.pop_scope()

            self.buffer.emit_label(end_label)

    def generate_while_statement(self, while_stmt: WhileStatement) -> None:
        loop_label = self.buffer.generate_label()
        end_label = self.buffer.generate_label()

        self.buffer.emit_label(loop_label)
        self.generate_expression(while_stmt.condition)
        self.buffer.emit(OpCode.JZ, end_label)

        if while_stmt.body:
            self.symbol_table.push_scope()
            self.generate_block(while_stmt.body)
            self.symbol_table.pop_scope()

        self.buffer.emit(OpCode.JMP, loop_label)
        self.buffer.emit_label(end_label)

    def generate_return_statement(self, ret_stmt: ReturnStatement) -> None:
        if ret_stmt.value:
            self.generate_expression(ret_stmt.value)
            if self.current_return_type:
                self.emit_assignment_conversion(
                    self.expression_type(ret_stmt.value),
                    self.current_return_type,
                )

        self.buffer.emit(OpCode.RET, 1 if ret_stmt.value else 0)

    def generate_print_statement(self, stmt: PrintStatement) -> None:
        if not stmt.argument:
            return

        self.generate_expression(stmt.argument)
        arg_type = self.expression_type(stmt.argument)
        if arg_type == 'float':
            self.buffer.emit(OpCode.PRINTF32)
        elif arg_type == 'char':
            self.buffer.emit(OpCode.PRINTC)
        elif arg_type == 'string':
            self.buffer.emit(OpCode.PRINTS)
        else:
            self.buffer.emit(OpCode.PRINT)

    def generate_expression(self, expr: Expression) -> None:
        if isinstance(expr, Literal):
            self.generate_literal(expr)
        elif isinstance(expr, Identifier):
            symbol = self.symbol_table.lookup(expr.name)
            if not symbol:
                raise CodeGenError(f"Undefined variable: {expr.name}")
            self.buffer.emit(OpCode.LOAD, symbol.offset)
        elif isinstance(expr, BinaryExpression):
            self.generate_binary_expression(expr)
        elif isinstance(expr, UnaryExpression):
            self.generate_unary_expression(expr)
        elif isinstance(expr, FunctionCall):
            self.generate_function_call(expr)
        elif isinstance(expr, ArrayAccess):
            self.generate_array_access(expr)
        else:
            raise CodeGenError(f"Unknown expression type: {type(expr)}")

    def generate_binary_expression(self, expr: BinaryExpression) -> None:
        left_type = self.expression_type(expr.left)
        right_type = self.expression_type(expr.right)
        result_type = TypeChecker.binary_operation_type(left_type, expr.operator, right_type)
        arithmetic = expr.operator in ['+', '-', '*', '/', '%']
        use_float = arithmetic and result_type == 'float'

        if use_float:
            self.generate_expression_as(expr.left, 'float')
            self.generate_expression_as(expr.right, 'float')
        else:
            self.generate_expression(expr.left)
            self.generate_expression(expr.right)

        if use_float:
            opcodes = {
                '+': OpCode.FADD,
                '-': OpCode.FSUB,
                '*': OpCode.FMUL,
                '/': OpCode.FDIV,
                '%': OpCode.FMOD,
            }
        elif left_type == 'float' and right_type == 'float' and expr.operator in ['==', '!=', '<', '>', '<=', '>=']:
            opcodes = {
                '==': OpCode.FEQ,
                '!=': OpCode.FNE,
                '<': OpCode.FLT,
                '>': OpCode.FGT,
                '<=': OpCode.FLE,
                '>=': OpCode.FGE,
            }
        else:
            opcodes = {
                '+': OpCode.ADD,
                '-': OpCode.SUB,
                '*': OpCode.MUL,
                '/': OpCode.DIV,
                '%': OpCode.MOD,
                '==': OpCode.EQ,
                '!=': OpCode.NE,
                '<': OpCode.LT,
                '>': OpCode.GT,
                '<=': OpCode.LE,
                '>=': OpCode.GE,
                '&&': OpCode.AND,
                '||': OpCode.OR,
            }

        if expr.operator not in opcodes:
            raise CodeGenError(f"Unknown binary operator: {expr.operator}")
        self.buffer.emit(opcodes[expr.operator])

    def generate_unary_expression(self, expr: UnaryExpression) -> None:
        self.generate_expression(expr.operand)

        if expr.operator == '-':
            opcode = OpCode.FNEG if self.expression_type(expr.operand) == 'float' else OpCode.NEG
            self.buffer.emit(opcode)
        elif expr.operator == '!':
            self.buffer.emit(OpCode.NOT)
        else:
            raise CodeGenError(f"Unknown unary operator: {expr.operator}")

    def generate_function_call(self, call: FunctionCall) -> None:
        for arg, target_type in zip(call.arguments, self.function_param_types.get(call.name, [])):
            self.generate_expression(arg)
            self.emit_assignment_conversion(self.expression_type(arg), target_type)

        label = self.function_labels.get(call.name)
        if not label:
            raise CodeGenError(f"Undefined function: {call.name}")

        self.buffer.emit(OpCode.CALL, f"{label} {len(call.arguments)}")

    def generate_array_access(self, expr: ArrayAccess) -> None:
        symbol = self.symbol_table.lookup(expr.array_name)
        if not symbol:
            raise CodeGenError(f"Undefined variable: {expr.array_name}")

        self.generate_expression(expr.index)
        self.buffer.emit(OpCode.LOAD_INDEXED, symbol.offset)

    def generate_literal(self, literal: Literal) -> None:
        if literal.type_name == 'float':
            self.buffer.emit(OpCode.PUSHF32, self.float32_bits(literal.value))
        elif literal.type_name == 'char':
            self.buffer.emit(OpCode.PUSH, ord(literal.value))
        elif literal.type_name == 'bool':
            self.buffer.emit(OpCode.PUSH, 1 if literal.value else 0)
        elif literal.type_name == 'string':
            escaped = literal.value.replace('\\', '\\\\').replace('"', '\\"')
            self.buffer.emit(OpCode.PUSHS, f'"{escaped}"')
        else:
            self.buffer.emit(OpCode.PUSH, literal.value)

    def generate_expression_as(self, expr: Expression, target_type: str) -> None:
        actual_type = self.expression_type(expr)
        self.generate_expression(expr)
        self.emit_assignment_conversion(actual_type, target_type)

    def emit_assignment_conversion(self, from_type: str, to_type: str) -> None:
        if from_type == 'int' and to_type == 'float':
            self.buffer.emit(OpCode.ITOF)

    def expression_type(self, expr: Expression) -> str:
        if isinstance(expr, Literal):
            return expr.type_name
        if isinstance(expr, Identifier):
            symbol = self.symbol_table.lookup(expr.name)
            if not symbol:
                raise CodeGenError(f"Undefined variable: {expr.name}")
            return symbol.type_name
        if isinstance(expr, BinaryExpression):
            return TypeChecker.binary_operation_type(
                self.expression_type(expr.left),
                expr.operator,
                self.expression_type(expr.right),
            )
        if isinstance(expr, UnaryExpression):
            return TypeChecker.unary_operation_type(expr.operator, self.expression_type(expr.operand))
        if isinstance(expr, FunctionCall):
            return_type, _ = self.function_table.get(expr.name, (None, []))
            return return_type if return_type else 'void'
        if isinstance(expr, ArrayAccess):
            symbol = self.symbol_table.lookup(expr.array_name)
            if not symbol:
                raise CodeGenError(f"Undefined variable: {expr.array_name}")
            return symbol.type_name
        raise CodeGenError(f"Unknown expression type: {type(expr)}")

    def count_locals(self, block: Block) -> int:
        count = 0
        for stmt in block.statements:
            if isinstance(stmt, VariableDecl):
                count += 1
            elif isinstance(stmt, Block):
                count += self.count_locals(stmt)
            elif isinstance(stmt, IfStatement):
                if stmt.then_block:
                    count += self.count_locals(stmt.then_block)
                if stmt.else_block:
                    count += self.count_locals(stmt.else_block)
            elif isinstance(stmt, WhileStatement) and stmt.body:
                count += self.count_locals(stmt.body)
        return count

    @staticmethod
    def float32_bits(value: float) -> str:
        bits = struct.unpack('>I', struct.pack('>f', float(value)))[0]
        return f"0x{bits:08x}"
