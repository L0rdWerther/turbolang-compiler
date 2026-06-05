"""
Symbol table for semantic analysis and code generation.
Maintains scope information and variable/function definitions.
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass


@dataclass
class Symbol:
    """Represents a symbol (variable or function)."""
    name: str
    type_name: str  # int, float, char, bool, function
    is_array: bool = False
    array_size: Optional[int] = None
    is_parameter: bool = False
    scope_level: int = 0
    offset: int = 0  # For code generation (memory offset)


class SymbolTable:
    """
    Symbol table with scope management.
    Supports nested scopes for blocks and functions.
    """
    
    def __init__(self):
        """Initialize symbol table."""
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Stack of scopes
        self.scope_level = 0
        self.current_offset = 0
    
    def push_scope(self):
        """Enter a new scope."""
        self.scopes.append({})
        self.scope_level += 1
    
    def pop_scope(self):
        """Exit current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.scope_level -= 1

    def reset_offset(self):
        """Reset the current offset."""
        self.current_offset = 0
    
    def define(self, name: str, type_name: str, is_array: bool = False,
               array_size: Optional[int] = None, is_parameter: bool = False) -> Symbol:
        """
        Define a new symbol in the current scope.
        
        Args:
            name: Symbol name
            type_name: Type of the symbol
            is_array: Whether this is an array
            array_size: Size of array (if applicable)
            is_parameter: Whether this is a function parameter
            
        Returns:
            The created Symbol
        """
        if name in self.scopes[-1]:
            raise ValueError(f"Symbol '{name}' already defined in current scope")
        
        symbol = Symbol(
            name=name,
            type_name=type_name,
            is_array=is_array,
            array_size=array_size,
            is_parameter=is_parameter,
            scope_level=self.scope_level,
            offset=self.current_offset
        )
        
        self.scopes[-1][name] = symbol
        
        # Allocate memory
        if type_name in ['int', 'bool']:
            self.current_offset += 1
        elif type_name == 'float':
            self.current_offset += 1
        elif type_name == 'char':
            self.current_offset += 1
        
        if is_array and array_size:
            self.current_offset += array_size - 1
        
        return symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol in all scopes (from innermost to outermost).
        
        Args:
            name: Symbol name
            
        Returns:
            Symbol if found, None otherwise
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def lookup_in_current_scope(self, name: str) -> Optional[Symbol]:
        """Look up a symbol only in the current scope."""
        return self.scopes[-1].get(name)
    
    def get_all_symbols_in_scope(self) -> Dict[str, Symbol]:
        """Get all symbols in current scope."""
        return self.scopes[-1].copy()
    
    def exists(self, name: str) -> bool:
        """Check if a symbol exists in any scope."""
        return self.lookup(name) is not None
    
    def exists_in_current_scope(self, name: str) -> bool:
        """Check if a symbol exists in current scope."""
        return name in self.scopes[-1]


class FunctionTable:
    """
    Table for function definitions.
    """
    
    def __init__(self):
        """Initialize function table."""
        self.functions: Dict[str, 'FunctionInfo'] = {}
    
    @dataclass
    class FunctionInfo:
        """Information about a function."""
        name: str
        return_type: Optional[str]
        parameters: List[tuple]  # List of (type, name) tuples
        parameters_count: int
    
    def define(self, name: str, return_type: Optional[str], 
               parameters: List[tuple]) -> 'FunctionTable.FunctionInfo':
        """
        Define a function.
        
        Args:
            name: Function name
            return_type: Return type
            parameters: List of (type_name, param_name) tuples
        """
        if name in self.functions:
            raise ValueError(f"Function '{name}' already defined")
        
        info = self.FunctionInfo(
            name=name,
            return_type=return_type,
            parameters=parameters,
            parameters_count=len(parameters)
        )
        
        self.functions[name] = info
        return info
    
    def lookup(self, name: str) -> Optional['FunctionTable.FunctionInfo']:
        """Look up a function."""
        return self.functions.get(name)
    
    def exists(self, name: str) -> bool:
        """Check if a function is defined."""
        return name in self.functions