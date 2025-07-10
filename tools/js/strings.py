"""
JavaScript-specific implementation for the 'strings' tool.

This module provides JavaScript expression evaluation capabilities while using
shared implementations for both pure and expression-based operations.
"""

from typing import Any, Optional
from lib.js import evaluate_expression
from tools.common.strings import strings_operation


def strings_tool(
    text: str,
    operation: str,
    param: Any = None,
    data: Optional[dict] = None,
) -> dict:
    """MCP tool wrapper for string operations."""
    return _strings_impl(text, operation, param, data)


def _js_expr_handler(expression: str, text: str) -> Any:
    """
    Handle JavaScript expression evaluation for expression-based operations.

    Args:
        expression: The JavaScript expression to evaluate
        text: The text string being processed

    Returns:
        The result of evaluating the expression
    """
    # For string operations, we typically don't need expressions,
    # but if we did, we would evaluate them here
    return evaluate_expression(expression, text)


def _strings_impl(
    text: str,
    operation: str,
    param: Any = None,
    data: Optional[dict] = None,
) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        # Delegate to common operation (no wrapping needed for JS)
        result = strings_operation(
            text=text,
            operation=operation,
            param=param,
            data=data,
            wrap=False,
        )

        return result

    except Exception as e:
        return {"error": f"Strings operation failed: {str(e)}"}
