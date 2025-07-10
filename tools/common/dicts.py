"""
Common operations for the 'dicts' tool.

This module contains shared implementations for dictionary operations that
the same way regardless of expression language, plus framework for
expression-based operations.
"""

import copy
import json
from typing import Any, Callable, Dict, Optional, Union


def _safe_copy(obj):
    """Safely copy an object, handling cases where deepcopy fails."""
    try:
        return copy.deepcopy(obj)
    except (TypeError, AttributeError):
        # If deepcopy fails, try JSON serialization round-trip
        try:
            return json.loads(json.dumps(obj, default=str))
        except (TypeError, ValueError):
            # If all else fails, create a new dict manually
            if isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    if isinstance(value, dict):
                        result[key] = _safe_copy(value)
                    elif isinstance(value, list):
                        result[key] = [
                            _safe_copy(item) if isinstance(item, (dict, list)) else item
                            for item in value
                        ]
                    else:
                        result[key] = value
                return result
            else:
                return obj


def _parse_path(path: Union[str, list]) -> list:
    """Parse path string or list into list of keys."""
    if isinstance(path, str):
        return path.split(".")
    elif isinstance(path, list):
        # Validate that all list elements are strings
        if not all(isinstance(k, str) for k in path):
            raise ValueError("path list elements must all be strings")
        return path
    else:
        raise ValueError("path must be a string or list of strings")


def _deep_merge_dicts(target: dict, source: dict) -> dict:
    """Deep merge two dictionaries."""
    result = _safe_copy(target)
    for key, value in source.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dicts(result[key], value)
        else:
            result[key] = _safe_copy(value)
    return result


# Pure operations that don't require expressions


def op_merge(obj: Any, **kwargs) -> dict:
    """Deep merges a list of dictionaries."""
    if not isinstance(obj, list):
        return {
            "value": None,
            "error": "merge operation requires a list of dictionaries",
        }

    if not obj:
        return {"value": {}}

    try:
        result = {}
        for item in obj:
            if not isinstance(item, dict):
                return {
                    "value": None,
                    "error": "All items in merge list must be dictionaries",
                }
            result = _deep_merge_dicts(result, item)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"merge failed: {str(e)}"}


def op_invert(obj: dict, **kwargs) -> dict:
    """Swaps keys and values in the dictionary."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "invert operation requires a dictionary"}

    try:
        result = {str(value): key for key, value in obj.items()}
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"invert failed: {str(e)}"}


def op_pick(obj: dict, param: Any = None, **kwargs) -> dict:
    """Creates a new dictionary with only the specified keys."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "pick operation requires a dictionary"}

    if not isinstance(param, list):
        return {
            "value": None,
            "error": "pick operation requires param to be a list of keys",
        }

    try:
        result = {key: obj[key] for key in param if key in obj}
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"pick failed: {str(e)}"}


def op_omit(obj: dict, param: Any = None, **kwargs) -> dict:
    """Creates a new dictionary excluding the specified keys."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "omit operation requires a dictionary"}

    if not isinstance(param, list):
        return {
            "value": None,
            "error": "omit operation requires param to be a list of keys",
        }

    try:
        result = {key: value for key, value in obj.items() if key not in param}
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"omit failed: {str(e)}"}


def op_set_value(obj: dict, path: Any = None, value: Any = None, **kwargs) -> dict:
    """Sets a deep property value using dot notation or path list."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "set_value operation requires a dictionary"}

    if path is None:
        return {"value": None, "error": "set_value operation requires a path"}

    try:
        path_parts = _parse_path(path)
        if not path_parts:
            return {"value": None, "error": "Invalid path provided"}

        result = _safe_copy(obj)
        current = result

        # Navigate to the parent of the target key
        for key in path_parts[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

        # Set the final value
        current[path_parts[-1]] = value
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"set_value failed: {str(e)}"}


def op_get_value(obj: dict, path: Any = None, default: Any = None, **kwargs) -> dict:
    """Gets a deep property value using dot notation or path list."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "get_value operation requires a dictionary"}

    if path is None:
        return {"value": None, "error": "get_value operation requires a path"}

    try:
        path_parts = _parse_path(path)
        if not path_parts:
            return {"value": default}

        current = obj
        for key in path_parts:
            if not isinstance(current, dict) or key not in current:
                return {"value": default}
            current = current[key]

        return {"value": current}
    except Exception as e:
        return {"value": None, "error": f"get_value failed: {str(e)}"}


def op_has_key(obj: dict, param: Any = None, **kwargs) -> dict:
    """Checks if a dictionary contains a specific key."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "has_key operation requires a dictionary"}

    if param is None:
        return {"value": None, "error": "has_key operation requires a key parameter"}

    return {"value": param in obj}


def op_is_equal(obj: dict, param: Any = None, **kwargs) -> dict:
    """Performs deep equality comparison between two dictionaries."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "is_equal operation requires a dictionary"}

    return {"value": obj == param}


def op_is_empty(obj: Any, **kwargs) -> dict:
    """Checks if a dictionary is empty (or if value is falsy)."""
    if obj is None or obj == 0 or obj is False:
        return {"value": True}

    if isinstance(obj, dict):
        return {"value": len(obj) == 0}

    return {"value": False}


def op_keys(obj: dict, **kwargs) -> dict:
    """Returns a list of all dictionary keys."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "keys operation requires a dictionary"}

    return {"value": list(obj.keys())}


def op_values(obj: dict, **kwargs) -> dict:
    """Returns a list of all dictionary values."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "values operation requires a dictionary"}

    return {"value": list(obj.values())}


def op_items(obj: dict, **kwargs) -> dict:
    """Returns a list of key-value pairs as tuples."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "items operation requires a dictionary"}

    return {"value": list(obj.items())}


def op_flatten_keys(obj: dict, **kwargs) -> dict:
    """Flattens nested dictionary keys using dot notation."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "flatten_keys operation requires a dictionary"}

    def flatten_recursive(d, parent_key=""):
        items = []
        for key, value in d.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict) and value:
                items.extend(flatten_recursive(value, new_key).items())
            else:
                items.append((new_key, value))
        return dict(items)

    try:
        result = flatten_recursive(obj)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"flatten_keys failed: {str(e)}"}


def op_unflatten_keys(obj: dict, **kwargs) -> dict:
    """Converts dot-notation keys back to nested dictionary structure."""
    if not isinstance(obj, dict):
        return {
            "value": None,
            "error": "unflatten_keys operation requires a dictionary",
        }

    try:
        result = {}
        for key, value in obj.items():
            path_parts = key.split(".")
            current = result

            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[path_parts[-1]] = value

        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"unflatten_keys failed: {str(e)}"}


# Expression-based operations that require handler functions


def op_map_keys(obj: dict, expression: str, expr_handler: Callable, **kwargs) -> dict:
    """Transforms all dictionary keys using an expression."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "map_keys operation requires a dictionary"}

    if not expression:
        return {"value": None, "error": "expression is required for map_keys operation"}

    try:
        result = {}
        for key, value in obj.items():
            new_key = expr_handler(expression, key, key, value, obj)
            result[str(new_key)] = value
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"map_keys failed: {str(e)}"}


def op_map_values(obj: dict, expression: str, expr_handler: Callable, **kwargs) -> dict:
    """Transforms all dictionary values using an expression."""
    if not isinstance(obj, dict):
        return {"value": None, "error": "map_values operation requires a dictionary"}

    if not expression:
        return {
            "value": None,
            "error": "expression is required for map_values operation",
        }

    try:
        result = {}
        for key, value in obj.items():
            new_value = expr_handler(expression, value, key, value, obj)
            result[key] = new_value
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"map_values failed: {str(e)}"}


# Pure operations registry - these don't require expressions
PURE_OPERATIONS: Dict[str, Callable] = {
    "merge": op_merge,
    "invert": op_invert,
    "pick": op_pick,
    "omit": op_omit,
    "set_value": op_set_value,
    "get_value": op_get_value,
    "has_key": op_has_key,
    "is_equal": op_is_equal,
    "is_empty": op_is_empty,
    "keys": op_keys,
    "values": op_values,
    "items": op_items,
    "flatten_keys": op_flatten_keys,
    "unflatten_keys": op_unflatten_keys,
}

# Expression-based operations registry - these require an expression handler
EXPRESSION_OPERATIONS: Dict[str, Callable] = {
    "map_keys": op_map_keys,
    "map_values": op_map_values,
}


def dicts_operation(
    obj: Any,
    operation: str,
    param: Any = None,
    path: Any = None,
    value: Any = None,
    default: Any = None,
    expression: Optional[str] = None,
    expr_handler: Optional[Callable] = None,
    wrap: bool = False,
) -> dict:
    """
    Execute a dicts tool operation.

    Args:
        obj: The input object (dict for most operations, list for merge)
        operation: Name of the operation to perform
        param: Optional parameter for some operations
        path: Optional path for get_value/set_value operations
        value: Optional value for set_value operation
        default: Optional default for get_value operation
        expression: Optional expression for expression-based operations
        expr_handler: Function to handle expression evaluation
        wrap: Whether to wrap the result (for Lua compatibility)

    Returns:
        Dict with 'value' key and optional 'error' key
    """
    try:
        # Add type validation for dict operations - most should work on dictionaries
        if (
            operation not in ["merge", "is_empty"]
            and obj is not None
            and not isinstance(obj, dict)
        ):
            return {
                "value": None,
                "error": (
                    f"Dict operation '{operation}' requires a dictionary input, "
                    f"got {type(obj).__name__}. Use 'any.is_equal' for "
                    "comparing non-dictionary types."
                ),
            }

        # Check if it's a pure operation
        if operation in PURE_OPERATIONS:
            op_func = PURE_OPERATIONS[operation]
            result = op_func(
                obj=obj,
                param=param,
                path=path,
                value=value,
                default=default,
            )
            return result

        # Check if it's an expression-based operation
        elif operation in EXPRESSION_OPERATIONS:
            if not expression:
                return {
                    "value": None,
                    "error": f"expression is required for {operation} operation",
                }
            if not expr_handler:
                return {
                    "value": None,
                    "error": f"No expression handler provided for operation "
                    f"'{operation}'.",
                }

            op_func = EXPRESSION_OPERATIONS[operation]
            result = op_func(
                obj=obj,
                expression=expression,
                expr_handler=expr_handler,
                param=param,
                path=path,
                value=value,
                default=default,
            )
            return result

        else:
            return {"value": None, "error": f"Unknown operation: {operation}"}

    except Exception as e:
        return {"value": None, "error": f"Dicts operation failed: {str(e)}"}
