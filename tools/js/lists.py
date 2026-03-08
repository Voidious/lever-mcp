"""
JavaScript-specific implementation for the 'lists' tool.

This module provides JavaScript expression evaluation capabilities while using
shared implementations for both pure and expression-based operations.
"""

from typing import Any, Optional
from lib.js import evaluate_expression
from tools.common.lists import lists_operation


def lists_tool(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
) -> dict:
    """MCP tool wrapper for list operations."""
    return _lists_impl(items, operation, param, others, expression)


def _js_expr_handler(
    expression: str, item: Any, index: int, items: list, context: Optional[dict] = None
) -> Any:
    """
    Handle JavaScript expression evaluation for expression-based operations.

    Args:
        expression: The JavaScript expression to evaluate
        item: The current item being processed
        index: The 1-based index of the item (converted from 1-based to 0-based)
        items: The full list being processed
        context: Optional additional context for the expression

    Returns:
        The result of evaluating the expression
    """
    # Set up context with item, index, and items available
    # Note: JavaScript uses 0-based indexing, so we convert from 1-based
    full_context = {
        "item": item,
        "index": index - 1,  # Convert to 0-based for JavaScript
        "items": items,
    }
    if context:
        # For context provided by common operations (like 'acc' in reduce),
        # we might want to convert some values too if they are 1-based,
        # but usually they are just values.
        full_context.update(context)

    return evaluate_expression(expression, item, context=full_context)


def _lists_impl(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        # Delegate to common operation (no wrapping needed for JS)
        result = lists_operation(
            items=items,
            operation=operation,
            param=param,
            others=others,
            expression=expression,
            expr_handler=_js_expr_handler,
            wrap=False,
        )

        return result

    except Exception as e:
        return {"error": f"Lists operation failed: {str(e)}"}
