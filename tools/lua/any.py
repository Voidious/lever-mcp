"""
Lua-specific implementation for the 'any' tool.

This module provides Lua expression evaluation capabilities while using
shared implementations for non-expression operations.
"""

from typing import Any, Optional
from lib.lua import evaluate_expression
from tools.common.any import any_operation


def any_tool(
    value: Any,
    operation: str,
    param: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """MCP tool wrapper for type-agnostic operations with Lua expressions."""
    return _any_impl(value, operation, param, expression, wrap=False)


def _evaluate_expression_optimized(expr, value, value_context=None):
    """Optimized expression evaluation with fast path for simple key access."""
    if isinstance(value, dict) and expr.isidentifier() and expr in value:
        # Fast path: simple key lookup without Lua runtime
        return value[expr]
    else:
        # Full expression evaluation with any context (includes dict keys as variables)
        context = value_context or {}
        return evaluate_expression(expr, value, context=context)


def _lua_eval_handler(expression: str, value: Any) -> Any:
    """
    Handle Lua expression evaluation for the eval operation.

    Args:
        expression: The Lua expression to evaluate
        value: The input value to use as context

    Returns:
        The result of evaluating the expression
    """
    # Create a context where both dict property access AND 'value' parameter work
    context = {"value": value}
    if isinstance(value, dict):
        # Add dict keys as direct variables for convenience
        for key, val in value.items():
            if (
                isinstance(key, str)
                and key.isidentifier()
                and key
                not in ["and", "or", "not", "if", "then", "else", "end", "value"]
            ):
                context[key] = val

    return _evaluate_expression_optimized(expression, value, value_context=context)


def _any_impl(
    value: Any,
    operation: str,
    param: Any = None,
    expression: Optional[str] = None,
    wrap: bool = False,
) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        from . import unwrap_input, unwrap_list_input

        # Unwrap input parameters with appropriate handling
        # contains operation can work with strings or lists, so use
        # unwrap_list_input for value
        if operation == "contains":
            value = unwrap_list_input(value)
        else:
            value = unwrap_input(value)

        param = unwrap_input(param)

        return any_operation(
            value=value,
            operation=operation,
            param=param,
            expression=expression,
            eval_handler=_lua_eval_handler,
            wrap=wrap,
        )
    except Exception as e:
        return {"error": f"Any operation failed: {str(e)}"}
