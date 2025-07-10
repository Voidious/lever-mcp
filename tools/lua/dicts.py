"""
Lua-specific implementation for the 'dicts' tool.

This module provides Lua expression evaluation capabilities while using
shared implementations for both pure and expression-based operations.
"""

from typing import Any, Optional
from lib.lua import evaluate_expression
from tools.common.dicts import dicts_operation


def dicts_tool(
    obj: Any,
    operation: str,
    param: Any = None,
    path: Any = None,
    value: Any = None,
    default: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """MCP tool wrapper for dictionary operations."""
    return _dicts_impl(
        obj, operation, param, path, value, default, expression, wrap=False
    )


def _evaluate_expression_optimized(expr, key_or_value, key=None, value=None, obj=None):
    """Optimized expression evaluation with fast path for simple key access."""
    if isinstance(key_or_value, dict) and expr.isidentifier() and expr in key_or_value:
        # Fast path: simple key lookup without Lua runtime
        return key_or_value[expr]
    else:
        # Full expression evaluation with dicts context
        context = {}
        if key is not None:
            context["key"] = key
        if value is not None:
            context["value"] = value
        if obj is not None:
            context["obj"] = obj
        return evaluate_expression(expr, key_or_value, context=context)


def _lua_expr_handler(
    expression: str, key_or_value: Any, key: Any, value: Any, obj: Any
) -> Any:
    """
    Handle Lua expression evaluation for expression-based operations.

    Args:
        expression: The Lua expression to evaluate
        key_or_value: The primary value being transformed (key for map_keys,
            value for map_values)
        key: The current key
        value: The current value
        obj: The original dictionary

    Returns:
        The result of evaluating the expression
    """
    return _evaluate_expression_optimized(expression, key_or_value, key, value, obj)


def _dicts_impl(
    obj: Any,
    operation: str,
    param: Any = None,
    path: Any = None,
    value: Any = None,
    default: Any = None,
    expression: Optional[str] = None,
    wrap: bool = False,
) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        from lib.lua import _apply_wrapping
        from . import unwrap_input, unwrap_list_input

        # Unwrap input parameters with appropriate handling
        # merge operation expects a list of dicts, so use unwrap_list_input
        if operation == "merge":
            obj = unwrap_list_input(obj)
        else:
            obj = unwrap_input(obj)

        param = unwrap_input(param)
        path = unwrap_input(path)
        value = unwrap_input(value)
        default = unwrap_input(default)

        # Delegate to common operation
        result = dicts_operation(
            obj=obj,
            operation=operation,
            param=param,
            path=path,
            value=value,
            default=default,
            expression=expression,
            expr_handler=_lua_expr_handler,
            wrap=False,
        )

        # Apply wrapping if requested
        if wrap and "value" in result and result["value"] is not None:
            result["value"] = _apply_wrapping(result["value"], wrap)

        return result

    except Exception as e:
        return {"error": f"Dicts operation failed: {str(e)}"}
