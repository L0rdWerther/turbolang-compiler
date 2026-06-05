"""
Code generator for TurboLang.
Generates SaM assembly code from the AST.
"""

from typing import Dict, Optional, List, Tuple
from parser.ast_nodes import *
from semantic.symbol_table import SymbolTable, FunctionTable
from codegen.sam_instructions import InstructionBuffer, OpCode


class CodeGenError(Exception):
    """Exception for code generation errors."""
    pass


class CodeGenerator:
    """
    Code generator for TurboLang.
    Converts AST to SaM assembly code.
    """
    
    def __init__(self):
        """Initialize code generator."""
        self.buffer = InstructionBuffer()
        self.symbol_table = SymbolTable()
        self.function_table: Dict[str, Tuple[Optional[str], List[str]]] = {}
        self.current_function: Optional[str] = None
        self.function_labels: Dict[str, str] = {}

    def generate(self, program: Program) -> str:
        # Register all functions
        for func in program.functions:
            label = self.buffer.generate_label()
            self.function_labels[func.name] = label
            self.function_table[func.name] = (func.return_type,
                                              [p.name for p in func.parameters])

        # Generate function code
        for func in program.functions:
            self.generate_function(func)

        return self.buffer.get_code()

    def generate_function(self, func: FunctionDecl) -> None:
        """Generate code for a function."""
        self.current_function = func.name
        self.symbol_table.push_scope()
        self.symbol_table.reset_offset()

        self.buffer.emit_label(self.function_labels[func.name])

        for param in func.parameters:
            self.symbol_table.define(param.name, param.type_name, is_parameter=True)

        if func.body:
            self.generate_block(func.body)

        # main termina com HALT; funções void terminam com RET
        if func.name == 'main':
            self.buffer.emit(OpCode.HALT)
        elif not func.return_type:
            self.buffer.emit(OpCode.RET)

        self.symbol_table.pop_scope()
        self.current_function = None
    
    def generate_block(self, block: Block) -> None:
        """Generate code for a block."""
        for stmt in block.statements:
            self.generate_statement(stmt)
    
    def generate_statement(self, stmt: Statement) -> None:
        """Generate code for a statement."""
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
                # Pop unused result
                self.buffer.emit(OpCode.POP)
        
        elif isinstance(stmt, IfStatement):
            self.generate_if_statement(stmt)
        
        elif isinstance(stmt, WhileStatement):
            self.generate_while_statement(stmt)
        
        elif isinstance(stmt, ReturnStatement):
            self.generate_return_statement(stmt)
        
        elif isinstance(stmt, PrintStatement):
            if stmt.argument:
                self.generate_expression(stmt.argument)
                self.buffer.emit(OpCode.PRINT)
    
    def generate_variable_decl(self, decl: VariableDecl) -> None:
        """Generate code for variable declaration."""
        # Define in symbol table
        self.symbol_table.define(decl.name, decl.type_name)
        
        # If initialized, generate initialization code
        if decl.initial_value:
            self.generate_expression(decl.initial_value)
            symbol = self.symbol_table.lookup(decl.name)
            self.buffer.emit(OpCode.STORE, symbol.offset)
    
    def generate_assignment(self, assign: Assignment) -> None:
        """Generate code for assignment."""
        # Generate value expression
        self.generate_expression(assign.value)
        
        # Store in variable
        symbol = self.symbol_table.lookup(assign.target)
        if not symbol:
            raise CodeGenError(f"Undefined variable: {assign.target}")
        
        self.buffer.emit(OpCode.STORE, symbol.offset)

    def generate_if_statement(self, if_stmt: IfStatement) -> None:
        """Generate code for if statement."""
        # Com else: precisamos de dois labels
        # Sem else: só precisamos do label de fim
        if if_stmt.else_block:
            else_label = self.buffer.generate_label()
            end_label = self.buffer.generate_label()

            self.generate_expression(if_stmt.condition)
            self.buffer.emit(OpCode.JZ, else_label)

            if if_stmt.then_block:
                self.generate_block(if_stmt.then_block)

            self.buffer.emit(OpCode.JMP, end_label)

            self.buffer.emit_label(else_label)
            self.generate_block(if_stmt.else_block)

            self.buffer.emit_label(end_label)
        else:
            end_label = self.buffer.generate_label()

            self.generate_expression(if_stmt.condition)
            self.buffer.emit(OpCode.JZ, end_label)

            if if_stmt.then_block:
                self.generate_block(if_stmt.then_block)

            self.buffer.emit_label(end_label)
    
    def generate_while_statement(self, while_stmt: WhileStatement) -> None:
        """Generate code for while loop."""
        loop_label = self.buffer.generate_label()
        end_label = self.buffer.generate_label()
        
        # Loop label
        self.buffer.emit_label(loop_label)
        
        # Generate condition
        self.generate_expression(while_stmt.condition)
        
        # Jump to end if false
        self.buffer.emit(OpCode.JZ, end_label)
        
        # Generate body
        if while_stmt.body:
            self.generate_block(while_stmt.body)
        
        # Jump back to loop
        self.buffer.emit(OpCode.JMP, loop_label)
        
        # End label
        self.buffer.emit_label(end_label)
    
    def generate_return_statement(self, ret_stmt: ReturnStatement) -> None:
        """Generate code for return statement."""
        if ret_stmt.value:
            self.generate_expression(ret_stmt.value)
        
        self.buffer.emit(OpCode.RET)
    
    def generate_expression(self, expr: Expression) -> None:
        """Generate code for an expression."""
        if isinstance(expr, Literal):
            self.buffer.emit(OpCode.PUSH, expr.value)
        
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
        """Generate code for binary expression."""
        # Generate left operand
        self.generate_expression(expr.left)
        
        # Generate right operand
        self.generate_expression(expr.right)
        
        # Generate operation
        if expr.operator == '+':
            self.buffer.emit(OpCode.ADD)
        elif expr.operator == '-':
            self.buffer.emit(OpCode.SUB)
        elif expr.operator == '*':
            self.buffer.emit(OpCode.MUL)
        elif expr.operator == '/':
            self.buffer.emit(OpCode.DIV)
        elif expr.operator == '%':
            self.buffer.emit(OpCode.MOD)
        elif expr.operator == '==':
            self.buffer.emit(OpCode.EQ)
        elif expr.operator == '!=':
            self.buffer.emit(OpCode.NE)
        elif expr.operator == '<':
            self.buffer.emit(OpCode.LT)
        elif expr.operator == '>':
            self.buffer.emit(OpCode.GT)
        elif expr.operator == '<=':
            self.buffer.emit(OpCode.LE)
        elif expr.operator == '>=':
            self.buffer.emit(OpCode.GE)
        elif expr.operator == '&&':
            self.buffer.emit(OpCode.AND)
        elif expr.operator == '||':
            self.buffer.emit(OpCode.OR)
        else:
            raise CodeGenError(f"Unknown binary operator: {expr.operator}")
    
    def generate_unary_expression(self, expr: UnaryExpression) -> None:
        """Generate code for unary expression."""
        self.generate_expression(expr.operand)
        
        if expr.operator == '-':
            self.buffer.emit(OpCode.NEG)
        elif expr.operator == '!':
            self.buffer.emit(OpCode.NOT)
        else:
            raise CodeGenError(f"Unknown unary operator: {expr.operator}")
    
    def generate_function_call(self, call: FunctionCall) -> None:
        """Generate code for function call."""
        # Generate arguments
        for arg in call.arguments:
            self.generate_expression(arg)
        
        # Call function
        label = self.function_labels.get(call.name)
        if not label:
            raise CodeGenError(f"Undefined function: {call.name}")
        
        self.buffer.emit(OpCode.CALL, label)

    def generate_array_access(self, expr: ArrayAccess) -> None:
        symbol = self.symbol_table.lookup(expr.array_name)
        if not symbol:
            raise CodeGenError(f"Undefined variable: {expr.array_name}")

        # Apenas o índice fica na pilha
        self.generate_expression(expr.index)
        
        # Emite LOAD_INDEXED passando o offset base como operando
        self.buffer.emit(OpCode.LOAD_INDEXED, symbol.offset)