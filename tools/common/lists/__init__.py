"""
Common operations for the 'lists' tool.

This module contains shared implementations for list operations that work
the same way regardless of expression language, plus framework for
expression-based operations.
"""

from typing import Any, Callable, Dict, Optional
from .basic import (
    op_chunk,
    op_compact,
    op_contains,
    op_drop,
    op_drop_right,
    op_flatten,
    op_flatten_deep,
    op_head,
    op_initial,
    op_is_empty,
    op_is_equal,
    op_join,
    op_last,
    op_max,
    op_min,
    op_nth,
    op_sample,
    op_sample_size,
    op_shuffle,
    op_tail,
    op_take,
    op_take_right,
    op_unzip_list,
    op_zip_lists,
)
from .query import (
    op_all_by,
    op_any_by,
    op_count_by,
    op_filter_by,
    op_find_by,
    op_flat_map,
    op_group_by,
    op_index_of,
    op_key_by,
    op_map,
    op_max_by,
    op_min_by,
    op_partition,
    op_pluck,
    op_random_except,
    op_reduce,
    op_remove_by,
    op_sort_by,
    op_uniq_by,
    op_zip_with,
)
from .setops import (
    op_difference,
    op_difference_by,
    op_intersection,
    op_intersection_by,
    op_union,
    op_xor,
)


# Pure operations that don't require expressions


# Expression-based operations that require handler functions


# Pure operations registry - these don't require expressions
PURE_OPERATIONS: Dict[str, Callable] = {
    "xor": op_xor,
    "shuffle": op_shuffle,
    "sample_size": op_sample_size,
    "is_empty": op_is_empty,
    "head": op_head,
    "last": op_last,
    "tail": op_tail,
    "initial": op_initial,
    "drop": op_drop,
    "drop_right": op_drop_right,
    "take": op_take,
    "take_right": op_take_right,
    "flatten": op_flatten,
    "flatten_deep": op_flatten_deep,
    "compact": op_compact,
    "chunk": op_chunk,
    "zip_lists": op_zip_lists,
    "unzip_list": op_unzip_list,
    "union": op_union,
    "intersection": op_intersection,
    "difference": op_difference,
    "sample": op_sample,
    "nth": op_nth,
    "contains": op_contains,
    "is_equal": op_is_equal,
    "min": op_min,
    "max": op_max,
    "join": op_join,
}

# Expression-based operations registry - these require an expression handler
EXPRESSION_OPERATIONS: Dict[str, Callable] = {
    "sort_by": op_sort_by,
    "filter_by": op_filter_by,
    "map": op_map,
    "find_by": op_find_by,
    "group_by": op_group_by,
    "uniq_by": op_uniq_by,
    "partition": op_partition,
    "pluck": op_pluck,
    "remove_by": op_remove_by,
    "count_by": op_count_by,
    "key_by": op_key_by,
    "min_by": op_min_by,
    "max_by": op_max_by,
    "index_of": op_index_of,
    "random_except": op_random_except,
    "flat_map": op_flat_map,
    "difference_by": op_difference_by,
    "intersection_by": op_intersection_by,
    "all_by": op_all_by,
    "every": op_all_by,  # Alias for all_by
    "any_by": op_any_by,
    "some": op_any_by,  # Alias for any_by
    "reduce": op_reduce,
    "zip_with": op_zip_with,
}


def lists_operation(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
    expr_handler: Optional[Callable] = None,
    wrap: bool = False,
) -> dict:
    """
    Execute a lists tool operation.

    Args:
        items: The input list to operate on
        operation: Name of the operation to perform
        param: Optional parameter for some operations
        others: Optional second list for set operations
        expression: Optional expression for expression-based operations
        expr_handler: Function to handle expression evaluation
        wrap: Whether to wrap the result (for Lua compatibility)

    Returns:
        Dict with 'value' key and optional 'error' key
    """
    try:
        # Check if it's a pure operation
        if operation in PURE_OPERATIONS:
            op_func = PURE_OPERATIONS[operation]
            result = op_func(
                items=items,
                param=param,
                others=others,
            )
            return result

        # Check if it's an expression-based operation
        elif operation in EXPRESSION_OPERATIONS:
            # Some operations can use param as expression fallback
            # (backward compatibility)
            backward_compat_ops = [
                "min_by",
                "max_by",
                "sort_by",
                "uniq_by",
                "partition",
                "pluck",
                "group_by",
                "count_by",
                "key_by",
                "find_by",
                "index_of",
                "random_except",
                "difference_by",
                "intersection_by",
            ]
            if not expression and (operation not in backward_compat_ops or not param):
                return {
                    "value": None,
                    "error": (
                        f"Missing required expression for operation '{operation}'."
                    ),
                }
            if not expr_handler:
                return {
                    "value": None,
                    "error": (
                        f"No expression handler provided for operation '{operation}'."
                    ),
                }

            op_func = EXPRESSION_OPERATIONS[operation]
            result = op_func(
                items=items,
                expression=expression,
                expr_handler=expr_handler,
                param=param,
                others=others,
            )
            return result

        else:
            return {"value": None, "error": f"Unknown operation: {operation}"}

    except Exception as e:
        return {"value": None, "error": f"Lists operation failed: {str(e)}"}
