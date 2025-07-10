"""
Lua-specific implementation for the 'lists' tool.

This module provides Lua expression evaluation capabilities while using
shared implementations for both pure and expression-based operations.
"""

from typing import Any, Optional
from lib.lua import evaluate_expression
from tools.common.lists import lists_operation


def lists_tool(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
) -> dict:
    """MCP tool wrapper for list operations."""
    return _lists_impl(items, operation, param, others, expression, wrap=False)


def _evaluate_expression_optimized(expr, item, index=None, items_list=None):
    """Optimized expression evaluation with fast path for simple key access."""
    if isinstance(item, dict) and expr.isidentifier() and expr in item:
        # Fast path: simple key lookup without Lua runtime
        return item[expr]
    else:
        # Full expression evaluation with lists context
        context = {"item": item}
        if index is not None:
            context["index"] = index
        if items_list is not None:
            context["items"] = items_list
        return evaluate_expression(expr, item, context=context)


def _lua_expr_handler(expression: str, item: Any, index: int, items: list) -> Any:
    """
    Handle Lua expression evaluation for expression-based operations.

    Args:
        expression: The Lua expression to evaluate
        item: The current item being processed
        index: The 1-based index of the item
        items: The full list being processed

    Returns:
        The result of evaluating the expression
    """
    return _evaluate_expression_optimized(expression, item, index, items)


def _lists_impl(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
    wrap: bool = False,
) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        from lib.lua import _apply_wrapping
        from . import unwrap_input, unwrap_list_input

        # Unwrap input parameters with appropriate handling
        items = unwrap_list_input(items)  # Always expect a list
        others = (
            None if others is None else unwrap_list_input(others)
        )  # Always expect a list when provided

        # param could be a list (for is_equal) or scalar (for most operations)
        # Use list unwrapping for is_equal, standard unwrapping for others
        if operation == "is_equal":
            param = unwrap_list_input(param)
        else:
            param = unwrap_input(param)

        # Delegate to common operation
        result = lists_operation(
            items=items,
            operation=operation,
            param=param,
            others=others,
            expression=expression,
            expr_handler=_lua_expr_handler,
            wrap=False,
        )

        # Apply wrapping if requested
        if wrap and "value" in result and result["value"] is not None:
            result["value"] = _apply_wrapping(result["value"], wrap)

        return result

    except Exception as e:
        return {"error": f"Lists operation failed: {str(e)}"}
