"""
Any tool implementation for Lever MCP.

This module contains the any tool functionality for type-agnostic property checks,
comparisons, and expression evaluation.
"""

from typing import Any, Optional
from lib.lua import evaluate_expression


def any_tool(
    value: Any,
    operation: str,
    param: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """MCP tool wrapper for type-agnostic operations."""
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


def _any_impl(
    value: Any,
    operation: str,
    param: Any = None,
    expression: Optional[str] = None,
    wrap: bool = False,
) -> dict:
    # Handle wrapped objects
    if isinstance(value, dict) and "__type" in value and "data" in value:
        obj_type = value["__type"]
        value = value["data"]
        # Convert Lua table to appropriate Python type if needed
        if hasattr(value, "keys"):
            if obj_type == "list":
                keys = list(value.keys())
                if keys and all(isinstance(k, int) and k > 0 for k in keys):
                    max_k = max(keys)
                    value = [value.get(k) for k in range(1, max_k + 1)]
                else:
                    value = list(value.values())
            else:  # dict type
                value = dict(value)

    try:
        if operation == "is_equal":
            return {"value": value == param}
        elif operation == "is_empty":
            if value is None or value == 0 or value is False:
                return {"value": True}
            if isinstance(value, (str, list, dict)):
                return {"value": len(value) == 0}
            return {"value": False}
        elif operation == "is_nil":
            return {"value": value is None}
        elif operation == "contains":
            if isinstance(value, (str, list)):
                return {"value": param in value}
            return {"value": False}
        elif operation == "eval":
            if not expression:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression parameter for operation 'eval'.",
                    ),
                }
            # Use evaluate_expression_optimized for consistency and to support auto-wrap
            # functionality. Create a context where both dict property access AND
            # 'value' parameter work.
            context = {"value": value}
            if isinstance(value, dict):
                # Add dict keys as direct variables for convenience
                for key, val in value.items():
                    if (
                        isinstance(key, str)
                        and key.isidentifier()
                        and key
                        not in [
                            "and",
                            "or",
                            "not",
                            "if",
                            "then",
                            "else",
                            "end",
                            "value",
                        ]
                    ):
                        context[key] = val

            try:
                result = _evaluate_expression_optimized(
                    expression, value, value_context=context
                )
                return {"value": result}
            except Exception as e:
                return {"value": None, "error": f"Error in eval expression: {e}"}
        elif operation == "size":
            if hasattr(value, "__len__"):
                return {"value": len(value)}
            elif value is None:
                return {"value": 0}
            else:
                return {"value": 1}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}
