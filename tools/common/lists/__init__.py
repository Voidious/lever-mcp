"""
Common operations for the 'lists' tool.

This module contains shared implementations for list operations that
the same way regardless of expression language, plus framework for
expression-based operations.
"""

from typing import Any, Callable, Optional
from .basic import EXPRESSION_OPERATIONS, PURE_OPERATIONS
from .basic import op_chunk  # fmt: skip # noqa: F401, E501
from .basic import op_compact  # fmt: skip # noqa: F401, E501
from .basic import op_contains  # fmt: skip # noqa: F401, E501
from .basic import op_difference  # fmt: skip # noqa: F401, E501
from .basic import op_drop  # fmt: skip # noqa: F401, E501
from .basic import op_drop_right  # fmt: skip # noqa: F401, E501
from .basic import op_flatten  # fmt: skip # noqa: F401, E501
from .basic import op_flatten_deep  # fmt: skip # noqa: F401, E501
from .basic import op_head  # fmt: skip # noqa: F401, E501
from .basic import op_initial  # fmt: skip # noqa: F401, E501
from .basic import op_intersection  # fmt: skip # noqa: F401, E501
from .basic import op_is_empty  # fmt: skip # noqa: F401, E501
from .basic import op_is_equal  # fmt: skip # noqa: F401, E501
from .basic import op_join  # fmt: skip # noqa: F401, E501
from .basic import op_last  # fmt: skip # noqa: F401, E501
from .basic import op_nth  # fmt: skip # noqa: F401, E501
from .basic import op_sample  # fmt: skip # noqa: F401, E501
from .basic import op_sample_size  # fmt: skip # noqa: F401, E501
from .basic import op_shuffle  # fmt: skip # noqa: F401, E501
from .basic import op_tail  # fmt: skip # noqa: F401, E501
from .basic import op_take  # fmt: skip # noqa: F401, E501
from .basic import op_take_right  # fmt: skip # noqa: F401, E501
from .basic import op_union  # fmt: skip # noqa: F401, E501
from .basic import op_unzip_list  # fmt: skip # noqa: F401, E501
from .basic import op_xor  # fmt: skip # noqa: F401, E501
from .basic import op_zip_lists  # fmt: skip # noqa: F401, E501
from .expressions import op_all_by  # fmt: skip # noqa: F401, E501
from .expressions import op_any_by  # fmt: skip # noqa: F401, E501
from .expressions import op_count_by  # fmt: skip # noqa: F401, E501
from .expressions import op_difference_by  # fmt: skip # noqa: F401, E501
from .expressions import op_filter_by  # fmt: skip # noqa: F401, E501
from .expressions import op_find_by  # fmt: skip # noqa: F401, E501
from .expressions import op_flat_map  # fmt: skip # noqa: F401, E501
from .expressions import op_group_by  # fmt: skip # noqa: F401, E501
from .expressions import op_index_of  # fmt: skip # noqa: F401, E501
from .expressions import op_intersection_by  # fmt: skip # noqa: F401, E501
from .expressions import op_key_by  # fmt: skip # noqa: F401, E501
from .expressions import op_map  # fmt: skip # noqa: F401, E501
from .expressions import op_max  # fmt: skip # noqa: F401, E501
from .expressions import op_max_by  # fmt: skip # noqa: F401, E501
from .expressions import op_min  # fmt: skip # noqa: F401, E501
from .expressions import op_min_by  # fmt: skip # noqa: F401, E501
from .expressions import op_partition  # fmt: skip # noqa: F401, E501
from .expressions import op_pluck  # fmt: skip # noqa: F401, E501
from .expressions import op_random_except  # fmt: skip # noqa: F401, E501
from .expressions import op_reduce  # fmt: skip # noqa: F401, E501
from .expressions import op_remove_by  # fmt: skip # noqa: F401, E501
from .expressions import op_sort_by  # fmt: skip # noqa: F401, E501
from .expressions import op_uniq_by  # fmt: skip # noqa: F401, E501
from .expressions import op_zip_with  # fmt: skip # noqa: F401, E501


# Pure operations that don't require expressions


# Expression-based operations that require handler functions


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
