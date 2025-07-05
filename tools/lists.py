"""
Lists tool implementation for Lever MCP.

This module contains the lists tool functionality for list operations
including mutations, selections, set-like operations, grouping, and filtering.
"""

from typing import Any, Optional
import random
import json
from lib.lua import _unwrap_input, _apply_wrapping, _wrap_result, evaluate_expression


def lists_tool(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
) -> dict:
    """
    Performs list operations and mutations with support for Lua expressions.

    Supported operations:
        - 'chunk': Split into chunks (param: int)
        - 'compact': Remove falsy values
        - 'contains': Check if item exists (param: value)
        - 'count_by': Count occurrences by expression result
          (expression: Lua expression)
        - 'difference': Items in first not in second
        - 'difference_by': Items in first list not matching expression in second
        - 'drop': Drop n elements from start (param: int)
        - 'drop_right': Drop n elements from end (param: int)
        - 'filter_by': Return all items matching the expression
          (expression: Lua expression)
        - 'find_by': Find first item matching expression
          (expression: Lua expression)
        - 'flat_map': Like map, but flattens one level if the mapping returns
          lists (expression: Lua expression)
        - 'flatten': Flatten one level (non-list elements are preserved as-is)
        - 'flatten_deep': Flatten completely
        - 'group_by': Group items by expression result (expression: Lua expression)
        - 'head': First element
        - 'index_of': Find index of item (expression: Lua expression)
        - 'initial': All but last element
        - 'intersection': Items in both lists
        - 'intersection_by': Items in first list matching expression in second
        - 'is_empty': Check if list is empty
        - 'is_equal': Check if lists are equal (param: list)
        - 'join': Join list items into string with delimiter (param: str delimiter)
        - 'key_by': Create dict keyed by expression result (expression: Lua expression)
        - 'last': Last element
        - 'map': Apply a Lua expression to each item (expression: Lua expression)
        - 'max': Find maximum value in list
        - 'max_by': Find item with maximum property value (expression: Lua expression)
        - 'min': Find minimum value in list
        - 'min_by': Find item with minimum property value (expression: Lua expression)
        - 'nth': Get nth element (param: int, supports negative indexing)
        - 'partition': Split by expression result/boolean (expression: Lua expression)
        - 'pluck': Extract values by expression (expression: Lua expression)
        - 'random_except': Random item excluding condition (expression: Lua expression)
        - 'reduce': Aggregate the list using a binary Lua expression (uses 'acc' and
          'item') with optional initial accumulator value (param: initial value,
          expression: Lua expression)
        - 'sample': Get one random item
        - 'sample_size': Get n random items (param: int)
        - 'shuffle': Randomize order
        - 'sort_by': Sort by expression result (expression: Lua expression)
        - 'tail': All but first element
        - 'take': Take n elements from start (param: int)
        - 'take_right': Take n elements from end (param: int)
        - 'union': Unique values from all lists
        - 'uniq_by': Remove duplicates by expression result (expression: Lua expression)
        - 'unzip_list': Unzip list of lists
        - 'xor': Symmetric difference
        - 'zip_lists': Zip multiple lists
        - 'zip_with': Combine two lists element-wise using a binary Lua expression
          (requires others: list, expression: Lua expression using 'item' and 'other')

    Returns:
        dict: Result with 'value' key containing a list (most operations), single value
            ('head', 'last', 'nth', 'sample', 'max', 'min', etc.), dict ('group_by',
            'key_by'), string ('join'), or boolean ('is_empty', 'is_equal', 'contains').
            On error, includes 'error' key.

    Expression Examples:
        - Filtering: 'age > 25', 'score >= 80', 'name == 'Alice''
        - Grouping: 'age >= 30 and 'senior' or 'junior''
        - Sorting: 'age * -1' (reverse age), 'string.lower(name)' (case-insensitive)
        - Extraction: 'string.upper(name)', 'age > 18 and name or 'minor''
        - Math: 'math.abs(score - 50)', 'x*x + y*y' (distance squared)
        - Functional programming: Use tool functions as expressions (e.g.,
          `lists.map(items, 'strings.upper_case')`).

    In Lua expressions, item refers to the current list element, index (1-based) refers
    to the current position, and items refers to the full list. For zip_with, item
    refers to the current element from the first list and other refers to the current
    element from the second list. Available in expressions: math.*, string.*,
    os.time/date/clock, type(), tonumber(), tostring(). Dictionary keys accessible
    directly (age, name, etc.) or via item.key. You may pass a single Lua expression or
    a block of Lua code. For multi-line code, use return to specify the result.

    MCP Usage Examples:
        lists([{'id': 1}, {'id': 2}, {'id': 1}], 'uniq_by', expression='id')
          # => {'value': [{'id': 1}, {'id': 2}]}
        lists([{'age': 30}, {'age': 20}], 'find_by', expression='age > 25')
          # => {'value': {'age': 30}}
        lists([1, 2, 3], 'chunk', param=2)  # => {'value': [[1, 2], [3]]}
        lists([1, 2, 3], 'difference', others=[2, 3])  # => {'value': [1]}

    Lua Function Call Examples:
        lists.head({1, 2, 3})  # => 1
        lists.filter_by({{age=25}, {age=30}}, 'age > 25')  # => {{'age': 30}}
        lists.group_by(
            {items={{age=30}, {age=20}}, expression='age >= 25 and "adult" or "young"'}
        )  # => {'adult': [{age=30}], 'young': [{age=20}]}
        lists.difference({items={1, 2, 3}, others={2, 3}, wrap=true})
          # => JSON: [1], Lua: {'__type': 'list', 'data': {1}}

    In Lua, an empty table represents an empty dict **OR** an empty list. Lever tools
    serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
    dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
    {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
    serialization. Use unwrap(o) to get the original table.
    """
    return _lists_impl(items, operation, param, others, expression, wrap=False)


def _lists_impl(
    items: list,
    operation: str,
    param: Any = None,
    others: Optional[list] = None,
    expression: Optional[str] = None,
    wrap: bool = False,
) -> dict:
    if others is None:
        others = []

    # Handle wrapped list objects
    if isinstance(items, dict) and "__type" in items and "data" in items:
        if items["__type"] == "list":
            items = items["data"]
            # Convert Lua table to Python list if needed
            if hasattr(items, "keys"):
                keys = list(items.keys())
                if keys and all(isinstance(k, int) and k > 0 for k in keys):
                    max_k = max(keys)
                    items = [items.get(k) for k in range(1, max_k + 1)]
                else:
                    items = list(items.values())

    if isinstance(others, dict) and "__type" in others and "data" in others:
        if others["__type"] == "list":
            others = others["data"]
            # Convert Lua table to Python list if needed
            if hasattr(others, "keys"):
                keys = list(others.keys())
                if keys and all(isinstance(k, int) and k > 0 for k in keys):
                    max_k = max(keys)
                    others = [others.get(k) for k in range(1, max_k + 1)]
                else:
                    others = list(others.values())

    # Support xor, shuffle, sample_size, is_empty as well
    if operation == "xor":
        if not isinstance(items, list) or not isinstance(others, list):
            return {"value": None, "error": "Both arguments must be lists for xor."}
        try:
            return {"value": list(set(items) ^ set(others))}
        except TypeError:
            # Fallback for unhashable types (e.g., lists of lists/dicts)
            result = [x for x in items if x not in others] + [
                x for x in others if x not in items
            ]
            return {"value": result}
    elif operation == "shuffle":
        if not isinstance(items, list):
            return {"value": None, "error": "Argument must be a list for shuffle."}
        result = items[:]
        random.shuffle(result)
        return {"value": result}
    elif operation == "sample_size":
        if not isinstance(items, list):
            return {
                "value": None,
                "error": "Argument must be a list for sample_size.",
            }
        n = param if isinstance(param, int) else 1
        if n < 0:
            return {"value": None, "error": "sample_size must be non-negative."}
        return {"value": random.sample(items, min(n, len(items)))}
    elif operation == "is_empty":
        # Accept 0, False as empty for lists
        if items is None or items == 0 or items is False:
            return {"value": True}
        return {"value": len(items) == 0}

    """
    Performs list operations, including mutation, selection, set-like, grouping,
    and property checks. For set-like operations, use items as the first list and
    others as the second list.

    Supported operations: all_by, any_by, chunk, compact, contains, count_by,
    difference, difference_by, drop, drop_right, filter_by, find_by, flat_map,
    flatten, flatten_deep, group_by, head, index_of, initial, intersection,
    intersection_by, is_equal, key_by, last, map, max_by, min_by, nth, partition,
    pluck, random_except, reduce, remove_by, sample, sort_by, tail, take,
    take_right, union, uniq_by, unzip_list, zip_lists, zip_with
    """

    # Unwrap input parameters
    items = _unwrap_input(items)
    param = _unwrap_input(param)
    others = _unwrap_input(others)

    def evaluate_expression_optimized(expr, item, index=None, items_list=None):
        """Optimized expression evaluation with fast path for simple key access."""
        if isinstance(item, dict) and expr.isidentifier() and expr in item:
            # Fast path: simple key lookup without Lua runtime
            return item[expr]
        else:
            # Full expression evaluation
            context = {"item": item}
            if index is not None:
                context["index"] = index
            if items_list is not None:
                context["items"] = items_list
            return evaluate_expression(expr, item, context=context)

    try:
        # Mutations
        if operation == "flatten_deep":
            result = []

            def _flatten(lst):
                for i in lst:
                    if isinstance(i, list):
                        _flatten(i)
                    else:
                        result.append(i)

            _flatten(items)
            return {"value": result}
        elif operation == "sort_by":
            # Use expression if provided, otherwise use param as expression
            sort_expr = expression or (param if isinstance(param, str) else None)
            if not sort_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'sort_by'."
                    ),
                }

            def get_sort_key(x):
                # For sort operations, we don't have a meaningful index context since
                # the order changes
                result = evaluate_expression_optimized(sort_expr, x)
                # Handle different result types for sorting
                if result is None:
                    return ""  # Sort None values first
                elif isinstance(result, dict):
                    return json.dumps(result, sort_keys=True)
                return result

            return {"value": sorted(items, key=get_sort_key)}
        elif operation == "uniq_by":
            # Use expression if provided, otherwise use param as expression
            uniq_expr = expression or (param if isinstance(param, str) else None)
            if not uniq_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'uniq_by'."
                    ),
                }
            seen = set()
            result = []
            for index, item in enumerate(items, 1):
                k = evaluate_expression_optimized(uniq_expr, item, index, items)
                k_hash = json.dumps(k, sort_keys=True) if isinstance(k, dict) else k
                if k_hash not in seen:
                    seen.add(k_hash)
                    result.append(item)
            return {"value": result}
        elif operation == "partition":
            # Use expression if provided, otherwise use param as expression
            part_expr = expression or (param if isinstance(param, str) else None)
            if not part_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'partition'."
                    ),
                }
            trues, falses = [], []
            for index, item in enumerate(items, 1):
                result = evaluate_expression_optimized(part_expr, item, index, items)
                (trues if result else falses).append(item)
            return {"value": [trues, falses]}
        elif operation == "pluck":
            # Use expression if provided, otherwise use param as expression
            pluck_expr = expression or (param if isinstance(param, str) else None)
            if not pluck_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'pluck'."
                    ),
                }
            return {
                "value": [
                    evaluate_expression_optimized(pluck_expr, item, index, items)
                    for index, item in enumerate(items, 1)
                ]
            }
        elif operation == "compact":
            return {"value": [item for item in items if item]}
        elif operation == "chunk":
            size = int(param)
            return {"value": [items[i : i + size] for i in range(0, len(items), size)]}
        elif operation == "zip_lists":
            return {"value": [list(t) for t in zip(*items)]}
        elif operation == "unzip_list":
            return {"value": [list(t) for t in zip(*items)]}
        elif operation == "remove_by":
            if not expression:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression parameter for operation "
                        "'remove_by'."
                    ),
                }
            return {
                "value": [
                    item
                    for index, item in enumerate(items, 1)
                    if not evaluate_expression_optimized(expression, item, index, items)
                ]
            }
        elif operation == "tail":
            result = {"value": items[1:] if len(items) > 1 else []}
            return _wrap_result(result, wrap)
        elif operation == "initial":
            result = {"value": items[:-1] if items else []}
            return _wrap_result(result, wrap)
        elif operation == "drop":
            return {"value": items[int(param) :]}
        elif operation == "drop_right":
            return {"value": items[: -int(param)] if int(param) > 0 else items[:]}
        elif operation == "take":
            return {"value": items[: int(param)]}
        elif operation == "take_right":
            result = {"value": items[-int(param) :] if int(param) > 0 else []}
            return _wrap_result(result, wrap)
        elif operation == "flatten":
            result = []
            for sublist in items:
                if isinstance(sublist, list):
                    result.extend(sublist)
                else:
                    result.append(sublist)
            return {"value": result}
        elif operation == "union":
            result = []
            seen = set()
            for sublist in items:
                for item in sublist:
                    if item not in seen:
                        seen.add(item)
                        result.append(item)
            return {"value": result}
        # Set-like operations
        elif operation == "difference_by":
            # Use expression if provided, otherwise use param as expression
            diff_expr = expression or (param if isinstance(param, str) else None)
            if not diff_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'difference_by'."
                    ),
                }

            # Extract keys from others list using expression
            others_keys = set()
            for index, item in enumerate(others, 1):
                key_val = evaluate_expression_optimized(diff_expr, item, index, others)
                others_keys.add(key_val)

            # Return items from main list whose key is not in others_keys
            result = []
            for index, item in enumerate(items, 1):
                key_val = evaluate_expression_optimized(diff_expr, item, index, items)
                if key_val not in others_keys:
                    result.append(item)

            return {"value": result}
        elif operation == "intersection_by":
            # Use expression if provided, otherwise use param as expression
            inter_expr = expression or (param if isinstance(param, str) else None)
            if not inter_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'intersection_by'."
                    ),
                }

            # Extract keys from others list using expression
            others_keys = set()
            for index, item in enumerate(others, 1):
                key_val = evaluate_expression_optimized(inter_expr, item, index, others)
                others_keys.add(key_val)

            # Return items from main list whose key is in others_keys
            result = []
            for index, item in enumerate(items, 1):
                key_val = evaluate_expression_optimized(inter_expr, item, index, items)
                if key_val in others_keys:
                    result.append(item)

            return {"value": result}
        elif operation == "intersection":
            # Support intersection for multiple lists (not just two)
            if isinstance(items, list) and all(isinstance(x, list) for x in items):
                # If others is provided and is a list of lists, do value-based
                # intersection
                if others and all(isinstance(x, list) for x in others):
                    result = [x for x in items if any(x == y for y in others)]
                    return {"value": result}
                # Otherwise, do intersection across all sublists (lists of lists of
                # lists)
                if not items:
                    return {"value": []}
                result = (
                    set(tuple(x) for x in items[0])
                    if all(isinstance(x, list) for x in items[0])
                    else set(tuple(x) for x in items[0:1])
                )
                for sublist in items[1:]:
                    result &= set(tuple(x) for x in sublist)
                return {"value": [list(x) for x in result]}
            elif isinstance(items, list) and isinstance(others, list):
                # If both are lists of lists, compare by value (not tuple)
                if all(isinstance(x, list) for x in items) and all(
                    isinstance(x, list) for x in others
                ):
                    result = [x for x in items if any(x == y for y in others)]
                    return {"value": result}
                try:
                    return {"value": [item for item in items if item in others]}
                except TypeError:
                    # Fallback for unhashable types
                    return {
                        "value": [
                            item
                            for item in items
                            if any(
                                json.dumps(item, sort_keys=True)
                                == json.dumps(other, sort_keys=True)
                                for other in others
                            )
                        ]
                    }
            else:
                return {"value": []}
        elif operation == "difference":
            if isinstance(items, list) and all(isinstance(x, list) for x in items):
                if not items:
                    return {"value": []}
                result = set(items[0])
                for sublist in items[1:]:
                    result -= set(sublist)
                return {"value": list(result)}
            elif isinstance(items, list) and isinstance(others, list):
                try:
                    return {"value": [item for item in items if item not in others]}
                except TypeError:
                    # Fallback for unhashable types
                    return {
                        "value": [
                            item
                            for item in items
                            if all(
                                json.dumps(item, sort_keys=True)
                                != json.dumps(other, sort_keys=True)
                                for other in others
                            )
                        ]
                    }
            else:
                return {"value": []}
        # Grouping/Counting
        elif operation == "group_by":
            # Use expression if provided, otherwise use param as expression
            group_expr = expression or (param if isinstance(param, str) else None)
            if not group_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'group_by'."
                    ),
                }
            result = {}
            for index, item in enumerate(items, 1):
                try:
                    k = evaluate_expression_optimized(group_expr, item, index, items)
                    # Convert result to string for consistent grouping
                    k = str(k) if k is not None else "None"
                    result.setdefault(k, []).append(item)
                except Exception:
                    # If expression fails, group under "error"
                    result.setdefault("error", []).append(item)
            return {"value": result}
        elif operation == "count_by":
            # Use expression if provided, otherwise use param as expression
            count_expr = expression or (param if isinstance(param, str) else None)
            if not count_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'count_by'."
                    ),
                }
            result = {}
            for index, item in enumerate(items, 1):
                k = evaluate_expression_optimized(count_expr, item, index, items)
                # Convert result to string for consistent dictionary keys
                k = str(k) if k is not None else "null"
                result[k] = result.get(k, 0) + 1
            return {"value": result}
        elif operation == "key_by":
            # Use expression if provided, otherwise use param as expression
            key_expr = expression or (param if isinstance(param, str) else None)
            if not key_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'key_by'."
                    ),
                }
            # Convert integer keys to strings to avoid Lua table->list conversion
            result = {}
            for index, item in enumerate(items, 1):
                k = evaluate_expression_optimized(key_expr, item, index, items)
                # Convert integer keys to strings like JSON does
                if isinstance(k, int):
                    k = str(k)
                result[k] = item
            return {"value": result}
        # Selection
        elif operation == "find_by":
            # Use expression if provided, otherwise use param as expression
            find_expr = expression or (param if isinstance(param, str) else None)
            if not find_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'find_by'."
                    ),
                }

            # Find first item where expression is truthy
            for index, item in enumerate(items, 1):
                result = evaluate_expression_optimized(find_expr, item, index, items)
                if result:
                    return {"value": item}
            return {"value": None}
        elif operation == "head":
            if not isinstance(items, list):
                return {"value": None, "error": "head operation requires a list"}
            return {"value": items[0] if items else None}
        elif operation == "last":
            if not isinstance(items, list):
                return {"value": None, "error": "last operation requires a list"}
            return {"value": items[-1] if items else None}
        elif operation == "sample":
            if not isinstance(items, list):
                return {"value": None, "error": "sample operation requires a list"}
            if not items:
                return {"value": None}
            return {"value": random.choice(items)}
        elif operation == "nth":
            if not isinstance(items, list):
                return {"value": None, "error": "nth operation requires a list"}
            idx = param
            if param is None:
                return {
                    "value": None,
                    "error": "nth operation requires an index parameter",
                }
            if -len(items) <= idx < len(items):
                return {"value": items[idx]}
            return {"value": None}
        elif operation == "min_by":
            # Use expression if provided, otherwise use param as expression
            min_expr = expression or (param if isinstance(param, str) else None)
            if not min_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'min_by'."
                    ),
                }

            def min_key(x):
                # For sort operations, we don't have a meaningful index context
                result = evaluate_expression_optimized(min_expr, x)
                return result if result is not None else float("inf")

            return {"value": min(items, key=min_key)}
        elif operation == "max_by":
            # Use expression if provided, otherwise use param as expression
            max_expr = expression or (param if isinstance(param, str) else None)
            if not max_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'max_by'."
                    ),
                }

            def max_key(x):
                # For sort operations, we don't have a meaningful index context
                result = evaluate_expression_optimized(max_expr, x)
                return result if result is not None else float("-inf")

            return {"value": max(items, key=max_key)}
        elif operation == "index_of":
            # Use expression if provided, otherwise use param as expression
            index_expr = expression or (param if isinstance(param, str) else None)
            if not index_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'index_of'."
                    ),
                }

            # Find first item where expression is truthy
            for idx, item in enumerate(items):
                # Note: idx is 0-based for index_of operation, but we pass 1-based index
                # to expressions
                result = evaluate_expression_optimized(index_expr, item, idx + 1, items)
                if result:
                    return {"value": idx}
            return {"value": -1}
        elif operation == "random_except":
            # Use expression if provided, otherwise use param as expression
            except_expr = expression or (param if isinstance(param, str) else None)
            if not except_expr:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression or param parameter for operation "
                        "'random_except'."
                    ),
                }

            # Exclude items where expression is truthy
            filtered = [
                item
                for index, item in enumerate(items, 1)
                if not evaluate_expression_optimized(except_expr, item, index, items)
            ]
            if not filtered:
                return {"value": None}
            return {"value": random.choice(filtered)}
        # New: contains, is_equal
        elif operation == "contains":
            return {"value": param in items}
        elif operation == "is_equal":
            return {"value": items == param}
        # --- New Functional Operations ---
        elif operation == "map":
            if not expression:
                return {"value": None, "error": "'expression' is required for map."}
            result = []
            for index, item in enumerate(items, 1):
                mapped = evaluate_expression(
                    expression,
                    item,
                    context={"item": item, "index": index, "items": items},
                )
                result.append(mapped)
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "reduce":
            if not expression:
                return {"value": None, "error": "'expression' is required for reduce."}
            if not items:
                return {"value": param if param is not None else None}
            acc = param if param is not None else items[0]
            start_idx = 0 if param is not None else 1
            for i in range(start_idx, len(items)):
                # The Lua expression can use 'acc' and 'item'
                acc = evaluate_expression(
                    expression, None, context={"acc": acc, "item": items[i]}
                )
            return {"value": acc}
        elif operation == "flat_map":
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for flat_map.",
                }
            result = []
            for index, item in enumerate(items, 1):
                mapped = evaluate_expression(
                    expression,
                    item,
                    context={"item": item, "index": index, "items": items},
                )
                # Convert Lua tables to Python lists
                from lib.lua import lua_to_python
                if "LuaTable" in type(mapped).__name__:
                    mapped = lua_to_python(mapped)
                if isinstance(mapped, list):
                    result.extend(mapped)
                else:
                    result.append(mapped)
            return {"value": result}
        elif operation in ("all_by", "every"):
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for all_by/every.",
                }
            return {
                "value": all(
                    bool(
                        evaluate_expression(
                            expression,
                            item,
                            context={"item": item, "index": index, "items": items},
                        )
                    )
                    for index, item in enumerate(items, 1)
                )
            }
        elif operation in ("any_by", "some"):
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for any_by/some.",
                }
            return {
                "value": any(
                    bool(
                        evaluate_expression(
                            expression,
                            item,
                            context={"item": item, "index": index, "items": items},
                        )
                    )
                    for index, item in enumerate(items, 1)
                )
            }
        elif operation == "filter_by":
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for filter_by.",
                }
            return {
                "value": [
                    item
                    for index, item in enumerate(items, 1)
                    if bool(
                        evaluate_expression(
                            expression,
                            item,
                            context={"item": item, "index": index, "items": items},
                        )
                    )
                ]
            }
        elif operation == "zip_with":
            if not expression:
                return {
                    "value": None,
                    "error": "'expression' is required for zip_with.",
                }
            if not isinstance(items, list) or not isinstance(others, list):
                return {
                    "value": None,
                    "error": "Both 'items' and 'others' must be lists for zip_with.",
                }
            min_len = min(len(items), len(others))
            result = []
            for i in range(min_len):
                val = evaluate_expression(
                    expression, None, context={"item": items[i], "other": others[i]}
                )
                result.append(val)
            return {"value": result}
        # --- End New Functional Operations ---
        elif operation == "min":
            if not items:
                return {"value": None, "error": "Cannot find minimum of empty list"}
            try:
                return {"value": min(items)}
            except TypeError as e:
                return {
                    "value": None,
                    "error": f"Cannot compare items for minimum: {e}",
                }
        elif operation == "max":
            if not items:
                return {"value": None, "error": "Cannot find maximum of empty list"}
            try:
                return {"value": max(items)}
            except TypeError as e:
                return {
                    "value": None,
                    "error": f"Cannot compare items for maximum: {e}",
                }
        elif operation == "join":
            delimiter = param if param is not None else ""
            return {"value": delimiter.join(str(item) for item in items)}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}


# Export the main function for use in other modules
__all__ = ['lists_tool', '_lists_impl']