"""
Common operations for the 'any' tool that don't require expression evaluation.

This module contains shared implementations for type-agnostic property checks
and comparisons that work the same way regardless of expression language.
"""

from typing import Any, Callable, Dict, Optional


def op_is_equal(value: Any, param: Any = None, **kwargs) -> dict:
    """Check if two values are deeply equal."""
    return {"value": value == param}


def op_is_empty(value: Any, **kwargs) -> dict:
    """Check if the value is empty."""
    if value is None or value == 0 or value is False:
        return {"value": True}
    if isinstance(value, (str, list, dict)):
        return {"value": len(value) == 0}
    return {"value": False}


def op_is_nil(value: Any, **kwargs) -> dict:
    """Check if the value is None."""
    return {"value": value is None}


def op_contains(value: Any, param: Any = None, **kwargs) -> dict:
    """Check if a string or list contains a value."""
    if isinstance(value, (str, list)):
        return {"value": param in value}
    return {"value": False}


def op_size(value: Any, **kwargs) -> dict:
    """Get the size/length of any collection type or 1 for scalars."""
    if hasattr(value, "__len__"):
        return {"value": len(value)}
    elif value is None:
        return {"value": 0}
    else:
        return {"value": 1}


def op_eval(
    value: Any,
    expression: Optional[str] = None,
    eval_handler: Optional[Callable[[str, Any], Any]] = None,
    **kwargs,
) -> dict:
    """
    Evaluate an expression with value as context.

    This operation requires an eval_handler function that knows how to
    evaluate expressions in the target language (Lua or JavaScript).
    """
    if not expression:
        return {
            "value": None,
            "error": "Missing required expression parameter for operation 'eval'.",
        }

    if not eval_handler:
        return {
            "value": None,
            "error": "No expression handler provided for eval operation.",
        }

    try:
        result = eval_handler(expression, value)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"Error in eval expression: {e}"}


# Operation registry - maps operation names to functions
OPERATIONS: Dict[str, Callable] = {
    "is_equal": op_is_equal,
    "is_empty": op_is_empty,
    "is_nil": op_is_nil,
    "contains": op_contains,
    "size": op_size,
    "eval": op_eval,
}


def any_operation(
    value: Any,
    operation: str,
    param: Any = None,
    expression: Optional[str] = None,
    eval_handler: Optional[Callable[[str, Any], Any]] = None,
    wrap: bool = False,
) -> dict:
    """
    Execute an any tool operation.

    Args:
        value: The input value to operate on
        operation: Name of the operation to perform
        param: Optional parameter for some operations
        expression: Optional expression for eval operation
        eval_handler: Function to handle expression evaluation for eval operation
        wrap: Whether to wrap the result (for Lua compatibility)

    Returns:
        Dict with 'value' key and optional 'error' key
    """
    try:
        if operation not in OPERATIONS:
            raise ValueError(f"Unknown operation: {operation}")

        # Get the operation function and call it
        op_func = OPERATIONS[operation]
        result = op_func(
            value=value,
            param=param,
            expression=expression,
            eval_handler=eval_handler,
        )

        return result

    except Exception as e:
        return {"value": None, "error": str(e)}
