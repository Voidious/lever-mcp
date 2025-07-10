"""
JavaScript-specific implementation for the 'dicts' tool.

This module provides JavaScript expression evaluation capabilities while using
shared implementations for both pure and expression-based operations.
"""

from typing import Any, Optional
from lib.js import evaluate_expression
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
    return _dicts_impl(obj, operation, param, path, value, default, expression)


def _js_expr_handler(
    expression: str, key_or_value: Any, key: Any, value: Any, obj: Any
) -> Any:
    """
    Handle JavaScript expression evaluation for expression-based operations.

    Args:
        expression: The JavaScript expression to evaluate
        key_or_value: The primary value being transformed (key for map_keys,
            value for map_values)
        key: The current key
        value: The current value
        obj: The original dictionary

    Returns:
        The result of evaluating the expression
    """
    # Set up context with key, value, and obj available
    context = {}
    if key is not None:
        context["key"] = key
    if value is not None:
        context["value"] = value
    if obj is not None:
        context["obj"] = obj

    return evaluate_expression(expression, key_or_value, context=context)


def _dicts_impl(
    obj: Any,
    operation: str,
    param: Any = None,
    path: Any = None,
    value: Any = None,
    default: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        # Convert PythonMonkey objects to pure Python objects to avoid copy issues
        def clean_object(item):
            if isinstance(item, dict):
                return {key: clean_object(val) for key, val in item.items()}
            elif isinstance(item, list):
                return [clean_object(val) for val in item]
            elif isinstance(item, float) and item.is_integer():
                return int(item)
            else:
                return item

        cleaned_obj = clean_object(obj)
        cleaned_param = clean_object(param) if param is not None else None
        cleaned_value = clean_object(value) if value is not None else None
        cleaned_default = clean_object(default) if default is not None else None

        # Delegate to common operation (no wrapping needed for JS)
        result = dicts_operation(
            obj=cleaned_obj,
            operation=operation,
            param=cleaned_param,
            path=path,
            value=cleaned_value,
            default=cleaned_default,
            expression=expression,
            expr_handler=_js_expr_handler,
            wrap=False,
        )

        return result

    except Exception as e:
        return {"error": f"Dicts operation failed: {str(e)}"}
