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

    MCP Usage Examples:
        strings('foo bar', 'camel_case')  # => {'value': 'fooBar'}
        strings('Hello, {name}!', 'template', data={'name': 'World'})
          # => {'value': 'Hello, World!'}
        strings('abc', 'contains', param='a')  # => {'value': True}

    Lua Function Call Examples:
        strings.upper_case("hello")  # => "HELLO"
        strings.contains("hello world", "world")  # => true
        strings.replace({text="hello world", data={old="world", new="Lua"}})  # => "hello Lua"
        strings.template({text="Hello {name}!", data={name="World"}})  # => "Hello World!"
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
        # Add type validation for string operations that specifically require strings
        # is_empty and is_equal can work on any type
        string_only_operations = [
            "deburr", "template", "replace", "starts_with", "ends_with", 
            "upper_case", "lower_case", "capitalize", "reverse", "trim",
            "camel_case", "snake_case", "kebab_case", "contains", "is_digit", 
            "is_alpha", "is_upper", "is_lower", "xor", "shuffle", "sample_size"
        ]
        if operation in string_only_operations and text is not None and not isinstance(text, str):
            return {"value": None, "error": f"String operation '{operation}' requires a string input, got {type(text).__name__}"}
        
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
            if param is None:
                raise ValueError("'param' argument is required for 'starts_with' operation")
            result = text.startswith(param)
        elif operation == "ends_with":
            if param is None:
                raise ValueError("'param' argument is required for 'ends_with' operation")
            result = text.endswith(param)
        elif operation == "is_empty":
            result = len(text) == 0
        elif operation == "xor":
            # Symmetric difference of two strings (unique characters in either, not
            # both)
            if not isinstance(text, str) or not isinstance(param, str):
                return {
                    "value": None,
                    "error": "Both arguments must be strings for xor.",
                }
            set1 = set(text)
            set2 = set(param)
            result = "".join(sorted(set1 ^ set2))
        elif operation == "shuffle":
            import random

            chars = list(text)
            random.shuffle(chars)
            result = "".join(chars)
        elif operation == "sample_size":
            import random

            n = param if isinstance(param, int) else 1
            if n < 0:
                return {"value": None, "error": "sample_size must be non-negative."}
            if not isinstance(text, str):
                return {
                    "value": None,
                    "error": "Argument must be a string for sample_size.",
                }
            result = "".join(random.sample(text, min(n, len(text))))
        elif operation == "is_equal":
            result = text == param
        elif operation == "contains":
            if param is None:
                raise ValueError("'param' argument is required for 'contains' operation")
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
            - 'all_by'/'every': Return True if all items satisfy the expression
            - 'any_by'/'some': Return True if any item satisfies the expression
            - 'count_by': Count occurrences by expression result/key
            - 'difference_by': Items in first list not matching expression in second
            - 'filter_by': Return all items matching the expression (predicate)
            - 'find_by': Find first item matching expression/key-value
            - 'flat_map': Like map, but flattens one level if the mapping returns lists
            - 'group_by': Group items by expression result/key value
            - 'intersection_by': Items in first list matching expression in second
            - 'key_by': Create dict keyed by expression result/field
            - 'map': Apply a Lua expression to each item and return the transformed list
            - 'max_by': Find max by expression result/key
            - 'min_by': Find min by expression result/key
            - 'partition': Split by expression result/boolean key
            - 'pluck': Extract values by expression/key (expression: any value)
            - 'reduce': Aggregate the list using a binary Lua expression (uses 'acc' and
              'item') and optional initializer (param)
            - 'remove_by': Remove items matching expression/key-value
            - 'sort_by': Sort by expression result/key
              (expression: any comparable value)
            - 'uniq_by': Remove duplicates by expression result/key
            - 'zip_with': Combine two lists element-wise using a binary Lua expression
              (uses 'item1' and 'item2')

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

    In Lua expressions, item refers to the current object. Available in expressions:
    math.*, string.*, os.time/date/clock, type(), tonumber(), tostring(). Dictionary
    keys accessible directly (age, name, etc.) or via item.key. You may pass a single
    Lua expression or a block of Lua code. For multi-line code, use return to specify
    the result.

    Returns:
        dict: Result with 'value' key. On error, includes 'error' key.

    MCP Usage Examples:
        lists([{'id': 1}, {'id': 2}, {'id': 1}], 'uniq_by', key='id')
          # => {'value': [{'id': 1}, {'id': 2}]}
        lists([{'age': 30}, {'age': 20}], 'find_by', expression="age > 25")
          # => {'value': {'age': 30}}
        lists(
            [{'age': 30}, {'age': 20}],
            'group_by',
            expression="age >= 25 and 'adult' or 'young'"
        )  # => {'value': {'adult': [{'age': 30}], 'young': [{'age': 20}]}}
        lists([1, 2, 3], 'chunk', param=2)  # => {'value': [[1, 2], [3]]}
        lists([1, 2, 3], 'difference', others=[2, 3])  # => {'value': [1]}

    Lua Function Call Examples:
        lists.head({1, 2, 3})  # => 1
        lists.filter_by({{age=25}, {age=30}}, "age > 25")  # => [{"age": 30}]
        lists.map({items={{name="alice"}, {name="bob"}}, expression="strings.upper_case(name)"})  # => ["ALICE", "BOB"]
        lists.sort_by({items={{"name":"charlie"}, {"name":"alice"}}, expression="strings.lower_case(name)"})  # => [{"name":"alice"}, {"name":"charlie"}]
        lists.difference({items={1, 2, 3}, others={2, 3}})  # => [1]
        lists.group_by({items={{age=30}, {age=20}}, expression="age >= 25 and 'adult' or 'young'"})  # => {adult=[{age=30}], young=[{age=20}]}
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

    Supported operations: all_by, any_by, chunk, compact, contains, count_by,
    difference, difference_by, drop, drop_right, filter_by, find_by, flat_map, flatten,
    flatten_deep, group_by, head, index_of, initial, intersection, intersection_by,
    is_equal, key_by, last, map, max_by, min_by, nth, partition, pluck, random_except,
    reduce, remove_by, sample, sort_by, tail, take, take_right, union, uniq_by,
    unzip_list, zip_lists, zip_with
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
                if expression:
                    # Use Lua expression
                    result = evaluate_expression(expression, item)
                else:
                    # Use param key
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
            if not key and not expression:
                return {
                    "value": None,
                    "error": "Missing required key or expression parameter for operation 'count_by'.",
                }
            result = {}
            for item in items:
                if expression:
                    # Use expression evaluation
                    k = evaluate_expression(expression, item)
                    # Convert result to string for consistent dictionary keys
                    k = str(k) if k is not None else "null"
                else:
                    # Use key parameter (legacy behavior)
                    if not isinstance(item, dict):
                        return {
                            "value": None,
                            "error": "All items must be dicts when using key parameter for 'count_by'.",
                        }
                    k = item.get(key)
                    k = str(k) if k is not None else "null"
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
            # Convert integer keys to strings to avoid Lua table->list conversion
            result = {}
            for item in items:
                k = item[key]
                # Convert integer keys to strings like JSON does
                if isinstance(k, int):
                    k = str(k)
                result[k] = item
            return {"value": result}
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
                return {"value": None, "error": "nth operation requires an index parameter"}
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
        # --- New Functional Operations ---
        elif operation == "map":
            if not expression:
                return {"value": None, "error": "'expression' is required for map."}
            return {"value": [evaluate_expression(expression, item) for item in items]}
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
            for item in items:
                mapped = evaluate_expression(expression, item)
                # Convert Lua tables to Python lists
                if "LuaTable" in type(mapped).__name__:
                    mapped = decode_null_from_lua(mapped)
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
                    bool(evaluate_expression(expression, item)) for item in items
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
                    bool(evaluate_expression(expression, item)) for item in items
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
                    for item in items
                    if bool(evaluate_expression(expression, item))
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
                    expression, None, context={"item1": items[i], "item2": others[i]}
                )
                result.append(val)
            return {"value": result}
        # --- End New Functional Operations ---
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

    MCP Usage Examples:
        dicts({'a': 1, 'b': 2}, 'pick', ['a'])  # => {'value': {'a': 1}}
        dicts({'a': {'b': 1}}, 'set_value', path=['a', 'b'], value=2)
          # => {'value': {'a': {'b': 2}}}
        dicts({'a': 1}, 'get_value', path='b', default=42)  # => {'value': 42}

    Lua Function Call Examples:
        dicts.has_key({a=1, b=2}, "a")  # => true
        dicts.get_value({obj={a={b=1}}, path="a.b"})  # => 1
        dicts.pick({obj={a=1, b=2, c=3}, param={"a", "c"}})  # => {a=1, c=3}
        dicts.merge({obj={{a=1}, {b=2}}})  # => {a=1, b=2}
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
        # Add type validation for dict operations - dicts tool should only work on dictionaries
        # For comparing any types, use any.is_equal instead
        if operation not in ["merge", "is_empty"] and obj is not None and not isinstance(obj, dict):
            return {"value": None, "error": f"Dict operation '{operation}' requires a dictionary input, got {type(obj).__name__}. Use 'any.is_equal' for comparing non-dictionary types."}
        
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

    Expression Examples:
        - Boolean check: "age > 25", "score >= 80", "name == 'Alice'"
        - Math: "math.abs(x - y)", "x*x + y*y"
        - String manipulation: "string.upper(item)", "string.sub(item, 1, 3)"
        - Null check: "item == null", "score ~= null"
        - Type check: "type(item) == 'table'", "type(item) == 'string'"

    In Lua expressions, item refers to the current object. Available in expressions:
    math.*, string.*, os.time/date/clock, type(), tonumber(), tostring(). Dictionary
    keys accessible directly (age, name, etc.) or via item.key. You may pass a single
    Lua expression or a block of Lua code. For multi-line code, use return to specify
    the result.

    Returns:
        dict: The result, always wrapped in a dictionary with a 'value' key. If an error
            occurs, an 'error' key is also present.

    MCP Usage Examples:
        any('abc', 'contains', 'b')  # => {'value': True}
        any([1, 2, 3], 'contains', 2)  # => {'value': True}
        any([], 'is_empty')  # => {'value': True}
        any(None, 'is_nil')  # => {'value': True}
        any(42, 'is_equal', 42)  # => {'value': True}

    Lua Function Call Examples:
        any.is_equal(42, 42)  # => true
        any.is_empty("")  # => true
        any.contains("hello", "ell")  # => true
        any.eval({age=30}, "age > 25")  # => true
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

    MCP Usage Examples:
        generate(None, 'range', [0, 5])  # => {'value': [0, 1, 2, 3, 4]}
        generate('x', 'repeat', 3)  # => {'value': ['x', 'x', 'x']}
        generate([1, 2, 3], 'powerset')
          # => {'value': [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]}
        generate([[1, 2], ['a', 'b']], 'cartesian_product')
          # => {'value': [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]}

    Lua Function Call Examples:
        generate.range(nil, {0, 5})  # => [0, 1, 2, 3, 4]
        generate["repeat"]("x", 3)  # => ["x", "x", "x"] (bracket syntax for reserved keyword)
        generate.powerset({1, 2})  # => [[], [1], [2], [1, 2]]
        generate.cartesian_product({{1, 2}, {"a", "b"}})  # => [[1, "a"], [1, "b"], [2, "a"], [2, "b"]]
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

    MCP Usage Examples:
        chain(
            [1, [2, [3, 4], 5]],
            [
                {"tool": "lists", "params": {"operation": "flatten_deep"}},
                {"tool": "lists", "params": {"operation": "compact"}},
                {"tool": "lists", "params": {"operation": "sort_by", "param": None}}
            ]
        )
        # => {'value': [1, 2, 3, 4, 5]}

    Lua Function Call Examples:
        -- Note: chain is not exposed as a Lua function since it operates on tool calls
        -- Use direct tool function calls instead:
        local result = lists.sort_by(lists.compact(lists.flatten_deep({1, {2, {3, 4}, 5}})))
        -- => [1, 2, 3, 4, 5]
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




def _register_mcp_tools_in_lua(lua_runtime: lupa.LuaRuntime):
    """
    Register MCP tool functions in the Lua runtime to enable calling them
    as functions like strings.is_alpha(s) or lists.filter_by(items, expr).
    """
    
    def create_tool_wrapper(tool_name, operation_name):
        """Create a wrapper function for a specific tool operation."""
        def wrapper(*args):
            # Get null sentinel for proper conversion
            null_sentinel = lua_runtime.eval("null")
            # Support both positional args and table-based args
            if len(args) == 1 and hasattr(args[0], 'values'):
                # Check if this is a parameter table or just data
                table_dict = dict(args[0])
                
                # Parameter tables have tool-specific parameter names as keys
                param_keys = set()
                if tool_name == 'strings':
                    param_keys = {'text', 'param', 'data'}
                elif tool_name == 'lists':
                    param_keys = {'items', 'param', 'others', 'key', 'text', 'expression'}
                elif tool_name == 'dicts':
                    param_keys = {'obj', 'param', 'path', 'value', 'default'}
                elif tool_name == 'any_tool':
                    param_keys = {'value', 'param', 'expression'}
                elif tool_name == 'generate':
                    param_keys = {'text', 'param'}
                
                # If any table key matches parameter names, treat as parameter table
                is_param_table = bool(param_keys.intersection(table_dict.keys()))
                
                if is_param_table:
                    # Single table argument - extract named parameters
                    params_table = decode_null_from_lua(table_dict)
                    
                    # Call the tool function with named parameters from the table
                    if tool_name == 'strings':
                        result = strings.fn(
                            text=params_table.get('text'),
                            operation=operation_name,
                            param=params_table.get('param'),
                            data=params_table.get('data')
                        )
                    elif tool_name == 'lists':
                        result = lists.fn(
                            items=params_table.get('items'),
                            operation=operation_name,
                            param=params_table.get('param'),
                            others=params_table.get('others'),
                            key=params_table.get('key', ''),
                            text=params_table.get('text'),
                            expression=params_table.get('expression')
                        )
                    elif tool_name == 'dicts':
                        result = dicts.fn(
                            obj=params_table.get('obj'),
                            operation=operation_name,
                            param=params_table.get('param'),
                            path=params_table.get('path'),
                            value=params_table.get('value'),
                            default=params_table.get('default')
                        )
                    elif tool_name == 'any_tool':
                        result = any_tool.fn(
                            value=params_table.get('value'),
                            operation=operation_name,
                            param=params_table.get('param'),
                            expression=params_table.get('expression')
                        )
                    elif tool_name == 'generate':
                        result = generate.fn(
                            text=params_table.get('text'),
                            operation=operation_name,
                            param=params_table.get('param')
                        )
                    else:
                        return None
                else:
                    # Single table that's data, not parameters - treat as positional
                    data_table = decode_null_from_lua(args[0], null_sentinel)
                    
                    # Call with the table as the first positional argument
                    if tool_name == 'strings':
                        result = strings.fn(text=data_table, operation=operation_name)
                    elif tool_name == 'lists':
                        result = lists.fn(items=data_table, operation=operation_name)
                    elif tool_name == 'dicts':
                        result = dicts.fn(obj=data_table, operation=operation_name)
                    elif tool_name == 'any_tool':
                        result = any_tool.fn(value=data_table, operation=operation_name)
                    elif tool_name == 'generate':
                        result = generate.fn(text=data_table, operation=operation_name)
                    else:
                        return None
            else:
                # Positional arguments - convert and use positional mapping
                py_args = []
                for i, arg in enumerate(args):
                    if hasattr(arg, 'values'):  # Lua table
                        # Check if this is the null sentinel
                        if arg is null_sentinel:
                            py_args.append(None)
                        else:
                            converted_table = decode_null_from_lua(dict(arg))
                            
                            # Special handling for first argument that might be a parameter table
                            if i == 0 and isinstance(converted_table, dict):
                                # Check if this looks like a parameter table for this tool
                                if tool_name == 'lists' and 'items' in converted_table:
                                    # Extract the items value for lists operations
                                    py_args.append(converted_table['items'])
                                elif tool_name == 'strings' and 'text' in converted_table:
                                    # Extract the text value for strings operations  
                                    py_args.append(converted_table['text'])
                                elif tool_name == 'dicts' and 'obj' in converted_table:
                                    # Extract the obj value for dicts operations
                                    py_args.append(converted_table['obj'])
                                elif tool_name == 'any_tool' and 'value' in converted_table:
                                    # Extract the value for any_tool operations
                                    py_args.append(converted_table['value'])
                                elif tool_name == 'generate' and 'text' in converted_table:
                                    # Extract the text value for generate operations
                                    py_args.append(converted_table['text'])
                                else:
                                    # Not a parameter table, use as-is
                                    py_args.append(converted_table)
                            else:
                                py_args.append(converted_table)
                    elif hasattr(arg, '__iter__') and not isinstance(arg, str):  # Other Lua tables
                        try:
                            py_args.append(decode_null_from_lua(dict(arg)))
                        except:
                            py_args.append(list(arg))
                    else:
                        py_args.append(arg)
                
                # Call the tool function directly using .fn to access the underlying implementation
                if tool_name == 'strings':
                    result = strings.fn(text=py_args[0] if py_args else None, operation=operation_name,
                                      param=py_args[1] if len(py_args) > 1 else None,
                                      data=py_args[2] if len(py_args) > 2 else None)
                elif tool_name == 'lists':
                    # For lists, the second argument is usually expression, third is param, fourth is key
                    items_arg = py_args[0] if py_args else None
                    expression_arg = py_args[1] if len(py_args) > 1 else None
                    key_arg = py_args[3] if len(py_args) > 3 else ""
                    if operation_name == 'key_by':
                        print(f"DEBUG lists.key_by: items={items_arg}, key={key_arg}")
                    result = lists.fn(items=items_arg, operation=operation_name,
                                    expression=expression_arg,
                                    param=py_args[2] if len(py_args) > 2 else None,
                                    key=key_arg,
                                    others=py_args[4] if len(py_args) > 4 else None)
                    if operation_name == 'key_by':
                        print(f"DEBUG lists.key_by result: {result}")
                elif tool_name == 'dicts':
                    result = dicts.fn(obj=py_args[0] if py_args else None, operation=operation_name,
                                    param=py_args[1] if len(py_args) > 1 else None,
                                    path=py_args[2] if len(py_args) > 2 else None,
                                    value=py_args[3] if len(py_args) > 3 else None)
                elif tool_name == 'any_tool':
                    # For any_tool, param vs expression depends on the operation
                    if operation_name in ['contains', 'is_equal']:
                        # These operations use param for second argument
                        result = any_tool.fn(value=py_args[0] if py_args else None, operation=operation_name,
                                           param=py_args[1] if len(py_args) > 1 else None)
                    else:
                        # Operations like 'eval' use expression for second argument
                        result = any_tool.fn(value=py_args[0] if py_args else None, operation=operation_name,
                                           expression=py_args[1] if len(py_args) > 1 else None,
                                           param=py_args[2] if len(py_args) > 2 else None)
                elif tool_name == 'generate':
                    result = generate.fn(text=py_args[0] if py_args else None, operation=operation_name,
                                       param=py_args[1] if len(py_args) > 1 else None)
                else:
                    return None
            
            # Return the value directly, or None if error
            if isinstance(result, dict) and "value" in result:
                return encode_null_for_lua(result["value"], lua_runtime)
            return None
        
        return wrapper

    # String operations
    string_ops = [
        'camel_case', 'capitalize', 'contains', 'deburr', 'ends_with', 'is_alpha',
        'is_digit', 'is_empty', 'is_equal', 'is_lower', 'is_upper', 'kebab_case',
        'lower_case', 'replace', 'reverse', 'sample_size', 'shuffle', 'snake_case',
        'starts_with', 'template', 'trim', 'upper_case', 'xor'
    ]
    
    # List operations
    list_ops = [
        'all_by', 'every', 'any_by', 'some', 'count_by', 'difference_by', 'filter_by',
        'find_by', 'flat_map', 'group_by', 'intersection_by', 'key_by', 'map',
        'max_by', 'min_by', 'partition', 'pluck', 'reduce', 'remove_by', 'sort_by',
        'uniq_by', 'zip_with', 'chunk', 'compact', 'contains', 'drop', 'drop_right',
        'flatten', 'flatten_deep', 'head', 'index_of', 'initial', 'is_empty',
        'is_equal', 'last', 'nth', 'random_except', 'sample', 'sample_size',
        'shuffle', 'tail', 'take', 'take_right', 'difference', 'intersection',
        'union', 'xor', 'unzip_list', 'zip_lists'
    ]
    
    # Dict operations  
    dict_ops = [
        'get_value', 'has_key', 'invert', 'is_empty', 'is_equal', 'merge',
        'omit', 'pick', 'set_value'
    ]
    
    # Any operations
    any_ops = ['contains', 'eval', 'is_empty', 'is_equal', 'is_nil']
    
    # Generate operations
    generate_ops = [
        'accumulate', 'cartesian_product', 'combinations', 'cycle', 'permutations',
        'powerset', 'range', 'repeat', 'unique_pairs', 'windowed', 'zip_with_index'
    ]
    
    # Create string table with operations
    strings_table = {}
    for op in string_ops:
        strings_table[op] = create_tool_wrapper('strings', op)
    lua_runtime.globals()['strings'] = lua_runtime.table_from(strings_table)
    
    # Create lists table with operations
    lists_table = {}
    for op in list_ops:
        lists_table[op] = create_tool_wrapper('lists', op)
    lua_runtime.globals()['lists'] = lua_runtime.table_from(lists_table)
    
    # Create dicts table with operations
    dicts_table = {}
    for op in dict_ops:
        dicts_table[op] = create_tool_wrapper('dicts', op)
    lua_runtime.globals()['dicts'] = lua_runtime.table_from(dicts_table)
    
    # Create any table with operations (renamed from any_tool to avoid Lua keyword)
    any_table = {}
    for op in any_ops:
        any_table[op] = create_tool_wrapper('any_tool', op)
    lua_runtime.globals()['any'] = lua_runtime.table_from(any_table)
    
    # Create generate table with operations
    generate_table = {}
    for op in generate_ops:
        generate_table[op] = create_tool_wrapper('generate', op)
    lua_runtime.globals()['generate'] = lua_runtime.table_from(generate_table)


def create_lua_runtime(safe_mode: Optional[bool] = None) -> lupa.LuaRuntime:
    """
    Create a Lua runtime with optional sandboxing and MCP tool function registration.

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

    # Register MCP tool functions in Lua runtime
    _register_mcp_tools_in_lua(lua_runtime)

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
    Also converts Lua tables with only positive integer keys starting at 1 to lists.
    """
    if null_sentinel is not None and obj is null_sentinel:
        return None
    elif isinstance(obj, list):
        return [decode_null_from_lua(x, null_sentinel) for x in obj]
    elif isinstance(obj, dict):
        # If all keys are positive integers starting at 1, treat as list
        keys = list(obj.keys())
        if keys and all(isinstance(k, int) and k > 0 for k in keys):
            min_k, max_k = min(keys), max(keys)
            if min_k == 1 and max_k == len(keys):
                # Convert to list in order
                return [
                    decode_null_from_lua(obj[k], null_sentinel)
                    for k in range(1, max_k + 1)
                ]
        # Otherwise, keep as dict
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
    expression: str,
    item: Any,
    safe_mode: Optional[bool] = None,
    context: Optional[Dict] = None,
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
        context: Optional dict of additional variables to set in the Lua context.
    """
    try:
        lua_runtime = create_lua_runtime(safe_mode)
        # Set up context
        if context is not None:
            for k, v in context.items():
                lua_runtime.globals()[k] = encode_null_for_lua(v, lua_runtime)  # type: ignore  # noqa
        else:
            if isinstance(item, dict):
                for key, value in item.items():
                    if (
                        isinstance(key, str)
                        and key.isidentifier()
                        and key not in ["and", "or", "not", "if", "then", "else", "end"]
                    ):
                        lua_runtime.globals()[key] = encode_null_for_lua(value, lua_runtime)  # type: ignore  # noqa
            lua_runtime.globals()["item"] = encode_null_for_lua(item, lua_runtime)  # type: ignore  # noqa
        # Evaluate the expression
        try:
            result = lua_runtime.execute("return (" + expression + ")")
        except lupa.LuaError:
            result = lua_runtime.execute(expression)
        
        # Check if the result is a Lua function - if so, call it with the item
        if hasattr(result, '__call__'):
            try:
                # Call the function with the item as argument
                result = result(encode_null_for_lua(item, lua_runtime))
            except Exception:
                # If calling the function fails, return the original result
                pass
        
        # Convert Lua results back to Python
        null_sentinel = lua_runtime.eval("null")
        return decode_null_from_lua(result, null_sentinel)
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
