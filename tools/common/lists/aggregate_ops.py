from typing import Any, Callable, Optional


def op_xor(items: list, others: Optional[list] = None, **kwargs) -> dict:
    """Symmetric difference between two lists."""
    if not isinstance(items, list) or not isinstance(others, list):
        return {"value": None, "error": "Both arguments must be lists for xor."}
    try:
        return {"value": list(set(items) ^ set(others))}
    except TypeError:
        # Fallback for unhashable types
        result = [x for x in items if x not in others] + [
            x for x in others if x not in items
        ]
        return {"value": result}


def op_union(items: list, others: Optional[list] = None, **kwargs) -> dict:
    """Unique values from multiple lists. Expects items to be a list of lists."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for union."}

    try:
        result = []
        seen = set()
        for sublist in items:
            if isinstance(sublist, list):
                for item in sublist:
                    try:
                        if item not in seen:
                            seen.add(item)
                            result.append(item)
                    except TypeError:
                        # Handle unhashable types
                        if item not in result:
                            result.append(item)
            else:
                # Handle case where items is not a list of lists
                try:
                    if sublist not in seen:
                        seen.add(sublist)
                        result.append(sublist)
                except TypeError:
                    if sublist not in result:
                        result.append(sublist)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"union failed: {str(e)}"}


def op_intersection(items: list, others: Optional[list] = None, **kwargs) -> dict:
    """Items present in both lists."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for intersection."}
    if others is None:
        others = []
    if not isinstance(others, list):
        return {"value": None, "error": "Others must be a list for intersection."}

    try:
        return {"value": list(set(items) & set(others))}
    except TypeError:
        # Fallback for unhashable types
        return {"value": [x for x in items if x in others]}


def op_difference(items: list, others: Optional[list] = None, **kwargs) -> dict:
    """Items in first list not in second."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for difference."}
    if others is None:
        others = []
    if not isinstance(others, list):
        return {"value": None, "error": "Others must be a list for difference."}

    try:
        return {"value": list(set(items) - set(others))}
    except TypeError:
        # Fallback for unhashable types
        return {"value": [x for x in items if x not in others]}


def op_group_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Groups items by expression result."""
    if not isinstance(items, list):
        return {"value": None, "error": "Argument must be a list for group_by."}

    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    group_expr = expression or (param if isinstance(param, str) else None)
    if not group_expr:
        return {"value": None, "error": "expression is required for group_by operation"}

    try:
        result = {}
        for index, item in enumerate(items, 1):
            key = expr_handler(group_expr, item, index, items)
            # Convert result to string for consistent grouping
            key = str(key) if key is not None else "None"
            result.setdefault(key, []).append(item)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"group_by failed: {str(e)}"}


def op_uniq_by(
    items: list, expression: str, expr_handler: Callable, param: Any = None, **kwargs
) -> dict:
    """Remove duplicates by expression result."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    uniq_expr = expression or (param if isinstance(param, str) else None)
    if not uniq_expr:
        return {"value": None, "error": "expression is required for uniq_by operation"}

    try:
        seen = set()
        result = []
        for index, item in enumerate(items, 1):
            k = expr_handler(uniq_expr, item, index, items)
            # Handle unhashable types by converting to JSON
            try:
                k_hash = (
                    k if isinstance(k, (str, int, float, bool, type(None))) else str(k)
                )
                if k_hash not in seen:
                    seen.add(k_hash)
                    result.append(item)
            except (TypeError, ValueError):
                import json

                k_hash = (
                    json.dumps(k, sort_keys=True) if isinstance(k, dict) else str(k)
                )
                if k_hash not in seen:
                    seen.add(k_hash)
                    result.append(item)
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"uniq_by failed: {str(e)}"}


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


def op_difference_by(
    items: list,
    others: list,
    expression: str,
    expr_handler: Callable,
    param: Any = None,
    **kwargs,
) -> dict:
    """Items in first not matching expression in second."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    diff_expr = expression or (param if isinstance(param, str) else None)
    if not diff_expr:
        return {
            "value": None,
            "error": "expression is required for difference_by operation",
        }

    try:
        # Extract keys from others list using expression
        others_keys = set()
        for index, item in enumerate(others, 1):
            key_val = expr_handler(diff_expr, item, index, others)
            others_keys.add(key_val)

        # Return items from main list whose key is not in others_keys
        result = []
        for index, item in enumerate(items, 1):
            key_val = expr_handler(diff_expr, item, index, items)
            if key_val not in others_keys:
                result.append(item)

        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"difference_by failed: {str(e)}"}


def op_intersection_by(
    items: list,
    others: list,
    expression: str,
    expr_handler: Callable,
    param: Any = None,
    **kwargs,
) -> dict:
    """Items in first list matching expression in second."""
    # Use expression if provided, otherwise use param as expression
    # (backward compatibility)
    inter_expr = expression or (param if isinstance(param, str) else None)
    if not inter_expr:
        return {
            "value": None,
            "error": "expression is required for intersection_by operation",
        }

    try:
        # Extract keys from others list using expression
        others_keys = set()
        for index, item in enumerate(others, 1):
            key_val = expr_handler(inter_expr, item, index, others)
            others_keys.add(key_val)

        # Return items from main list whose key is in others_keys
        result = []
        for index, item in enumerate(items, 1):
            key_val = expr_handler(inter_expr, item, index, items)
            if key_val in others_keys:
                result.append(item)

        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"intersection_by failed: {str(e)}"}


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
