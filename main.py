from fastmcp import FastMCP
from typing import Any, Dict, List, Optional
import inspect
import argparse
import lupa

# Global configuration for Lua safety mode
SAFE_MODE = True  # Default to safe mode, can be overridden by command line


# --- MCP Server Setup ---


class LeverMCP(FastMCP):
    pass


mcp = LeverMCP("Lever MCP")


@mcp.tool()
def strings(
    text: Optional[str] = None,
    operation: Optional[str] = None,
    param: Any = None,
    data: Optional[dict] = None,
    items: Any = None,
) -> dict:
    """
    Performs string operations and mutations.

    Parameters:
        text (str): The input string to operate on.
        operation (str): The operation to perform. One of:
            - 'camel_case': Converts to camelCase (e.g., 'foo bar' → 'fooBar').
            - 'capitalize': Capitalizes the first character (e.g.,
              'foo bar' → 'Foo bar').
            - 'contains': Checks if string contains a substring (param: str to find).
            - 'deburr': Removes accents/diacritics (e.g., 'Café' → 'Cafe').
            - 'ends_with': Checks if string ends with substring (param: str).
            - 'is_alpha': Checks if string contains only alphabetic characters.
            - 'is_digit': Checks if string contains only digits.
            - 'is_empty': Checks if string is empty.
            - 'is_equal': Checks if strings are equal (param: str to compare).
            - 'is_lower': Checks if string is all lowercase.
            - 'is_upper': Checks if string is all uppercase.
            - 'kebab_case': Converts to kebab-case (e.g., 'foo bar' → 'foo-bar').
            - 'lower_case': Converts to lowercase (e.g., 'Hello' → 'hello').
            - 'replace': Replaces all occurrences of a substring (requires
              data={'old': 'x', 'new': 'y'}).
            - 'reverse': Reverses the string (e.g., 'hello' → 'olleh').
            - 'sample_size': Returns n random characters (param: int).
            - 'shuffle': Randomly shuffles string characters.
            - 'snake_case': Converts to snake_case (e.g., 'foo bar' → 'foo_bar').
            - 'starts_with': Checks if string starts with substring (param: str).
            - 'template': Interpolates variables using {var} syntax (requires data
              dict).
            - 'trim': Removes leading and trailing whitespace.
            - 'upper_case': Converts to uppercase (e.g., 'Hello' → 'HELLO').
            - 'xor': String-specific XOR operation (param: str).
        param (Any, optional): Parameter for operations that require one.
        data (dict, optional): Data for 'template' and 'replace' operations.

    Returns:
        dict: The result, always wrapped in a dictionary with a 'value' key. If an error
            occurs, an 'error' key is also present.

    Usage Example:
        strings('foo bar', 'camel_case')  # => {'value': 'fooBar'}
        strings('Hello, {name}!', 'template', data={'name': 'World'})
          # => {'value': 'Hello, World!'}
        strings('abc', 'contains', param='a')  # => {'value': True}
    """
    # Accept 'items' as an alias for text for compatibility with test_extended.py
    if text is None and items is not None:
        text = items
    if text is None:
        text = ""
    if data is None:
        data = {}
    if text is None:
        text = ""
    if data is None:
        data = {}
    import re
    import unicodedata

    try:
        if operation == "deburr":
            result = "".join(
                c
                for c in unicodedata.normalize("NFKD", text)
                if not unicodedata.combining(c)
            )
        elif operation == "template":
            if not data:
                raise ValueError("'data' argument is required for 'template' mutation.")

            def replacer(match):
                key = match.group(1)
                return str(data.get(key, match.group(0)))

            result = re.sub(r"\{(\w+)\}", replacer, text)
        elif operation == "camel_case":
            s = re.sub(r"(_|-)+", " ", text).title().replace(" ", "")
            result = s[0].lower() + s[1:] if s else ""
        elif operation == "kebab_case":
            s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
            result = re.sub(r"(\s|_|-)+", "-", s).lower().strip("-_")
        elif operation == "snake_case":
            s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
            result = re.sub(r"(\s|-)+", "_", s).lower().strip("-_")
        elif operation == "capitalize":
            result = text.capitalize()
        elif operation == "reverse":
            result = text[::-1]
        elif operation == "trim":
            result = text.strip()
        elif operation == "lower_case":
            result = text.lower()
        elif operation == "upper_case":
            result = text.upper()
        elif operation == "replace":
            if not data or "old" not in data or "new" not in data:
                raise ValueError(
                    "'data' with 'old' and 'new' is required for 'replace' mutation."
                )
            result = text.replace(data["old"], data["new"])
        elif operation == "starts_with":
            result = text.startswith(param)
        elif operation == "ends_with":
            result = text.endswith(param)
        elif operation == "is_empty":
            if isinstance(text, str):
                result = len(text) == 0
            elif isinstance(text, list) or isinstance(text, dict):
                result = len(text) == 0
            elif text is None:
                result = True
            elif text == 0 or text is False:
                result = True
            else:
                result = False
        elif operation == "xor":
            # Symmetric difference of two lists
            if not isinstance(text, list) or not isinstance(param, list):
                return {"value": None, "error": "Both arguments must be lists for xor."}
            result = list(set(text) ^ set(param))
        elif operation == "shuffle":
            import random

            if not isinstance(text, list):
                return {"value": None, "error": "Argument must be a list for shuffle."}
            result = list(text)
            random.shuffle(result)
        elif operation == "sample_size":
            import random

            if not isinstance(text, list):
                return {
                    "value": None,
                    "error": "Argument must be a list for sample_size.",
                }
            n = param if isinstance(param, int) else 1
            if n < 0:
                return {"value": None, "error": "sample_size must be non-negative."}
            result = random.sample(text, min(n, len(text)))
        elif operation == "is_equal":
            result = text == param
        elif operation == "contains":
            result = param in text
        elif operation == "is_digit":
            result = text.isdigit()
        elif operation == "is_alpha":
            result = text.isalpha()
        elif operation == "is_upper":
            result = text.isupper()
        elif operation == "is_lower":
            result = text.islower()
        else:
            raise ValueError(f"Unknown operation: {operation}")
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": str(e)}


@mcp.tool()
def lists(
    items: Optional[list] = None,
    operation: Optional[str] = None,
    param: Any = None,
    others: Optional[list] = None,
    key: str = "",
    text: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """
    Performs list operations and mutations with support for Lua expressions.

    Parameters:
        items (list): The input list to operate on.
        operation (str): The operation to perform. Available operations:
            EXPRESSION OPERATIONS (use expression parameter):
            - 'count_by': Count occurrences by expression result/key
            - 'difference_by': Items in first list not matching expression in second
            - 'find_by': Find first item matching expression/key-value
            - 'group_by': Group items by expression result/key value
            - 'intersection_by': Items in first list matching expression in second
            - 'key_by': Create dict keyed by expression result/field
            - 'max_by': Find max by expression result/key
            - 'min_by': Find min by expression result/key
            - 'partition': Split by expression result/boolean key
            - 'pluck': Extract values by expression/key (expression: any value)
            - 'remove_by': Remove items matching expression/key-value
            - 'sort_by': Sort by expression result/key
              (expression: any comparable value)
            - 'uniq_by': Remove duplicates by expression result/key

            BASIC OPERATIONS:
            - 'chunk': Split into chunks (param: int)
            - 'compact': Remove falsy values
            - 'contains': Check if item exists (param: value)
            - 'drop': Drop n elements from start (param: int)
            - 'drop_right': Drop n elements from end (param: int)
            - 'flatten': Flatten one level
            - 'flatten_deep': Flatten completely
            - 'head': First element
            - 'index_of': Find index of item (param: dict with 'key' and 'value')
            - 'initial': All but last element
            - 'is_empty': Check if list is empty
            - 'is_equal': Check if lists are equal (param: list)
            - 'last': Last element
            - 'nth': Get nth element (param: int, supports negative indexing)
            - 'random_except': Random item excluding condition
              (param: dict with 'key' and 'value')
            - 'sample': Get one random item
            - 'sample_size': Get n random items (param: int)
            - 'shuffle': Randomize order
            - 'tail': All but first element
            - 'take': Take n elements from start (param: int)
            - 'take_right': Take n elements from end (param: int)

            SET OPERATIONS (use others parameter):
            - 'difference': Items in first not in second
            - 'intersection': Items in both lists
            - 'union': Unique values from all lists
            - 'xor': Symmetric difference

            UTILITIES:
            - 'unzip_list': Unzip list of tuples
            - 'zip_lists': Zip multiple lists

        param (Any, optional): Parameter for operations requiring one
        others (list, optional): Second list for set operations
        key (str, optional): Property name for *_by operations (faster, alternative to
            expression)
        expression (str, optional): Lua expression for advanced
            filtering/grouping/sorting/extraction

    Expression Examples:
        - Filtering: "age > 25", "score >= 80", "name == 'Alice'"
        - Complex conditions: "age > 25 and score >= 80", "status == 'active' or
          priority == 'high'"
        - Grouping: "age >= 30 and 'senior' or 'junior'"
        - Sorting: "age * -1" (reverse age), "string.lower(name)" (case-insensitive)
        - Extraction: "string.upper(name)", "age > 18 and name or 'minor'"
        - Math: "math.abs(score - 50)", "x*x + y*y" (distance squared)

    Available in expressions: math.*, string.*, os.time/date/clock, type(), tonumber(),
    tostring(). Dictionary keys accessible directly (age, name, etc.) or via item.key.

    Returns:
        dict: Result with 'value' key. On error, includes 'error' key.

    Examples:
        lists([{'id': 1}, {'id': 2}, {'id': 1}], 'uniq_by', key='id')
          # => {'value': [{'id': 1}, {'id': 2}]}
        lists([{'age': 30}, {'age': 20}], 'find_by', expression="age > 25")
          # => {'value': {'age': 30}}
        lists(
            [{'age': 30}, {'age': 20}],
            'group_by',
            expression="age >= 25 and 'adult' or 'young'"
        )  # => {'value': {'adult': [{'age': 30}], 'young': [{'age': 20}]}}
        lists(
            [{'name': 'bob'},
            {'name': 'Alice'}],
            'sort_by', expression="string.lower(name)"
        )  # => {'value': [{'name': 'Alice'}, {'name': 'bob'}]}
        lists([{'x': 1, 'y': 2}, {'x': 3, 'y': 4}], 'pluck', expression="x + y")
          # => {'value': [3, 7]}
        lists([1, 2, 3], 'chunk', param=2)  # => {'value': [[1, 2], [3]]}
        lists([1, 2, 3], 'difference', others=[2, 3])  # => {'value': [1]}
    """
    # Accept 'text' as an alias for items for compatibility with test_extended.py
    if items is None and text is not None:
        items = text
    if items is None:
        items = []
    if others is None:
        others = []
    if items is None:
        items = []
    if others is None:
        others = []
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
        import random

        if not isinstance(items, list):
            return {"value": None, "error": "Argument must be a list for shuffle."}
        result = items[:]
        random.shuffle(result)
        return {"value": result}
    elif operation == "sample_size":
        import random

        if not isinstance(items, list):
            return {"value": None, "error": "Argument must be a list for sample_size."}
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
    Performs list operations, including mutation, selection, set-like, grouping, and
    property checks. For set-like operations, use items as the first list and others as
    the second list.
    Supported operations: flatten_deep, sort_by, uniq_by, partition, pluck, compact,
    chunk, zip_lists, unzip_list, remove_by, tail, initial, drop, drop_right, take,
    take_right, flatten, union, difference_by, intersection_by, intersection,
    difference, group_by, count_by, key_by, find_by, head, last, sample, nth, min_by,
    max_by, index_of, random_except, contains, is_equal
    """
    import random, json

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
            if expression:
                # Use Lua expression for sorting
                def get_sort_key_expr(x):
                    result = evaluate_expression(expression, x)
                    # Handle different result types for sorting
                    if result is None:
                        return ""  # Sort None values first
                    elif isinstance(result, dict):
                        return json.dumps(result, sort_keys=True)
                    return result

                return {"value": sorted(items, key=get_sort_key_expr)}
            elif param:
                # Use traditional key-based sorting
                def get_sort_key_param(x):
                    v = (
                        x.get(param, "")
                        if isinstance(x, dict)
                        else getattr(x, param, "")
                    )
                    if isinstance(v, dict):
                        return json.dumps(v, sort_keys=True)
                    return v

                return {"value": sorted(items, key=get_sort_key_param)}
            else:
                return {
                    "value": None,
                    "error": (
                        "Missing required param (key name) or expression for operation "
                        "'sort_by'.",
                    ),
                }
        elif operation == "uniq_by":
            seen = set()
            result = []
            for item in items:
                k = (
                    item.get(param)
                    if isinstance(item, dict)
                    else getattr(item, param, None)
                )
                k_hash = json.dumps(k, sort_keys=True) if isinstance(k, dict) else k
                if k_hash not in seen:
                    seen.add(k_hash)
                    result.append(item)
            return {"value": result}
        elif operation == "partition":
            trues, falses = [], []
            for item in items:
                result = (
                    item.get(param)
                    if isinstance(item, dict)
                    else getattr(item, param, False)
                )
                (trues if result else falses).append(item)
            return {"value": [trues, falses]}
        elif operation == "pluck":
            if expression:
                # Use Lua expression for extraction
                return {
                    "value": [evaluate_expression(expression, item) for item in items]
                }
            elif param:
                # Use traditional key-based extraction
                return {
                    "value": [
                        (
                            item.get(param)
                            if isinstance(item, dict)
                            else getattr(item, param, None)
                        )
                        for item in items
                    ]
                }
            else:
                return {
                    "value": None,
                    "error": (
                        "Missing required param (key name) or expression for operation "
                        "'pluck'.",
                    ),
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
            if expression:
                # Use Lua expression - remove items that match the expression
                return {
                    "value": [
                        item
                        for item in items
                        if not evaluate_expression(expression, item)
                    ]
                }
            else:
                # Use traditional key-value matching
                key_ = param["key"]
                value_ = param["value"]
                return {
                    "value": [
                        item
                        for item in items
                        if (
                            item.get(key_)
                            if isinstance(item, dict)
                            else getattr(item, key_, None)
                        )
                        != value_
                    ]
                }
        elif operation == "tail":
            return {"value": items[1:] if len(items) > 1 else []}
        elif operation == "initial":
            return {"value": items[:-1] if items else []}
        elif operation == "drop":
            return {"value": items[int(param) :]}
        elif operation == "drop_right":
            return {"value": items[: -int(param)] if int(param) > 0 else items[:]}
        elif operation == "take":
            return {"value": items[: int(param)]}
        elif operation == "take_right":
            return {"value": items[-int(param) :] if int(param) > 0 else []}
        elif operation == "flatten":
            return {"value": [item for sublist in items for item in sublist]}
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
            if expression:
                # Use Lua expression to find matching items in others
                others_matching_expression = [
                    item for item in others if evaluate_expression(expression, item)
                ]
                # Return items from main list that don't match any in others
                return {
                    "value": [
                        item
                        for item in items
                        if not any(
                            evaluate_expression(expression, other)
                            and evaluate_expression(expression, item)
                            for other in others_matching_expression
                        )
                    ]
                }
            elif not key:
                return {
                    "value": None,
                    "error": (
                        "Missing required key parameter or expression for operation "
                        "'difference_by'.",
                    ),
                }
            else:
                # Use traditional key-based comparison
                others_keys = set(
                    (
                        item.get(key)
                        if isinstance(item, dict)
                        else getattr(item, key, None)
                    )
                    for item in others
                )
                return {
                    "value": [
                        item
                        for item in items
                        if (
                            item.get(key)
                            if isinstance(item, dict)
                            else getattr(item, key, None)
                        )
                        not in others_keys
                    ]
                }
        elif operation == "intersection_by":
            if expression:
                # Use Lua expression to find matching items in others
                others_matching_expression = [
                    item for item in others if evaluate_expression(expression, item)
                ]
                # Return items from main list that match any in others
                return {
                    "value": [
                        item
                        for item in items
                        if any(
                            evaluate_expression(expression, other)
                            and evaluate_expression(expression, item)
                            for other in others_matching_expression
                        )
                    ]
                }
            elif not key:
                return {
                    "value": None,
                    "error": (
                        "Missing required key parameter or expression for operation "
                        "'intersection_by'.",
                    ),
                }
            else:
                # Use traditional key-based comparison
                others_keys = set(
                    (
                        item.get(key)
                        if isinstance(item, dict)
                        else getattr(item, key, None)
                    )
                    for item in others
                )
                return {
                    "value": [
                        item
                        for item in items
                        if (
                            item.get(key)
                            if isinstance(item, dict)
                            else getattr(item, key, None)
                        )
                        in others_keys
                    ]
                }
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
            if expression:
                # Use Lua expression to compute grouping key
                result = {}
                for item in items:
                    try:
                        k = evaluate_expression(expression, item)
                        # Convert result to string for consistent grouping
                        k = str(k) if k is not None else "None"
                        result.setdefault(k, []).append(item)
                    except Exception:
                        # If expression fails, group under "error"
                        result.setdefault("error", []).append(item)
                return {"value": result}
            elif not key:
                return {
                    "value": None,
                    "error": (
                        "Missing required key parameter or expression for operation "
                        "'group_by'.",
                    ),
                }
            else:
                # Use traditional key-based grouping
                if not all(isinstance(item, dict) for item in items):
                    return {
                        "value": None,
                        "error": "All items must be dicts for operation 'group_by'.",
                    }
                result = {}
                for item in items:
                    k = item.get(key)
                    result.setdefault(k, []).append(item)
                return {"value": result}
        elif operation == "count_by":
            if not key:
                return {
                    "value": None,
                    "error": "Missing required key parameter for operation 'count_by'.",
                }
            if not all(isinstance(item, dict) for item in items):
                return {
                    "value": None,
                    "error": "All items must be dicts for operation 'count_by'.",
                }
            result = {}
            for item in items:
                k = item.get(key)
                result[k] = result.get(k, 0) + 1
            return {"value": result}
        elif operation == "key_by":
            if not key:
                return {
                    "value": None,
                    "error": "Missing required key parameter for operation 'key_by'.",
                }
            if not all(isinstance(item, dict) for item in items):
                return {
                    "value": None,
                    "error": "All items must be dicts for operation 'key_by'.",
                }
            return {"value": {item[key]: item for item in items}}
        # Selection
        elif operation == "find_by":
            if expression:
                # Use Lua expression
                for item in items:
                    result = evaluate_expression(expression, item)
                    # For find_by, treat result as boolean (truthy/falsy)
                    if result:
                        return {"value": item}
                return {"value": None}
            else:
                # Use traditional key-value matching
                key_ = param["key"]
                value_ = param["value"]
                if not all(isinstance(item, dict) for item in items):
                    return {
                        "value": None,
                        "error": "All items must be dicts for find_by.",
                    }
                for item in items:
                    v = item.get(key_)
                    if v == value_:
                        return {"value": item}
                return {"value": None}
        elif operation == "head":
            return {"value": items[0] if items else None}
        elif operation == "last":
            return {"value": items[-1] if items else None}
        elif operation == "sample":
            if not items:
                return {"value": None}
            return {"value": random.choice(items)}
        elif operation == "nth":
            idx = param
            if -len(items) <= idx < len(items):
                return {"value": items[idx]}
            return {"value": None}
        elif operation == "min_by":
            if expression:
                # Use Lua expression for min comparison
                def min_key_expr(x):
                    result = evaluate_expression(expression, x)
                    return result if result is not None else float("inf")

                return {"value": min(items, key=min_key_expr)}
            elif param:
                # Use traditional key-based min
                key_ = param

                def min_key_param(x):
                    v = x.get(key_) if isinstance(x, dict) else getattr(x, key_, None)
                    return v if v is not None else float("inf")

                return {"value": min(items, key=min_key_param)}
            else:
                return {
                    "value": None,
                    "error": (
                        "Missing required param (key name) or expression for operation "
                        "'min_by'.",
                    ),
                }
        elif operation == "max_by":
            if expression:
                # Use Lua expression for max comparison
                def max_key_expr(x):
                    result = evaluate_expression(expression, x)
                    return result if result is not None else float("-inf")

                return {"value": max(items, key=max_key_expr)}
            elif param:
                # Use traditional key-based max
                key_ = param

                def max_key_param(x):
                    v = x.get(key_) if isinstance(x, dict) else getattr(x, key_, None)
                    return v if v is not None else float("-inf")

                return {"value": max(items, key=max_key_param)}
            else:
                return {
                    "value": None,
                    "error": (
                        "Missing required param (key name) or expression for operation "
                        "'max_by'.",
                    ),
                }
        elif operation == "index_of":
            key_ = param["key"]
            value_ = param["value"]
            for idx, item in enumerate(items):
                v = (
                    item.get(key_)
                    if isinstance(item, dict)
                    else getattr(item, key_, None)
                )
                if v == value_:
                    return {"value": idx}
            return {"value": -1}
        elif operation == "random_except":
            key_ = param["key"]
            value_ = param["value"]
            filtered = [
                item
                for item in items
                if (
                    item.get(key_)
                    if isinstance(item, dict)
                    else getattr(item, key_, None)
                )
                != value_
            ]
            if not filtered:
                return {"value": None}
            return {"value": random.choice(filtered)}
        # New: contains, is_equal
        elif operation == "contains":
            return {"value": param in items}
        elif operation == "is_equal":
            return {"value": items == param}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}


@mcp.tool()
def dicts(
    obj: Any = None,
    operation: Optional[str] = None,
    param: Any = None,
    path: Any = None,
    value: Any = None,
    default: Any = None,
) -> dict:
    """
    Performs dictionary operations, including merge, set/get value, and property checks.

    Parameters:
        obj (dict or list): The source dictionary, or a list of dicts for 'merge'. Must
            be a dict for all operations except 'merge'.
        operation (str): The operation to perform. One of:
            - 'get_value': Gets a deep property by path (path: str or list,
              default: any).
            - 'has_key': Checks if a dict has a given key (param: str).
            - 'invert': Swaps keys and values.
            - 'is_empty': Checks if the dict is empty.
            - 'is_equal': Checks if two dicts are deeply equal (param: dict to compare).
            - 'merge': Deep merges a list of dictionaries (obj must be a list of dicts).
            - 'omit': Omits specified keys (param: list of keys).
            - 'pick': Picks specified keys (param: list of keys).
            - 'set_value': Sets a deep property by path (path: str or list, value: any).
        param (any, optional): Used for 'pick', 'omit', 'has_key', 'is_equal'.
        path (str or list, optional): Used for 'set_value' and 'get_value'.
        value (any, optional): Used for 'set_value'.
        default (any, optional): Used for 'get_value'.

    Returns:
        dict: The result, always wrapped in a dictionary with a 'value' key. If an error
            occurs, an 'error' key is also present.

    Usage Example:
        dicts({'a': 1, 'b': 2}, 'pick', ['a'])  # => {'value': {'a': 1}}
        dicts({'a': {'b': 1}}, 'set_value', path=['a', 'b'], value=2)
          # => {'value': {'a': {'b': 2}}}
        dicts({'a': 1}, 'get_value', path='b', default=42)  # => {'value': 42}
    """
    """
    Performs dictionary operations, including merge, set/get value, and property checks.
    For 'merge', obj should be a list of dicts. For other operations, obj should be a
    dict.
    Supported operations: merge, invert, pick, omit, set_value, get_value, has_key,
    is_equal, is_empty
    """
    import copy, re

    try:
        if operation == "merge":

            def deep_merge(a, b):
                for k, v in b.items():
                    if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                        a[k] = deep_merge(a[k], v)
                    else:
                        a[k] = copy.deepcopy(v)
                return a

            result = {}
            for d in obj:
                if not isinstance(d, dict):
                    return {
                        "value": None,
                        "error": "All items in obj must be dictionaries for merge.",
                    }
                result = deep_merge(result, d)
            return {"value": result}
        elif operation == "invert":
            return {"value": {str(value): key for key, value in obj.items()}}
        elif operation == "pick":
            if param is None:
                raise ValueError("'param' (list of keys) is required for 'pick'.")
            return {"value": {key: obj[key] for key in param if key in obj}}
        elif operation == "omit":
            if param is None:
                raise ValueError("'param' (list of keys) is required for 'omit'.")
            return {
                "value": {key: value for key, value in obj.items() if key not in param}
            }
        elif operation == "set_value":
            if not isinstance(obj, dict):
                return {"value": None, "error": "obj must be a dict for set_value."}
            if not isinstance(path, (str, list)):
                return {
                    "value": None,
                    "error": "'path' must be a string or list for set_value.",
                }
            if isinstance(path, list):
                if not path or not all(isinstance(k, str) for k in path):
                    return {
                        "value": None,
                        "error": (
                            "'path' list elements must all be non-empty strings for "
                            "set_value.",
                        ),
                    }
            p = path
            if isinstance(p, str):
                p = re.findall(r"[^.\[\]]+", p)
            d = obj
            for k in p[:-1]:
                if k not in d or not isinstance(d[k], dict):
                    d[k] = {}
                d = d[k]
            d[p[-1]] = value
            return {"value": obj}
        elif operation == "get_value":
            if not isinstance(obj, dict):
                return {"value": None, "error": "obj must be a dict for get_value."}
            if not isinstance(path, (str, list)):
                return {
                    "value": None,
                    "error": "'path' must be a string or list for get_value.",
                }
            if isinstance(path, list):
                if not path or not all(isinstance(k, str) for k in path):
                    return {
                        "value": None,
                        "error": (
                            "'path' list elements must all be non-empty strings for "
                            "get_value.",
                        ),
                    }
            p = path
            if isinstance(p, str):
                p = re.findall(r"[^.\[\]]+", p)
            d = obj
            for k in p:
                if isinstance(d, dict) and k in d:
                    d = d[k]
                else:
                    return {"value": default}
            return {"value": d}
        elif operation == "has_key":
            if not isinstance(obj, dict):
                return {"value": None, "error": "obj must be a dict for has_key."}
            return {"value": bool(param in obj)}
        elif operation == "is_equal":
            return {"value": obj == param}
        elif operation == "is_empty":
            if isinstance(obj, dict):
                return {"value": len(obj) == 0}
            elif obj is None:
                return {"value": True}
            elif obj == 0 or obj is False:
                return {"value": True}
            else:
                return {"value": False}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}


@mcp.tool("any")
def any_tool(
    value: Any = None,
    operation: Optional[str] = None,
    param: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """
    Performs type-agnostic property checks, comparisons, and expression evaluation.

    Parameters:
        value (Any): The value to check or use as context for expression evaluation.
        operation (str): The operation to perform. One of:
            - 'contains': Checks if a string or list contains a value
              (param: value to check).
            - 'eval': Evaluate a Lua expression with value as context
              (expression: Lua code).
            - 'is_empty': Checks if the value is empty.
            - 'is_equal': Checks if two values are deeply equal
              (param: value to compare).
            - 'is_nil': Checks if the value is None.
        param (Any, optional): The parameter for the operation, if required.
        expression (str, optional): Lua expression to evaluate (for 'eval' operation).

    Returns:
        dict: The result, always wrapped in a dictionary with a 'value' key. If an error
            occurs, an 'error' key is also present.

    Usage Example:
        any('abc', 'contains', 'b')  # => {'value': True}
        any([1, 2, 3], 'contains', 2)  # => {'value': True}
        any([], 'is_empty')  # => {'value': True}
        any(None, 'is_nil')  # => {'value': True}
        any(42, 'is_equal', 42)  # => {'value': True}
        any({'age': 30, 'name': 'Alice'}, 'eval', expression="age > 25")
          # => {'value': True}
        any({'x': 3, 'y': 4}, 'eval', expression="math.sqrt(x*x + y*y)")
          # => {'value': 5.0}
        any("hello", 'eval', expression="string.upper(item)")  # => {'value': 'HELLO'}
    """
    try:
        if operation == "is_equal":
            return {"value": unwrap_result(value == param)}
        elif operation == "is_empty":
            if value is None or value == 0 or value is False:
                return {"value": unwrap_result(True)}
            if isinstance(value, (str, list, dict)):
                return {"value": unwrap_result(len(value) == 0)}
            return {"value": unwrap_result(False)}
        elif operation == "is_nil":
            return {"value": unwrap_result(value is None)}
        elif operation == "contains":
            if isinstance(value, (str, list)):
                return {"value": unwrap_result(param in value)}
            return {"value": unwrap_result(False)}
        elif operation == "eval":
            if not expression:
                return {
                    "value": None,
                    "error": (
                        "Missing required expression parameter for operation 'eval'.",
                    ),
                }
            result = evaluate_expression(expression, value)
            return {"value": unwrap_result(result)}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}


@mcp.tool()
def generate(
    text: Any = None, operation: Optional[str] = None, param: Any = None
) -> dict:
    """
    Generates sequences or derived data from input using the specified operation.

    Parameters:
        text (Any): The input list or value.
        operation (str): The operation to perform. One of:
            - 'accumulate': Running totals (or with a binary function if param is
              provided). param: None or a supported function name (e.g., 'mul')
            - 'cartesian_product': Cartesian product of multiple input lists.
              param: None
            - 'combinations': All combinations of a given length (param: int, required)
            - 'cycle': Repeat the sequence up to param times.
              param: int (max length, optional)
            - 'permutations': All permutations of a given length
              (param: int, optional, default=len(input))
            - 'powerset': All possible subsets of a list. param: None
            - 'range': Generate a list of numbers from start to end (optionally step).
              param: [start, end, step?]
            - 'repeat': Repeat a value or sequence a specified number of times.
              param: int (number of times)
            - 'unique_pairs': All unique pairs from a list. param: None
            - 'windowed': Sliding windows of a given size. param: int (window size)
            - 'zip_with_index': Tuples of (index, value). param: None
        param (Any, optional): Parameter for the operation, if required.

    Returns:
        dict: The result, always wrapped in a dictionary with a 'value' key. If an error
            occurs, an 'error' key is also present.

    Usage Example:
        generate(None, 'range', [0, 5])  # => {'value': [0, 1, 2, 3, 4]}
        generate('x', 'repeat', 3)  # => {'value': ['x', 'x', 'x']}
        generate([1, 2, 3], 'powerset')
          # => {'value': [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]}
        generate([[1, 2], ['a', 'b']], 'cartesian_product')
          # => {'value': [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]}
    """
    import itertools
    import operator

    try:
        if operation == "range":
            if not isinstance(param, list) or len(param) < 2:
                return {
                    "value": None,
                    "error": (
                        "'param' must be [start, end] or [start, end, step] for "
                        "'range'.",
                    ),
                }
            start, end = param[0], param[1]
            step = param[2] if len(param) > 2 else 1
            return {"value": list(range(start, end, step))}
        elif operation == "cartesian_product":
            return {"value": list(itertools.product(*text))}
        elif operation == "repeat":
            if not isinstance(param, int):
                return {
                    "value": None,
                    "error": "'param' must be an integer for 'repeat'.",
                }
            return {"value": list(itertools.repeat(text, param))}
        elif operation == "powerset":
            s = list(text)
            if not s:
                return {"value": [[]]}
            return {
                "value": [
                    list(combo)
                    for r in range(len(s) + 1)
                    for combo in itertools.combinations(s, r)
                ]
            }
        elif operation == "windowed":
            if not isinstance(param, int) or param < 1:
                return {
                    "value": None,
                    "error": "'param' must be a positive integer for 'windowed'.",
                }
            s = list(text)
            return {
                "value": [list(s[i : i + param]) for i in range(len(s) - param + 1)]
            }
        elif operation == "cycle":
            s = list(text)
            if param is not None:
                return {"value": [s[i % len(s)] for i in range(param)] if s else []}
            else:
                raise ValueError("'cycle' without a length limit is not supported.")
        elif operation == "accumulate":
            s = list(text)
            if param is None:
                return {"value": list(itertools.accumulate(s))}
            elif param == "mul":
                return {"value": list(itertools.accumulate(s, operator.mul))}
            else:
                raise ValueError("'accumulate' only supports param=None or 'mul'.")
        elif operation == "zip_with_index":
            return {"value": [[i, v] for i, v in enumerate(text)]}
        elif operation == "unique_pairs":
            s = list(text)
            return {"value": [list(pair) for pair in itertools.combinations(s, 2)]}
        elif operation == "permutations":
            s = list(text)
            r = param if isinstance(param, int) else None
            if not s:
                return {"value": [[]]}
            return {"value": [list(p) for p in itertools.permutations(s, r)]}
        elif operation == "combinations":
            s = list(text)
            if not isinstance(param, int):
                raise ValueError("'param' must be an integer for 'combinations'.")
            if not s:
                return {"value": []}
            return {"value": [list(c) for c in itertools.combinations(s, param)]}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}


@mcp.tool()
async def chain(input: Any, tool_calls: List[Dict[str, Any]]) -> dict:
    """
    Chains multiple tool calls, piping the output of one as the input to the next.

    Parameters:
        input (Any): The initial input to the chain.
        tool_calls (List[Dict[str, Any]]): Each dict must have:
            - 'tool': the tool name (str)
            - 'params': dict of additional parameters (optional, default empty)

    Returns:
        dict: The result of the last tool in the chain, always wrapped in a dictionary
            with a 'value' key. If an error occurs, an 'error' key is also present.

    Chaining Rule:
        The output from one tool is always used as the input to the next tool's primary
        parameter. You must not specify the primary parameter in params for any tool in
        the chain.

    Usage Example:
        chain(
            [1, [2, [3, 4], 5]],
            [
                {"tool": "lists", "params": {"operation": "flatten_deep"}},
                {"tool": "lists", "params": {"operation": "compact"}},
                {"tool": "lists", "params": {"operation": "sort_by", "param": None}}
            ]
        )
        # => {'value': [1, 2, 3, 4, 5]}
    """
    value = input
    for i, step in enumerate(tool_calls):
        tool_name = step.get("tool")
        params = step.get("params", {})
        if not tool_name:
            return {"value": None, "error": f"Step {i}: Missing 'tool' name."}
        try:
            tool_or_coro = mcp._tool_manager.get_tool(tool_name)
            if inspect.isawaitable(tool_or_coro):
                tool = await tool_or_coro
            else:
                tool = tool_or_coro
        except Exception as e:
            return {
                "value": None,
                "error": f"Step {i}: Tool '{tool_name}' not found: {e}",
            }
        if not hasattr(tool, "run") or not callable(getattr(tool, "run", None)):
            return {
                "value": None,
                "error": f"Step {i}: Tool '{tool_name}' is not a valid tool object.",
            }
        param_schema = tool.parameters.get("properties", {})
        required = tool.parameters.get("required", [])
        primary_param = None

        # Prioritize common primary parameter names
        for p_name in ["text", "items", "obj", "value"]:
            if p_name in param_schema:
                primary_param = p_name
                break

        # Fallback to required parameters (excluding 'operation')
        if not primary_param:
            for k in required:
                if k != "operation":
                    primary_param = k
                    break

        # Fallback to first non-'operation' parameter in schema
        if not primary_param and param_schema:
            for k in param_schema:
                if k != "operation":
                    primary_param = k
                    break

        arguments = dict(params)
        if primary_param:
            if primary_param in arguments:
                return {
                    "value": None,
                    "error": f"Step {i}: Chaining does not allow specifying the "
                    f"primary parameter '{primary_param}' in params. The output from "
                    "the previous tool is always used as input.",
                }
            # Unwrap the value before passing to the next tool
            arguments[primary_param] = unwrap_result(value)
        elif len(param_schema) == 1:
            only_param = next(iter(param_schema))
            if only_param in arguments:
                return {
                    "value": None,
                    "error": f"Step {i}: Chaining does not allow specifying the "
                    f"primary parameter '{only_param}' in params. The output from the "
                    "previous tool is always used as input.",
                }
            arguments[only_param] = unwrap_result(value)
        elif not param_schema:
            arguments = {}
        try:
            result = await tool.run(arguments)
        except Exception as e:
            return {
                "value": None,
                "error": f"Step {i}: Error calling tool '{tool_name}': {e}",
            }
        unwrapped = unwrap_result(result)
        value = unwrapped
        if isinstance(value, dict) and "error" in value:
            return {
                "value": None,
                "error": (
                    f"Step {i}: Error calling tool '{tool_name}': " f"{value['error']}"
                ),
            }
        elif isinstance(value, dict) and "value" in value:
            value = value["value"]
    return {"value": value}


def create_lua_runtime(safe_mode: Optional[bool] = None) -> lupa.LuaRuntime:
    """
    Create a Lua runtime with optional sandboxing.

    Args:
        safe_mode: If True, applies safety rails. If None, uses global SAFE_MODE
            setting.
    """
    if safe_mode is None:
        safe_mode = SAFE_MODE

    lua_runtime = lupa.LuaRuntime()

    # Always define a global 'null' table as the None sentinel
    lua_runtime.execute("null = {}")

    if safe_mode:
        # Apply safety rails - disable dangerous functions but keep useful ones
        lua_runtime.execute(
            """
            -- Disable dangerous file/system operations
            os = {
                -- Keep safe time/date functions
                time = os.time,
                date = os.date,
                clock = os.clock,
                difftime = os.difftime,
                -- Remove dangerous ones: execute, exit, getenv, remove, rename, etc.
            }

            -- Disable file I/O
            io = nil

            -- Disable module loading that could access filesystem
            require = nil
            dofile = nil
            loadfile = nil

            -- Keep package.loaded for accessing already loaded safe modules
            if package then
                package.loadlib = nil
                package.searchpath = nil
                package.searchers = nil
                package.path = nil
                package.cpath = nil
            end

            -- Disable debug library (could be used for introspection attacks)
            debug = nil
        """
        )

    return lua_runtime


def encode_null_for_lua(obj, lua_runtime):
    """
    Recursively replace None (from JSON null) with the Lua 'null' table before passing
    to Lua. All None values become 'null' sentinels, enabling consistent null checks
    with 'item == null'. Lists are always preserved as arrays, dicts as tables.
    """
    null_sentinel = lua_runtime.eval("null")
    if obj is None:
        return null_sentinel
    elif isinstance(obj, list):
        # Convert each element and then convert the whole list to a Lua table
        converted_items = [encode_null_for_lua(x, lua_runtime) for x in obj]
        return lua_runtime.table_from(converted_items)
    elif isinstance(obj, dict):
        # Convert each value, handling nested lists
        converted_dict = {}
        for k, v in obj.items():
            converted_dict[k] = encode_null_for_lua(v, lua_runtime)
        return lua_runtime.table_from(converted_dict)
    else:
        return obj


def decode_null_from_lua(obj, null_sentinel=None):
    """
    Recursively replace the Lua 'null' table with None (for JSON null output). Converts
    all 'null' sentinels back to Python None for JSON serialization.
    """
    if null_sentinel is not None and obj is null_sentinel:
        return None
    elif isinstance(obj, list):
        return [decode_null_from_lua(x, null_sentinel) for x in obj]
    elif isinstance(obj, dict):
        # Preserve dicts as dicts (no longer convert integer-keyed dicts to lists)
        return {k: decode_null_from_lua(v, null_sentinel) for k, v in obj.items()}
    # Check for LuaTable objects that might be the null sentinel
    elif "LuaTable" in type(obj).__name__:
        # If it's an empty LuaTable, it might be the null sentinel
        try:
            keys = list(obj.keys())
            if len(keys) == 0:
                return None
            else:
                # Convert to dict and recurse
                return decode_null_from_lua({k: obj[k] for k in keys}, null_sentinel)
        except Exception:
            return obj
    else:
        return obj


def evaluate_expression(
    expression: str, item: Any, safe_mode: Optional[bool] = None
) -> Any:
    """
    Evaluate a Lua expression against an item. The item is available as 'item' in the
    Lua context, and dict keys are directly accessible. All None (JSON null) values are
    converted to 'null' table for consistent null checks.

    Args:
        expression: Lua expression to evaluate (can return any value)
        item: The data item to evaluate against (None values become 'null')
        safe_mode: If True, applies safety rails. If None, uses global SAFE_MODE
            setting.
    """
    try:
        lua_runtime = create_lua_runtime(safe_mode)
        # Set up context
        if isinstance(item, dict):
            for key, value in item.items():
                if (
                    isinstance(key, str)
                    and key.isidentifier()
                    and key not in ["and", "or", "not", "if", "then", "else", "end"]
                ):
                    lua_runtime.globals()[key] = encode_null_for_lua(value, lua_runtime)  # type: ignore  # noqa

        # Convert the top-level item (encode_null_for_lua now handles table conversion)
        lua_runtime.globals()["item"] = encode_null_for_lua(item, lua_runtime)  # type: ignore  # noqa

        try:
            # Try to execute as a statement returning a value. This works for simple
            # expressions.
            return lua_runtime.execute("return (" + expression + ")")
        except lupa.LuaError:
            # If that fails, it's likely a multi-line script that already contains
            # 'return'.
            return lua_runtime.execute(expression)

    except Exception:
        return None


def unwrap_result(result):
    """
    Unwraps the result from a tool call. The result from the client is typically a list
    containing a single Content object. This function extracts the text from that object
    and decodes it from JSON.
    """
    import json

    def _convert_lua_table(lua_table):
        try:
            keys = list(lua_table.keys())

            # Check if this is the null sentinel (empty table)
            if len(keys) == 0:
                return None

            # If all keys are positive integers, treat as a list
            if keys and all(isinstance(k, int) and k > 0 for k in keys):
                max_index = max(keys)
                result = [None] * max_index
                for k in keys:
                    val = lua_table[k]
                    # Check if this value is an empty LuaTable (null sentinel)
                    if "LuaTable" in type(val).__name__:
                        try:
                            if len(list(val.keys())) == 0:
                                result[k - 1] = None
                            else:
                                result[k - 1] = _convert_lua_table(val)
                        except Exception:
                            result[k - 1] = val
                    else:
                        result[k - 1] = val
                return result
            else:
                result = {}
                for k in keys:
                    val = lua_table[k]
                    # Check if this value is an empty LuaTable (null sentinel)
                    if "LuaTable" in type(val).__name__:
                        try:
                            if len(list(val.keys())) == 0:
                                result[k] = None
                            else:
                                result[k] = _convert_lua_table(val)
                        except Exception:
                            result[k] = val
                    else:
                        result[k] = val
                return result
        except Exception:
            return None

    # The result from client.call_tool is a list of Content objects.
    # For our tools, it's typically a single object in the list.
    if (
        isinstance(result, list)
        and result
        and hasattr(result[0], "text")
        and isinstance(result[0], object)
    ):
        try:
            # The text attribute contains the JSON string of the actual return value.
            unwrapped = json.loads(result[0].text)  # type: ignore[attr-defined]
        except (json.JSONDecodeError, TypeError):
            # If it's not valid JSON, return the text as is.
            unwrapped = getattr(result[0], "text", result[0])
    # Fallback for single Content object or other types passed from tests
    elif (
        not isinstance(result, list)
        and hasattr(result, "text")
        and result.text is not None
    ):
        try:
            unwrapped = json.loads(result.text)  # type: ignore[attr-defined]
        except (json.JSONDecodeError, TypeError):
            unwrapped = result.text  # type: ignore[attr-defined]
    else:
        unwrapped = result

    # Recursively convert LuaTable objects
    if "LuaTable" in type(unwrapped).__name__:
        return _convert_lua_table(unwrapped)
    elif isinstance(unwrapped, list):
        return [
            _convert_lua_table(item) if type(item).__name__ == "LuaTable" else item
            for item in unwrapped
        ]
    elif isinstance(unwrapped, dict):
        return {
            k: _convert_lua_table(v) if type(v).__name__ == "LuaTable" else v
            for k, v in unwrapped.items()
        }
    return unwrapped


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Lever MCP server.")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Start the server with Streamable HTTP (instead of stdio)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for HTTP server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP server (default: 8000)",
    )
    parser.add_argument(
        "--unsafe",
        action="store_true",
        help="Disable Lua safety rails (allows file I/O and system commands)",
    )
    args = parser.parse_args()

    # Update global safe mode setting based on command line args
    SAFE_MODE = not args.unsafe

    if args.http:
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()
