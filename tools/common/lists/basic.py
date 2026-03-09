from typing import Any
import random


def op_shuffle(items: list, **kwargs) -> dict:
    """Randomizes order of items."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for shuffle."}
    result = items[:]
    random.shuffle(result)
    return {"value": result}


def op_sample_size(items: list, param: Any = None, **kwargs) -> dict:
    """Gets n random items."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for sample_size."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    if n <= 0:
        return {"value": []}
    if n >= len(items):
        return {"value": items[:]}
    return {"value": random.sample(items, n)}


def op_is_empty(items: list, **kwargs) -> dict:
    """Checks if list is empty."""
    # Accept 0, False, None as empty for lists (matching original behavior)
    if items is None or items == 0 or items is False:
        return {"value": True}
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for is_empty."}
    return {"value": len(items) == 0}


def op_head(items: list, **kwargs) -> dict:
    """First element."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for head."}
    return {"value": items[0] if items else None}


def op_last(items: list, **kwargs) -> dict:
    """Last element."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for last."}
    return {"value": items[-1] if items else None}


def op_tail(items: list, **kwargs) -> dict:
    """All elements except first."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for tail."}
    return {"value": items[1:] if items else []}


def op_initial(items: list, **kwargs) -> dict:
    """All elements except last."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for initial."}
    return {"value": items[:-1] if items else []}


def op_drop(items: list, param: Any = None, **kwargs) -> dict:
    """Drops n elements from start."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for drop."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    return {"value": items[n:]}


def op_drop_right(items: list, param: Any = None, **kwargs) -> dict:
    """Drops n elements from end."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for drop_right."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    return {"value": items[:-n] if n > 0 else items}


def op_take(items: list, param: Any = None, **kwargs) -> dict:
    """Takes n elements from start."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for take."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    return {"value": items[:n]}


def op_take_right(items: list, param: Any = None, **kwargs) -> dict:
    """Takes n elements from end."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for take_right."}
    # Handle both int and float that represents an integer
    if isinstance(param, int):
        n = param
    elif isinstance(param, float) and param.is_integer():
        n = int(param)
    else:
        n = 1
    return {"value": items[-n:] if n > 0 else []}


def op_flatten(items: list, **kwargs) -> dict:
    """Flattens one level of nesting."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for flatten."}
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return {"value": result}


def op_flatten_deep(items: list, **kwargs) -> dict:
    """Flattens nested lists completely."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for flatten_deep."}

    def flatten_recursive(lst):
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(flatten_recursive(item))
            else:
                result.append(item)
        return result

    return {"value": flatten_recursive(items)}


def op_compact(items: list, **kwargs) -> dict:
    """Removes falsy values."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for compact."}

    def is_truthy(item):
        # Handle PythonMonkey null type specifically
        # PythonMonkey null comes through as the null type itself, not an instance
        if str(item) == "<class 'pythonmonkey.null'>":
            return False
        return bool(item)

    return {"value": [item for item in items if is_truthy(item)]}


def op_chunk(items: list, param: Any = None, **kwargs) -> dict:
    """Splits into chunks of specified size."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for chunk."}
    if param is None:
        return {"value": None, "error": "chunk operation requires a size parameter"}
    try:
        size = int(param)
        if size <= 0:
            return {"value": None, "error": "chunk size must be positive"}
        return {"value": [items[i : i + size] for i in range(0, len(items), size)]}
    except (ValueError, TypeError):
        return {"value": None, "error": "chunk size must be an integer"}


def op_zip_lists(items: list, **kwargs) -> dict:
    """Zips multiple lists together."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for zip_lists."}
    if not items:
        return {"value": []}
    return {"value": [list(t) for t in zip(*items)]}


def op_unzip_list(items: list, **kwargs) -> dict:
    """Unzips list of lists."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for unzip_list."}
    if not items:
        return {"value": []}
    return {"value": [list(t) for t in zip(*items)]}


def op_sample(items: list, **kwargs) -> dict:
    """One random item."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for sample."}
    return {"value": random.choice(items) if items else None}


def op_nth(items: list, param: Any = None, **kwargs) -> dict:
    """Element at specific index."""
    if not isinstance(items, list):
        return {"value": None, "error": "nth operation requires a list"}
    if param is None:
        return {"value": None, "error": "nth operation requires an index parameter"}
    if not isinstance(param, int):
        return {"value": None, "error": "nth index must be an integer"}
    try:
        if -len(items) <= param < len(items):
            return {"value": items[param]}
        return {"value": None}
    except Exception as e:
        return {"value": None, "error": f"nth failed: {str(e)}"}


def op_contains(items: list, param: Any = None, **kwargs) -> dict:
    """Checks if list contains specific value."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for contains."}
    return {"value": param in items}


def op_is_equal(items: list, param: Any = None, **kwargs) -> dict:
    """Checks if two lists are equal."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for is_equal."}
    if not isinstance(param, list):
        return {"value": False}
    return {"value": items == param}


def op_min(items: list, **kwargs) -> dict:
    """Minimum value in list."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for min."}
    if not items:
        return {"value": None, "error": "Cannot find minimum of empty list"}
    try:
        return {"value": min(items)}
    except TypeError as e:
        return {"value": None, "error": f"Cannot compare items for minimum: {e}"}


def op_max(items: list, **kwargs) -> dict:
    """Maximum value in list."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for max."}
    if not items:
        return {"value": None, "error": "Cannot find maximum of empty list"}
    try:
        return {"value": max(items)}
    except TypeError as e:
        return {"value": None, "error": f"Cannot compare items for maximum: {e}"}


def op_join(items: list, param: Any = None, **kwargs) -> dict:
    """Joins list items into string with delimiter."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for join."}
    delimiter = str(param) if param is not None else ""
    try:

        def convert_item(item):
            # Convert float integers to ints before stringifying
            if isinstance(item, float) and item.is_integer():
                return str(int(item))
            return str(item)

        return {"value": delimiter.join(convert_item(item) for item in items)}
    except Exception as e:
        return {"value": None, "error": f"Join failed: {str(e)}"}
