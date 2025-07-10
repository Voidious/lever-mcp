"""
Common operations for the 'generate' tool.

This module contains shared implementations for sequence generation operations
that work the same way regardless of language (no expressions needed).
"""

import itertools
import operator
from typing import Callable, Dict


def op_range(options: dict, **kwargs) -> dict:
    """Generate a list of numbers."""
    from_val = options.get("from")
    to_val = options.get("to")
    step = options.get("step", 1)

    if from_val is None or to_val is None:
        return {
            "value": None,
            "error": "range requires 'from' and 'to' in options dict",
        }

    try:
        # Convert to integers if they're floats that represent whole numbers
        if isinstance(from_val, float) and from_val.is_integer():
            from_val = int(from_val)
        if isinstance(to_val, float) and to_val.is_integer():
            to_val = int(to_val)
        if isinstance(step, float) and step.is_integer():
            step = int(step)

        result = list(range(from_val, to_val, step))
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"range failed: {str(e)}"}


def op_cartesian_product(options: dict, **kwargs) -> dict:
    """Cartesian product of multiple lists."""
    lists = options.get("lists")
    if lists is None:
        return {
            "value": None,
            "error": "cartesian_product requires 'lists' in options dict",
        }

    try:
        result = list(itertools.product(*lists))
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"cartesian_product failed: {str(e)}"}


def op_repeat(options: dict, **kwargs) -> dict:
    """Repeat a value N times."""
    if "value" not in options or "count" not in options:
        return {
            "value": None,
            "error": "repeat requires 'value' and 'count' in options dict",
        }

    try:
        value = options["value"]
        count = options["count"]

        # Convert count to integer if it's a float that represents a whole number
        if isinstance(count, float) and count.is_integer():
            count = int(count)

        result = [value] * count
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"repeat failed: {str(e)}"}


def op_powerset(options: dict, **kwargs) -> dict:
    """All possible subsets of a list."""
    items = options.get("items")
    if items is None:
        return {
            "value": None,
            "error": "powerset requires 'items' in options dict",
        }

    try:
        result = []
        for r in range(len(items) + 1):
            result.extend(itertools.combinations(items, r))
        # Convert tuples to lists for JSON serialization
        result = [list(combo) for combo in result]
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"powerset failed: {str(e)}"}


def op_windowed(options: dict, **kwargs) -> dict:
    """Sliding windows of a given size."""
    items = options.get("items")
    size = options.get("size")

    if items is None or size is None:
        return {
            "value": None,
            "error": "windowed requires 'items' and 'size' in options dict",
        }

    try:
        # Convert size to integer if it's a float that represents a whole number
        if isinstance(size, float) and size.is_integer():
            size = int(size)

        if size <= 0:
            return {
                "value": None,
                "error": "size must be positive for windowed operation",
            }

        result = []
        for i in range(len(items) - size + 1):
            result.append(items[i : i + size])
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"windowed failed: {str(e)}"}


def op_cycle(options: dict, **kwargs) -> dict:
    """Repeat the sequence up to N times."""
    items = options.get("items")
    count = options.get("count")

    if items is None or count is None:
        return {
            "value": None,
            "error": "cycle requires 'items' and 'count' in options dict",
        }

    try:
        if not items:
            return {"value": []}

        # Convert count to integer if it's a float that represents a whole number
        if isinstance(count, float) and count.is_integer():
            count = int(count)

        result = []
        cycler = itertools.cycle(items)
        for _ in range(count):
            result.append(next(cycler))
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"cycle failed: {str(e)}"}


def op_accumulate(options: dict, **kwargs) -> dict:
    """Running totals with specified function."""
    items = options.get("items")
    func = options.get("func", "add")

    if items is None:
        return {
            "value": None,
            "error": "accumulate requires 'items' in options dict",
        }

    try:
        if not items:
            return {"value": []}

        # Map function names to operators
        func_map = {
            "add": operator.add,
            "mul": operator.mul,
            "max": max,
            "min": min,
            "sub": operator.sub,
            "div": operator.truediv,
        }

        if func not in func_map:
            return {
                "value": None,
                "error": f"Unknown accumulate function: {func}. "
                f"Available: {', '.join(func_map.keys())}",
            }

        op_func = func_map[func]

        if func in ["max", "min"]:
            # Special handling for max/min which need different signature
            result = [items[0]]
            for item in items[1:]:
                result.append(op_func(result[-1], item))
        else:
            result = list(itertools.accumulate(items, op_func))

        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"accumulate failed: {str(e)}"}


def op_zip_with_index(options: dict, **kwargs) -> dict:
    """Tuples of (index, value)."""
    items = options.get("items")
    if items is None:
        return {
            "value": None,
            "error": "zip_with_index requires 'items' in options dict",
        }

    try:
        result = [[i, v] for i, v in enumerate(items)]
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"zip_with_index failed: {str(e)}"}


def op_unique_pairs(options: dict, **kwargs) -> dict:
    """All unique pairs from a list."""
    items = options.get("items")
    if items is None:
        return {
            "value": None,
            "error": "unique_pairs requires 'items' in options dict",
        }

    try:
        result = list(itertools.combinations(items, 2))
        # Convert tuples to lists for JSON serialization
        result = [list(pair) for pair in result]
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"unique_pairs failed: {str(e)}"}


def op_permutations(options: dict, **kwargs) -> dict:
    """All permutations of a given length."""
    items = options.get("items")
    length = options.get("length")

    if items is None:
        return {
            "value": None,
            "error": "permutations requires 'items' in options dict",
        }

    try:
        if length is None:
            length = len(items)

        # Convert length to integer if it's a float that represents a whole number
        if isinstance(length, float) and length.is_integer():
            length = int(length)

        result = list(itertools.permutations(items, length))
        # Convert tuples to lists for JSON serialization
        result = [list(perm) for perm in result]
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"permutations failed: {str(e)}"}


def op_combinations(options: dict, **kwargs) -> dict:
    """All combinations of a given length."""
    items = options.get("items")
    length = options.get("length")

    if items is None or length is None:
        return {
            "value": None,
            "error": "combinations requires 'items' and 'length' in options dict",
        }

    try:
        # Convert length to integer if it's a float that represents a whole number
        if isinstance(length, float) and length.is_integer():
            length = int(length)

        result = list(itertools.combinations(items, length))
        # Convert tuples to lists for JSON serialization
        result = [list(combo) for combo in result]
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"combinations failed: {str(e)}"}


# Operations registry - all generate operations are pure (no expressions)
OPERATIONS: Dict[str, Callable] = {
    "range": op_range,
    "cartesian_product": op_cartesian_product,
    "repeat": op_repeat,
    "powerset": op_powerset,
    "windowed": op_windowed,
    "cycle": op_cycle,
    "accumulate": op_accumulate,
    "zip_with_index": op_zip_with_index,
    "unique_pairs": op_unique_pairs,
    "permutations": op_permutations,
    "combinations": op_combinations,
}


def generate_operation(
    options: dict,
    operation: str,
    wrap: bool = False,
) -> dict:
    """
    Execute a generate tool operation.

    Args:
        options: Configuration options for the operation
        operation: Name of the operation to perform
        wrap: Whether to wrap the result (for Lua compatibility)

    Returns:
        Dict with 'value' key and optional 'error' key
    """
    try:
        if operation not in OPERATIONS:
            return {"value": None, "error": f"Unknown operation: {operation}"}

        # Get the operation function and call it
        op_func = OPERATIONS[operation]
        result = op_func(options=options)

        return result

    except Exception as e:
        return {"value": None, "error": f"Generate operation failed: {str(e)}"}
