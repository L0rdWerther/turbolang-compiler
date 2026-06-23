"""
Code generator for TurboLang.
Generates SaM assembly code using the project's textual variant.
"""

from typing import Dict, List, Optional, Tuple

from parser.ast_nodes import *
from semantic.type_checker import TypeChecker


class CodeGenError(Exception):
    """Exception for code generation errors."""
    pass


class CodeGenerator:
    """Convert TurboLang AST nodes to the project SaM textual variant."""

    def __init__(self):
        self.lines: List[str] = []
        self.scopes: List[Dict[str, Tuple[str, int]]] = [{}]
        self.next_local_offset = 2
        self.label_counter = 0
        self.function_table: Dict[str, Tuple[Optional[str], List[str]]] = {}
        self.function_param_types: Dict[str, List[str]] = {}
        self.current_function: Optional[str] = None
        self.current_return_type: Optional[str] = None
        self.current_arg_count = 0
        self.current_local_count = 0

    def emit(self, instruction: str) -> None:
        self.lines.append(instruction)

    def emit_label(self, label: str) -> None:
        self.lines.append(f"{label}:")

    def new_label(self, prefix: str) -> str:
        self.label_counter += 1
        return f"{prefix}_{self.label_counter}"

    def push_scope(self) -> None:
        self.scopes.append({})

    def pop_scope(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    def define_symbol(self, name: str, type_name: str, offset: int) -> None:
        self.scopes[-1][name] = (type_name, offset)

    def lookup_symbol(self, name: str) -> Optional[Tuple[str, int]]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def require_symbol(self, name: str) -> Tuple[str, int]:
        symbol = self.lookup_symbol(name)
        if not symbol:
            raise CodeGenError(f"Undefined variable: {name}")
        return symbol

    def generate(self, program: Program) -> str:
        for func in program.functions:
            self.function_table[func.name] = (
                func.return_type,
                [param.name for param in func.parameters],
            )
            self.function_param_types[func.name] = [param.type_name for param in func.parameters]

        if "main" not in self.function_table:
            raise CodeGenError("No main function defined")

        self.emit("ADDSP 1")
        self.emit("LINK")
        self.emit("JSR FUNCAO_main")
        self.emit("POPFBR")
        self.emit("STOP")

        for func in program.functions:
            self.generate_function(func)

        return "\n".join(self.lines)

    def generate_function(self, func: FunctionDecl) -> None:
        self.current_function = func.name
        self.current_return_type = func.return_type
        self.current_arg_count = len(func.parameters)
        self.current_local_count = self.count_locals(func.body) if func.body else 0
        self.next_local_offset = 2
        self.scopes = [{}]

        self.emit_label(f"FUNCAO_{func.name}")

        offset = -1
        for param in reversed(func.parameters):
            self.define_symbol(param.name, param.type_name, offset)
            offset -= 1

        for _ in range(self.current_local_count):
            self.emit("ADDSP 1")

        if func.body:
            self.generate_block(func.body)

        if not self.lines[-1].endswith("JUMPIND"):
            self.emit_function_epilogue()

        self.current_function = None
        self.current_return_type = None
        self.current_arg_count = 0
        self.current_local_count = 0

    def emit_function_epilogue(self) -> None:
        if self.current_local_count > 0:
            self.emit(f"ADDSP -{self.current_local_count}")
        self.emit("JUMPIND")

    def generate_block(self, block: Block) -> None:
        for stmt in block.statements:
            self.generate_statement(stmt)

    def generate_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, Block):
            self.push_scope()
            self.generate_block(stmt)
            self.pop_scope()
        elif isinstance(stmt, VariableDecl):
            self.generate_variable_decl(stmt)
        elif isinstance(stmt, Assignment):
            self.generate_assignment(stmt)
        elif isinstance(stmt, ExpressionStatement):
            if stmt.expression:
                self.generate_expression(stmt.expression)
                if self.expression_type(stmt.expression) != "void":
                    self.emit("ADDSP -1")
        elif isinstance(stmt, IfStatement):
            self.generate_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self.generate_while_statement(stmt)
        elif isinstance(stmt, DoWhileStatement):
            self.generate_do_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self.generate_for_statement(stmt)
        elif isinstance(stmt, ReturnStatement):
            self.generate_return_statement(stmt)
        elif isinstance(stmt, PrintStatement):
            self.generate_print_statement(stmt)

    def generate_variable_decl(self, decl: VariableDecl) -> None:
        offset = self.next_local_offset
        self.next_local_offset += 1
        self.define_symbol(decl.name, decl.type_name, offset)

        if decl.initial_value:
            self.generate_expression(decl.initial_value)
            self.emit_assignment_conversion(self.expression_type(decl.initial_value), decl.type_name)
            self.emit(f"STOREOFF {offset}")

    def generate_assignment(self, assign: Assignment) -> None:
        if assign.index:
            raise CodeGenError("Array assignment is not supported by the reference SaM variant")

        target_type, offset = self.require_symbol(assign.target)
        self.generate_expression(assign.value)
        self.emit_assignment_conversion(self.expression_type(assign.value), target_type)
        self.emit(f"STOREOFF {offset}")

    def generate_if_statement(self, if_stmt: IfStatement) -> None:
        true_label = self.new_label("VERDADEIRO")
        end_label = self.new_label("FIM_SE")

        self.generate_expression(if_stmt.condition)
        self.emit(f"JUMPC {true_label}")

        if if_stmt.else_block:
            self.push_scope()
            self.generate_block(if_stmt.else_block)
            self.pop_scope()

        self.emit(f"JUMP {end_label}")
        self.emit_label(true_label)

        if if_stmt.then_block:
            self.push_scope()
            self.generate_block(if_stmt.then_block)
            self.pop_scope()

        self.emit_label(end_label)

    def generate_while_statement(self, while_stmt: WhileStatement) -> None:
        start_label = self.new_label("ENQUANTO_INICIO")
        end_label = self.new_label("ENQUANTO_FIM")

        self.emit_label(start_label)
        self.generate_expression(while_stmt.condition)
        self.emit("NOT")
        self.emit(f"JUMPC {end_label}")

        if while_stmt.body:
            self.push_scope()
            self.generate_block(while_stmt.body)
            self.pop_scope()

        self.emit(f"JUMP {start_label}")
        self.emit_label(end_label)

    def generate_do_while_statement(self, do_stmt: DoWhileStatement) -> None:
        start_label = self.new_label("FACA_INICIO")

        self.emit_label(start_label)
        if do_stmt.body:
            self.push_scope()
            self.generate_block(do_stmt.body)
            self.pop_scope()

        self.generate_expression(do_stmt.condition)
        self.emit(f"JUMPC {start_label}")

    def generate_for_statement(self, for_stmt: ForStatement) -> None:
        _, offset = self.require_symbol(for_stmt.variable)
        start_label = self.new_label("PARA_INICIO")
        end_label = self.new_label("PARA_FIM")

        self.generate_expression(for_stmt.start)
        self.emit(f"STOREOFF {offset}")

        self.emit_label(start_label)
        self.emit(f"PUSHOFF {offset}")
        self.generate_expression(for_stmt.end)
        self.emit("GREATER")
        self.emit(f"JUMPC {end_label}")

        if for_stmt.body:
            self.push_scope()
            self.generate_block(for_stmt.body)
            self.pop_scope()

        self.emit(f"PUSHOFF {offset}")
        self.emit("PUSHIMM 1")
        self.emit("ADD")
        self.emit(f"STOREOFF {offset}")
        self.emit(f"JUMP {start_label}")
        self.emit_label(end_label)

    def generate_return_statement(self, ret_stmt: ReturnStatement) -> None:
        if ret_stmt.value:
            self.generate_expression(ret_stmt.value)
            if self.current_return_type:
                self.emit_assignment_conversion(
                    self.expression_type(ret_stmt.value),
                    self.current_return_type,
                )
            return_offset = -(self.current_arg_count + 1)
            self.emit(f"STOREOFF {return_offset}")

        self.emit_function_epilogue()

    def generate_print_statement(self, stmt: PrintStatement) -> None:
        if not stmt.argument:
            return

        self.generate_expression(stmt.argument)
        arg_type = self.expression_type(stmt.argument)
        if arg_type == "float":
            self.emit("WRITEF")
        elif arg_type == "char":
            self.emit("WRITECH")
        elif arg_type == "string":
            self.emit("WRITES")
        else:
            self.emit("WRITE")

    def generate_expression(self, expr: Expression) -> None:
        if isinstance(expr, Literal):
            self.generate_literal(expr)
        elif isinstance(expr, Identifier):
            _, offset = self.require_symbol(expr.name)
            self.emit(f"PUSHOFF {offset}")
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
        arithmetic = expr.operator in ["+", "-", "*", "/", "%"]
        use_float = arithmetic and result_type == "float"

        if use_float:
            self.generate_expression_as(expr.left, "float")
            self.generate_expression_as(expr.right, "float")
        else:
            self.generate_expression(expr.left)
            self.generate_expression(expr.right)

        if use_float:
            instructions = {
                "+": "ADDF",
                "-": "SUBF",
                "*": "TIMESF",
                "/": "DIVF",
                "%": "MOD",
            }
        elif left_type == "float" and right_type == "float" and expr.operator in ["==", "!=", "<", ">", "<=", ">="]:
            instructions = {
                "==": ["CMPF", "ISNIL"],
                "!=": ["CMPF", "ISNIL", "NOT"],
                "<": ["CMPF", "ISNEG"],
                ">": ["CMPF", "ISPOS"],
                "<=": ["CMPF", "ISPOS", "NOT"],
                ">=": ["CMPF", "ISNEG", "NOT"],
            }
        else:
            instructions = {
                "+": "ADD",
                "-": "SUB",
                "*": "TIMES",
                "/": "DIV",
                "%": "MOD",
                "==": "EQUAL",
                "!=": ["EQUAL", "NOT"],
                "<": "LESS",
                ">": "GREATER",
                "<=": ["GREATER", "NOT"],
                ">=": ["LESS", "NOT"],
                "&&": "AND",
                "||": "OR",
            }

        instruction = instructions.get(expr.operator)
        if instruction is None:
            raise CodeGenError(f"Unknown binary operator: {expr.operator}")
        self.emit_instruction_or_sequence(instruction)

    def emit_instruction_or_sequence(self, instruction) -> None:
        if isinstance(instruction, list):
            for item in instruction:
                self.emit(item)
        else:
            self.emit(instruction)

    def generate_unary_expression(self, expr: UnaryExpression) -> None:
        if expr.operator == "-":
            if self.expression_type(expr.operand) == "float":
                self.emit("PUSHIMMF 0.0")
                self.generate_expression(expr.operand)
                self.emit("SUBF")
            else:
                self.emit("PUSHIMM 0")
                self.generate_expression(expr.operand)
                self.emit("SUB")
        elif expr.operator == "!":
            self.generate_expression(expr.operand)
            self.emit("NOT")
        else:
            raise CodeGenError(f"Unknown unary operator: {expr.operator}")

    def generate_function_call(self, call: FunctionCall) -> None:
        if call.name not in self.function_table:
            raise CodeGenError(f"Undefined function: {call.name}")

        self.emit("ADDSP 1")
        for arg, target_type in zip(call.arguments, self.function_param_types.get(call.name, [])):
            self.generate_expression(arg)
            self.emit_assignment_conversion(self.expression_type(arg), target_type)

        self.emit("LINK")
        self.emit(f"JSR FUNCAO_{call.name}")
        self.emit("POPFBR")

        if call.arguments:
            self.emit(f"ADDSP -{len(call.arguments)}")

    def generate_array_access(self, expr: ArrayAccess) -> None:
        _, offset = self.require_symbol(expr.array_name)
        self.generate_expression(expr.index)
        self.emit(f"PUSHOFF {offset}")
        self.emit("ADD")
        self.emit("PUSHIND")

    def generate_literal(self, literal: Literal) -> None:
        if literal.type_name == "float":
            self.emit(f"PUSHIMMF {literal.value}")
        elif literal.type_name == "char":
            escaped = self.escape_char_literal(literal.value)
            self.emit(f"PUSHIMMCH '{escaped}'")
        elif literal.type_name == "bool":
            self.emit(f"PUSHIMM {1 if literal.value else 0}")
        elif literal.type_name == "string":
            escaped = literal.value.replace("\\", "\\\\").replace('"', '\\"')
            self.emit(f'PUSHS "{escaped}"')
        else:
            self.emit(f"PUSHIMM {literal.value}")

    def generate_expression_as(self, expr: Expression, target_type: str) -> None:
        actual_type = self.expression_type(expr)
        self.generate_expression(expr)
        self.emit_assignment_conversion(actual_type, target_type)

    def emit_assignment_conversion(self, from_type: str, to_type: str) -> None:
        if from_type == "int" and to_type == "float":
            self.emit("ITOF")

    def expression_type(self, expr: Expression) -> str:
        if isinstance(expr, Literal):
            return expr.type_name
        if isinstance(expr, Identifier):
            type_name, _ = self.require_symbol(expr.name)
            return type_name
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
            return return_type if return_type else "void"
        if isinstance(expr, ArrayAccess):
            type_name, _ = self.require_symbol(expr.array_name)
            return type_name
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
            elif isinstance(stmt, DoWhileStatement) and stmt.body:
                count += self.count_locals(stmt.body)
            elif isinstance(stmt, ForStatement) and stmt.body:
                count += self.count_locals(stmt.body)
        return count

    @staticmethod
    def escape_char_literal(value: str) -> str:
        return (
            value
            .replace("\\", "\\\\")
            .replace("\n", "\\n")
            .replace("\t", "\\t")
            .replace("\r", "\\r")
            .replace("'", "\\'")
        )
