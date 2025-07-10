"""
JavaScript-specific implementation for the 'any' tool.

This module provides JavaScript expression evaluation capabilities while using
shared implementations for non-expression operations.
"""

from typing import Any, Optional
from lib.js import evaluate_expression
from tools.common.any import any_operation


def any_tool(
    value: Any,
    operation: str,
    param: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """MCP tool wrapper for type-agnostic operations."""
    return _any_impl(value, operation, param, expression)


def _js_eval_handler(expression: str, value: Any) -> Any:
    """
    Handle JavaScript expression evaluation for the eval operation.

    Args:
        expression: The JavaScript expression to evaluate
        value: The input value to use as context

    Returns:
        The result of evaluating the expression
    """
    # Create a context where both dict property access AND 'value' parameter work
    context = {"value": value}
    if isinstance(value, dict):
        # Add dict keys as direct variables for convenience
        for key, val in value.items():
            if isinstance(key, str) and key.isidentifier():
                context[key] = val

    return evaluate_expression(expression, value, context=context, safe_mode=None)


def _any_impl(
    value: Any,
    operation: str,
    param: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        # Delegate to common operation (no wrapping needed for JS)
        result = any_operation(
            value=value,
            operation=operation,
            param=param,
            expression=expression,
            eval_handler=_js_eval_handler,
            wrap=False,
        )

        return result

    except Exception as e:
        return {"error": f"Any operation failed: {str(e)}"}
