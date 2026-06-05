"""
Type checker for semantic validation.
"""

from typing import Optional, Tuple


class TypeCheckError(Exception):
    """Exception for type checking errors."""
    pass


class TypeChecker:
    """
    Type checker for TurboLang.
    Validates type compatibility and operations.
    """
    
    # Valid types
    VALID_TYPES = {'int', 'float', 'char', 'bool', 'string'}
    
    # Numeric types
    NUMERIC_TYPES = {'int', 'float'}
    
    # Comparable types
    COMPARABLE_TYPES = {'int', 'float', 'char'}
    
    # Boolean types
    BOOLEAN_TYPES = {'bool'}
    
    @staticmethod
    def is_valid_type(type_name: str) -> bool:
        """Check if a type is valid."""
        return type_name in TypeChecker.VALID_TYPES
    
    @staticmethod
    def is_numeric_type(type_name: str) -> bool:
        """Check if a type is numeric."""
        return type_name in TypeChecker.NUMERIC_TYPES
    
    @staticmethod
    def is_comparable_type(type_name: str) -> bool:
        """Check if a type can be compared."""
        return type_name in TypeChecker.COMPARABLE_TYPES
    
    @staticmethod
    def is_boolean_type(type_name: str) -> bool:
        """Check if a type is boolean."""
        return type_name in TypeChecker.BOOLEAN_TYPES
    
    @staticmethod
    def binary_operation_type(left_type: str, operator: str, right_type: str) -> str:
        """
        Determine the result type of a binary operation.
        
        Args:
            left_type: Type of left operand
            operator: Operation operator
            right_type: Type of right operand
            
        Returns:
            Result type
            
        Raises:
            TypeCheckError: If operation is invalid
        """
        # Arithmetic operations
        if operator in ['+', '-', '*', '/', '%']:
            if not TypeChecker.is_numeric_type(left_type):
                raise TypeCheckError(f"Left operand of {operator} must be numeric, got {left_type}")
            if not TypeChecker.is_numeric_type(right_type):
                raise TypeCheckError(f"Right operand of {operator} must be numeric, got {right_type}")
            
            # int + int = int, int + float = float, float + float = float
            if left_type == 'float' or right_type == 'float':
                return 'float'
            return 'int'
        
        # Comparison operations
        if operator in ['==', '!=']:
            if left_type != right_type:
                raise TypeCheckError(f"Cannot compare {left_type} and {right_type}")
            return 'bool'
        
        if operator in ['<', '>', '<=', '>=']:
            if not TypeChecker.is_comparable_type(left_type):
                raise TypeCheckError(f"Left operand of {operator} must be comparable, got {left_type}")
            if not TypeChecker.is_comparable_type(right_type):
                raise TypeCheckError(f"Right operand of {operator} must be comparable, got {right_type}")
            if left_type != right_type:
                raise TypeCheckError(f"Cannot compare {left_type} and {right_type}")
            return 'bool'
        
        # Logical operations
        if operator in ['&&', '||']:
            if not TypeChecker.is_boolean_type(left_type):
                raise TypeCheckError(f"Left operand of {operator} must be bool, got {left_type}")
            if not TypeChecker.is_boolean_type(right_type):
                raise TypeCheckError(f"Right operand of {operator} must be bool, got {right_type}")
            return 'bool'
        
        raise TypeCheckError(f"Unknown operator: {operator}")
    
    @staticmethod
    def unary_operation_type(operator: str, operand_type: str) -> str:
        """
        Determine the result type of a unary operation.
        
        Args:
            operator: Operation operator
            operand_type: Type of operand
            
        Returns:
            Result type
            
        Raises:
            TypeCheckError: If operation is invalid
        """
        if operator == '-':
            if not TypeChecker.is_numeric_type(operand_type):
                raise TypeCheckError(f"Operand of - must be numeric, got {operand_type}")
            return operand_type
        
        if operator == '!':
            if not TypeChecker.is_boolean_type(operand_type):
                raise TypeCheckError(f"Operand of ! must be bool, got {operand_type}")
            return 'bool'
        
        raise TypeCheckError(f"Unknown unary operator: {operator}")
    
    @staticmethod
    def is_compatible_assignment(from_type: str, to_type: str) -> bool:
        """
        Check if a value of from_type can be assigned to a variable of to_type.
        
        Args:
            from_type: Type of value being assigned
            to_type: Type of variable receiving value
            
        Returns:
            True if compatible, False otherwise
        """
        if from_type == to_type:
            return True
        
        # Allow int to float conversion
        if from_type == 'int' and to_type == 'float':
            return True
        
        return False