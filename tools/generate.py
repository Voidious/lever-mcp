"""
Generate tool implementation for Lever MCP.

This module contains the generate tool functionality for generating sequences
or derived data using various operations.
"""

import itertools
import operator
from lib.lua import _unwrap_input, _apply_wrapping


def generate_tool(options: dict, operation: str) -> dict:
    """MCP tool wrapper for generating sequences or derived data."""
    return _generate_impl(options, operation, wrap=False)


def _generate_impl(options: dict, operation: str, wrap: bool = False) -> dict:
    # Unwrap input parameters
    options = _unwrap_input(options)

    try:
        if operation == "range":
            from_val = options.get("from")
            to_val = options.get("to")
            step = options.get("step", 1)

            if from_val is None or to_val is None:
                return {
                    "value": None,
                    "error": "range requires 'from' and 'to' in options dict",
                }
            result = list(range(from_val, to_val, step))
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "cartesian_product":
            lists = options.get("lists")
            if lists is None:
                return {
                    "value": None,
                    "error": "cartesian_product requires 'lists' in options dict",
                }
            result = list(itertools.product(*lists))
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "repeat":
            if "value" not in options or "count" not in options:
                return {
                    "value": None,
                    "error": "repeat requires 'value' and 'count' in options dict",
                }
            value = options["value"]
            count = options["count"]
            if not isinstance(count, int):
                return {
                    "value": None,
                    "error": "'count' must be an integer for 'repeat'",
                }
            result = list(itertools.repeat(value, count))
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "powerset":
            items = options.get("items")
            if items is None:
                return {
                    "value": None,
                    "error": "powerset requires 'items' in options dict",
                }
            s = list(items)
            if not s:
                result = [[]]
            else:
                result = [
                    list(combo)
                    for r in range(len(s) + 1)
                    for combo in itertools.combinations(s, r)
                ]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "windowed":
            items = options.get("items")
            size = options.get("size")

            if items is None or size is None:
                return {
                    "value": None,
                    "error": "windowed requires 'items' and 'size' in options dict",
                }
            if not isinstance(size, int) or size < 1:
                return {
                    "value": None,
                    "error": "'size' must be a positive integer for 'windowed'",
                }
            s = list(items)
            result = [list(s[i : i + size]) for i in range(len(s) - size + 1)]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "cycle":
            items = options.get("items")
            count = options.get("count")

            if items is None or count is None:
                return {
                    "value": None,
                    "error": "cycle requires 'items' and 'count' in options dict",
                }
            s = list(items)
            result = [s[i % len(s)] for i in range(count)] if s else []
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "accumulate":
            items = options.get("items")
            func = options.get("func")

            if items is None:
                return {
                    "value": None,
                    "error": "accumulate requires 'items' in options dict",
                }
            s = list(items)
            if func is None or func == "add":
                result = list(itertools.accumulate(s))  # Default is addition
            elif func == "mul":
                result = list(itertools.accumulate(s, operator.mul))
            elif func == "max":
                result = list(itertools.accumulate(s, max))
            elif func == "min":
                result = list(itertools.accumulate(s, min))
            elif func == "sub":
                result = list(itertools.accumulate(s, operator.sub))
            elif func == "div":
                result = list(itertools.accumulate(s, operator.truediv))
            else:
                return {
                    "value": None,
                    "error": "accumulate supports func: None, 'add', 'mul', "
                    "'max', 'min', 'sub', 'div'",
                }
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "zip_with_index":
            items = options.get("items")
            if items is None:
                return {
                    "value": None,
                    "error": "zip_with_index requires 'items' in options dict",
                }
            result = [[i, v] for i, v in enumerate(items)]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "unique_pairs":
            items = options.get("items")
            if items is None:
                return {
                    "value": None,
                    "error": "unique_pairs requires 'items' in options dict",
                }
            s = list(items)
            result = [list(pair) for pair in itertools.combinations(s, 2)]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "permutations":
            items = options.get("items")
            length = options.get("length")

            if items is None:
                return {
                    "value": None,
                    "error": "permutations requires 'items' in options dict",
                }
            s = list(items)
            if not s:
                result = [[]]
            else:
                result = [list(p) for p in itertools.permutations(s, length)]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "combinations":
            items = options.get("items")
            length = options.get("length")

            if items is None or length is None:
                return {
                    "value": None,
                    "error": (
                        "combinations requires 'items' and 'length' in options dict"
                    ),
                }
            if not isinstance(length, int):
                return {
                    "value": None,
                    "error": "'length' must be an integer for 'combinations'",
                }
            s = list(items)
            if not s:
                result = []
            else:
                result = [list(c) for c in itertools.combinations(s, length)]
            return {"value": _apply_wrapping(result, wrap)}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}
