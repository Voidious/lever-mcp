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
    """
    Performs type-agnostic property checks, comparisons, and expression evaluation.

    Supported operations:
        - 'contains': Checks if a string or list contains a value (param: value to
          check)
        - 'eval': Evaluate a Lua expression with value as context (expression: Lua
          code)
        - 'is_empty': Checks if the value is empty
        - 'is_equal': Checks if two values are deeply equal (param: value to compare)
        - 'is_nil': Checks if the value is None
        - 'size': Gets the size/length of any collection type (strings, lists, dicts)
          or 1 for scalars

    Returns:
        dict: Result with 'value' key containing a boolean ('is_equal', 'is_empty',
        'is_nil',
            'contains'), integer ('size'), or any type ('eval' - depends on
            expression).
            On error, includes 'error' key.

    Expression Examples:
        - Boolean check: 'age > 25', 'score >= 80', 'name == 'Alice''
        - Math: 'math.abs(x - y)', 'x*x + y*y'
        - String manipulation: 'string.upper(value)', 'string.sub(value, 1, 3)'
        - Null check: 'value == null', 'score ~= null'
        - Type check: 'type(value) == 'table'', 'type(value) == 'string''
        - Functional programming: Use tool functions as expressions (e.g.,
          `lists.map(items, 'strings.upper_case')`).

    In Lua expressions, value refers to the input value being evaluated. Available in
    expressions: math.*, string.*, os.time/date/clock, type(), tonumber(), tostring().
    Dictionary keys accessible directly (age, name, etc.) or via value.key. You may pass
    a single Lua expression or a block of Lua code. For multi-line code, use return to
    specify the result.

    MCP Usage Examples:
        any('abc', 'contains', param='b')  # => {'value': true}
        any([1, 2, 3], 'contains', param=2)  # => {'value': true}
        any([], 'is_empty')  # => {'value': true}
        any(42, 'is_equal', param=42)  # => {'value': true}
        any([0, 0], 'eval', expression='lists.compact')  # => {'value': []}

    Lua Function Call Examples:
        any.is_equal(42, 42)  # => true
        any.is_empty('')  # => true
        any.contains('hello', 'ell')  # => true
        any.eval({age=30}, 'age > 25')  # => true
        any.eval(
            {value={{1}, {2}}, expression='lists.max_by(value, \"item[1]\")',
             wrap=true}
        )  # => JSON: {2}, Lua: {'__type': 'list', 'data': {2}}

    In Lua, an empty table represents an empty dict **OR** an empty list. Lever tools
    serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
    dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
    {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
    serialization. Use unwrap(o) to get the original table.
    """
    return _any_impl(value, operation, param, expression, wrap=False)


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
            # Use evaluate_expression for consistency and to support auto-wrap
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
                result = evaluate_expression(expression, value, context=context)
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
