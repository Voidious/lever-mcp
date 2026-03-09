from typing import Any, Callable


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


def op_pluck(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Extract values by expression."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    pluck_expr = expression or (param if isinstance(param, str) else None)
    if not pluck_expr:
        return {"value": None, "error": "expression is required for pluck operation"}

    try:
        result = [
            expr_handler(pluck_expr, item, index, items)
            for index, item in enumerate(items, 1)
        ]
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"pluck failed: {str(e)}"}


def op_count_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Count occurrences by expression result."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    count_expr = expression or (param if isinstance(param, str) else None)
    if not count_expr:
        return {"value": None, "error": "expression is required for count_by operation"}

    try:
        result = {}
        for index, item in enumerate(items, 1):
            k = expr_handler(count_expr, item, index, items)
            # Convert result to string for consistent dictionary keys
            k = str(k) if k is not None else "null"
            result[k] = result.get(k, 0) + 1
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"count_by failed: {str(e)}"}


def op_key_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Create dict keyed by expression result."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    key_expr = expression or (param if isinstance(param, str) else None)
    if not key_expr:
        return {"value": None, "error": "expression is required for key_by operation"}

    try:
        result = {}
        for index, item in enumerate(items, 1):
            k = expr_handler(key_expr, item, index, items)
            # Convert integer keys to strings like JSON does
            if isinstance(k, int):
                k = str(k)
            result[k] = item
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"key_by failed: {str(e)}"}


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


def op_all_by(items: list, expression: str, expr_handler: Callable, **kwargs) -> dict:
    """Check if all items match expression."""
    if not expression:
        return {"value": None, "error": "expression is required for all_by operation"}

    try:
        result = all(
            bool(expr_handler(expression, item, index, items))
            for index, item in enumerate(items, 1)
        )
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"all_by failed: {str(e)}"}


def op_any_by(items: list, expression: str, expr_handler: Callable, **kwargs) -> dict:
    """Check if any items match expression."""
    if not expression:
        return {"value": None, "error": "expression is required for any_by operation"}

    try:
        result = any(
            bool(expr_handler(expression, item, index, items))
            for index, item in enumerate(items, 1)
        )
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"any_by failed: {str(e)}"}


def op_reduce(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Aggregate the list using a binary expression."""
    if not expression:
        return {"value": None, "error": "expression is required for reduce operation"}

    try:
        if not items:
            return {"value": param if param is not None else None}

        # Use the provided expr_handler with 'acc' and 'item' context
        acc = param if param is not None else items[0]
        start_idx = 0 if param is not None else 1
        for i in range(start_idx, len(items)):
            # The expression can use 'acc' and 'item'
            acc = expr_handler(
                expression,
                items[i],
                i + 1,
                items,
                context={"acc": acc, "item": items[i]},
            )
        return {"value": acc}
    except Exception as e:
        return {"value": None, "error": f"reduce failed: {str(e)}"}
