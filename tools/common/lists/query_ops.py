from typing import Any, Callable
import random


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


def op_sample(items: list, **kwargs) -> dict:
    """One random item."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for sample."}
    return {"value": random.choice(items) if items else None}


def op_contains(items: list, param: Any = None, **kwargs) -> dict:
    """Checks if list contains specific value."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for contains."}
    return {"value": param in items}


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


def op_filter_by(
    items: list, expression: str, expr_handler: Callable, **kwargs
) -> dict:
    """Filters items where expression is truthy."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for filter_by."}
    if not expression:
        return {"value": None, "error": "Missing required expression for filter_by."}

    try:
        result = []
        for index, item in enumerate(items, 1):
            if expr_handler(expression, item, index, items):
                result.append(item)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"filter_by failed: {str(e)}"}


def op_find_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Finds first item where expression is truthy."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for find_by."}

    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    find_expr = expression or (param if isinstance(param, str) else None)
    if not find_expr:
        return {"value": None, "error": "expression is required for find_by operation"}

    try:
        for index, item in enumerate(items, 1):
            if expr_handler(find_expr, item, index, items):
                return {"value": item}
        return {"value": None}
    except Exception as e:
        return {"value": None, "error": f"find_by failed: {str(e)}"}


def op_remove_by(
    items: list, expression: str, expr_handler: Callable, **kwargs
) -> dict:
    """Remove items matching expression."""
    if not expression:
        return {
            "value": None,
            "error": "expression is required for remove_by operation",
        }

    try:
        result = [
            item
            for index, item in enumerate(items, 1)
            if not expr_handler(expression, item, index, items)
        ]
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"remove_by failed: {str(e)}"}


def op_min_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Find item with minimum property value."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    min_expr = expression or (param if isinstance(param, str) else None)
    if not min_expr:
        return {"value": None, "error": "expression is required for min_by operation"}

    try:
        if not items:
            return {"value": None}

        def min_key(x):
            result = expr_handler(
                min_expr, x, 1, items
            )  # Index not meaningful for min_by
            return result if result is not None else float("inf")

        return {"value": min(items, key=min_key)}
    except Exception as e:
        return {"value": None, "error": f"min_by failed: {str(e)}"}


def op_max_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Find item with maximum property value."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    max_expr = expression or (param if isinstance(param, str) else None)
    if not max_expr:
        return {"value": None, "error": "expression is required for max_by operation"}

    try:
        if not items:
            return {"value": None}

        def max_key(x):
            result = expr_handler(
                max_expr, x, 1, items
            )  # Index not meaningful for max_by
            return result if result is not None else float("-inf")

        return {"value": max(items, key=max_key)}
    except Exception as e:
        return {"value": None, "error": f"max_by failed: {str(e)}"}


def op_index_of(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Find index of first item matching expression."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    index_expr = expression or (param if isinstance(param, str) else None)
    if not index_expr:
        return {"value": None, "error": "expression is required for index_of operation"}

    try:
        for idx, item in enumerate(items):
            # Note: idx is 0-based for index_of operation, but we pass
            # 1-based index to expressions
            result = expr_handler(index_expr, item, idx + 1, items)
            if result:
                return {"value": idx}
        return {"value": -1}
    except Exception as e:
        return {"value": None, "error": f"index_of failed: {str(e)}"}


def op_random_except(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Get random item excluding condition."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    except_expr = expression or (param if isinstance(param, str) else None)
    if not except_expr:
        return {
            "value": None,
            "error": "expression is required for random_except operation",
        }

    try:

        # Exclude items where expression is truthy
        filtered = [
            item
            for index, item in enumerate(items, 1)
            if not expr_handler(except_expr, item, index, items)
        ]
        if not filtered:
            return {"value": None}
        return {"value": random.choice(filtered)}
    except Exception as e:
        return {"value": None, "error": f"random_except failed: {str(e)}"}
