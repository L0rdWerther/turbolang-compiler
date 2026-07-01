from typing import Dict, Optional, List, Any
from dataclasses import dataclass

@dataclass
class Symbol:
    name: str
    type_name: str
    is_array: bool = False
    array_size: Optional[int] = None
    is_parameter: bool = False
    scope_level: int = 0
    offset: int = 0

class SymbolTable:

    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]
        self.scope_level = 0
        self.current_offset = 0

    def push_scope(self):
        self.scopes.append({})
        self.scope_level += 1

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.scope_level -= 1

    def reset_offset(self):
        self.current_offset = 0

    def define(self, name: str, type_name: str, is_array: bool=False, array_size: Optional[int]=None, is_parameter: bool=False) -> Symbol:
        if name in self.scopes[-1]:
            raise ValueError(f"Symbol '{name}' already defined in current scope")
        symbol = Symbol(name=name, type_name=type_name, is_array=is_array, array_size=array_size, is_parameter=is_parameter, scope_level=self.scope_level, offset=self.current_offset)
        self.scopes[-1][name] = symbol
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
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_in_current_scope(self, name: str) -> Optional[Symbol]:
        return self.scopes[-1].get(name)

    def get_all_symbols_in_scope(self) -> Dict[str, Symbol]:
        return self.scopes[-1].copy()

    def exists(self, name: str) -> bool:
        return self.lookup(name) is not None

    def exists_in_current_scope(self, name: str) -> bool:
        return name in self.scopes[-1]

class FunctionTable:

    def __init__(self):
        self.functions: Dict[str, 'FunctionInfo'] = {}

    @dataclass
    class FunctionInfo:
        name: str
        return_type: Optional[str]
        parameters: List[tuple]
        parameters_count: int

    def define(self, name: str, return_type: Optional[str], parameters: List[tuple]) -> 'FunctionTable.FunctionInfo':
        if name in self.functions:
            raise ValueError(f"Function '{name}' already defined")
        info = self.FunctionInfo(name=name, return_type=return_type, parameters=parameters, parameters_count=len(parameters))
        self.functions[name] = info
        return info

    def lookup(self, name: str) -> Optional['FunctionTable.FunctionInfo']:
        return self.functions.get(name)

    def exists(self, name: str) -> bool:
        return name in self.functions
