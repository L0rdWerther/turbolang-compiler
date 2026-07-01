from typing import Optional, Tuple

class TypeCheckError(Exception):
    pass

class TypeChecker:
    VALID_TYPES = {'int', 'float', 'char', 'bool', 'string'}
    NUMERIC_TYPES = {'int', 'float'}
    COMPARABLE_TYPES = {'int', 'float', 'char'}
    BOOLEAN_TYPES = {'bool'}

    @staticmethod
    def is_valid_type(type_name: str) -> bool:
        return type_name in TypeChecker.VALID_TYPES

    @staticmethod
    def is_numeric_type(type_name: str) -> bool:
        return type_name in TypeChecker.NUMERIC_TYPES

    @staticmethod
    def is_comparable_type(type_name: str) -> bool:
        return type_name in TypeChecker.COMPARABLE_TYPES

    @staticmethod
    def is_boolean_type(type_name: str) -> bool:
        return type_name in TypeChecker.BOOLEAN_TYPES

    @staticmethod
    def binary_operation_type(left_type: str, operator: str, right_type: str) -> str:
        if operator in ['+', '-', '*', '/', '%']:
            if not TypeChecker.is_numeric_type(left_type):
                raise TypeCheckError(f'Left operand of {operator} must be numeric, got {left_type}')
            if not TypeChecker.is_numeric_type(right_type):
                raise TypeCheckError(f'Right operand of {operator} must be numeric, got {right_type}')
            if left_type == 'float' or right_type == 'float':
                return 'float'
            return 'int'
        if operator in ['==', '!=']:
            if left_type != right_type:
                raise TypeCheckError(f'Cannot compare {left_type} and {right_type}')
            return 'bool'
        if operator in ['<', '>', '<=', '>=']:
            if not TypeChecker.is_comparable_type(left_type):
                raise TypeCheckError(f'Left operand of {operator} must be comparable, got {left_type}')
            if not TypeChecker.is_comparable_type(right_type):
                raise TypeCheckError(f'Right operand of {operator} must be comparable, got {right_type}')
            if left_type != right_type:
                raise TypeCheckError(f'Cannot compare {left_type} and {right_type}')
            return 'bool'
        if operator in ['&&', '||']:
            if not TypeChecker.is_boolean_type(left_type):
                raise TypeCheckError(f'Left operand of {operator} must be bool, got {left_type}')
            if not TypeChecker.is_boolean_type(right_type):
                raise TypeCheckError(f'Right operand of {operator} must be bool, got {right_type}')
            return 'bool'
        raise TypeCheckError(f'Unknown operator: {operator}')

    @staticmethod
    def unary_operation_type(operator: str, operand_type: str) -> str:
        if operator == '-':
            if not TypeChecker.is_numeric_type(operand_type):
                raise TypeCheckError(f'Operand of - must be numeric, got {operand_type}')
            return operand_type
        if operator == '!':
            if not TypeChecker.is_boolean_type(operand_type):
                raise TypeCheckError(f'Operand of ! must be bool, got {operand_type}')
            return 'bool'
        raise TypeCheckError(f'Unknown unary operator: {operator}')

    @staticmethod
    def is_compatible_assignment(from_type: str, to_type: str) -> bool:
        if from_type == to_type:
            return True
        if from_type == 'int' and to_type == 'float':
            return True
        return False
