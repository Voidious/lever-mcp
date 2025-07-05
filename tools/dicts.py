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
    """
    Performs dictionary operations, including merge, set/get value, and property checks.

    Supported operations:
        - 'flatten_keys': Flattens nested dict with dot notation (e.g.,
          {'a': {'b': 1}} → {'a.b': 1})
        - 'get_value': Gets a deep property by path (path: str dot-notation like
          "a.b.c" or list like ["a","b","c"], default: any)
        - 'has_key': Checks if a dict has a given key (param: str)
        - 'invert': Swaps keys and values
        - 'is_empty': Checks if the dict is empty
        - 'is_equal': Checks if two dicts are deeply equal (param: dict to compare)
        - 'items': Gets key-value pairs as list of tuples
        - 'keys': Gets all dictionary keys as list
        - 'map_keys': Transforms all keys with Lua expression (expression: str)
        - 'map_values': Transforms all values with Lua expression (expression: str)
        - 'merge': Deep merges a list of dictionaries (obj must be a list of dicts)
        - 'omit': Omits specified keys (param: list of keys)
        - 'pick': Picks specified keys (param: list of keys)
        - 'set_value': Sets a deep property by path (path: str dot-notation like
          "a.b.c" or list like ["a","b","c"], value: any)
        - 'unflatten_keys': Unflattens dot-notation keys to nested dict (e.g.,
          {'a.b': 1} → {'a': {'b': 1}})
        - 'values': Gets all dictionary values as list

    Returns:
        dict: Result with 'value' key containing a dict (most operations), list
            ('keys', 'values', 'items'), or single value ('get_value', 'has_key',
            'is_empty', 'is_equal'). On error, includes 'error' key.

    Expression Examples:
        - Filtering: 'age > 25', 'score >= 80', 'name == 'Alice''
        - Grouping: 'age >= 30 and 'senior' or 'junior''
        - Sorting: 'age * -1' (reverse age), 'string.lower(name)'
          (case-insensitive)
        - Extraction: 'string.upper(name)', 'age > 18 and name or 'minor''
        - Math: 'math.abs(score - 50)', 'x*x + y*y' (distance squared)
        - Functional programming: Use tool functions as expressions (e.g.,
          `lists.map(items, 'strings.upper_case')`).

    In Lua expressions for map_keys: key (current key string), value (current value),
    obj (original dict). For map_values: value (current value), key (current key
    string), obj (original dict). For map_values, if value is a dict, its properties are
    also accessible directly (age, name, etc.). Available in expressions: math.*,
    string.*, os.time/date/clock, type(), tonumber(), tostring(). You may pass a single
    Lua expression or a block of Lua code. For multi-line code, use return to specify
    the result.

    MCP Usage Examples:
        dicts({'a': 1, 'b': 2}, 'pick', param=['a'])  # => {'value': {'a': 1}}
        dicts({'a': {'b': 1}}, 'set_value', path=['a', 'b'], value=2)
          # => {'value': {'a': {'b': 2}}}
        dicts({'a': 1}, 'get_value', path='b', default=42)  # => {'value': 42}
        dicts({'firstName': 'john'}, 'map_keys', expression='strings.snake_case')
          # => {'value': {'first_name': 'john'}}

    Lua Function Call Examples:
        dicts.has_key({name='alice', age=30}, 'email')  # => false
        dicts.get_value(
            {obj={user={profile={name='bob'}}}, path='user.profile.name'}
        )  # => 'bob'
        dicts.pick(
            {obj={id=1, name='alice', email='alice@test.com'}, param={'id', 'name'}}
        )  # => {'id': 1, 'name': 'alice'}
        dicts.omit({obj={password='secret', name='alice', age=30}, param={'password'}})
          # => {'name': 'alice', 'age': 30}
        dicts.merge({obj={{config={debug=true}}, {config={port=8080}}}, wrap=true})
          # => JSON: {'config': {'port': 8080}}, Lua: {'__type': 'dict', 'data': {...}}

    In Lua, an empty table represents an empty dict **OR** an empty list. Lever tools
    serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
    dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
    {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
    serialization. Use unwrap(o) to get the original table.
    """
    return _dicts_impl(
        obj, operation, param, path, value, default, expression, wrap=False
    )


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
                new_key = evaluate_expression(
                    expression, key, context={"key": key, "value": value, "obj": obj}
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
                new_value = evaluate_expression(
                    expression, value, context={"key": key, "value": value, "obj": obj}
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