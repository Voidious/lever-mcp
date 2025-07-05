"""
Dicts tool implementation for Lever MCP.

This module contains the dicts tool functionality for dictionary operations
including merge, get/set values, key manipulation, and property checks.
"""

from typing import Any, Optional
import copy
import re
from lib.lua import _unwrap_input, _apply_wrapping, evaluate_expression


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
    # Unwrap input parameters
    obj = _unwrap_input(obj)
    param = _unwrap_input(param)
    path = _unwrap_input(path)
    value = _unwrap_input(value)
    default = _unwrap_input(default)

    # Handle wrapped dict objects (legacy code)
    if isinstance(obj, dict) and "__type" in obj and "data" in obj:
        if obj["__type"] == "dict":
            obj = obj["data"]
            # Convert Lua table to Python dict if needed
            if hasattr(obj, "items"):
                obj = dict(obj)
        elif obj["__type"] == "list" and operation == "merge":
            # Special case: merge operation can accept wrapped lists containing dicts
            obj = obj["data"]
            if hasattr(obj, "keys"):
                # Convert Lua table list to Python list
                keys = list(obj.keys())
                if keys and all(isinstance(k, int) and k > 0 for k in keys):
                    max_k = max(keys)
                    obj = [obj.get(k) for k in range(1, max_k + 1)]
                else:
                    obj = list(obj.values())

    try:
        # Add type validation for dict operations - dicts tool should only work on
        # dictionaries
        # For comparing any types, use any.is_equal instead
        if (
            operation not in ["merge", "is_empty"]
            and obj is not None
            and not isinstance(obj, dict)
        ):
            return {
                "value": None,
                "error": (
                    f"Dict operation '{operation}' requires a dictionary input, "
                    f"got {type(obj).__name__}. Use 'any.is_equal' for comparing "
                    "non-dictionary types."
                ),
            }

        if operation == "merge":

            def deep_merge(a, b):
                for k, v in b.items():
                    if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                        a[k] = deep_merge(a[k], v)
                    else:
                        a[k] = copy.deepcopy(v)
                return a

            result = {}
            for d in obj:
                if not isinstance(d, dict):
                    return {
                        "value": None,
                        "error": "All items in obj must be dictionaries for merge.",
                    }
                result = deep_merge(result, d)
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "invert":
            result = {str(value): key for key, value in obj.items()}
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "pick":
            if param is None:
                raise ValueError("'param' (list of keys) is required for 'pick'.")
            result = {key: obj[key] for key in param if key in obj}
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "omit":
            if param is None:
                raise ValueError("'param' (list of keys) is required for 'omit'.")
            result = {key: value for key, value in obj.items() if key not in param}
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "set_value":
            if not isinstance(obj, dict):
                return {"value": None, "error": "obj must be a dict for set_value."}
            if not isinstance(path, (str, list)):
                return {
                    "value": None,
                    "error": "'path' must be a string or list for set_value.",
                }
            if isinstance(path, list):
                if not path or not all(isinstance(k, str) for k in path):
                    return {
                        "value": None,
                        "error": (
                            "'path' list elements must all be non-empty strings "
                            "for set_value."
                        ),
                    }
            p = path
            if isinstance(p, str):
                p = re.findall(r"[^.\[\]]+", p)
            d = obj
            for k in p[:-1]:
                if k not in d or not isinstance(d[k], dict):
                    d[k] = {}
                d = d[k]
            d[p[-1]] = value
            return {"value": _apply_wrapping(obj, wrap)}
        elif operation == "get_value":
            if not isinstance(obj, dict):
                return {"value": None, "error": "obj must be a dict for get_value."}
            if not isinstance(path, (str, list)):
                return {
                    "value": None,
                    "error": "'path' must be a string or list for get_value.",
                }
            if isinstance(path, list):
                if not path or not all(isinstance(k, str) for k in path):
                    return {
                        "value": None,
                        "error": (
                            "'path' list elements must all be non-empty strings "
                            "for get_value."
                        ),
                    }
            p = path
            if isinstance(p, str):
                p = re.findall(r"[^.\[\]]+", p)
            d = obj
            for k in p:
                if isinstance(d, dict) and k in d:
                    d = d[k]
                else:
                    return {"value": default}
            return {"value": d}
        elif operation == "has_key":
            if not isinstance(obj, dict):
                return {"value": None, "error": "obj must be a dict for has_key."}
            return {"value": bool(param in obj)}
        elif operation == "is_equal":
            return {"value": obj == param}
        elif operation == "is_empty":
            if isinstance(obj, dict):
                return {"value": len(obj) == 0}
            elif obj is None:
                return {"value": True}
            elif obj == 0 or obj is False:
                return {"value": True}
            else:
                return {"value": False}
        elif operation == "keys":
            if not isinstance(obj, dict):
                return {"value": None, "error": "obj must be a dict for keys operation"}
            result = list(obj.keys())
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "values":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for values operation",
                }
            result = list(obj.values())
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "items":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for items operation",
                }
            result = list(obj.items())
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "map_keys":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for map_keys operation",
                }
            if not expression:
                return {
                    "value": None,
                    "error": "expression is required for map_keys operation",
                }
            result = {}
            for key, value in obj.items():
                # For map_keys, evaluate expression with key as the item
                # This allows tool function references to work with auto-wrap
                new_key = _evaluate_expression_optimized(
                    expression, key, key=key, value=value, obj=obj
                )
                result[str(new_key)] = value
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "map_values":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for map_values operation",
                }
            if not expression:
                return {
                    "value": None,
                    "error": "expression is required for map_values operation",
                }
            result = {}
            for key, value in obj.items():
                # For map_values, evaluate expression with value as the item
                # This allows tool function references to work with auto-wrap
                new_value = _evaluate_expression_optimized(
                    expression, value, key=key, value=value, obj=obj
                )
                result[key] = new_value
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "flatten_keys":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for flatten_keys operation",
                }

            def flatten_dict(d, parent_key="", sep="."):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return dict(items)

            result = flatten_dict(obj)
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "unflatten_keys":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for unflatten_keys operation",
                }

            result = {}
            for key, value in obj.items():
                keys = key.split(".")
                d = result
                for k in keys[:-1]:
                    if k not in d:
                        d[k] = {}
                    d = d[k]
                d[keys[-1]] = value

            return {"value": _apply_wrapping(result, wrap)}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}
