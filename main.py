from fastmcp import FastMCP
from typing import Any, Dict, List, Optional
import inspect
import argparse
import lupa

# Global configuration for Lua safety mode
SAFE_MODE = True  # Default to safe mode, can be overridden by command line

# --- MCP Parameter Description Monkey Patch ---
PARAM_DESCRIPTIONS = {
    "strings": {
        "text": "(str) The input string to operate on",
        "operation": (
            "(str) The operation to perform. One of: 'camel_case', 'capitalize', "
            "'contains', 'deburr', 'ends_with', 'is_alpha', 'is_digit', 'is_empty', "
            "'is_equal', 'is_lower', 'is_upper', 'kebab_case', 'lower_case', "
            "'replace', 'reverse', 'sample_size', 'shuffle', 'slice', 'snake_case', "
            "'split', 'starts_with', 'template', 'trim', 'upper_case', 'xor'"
        ),
        "param": (
            "(any, optional) Parameter for operations that require one (e.g., "
            "substring for 'contains', int for 'sample_size')"
        ),
        "data": (
            "(dict, optional) Data for 'template' and 'replace' operations (e.g., "
            "{'old': 'x', 'new': 'y'} for 'replace')"
        ),
    },
    "lists": {
        "items": (
            "(list) The input list to operate on. For zip_lists/unzip_list/union, "
            "provide a list of lists"
        ),
        "operation": (
            "(str) The operation to perform. One of: 'chunk', 'compact', 'contains', "
            "'count_by', 'difference', 'difference_by', 'drop', 'drop_right', "
            "'filter_by', 'find_by', 'flat_map', 'flatten', 'flatten_deep', "
            "'group_by', 'head', 'index_of', 'initial', 'intersection', "
            "'intersection_by', 'is_empty', 'is_equal', 'join', 'key_by', 'last', "
            "'map', 'max', 'max_by', 'min', 'min_by', 'nth', 'partition', 'pluck', "
            "'random_except', 'reduce', 'sample', 'sample_size', 'shuffle', 'sort_by', "
            "'tail', 'take', 'take_right', 'union', 'uniq_by', 'unzip_list', 'xor', "
            "'zip_lists', 'zip_with'"
        ),
        "param": "(any, optional) Parameter for operations that require one",
        "others": "(list, optional) Second list for set operations",
        "expression": (
            "(str, optional) Lua expression for advanced filtering, grouping, "
            "sorting, or extraction"
        ),
    },
    "dicts": {
        "obj": (
            "(dict or list) The source dictionary, or a list of dicts for 'merge'. "
            "Must be a dict for all operations except 'merge'"
        ),
        "operation": (
            "(str) The operation to perform. One of: 'flatten_keys', 'get_value', "
            "'has_key', 'invert', 'is_empty', 'is_equal', 'items', 'keys', "
            "'map_keys', 'map_values', 'merge', 'omit', 'pick', 'set_value', "
            "'unflatten_keys', 'values'"
        ),
        "param": "(any, optional) Used for 'pick', 'omit', 'has_key', 'is_equal'",
        "path": "(str or list, optional) Used for 'set_value' and 'get_value'",
        "value": "(any, optional) Used for 'set_value'",
        "default": "(any, optional) Used for 'get_value'",
        "expression": "(str, optional) Lua expression for 'map_keys' and 'map_values'",
    },
    "any_tool": {
        "value": (
            "(any) The value to check or use as context for expression evaluation"
        ),
        "operation": (
            "(str) The operation to perform. One of: 'contains', 'eval', 'is_empty', "
            "'is_equal', 'is_nil', 'size'"
        ),
        "param": "(any, optional) The parameter for the operation, if required",
        "expression": (
            "(str, optional) Lua expression to evaluate (for 'eval' operation)"
        ),
    },
    "generate": {
        "options": (
            "(dict) Configuration options for the operation (parameter names vary by "
            "operation)"
        ),
        "operation": (
            "(str) The operation to perform. One of: 'accumulate', "
            "'cartesian_product', 'combinations', 'cycle', 'permutations', 'powerset', "
            "'range', 'repeat', 'unique_pairs', 'windowed', 'zip_with_index'"
        ),
    },
    "chain": {
        "input": "(any) The initial input to the chain",
        "tool_calls": (
            "(list) Each dict must have: 'tool': the tool name (str), 'params': "
            "dict of additional parameters (optional, default empty)"
        ),
    },
}
# --- End MCP Parameter Description Monkey Patch ---

try:
    from fastmcp.tools.tool import ParsedFunction

    # Only store the original if not already stored
    if "_original_from_function" not in globals():
        _original_from_function = ParsedFunction.from_function

    def patched_from_function(fn, exclude_args=None, validate=True):
        parsed = _original_from_function(
            fn, exclude_args=exclude_args, validate=validate
        )
        tool_name = getattr(fn, "__name__", None)
        if tool_name in PARAM_DESCRIPTIONS:
            param_descs = PARAM_DESCRIPTIONS[tool_name]
            props = parsed.parameters.get("properties")
            if props:
                for param, desc in param_descs.items():
                    if param in props:
                        props[param]["description"] = desc
        return parsed

    ParsedFunction.from_function = staticmethod(patched_from_function)
except ImportError:
    pass
# --- End MCP Parameter Description Monkey Patch ---


# --- MCP Server Setup ---


class LeverMCP(FastMCP):
    pass


mcp = LeverMCP("Lever MCP")


@mcp.tool()
def strings(
    text: str,
    operation: str,
    param: Any = None,
    data: Optional[dict] = None,
) -> dict:
    """
    Performs string operations and mutations.

    Supported operations:
        - 'camel_case': Converts to camelCase (e.g., 'foo bar' → 'fooBar').
        - 'capitalize': Capitalizes the first character (e.g., 'foo bar' → 'Foo bar').
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
        - 'replace': Replaces all occurrences of a substring (requires data={'old':
          'x', 'new': 'y'}).
        - 'reverse': Reverses the string (e.g., 'hello' → 'olleh').
        - 'sample_size': Returns n random characters (param: int).
        - 'shuffle': Randomly shuffles string characters.
        - 'slice': Extracts substring (requires data={'from': int, 'to': int}).
        - 'snake_case': Converts to snake_case (e.g., 'foo bar' → 'foo_bar').
        - 'split': Splits string into array by delimiter (param: str delimiter).
        - 'starts_with': Checks if string starts with substring (param: str).
        - 'template': Interpolates variables using {var} syntax (requires data dict).
        - 'trim': Removes leading and trailing whitespace.
        - 'upper_case': Converts to uppercase (e.g., 'Hello' → 'HELLO').
        - 'xor': String-specific XOR operation (param: str).

    Returns:
        dict: The result, always wrapped in a dictionary with a 'value' key containing
            a string (except 'split' which returns a list). If an error occurs, an
            'error' key is also present.

    MCP Usage Examples:
        strings('foo bar', 'camel_case')  # => {'value': 'fooBar'}
        strings('Hello, {name}!', 'template', data={'name': 'World'})
          # => {'value': 'Hello, World!'}
        strings('abc', 'contains', param='a')  # => {'value': true}

    Lua Function Call Examples:
        strings.upper_case('hello')  # => 'HELLO'
        strings.contains('hello world', 'world')  # => true
        strings.replace({text='hello world', data={old='world', new='Lua'}})
          # => 'hello Lua'
        strings.split({text='foo,bar', param=',', wrap=true})
          # => JSON: ['foo', 'bar'], Lua: {'__type': 'list', 'data': {'foo', 'bar'}}

    In Lua, an empty table represents an empty dict **OR** an empty list. Lever tools
    serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
    dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
    {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
    serialization. Use unwrap(o) to get the original table.
    """
    return _strings_impl(text, operation, param, data, wrap=False)


def _strings_impl(
    text: str,
    operation: str,
    param: Any = None,
    data: Optional[Dict[str, Any]] = None,
    wrap: bool = False,
) -> dict:
    try:
        import re
        import unicodedata
        import random

        # Unwrap input parameters
        text = _unwrap_input(text)
        param = _unwrap_input(param)
        data = _unwrap_input(data)

        # Basic validation
        if not isinstance(text, str):
            return {"value": None, "error": "text must be a string"}

        result = None

        if operation == "camel_case":
            # Convert to camelCase
            # First normalize: replace non-alphanumeric with spaces, then title case
            cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", text).strip()
            if not cleaned:
                result = ""
            else:
                words = cleaned.split()
                result = words[0].lower() + "".join(
                    word.capitalize() for word in words[1:]
                )

        elif operation == "capitalize":
            result = text.capitalize()

        elif operation == "contains":
            if param is None:
                return {
                    "value": None,
                    "error": "contains operation requires param (substring to find)",
                }
            result = str(param) in text

        elif operation == "deburr":
            # Remove accents/diacritics
            result = "".join(
                c
                for c in unicodedata.normalize("NFD", text)
                if unicodedata.category(c) != "Mn"
            )

        elif operation == "ends_with":
            if param is None:
                return {
                    "value": None,
                    "error": "ends_with operation requires param (suffix to check)",
                }
            result = text.endswith(str(param))

        elif operation == "is_alpha":
            result = text.isalpha()

        elif operation == "is_digit":
            result = text.isdigit()

        elif operation == "is_empty":
            result = len(text) == 0

        elif operation == "is_equal":
            if param is None:
                return {
                    "value": None,
                    "error": "is_equal operation requires param (string to compare)",
                }
            result = text == str(param)

        elif operation == "is_lower":
            result = text.islower()

        elif operation == "is_upper":
            result = text.isupper()

        elif operation == "kebab_case":
            # Convert to kebab-case: handle camelCase, PascalCase, snake_case, and
            # spaces. First insert hyphens before capitals that follow lowercase letters
            # or numbers.
            result = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
            # Replace underscores and other non-alphanumeric chars with hyphens
            result = re.sub(r"[^a-zA-Z0-9]+", "-", result)
            # Remove leading/trailing hyphens and convert to lowercase
            result = result.strip("-").lower()

        elif operation == "lower_case":
            result = text.lower()

        elif operation == "replace":
            if not data or "old" not in data or "new" not in data:
                return {
                    "value": None,
                    "error": (
                        "replace operation requires data with 'old' and 'new' keys"
                    ),
                }
            result = text.replace(str(data["old"]), str(data["new"]))

        elif operation == "reverse":
            result = text[::-1]

        elif operation == "sample_size":
            if param is None:
                return {
                    "value": None,
                    "error": (
                        "sample_size operation requires param (number of characters)"
                    ),
                }
            try:
                n = int(param)
                if n < 0:
                    return {
                        "value": None,
                        "error": "sample_size param must be non-negative",
                    }
                elif n == 0:
                    result = ""
                elif n >= len(text):
                    result = text
                else:
                    result = "".join(random.sample(text, n))
            except (ValueError, TypeError):
                return {
                    "value": None,
                    "error": "sample_size param must be a valid integer",
                }

        elif operation == "shuffle":
            char_list = list(text)
            random.shuffle(char_list)
            result = "".join(char_list)

        elif operation == "slice":
            if not data:
                return {
                    "value": None,
                    "error": "'data' with 'from' is required for slice operation",
                }
            try:
                from_idx = int(data.get("from", 0))
                to_idx = data.get("to", None)
                if to_idx is not None:
                    to_idx = int(to_idx)
                    result = text[from_idx:to_idx]
                else:
                    result = text[from_idx:]
            except (ValueError, TypeError, KeyError):
                return {
                    "value": None,
                    "error": (
                        "slice operation requires valid 'from' and optional 'to' "
                        "indices"
                    ),
                }

        elif operation == "snake_case":
            # Convert to snake_case
            # Handle camelCase and PascalCase
            s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
            s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
            # Replace non-alphanumeric with underscores
            cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", s2).strip("_")
            result = cleaned.lower()

        elif operation == "split":
            if param is None:
                # Default whitespace split (empty string produces empty list)
                result = text.split()
            else:
                delimiter = str(param)
                result = text.split(delimiter)

        elif operation == "starts_with":
            if param is None:
                return {
                    "value": None,
                    "error": "starts_with operation requires param (prefix to check)",
                }
            result = text.startswith(str(param))

        elif operation == "template":
            if not data:
                return {
                    "value": None,
                    "error": "template operation requires data with variable values",
                }
            try:
                # Simple template substitution using {var} syntax
                template_text = text
                for key, value in data.items():
                    placeholder = "{" + str(key) + "}"
                    template_text = template_text.replace(placeholder, str(value))
                result = template_text
            except Exception as e:
                return {
                    "value": None,
                    "error": f"template substitution failed: {str(e)}",
                }

        elif operation == "trim":
            result = text.strip()

        elif operation == "upper_case":
            result = text.upper()

        elif operation == "xor":
            if param is None:
                return {
                    "value": None,
                    "error": "xor operation requires param (string to XOR with)",
                }
            try:
                other = str(param)
                # XOR as symmetric difference of character sets
                set_a = set(text)
                set_b = set(other)
                xor_chars = set_a.symmetric_difference(set_b)
                result = "".join(sorted(xor_chars))
            except Exception as e:
                return {"value": None, "error": f"xor operation failed: {str(e)}"}

        else:
            return {"value": None, "error": f"Unknown operation: {operation}"}

        # Apply wrapping if requested
        if wrap:
            result = _apply_wrapping(result, wrap)

        return {"value": result}

    except Exception as e:
        return {"error": f"String operation failed: {str(e)}"}


@mcp.tool()
def lists(
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
        import random

        if not isinstance(items, list):
            return {"value": None, "error": "Argument must be a list for shuffle."}
        result = items[:]
        random.shuffle(result)
        return {"value": result}
    elif operation == "sample_size":
        import random

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
    import random, json

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


@mcp.tool()
def dicts(
    obj: Any,
    operation: str,
    param: Any = None,
    path: Any = None,
    value: Any = None,
    default: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """
    Performs dictionary operations, including merge, set/get value, and property checks.

    Supported operations:
        - 'flatten_keys': Flattens nested dict with dot notation (e.g.,
          {'a': {'b': 1}} → {'a.b': 1})
        - 'get_value': Gets a deep property by path (path: str dot-notation like
          "a.b.c" or list like ["a","b","c"], default: any)
        - 'has_key': Checks if a dict has a given key (param: str)
        - 'invert': Swaps keys and values
        - 'is_empty': Checks if the dict is empty
        - 'is_equal': Checks if two dicts are deeply equal (param: dict to compare)
        - 'items': Gets key-value pairs as list of tuples
        - 'keys': Gets all dictionary keys as list
        - 'map_keys': Transforms all keys with Lua expression (expression: str)
        - 'map_values': Transforms all values with Lua expression (expression: str)
        - 'merge': Deep merges a list of dictionaries (obj must be a list of dicts)
        - 'omit': Omits specified keys (param: list of keys)
        - 'pick': Picks specified keys (param: list of keys)
        - 'set_value': Sets a deep property by path (path: str dot-notation like
          "a.b.c" or list like ["a","b","c"], value: any)
        - 'unflatten_keys': Unflattens dot-notation keys to nested dict (e.g.,
          {'a.b': 1} → {'a': {'b': 1}})
        - 'values': Gets all dictionary values as list

    Returns:
        dict: Result with 'value' key containing a dict (most operations), list
            ('keys', 'values', 'items'), or single value ('get_value', 'has_key',
            'is_empty', 'is_equal'). On error, includes 'error' key.

    Expression Examples:
        - Filtering: 'age > 25', 'score >= 80', 'name == 'Alice''
        - Grouping: 'age >= 30 and 'senior' or 'junior''
        - Sorting: 'age * -1' (reverse age), 'string.lower(name)'
          (case-insensitive)
        - Extraction: 'string.upper(name)', 'age > 18 and name or 'minor''
        - Math: 'math.abs(score - 50)', 'x*x + y*y' (distance squared)
        - Functional programming: Use tool functions as expressions (e.g.,
          `lists.map(items, 'strings.upper_case')`).

    In Lua expressions for map_keys: key (current key string), value (current value),
    obj (original dict). For map_values: value (current value), key (current key
    string), obj (original dict). For map_values, if value is a dict, its properties are
    also accessible directly (age, name, etc.). Available in expressions: math.*,
    string.*, os.time/date/clock, type(), tonumber(), tostring(). You may pass a single
    Lua expression or a block of Lua code. For multi-line code, use return to specify
    the result.

    MCP Usage Examples:
        dicts({'a': 1, 'b': 2}, 'pick', param=['a'])  # => {'value': {'a': 1}}
        dicts({'a': {'b': 1}}, 'set_value', path=['a', 'b'], value=2)
          # => {'value': {'a': {'b': 2}}}
        dicts({'a': 1}, 'get_value', path='b', default=42)  # => {'value': 42}
        dicts({'firstName': 'john'}, 'map_keys', expression='strings.snake_case')
          # => {'value': {'first_name': 'john'}}

    Lua Function Call Examples:
        dicts.has_key({name='alice', age=30}, 'email')  # => false
        dicts.get_value(
            {obj={user={profile={name='bob'}}}, path='user.profile.name'}
        )  # => 'bob'
        dicts.pick(
            {obj={id=1, name='alice', email='alice@test.com'}, param={'id', 'name'}}
        )  # => {'id': 1, 'name': 'alice'}
        dicts.omit({obj={password='secret', name='alice', age=30}, param={'password'}})
          # => {'name': 'alice', 'age': 30}
        dicts.merge({obj={{config={debug=true}}, {config={port=8080}}}, wrap=true})
          # => JSON: {'config': {'port': 8080}}, Lua: {'__type': 'dict', 'data': {...}}

    In Lua, an empty table represents an empty dict **OR** an empty list. Lever tools
    serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
    dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
    {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
    serialization. Use unwrap(o) to get the original table.
    """
    return _dicts_impl(
        obj, operation, param, path, value, default, expression, wrap=False
    )


def _dicts_impl(
    obj: Any,
    operation: str,
    param: Any = None,
    path: Any = None,
    value: Any = None,
    default: Any = None,
    expression: Optional[str] = None,
    wrap: bool = False,
) -> dict:
    import copy, re

    # Unwrap input parameters
    obj = _unwrap_input(obj)
    param = _unwrap_input(param)
    path = _unwrap_input(path)
    value = _unwrap_input(value)
    default = _unwrap_input(default)

    # Handle wrapped dict objects (legacy code)
    if isinstance(obj, dict) and "__type" in obj and "data" in obj:
        if obj["__type"] == "dict":
            obj = obj["data"]
            # Convert Lua table to Python dict if needed
            if hasattr(obj, "items"):
                obj = dict(obj)
        elif obj["__type"] == "list" and operation == "merge":
            # Special case: merge operation can accept wrapped lists containing dicts
            obj = obj["data"]
            if hasattr(obj, "keys"):
                # Convert Lua table list to Python list
                keys = list(obj.keys())
                if keys and all(isinstance(k, int) and k > 0 for k in keys):
                    max_k = max(keys)
                    obj = [obj.get(k) for k in range(1, max_k + 1)]
                else:
                    obj = list(obj.values())

    try:
        # Add type validation for dict operations - dicts tool should only work on
        # dictionaries
        # For comparing any types, use any.is_equal instead
        if (
            operation not in ["merge", "is_empty"]
            and obj is not None
            and not isinstance(obj, dict)
        ):
            return {
                "value": None,
                "error": (
                    f"Dict operation '{operation}' requires a dictionary input, "
                    f"got {type(obj).__name__}. Use 'any.is_equal' for comparing "
                    "non-dictionary types."
                ),
            }

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
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "invert":
            result = {str(value): key for key, value in obj.items()}
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "pick":
            if param is None:
                raise ValueError("'param' (list of keys) is required for 'pick'.")
            result = {key: obj[key] for key in param if key in obj}
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "omit":
            if param is None:
                raise ValueError("'param' (list of keys) is required for 'omit'.")
            result = {key: value for key, value in obj.items() if key not in param}
            return {"value": _apply_wrapping(result, wrap)}
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
                            "'path' list elements must all be non-empty strings "
                            "for set_value."
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
            return {"value": _apply_wrapping(obj, wrap)}
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
                            "'path' list elements must all be non-empty strings "
                            "for get_value."
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
        elif operation == "keys":
            if not isinstance(obj, dict):
                return {"value": None, "error": "obj must be a dict for keys operation"}
            result = list(obj.keys())
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "values":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for values operation",
                }
            result = list(obj.values())
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "items":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for items operation",
                }
            result = list(obj.items())
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "map_keys":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for map_keys operation",
                }
            if not expression:
                return {
                    "value": None,
                    "error": "expression is required for map_keys operation",
                }
            result = {}
            for key, value in obj.items():
                # For map_keys, evaluate expression with key as the item
                # This allows tool function references to work with auto-wrap
                new_key = evaluate_expression(
                    expression, key, context={"key": key, "value": value, "obj": obj}
                )
                result[str(new_key)] = value
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "map_values":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for map_values operation",
                }
            if not expression:
                return {
                    "value": None,
                    "error": "expression is required for map_values operation",
                }
            result = {}
            for key, value in obj.items():
                # For map_values, evaluate expression with value as the item
                # This allows tool function references to work with auto-wrap
                new_value = evaluate_expression(
                    expression, value, context={"key": key, "value": value, "obj": obj}
                )
                result[key] = new_value
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "flatten_keys":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for flatten_keys operation",
                }

            def flatten_dict(d, parent_key="", sep="."):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return dict(items)

            result = flatten_dict(obj)
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "unflatten_keys":
            if not isinstance(obj, dict):
                return {
                    "value": None,
                    "error": "obj must be a dict for unflatten_keys operation",
                }

            result = {}
            for key, value in obj.items():
                keys = key.split(".")
                d = result
                for k in keys[:-1]:
                    if k not in d:
                        d[k] = {}
                    d = d[k]
                d[keys[-1]] = value

            return {"value": _apply_wrapping(result, wrap)}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}


@mcp.tool("any")
def any_tool(
    value: Any,
    operation: str,
    param: Any = None,
    expression: Optional[str] = None,
) -> dict:
    """
    Performs type-agnostic property checks, comparisons, and expression evaluation.

    Supported operations:
        - 'contains': Checks if a string or list contains a value (param: value to
          check)
        - 'eval': Evaluate a Lua expression with value as context (expression: Lua
          code)
        - 'is_empty': Checks if the value is empty
        - 'is_equal': Checks if two values are deeply equal (param: value to compare)
        - 'is_nil': Checks if the value is None
        - 'size': Gets the size/length of any collection type (strings, lists, dicts)
          or 1 for scalars

    Returns:
        dict: Result with 'value' key containing a boolean ('is_equal', 'is_empty',
        'is_nil',
            'contains'), integer ('size'), or any type ('eval' - depends on
            expression).
            On error, includes 'error' key.

    Expression Examples:
        - Boolean check: 'age > 25', 'score >= 80', 'name == 'Alice''
        - Math: 'math.abs(x - y)', 'x*x + y*y'
        - String manipulation: 'string.upper(value)', 'string.sub(value, 1, 3)'
        - Null check: 'value == null', 'score ~= null'
        - Type check: 'type(value) == 'table'', 'type(value) == 'string''
        - Functional programming: Use tool functions as expressions (e.g.,
          `lists.map(items, 'strings.upper_case')`).

    In Lua expressions, value refers to the input value being evaluated. Available in
    expressions: math.*, string.*, os.time/date/clock, type(), tonumber(), tostring().
    Dictionary keys accessible directly (age, name, etc.) or via value.key. You may pass
    a single Lua expression or a block of Lua code. For multi-line code, use return to
    specify the result.

    MCP Usage Examples:
        any('abc', 'contains', param='b')  # => {'value': true}
        any([1, 2, 3], 'contains', param=2)  # => {'value': true}
        any([], 'is_empty')  # => {'value': true}
        any(42, 'is_equal', param=42)  # => {'value': true}
        any([0, 0], 'eval', expression='lists.compact')  # => {'value': []}

    Lua Function Call Examples:
        any.is_equal(42, 42)  # => true
        any.is_empty('')  # => true
        any.contains('hello', 'ell')  # => true
        any.eval({age=30}, 'age > 25')  # => true
        any.eval(
            {value={{1}, {2}}, expression='lists.max_by(value, \"item[1]\")',
             wrap=true}
        )  # => JSON: {2}, Lua: {'__type': 'list', 'data': {2}}

    In Lua, an empty table represents an empty dict **OR** an empty list. Lever tools
    serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
    dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
    {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
    serialization. Use unwrap(o) to get the original table.
    """
    return _any_impl(value, operation, param, expression, wrap=False)


def _any_impl(
    value: Any,
    operation: str,
    param: Any = None,
    expression: Optional[str] = None,
    wrap: bool = False,
) -> dict:
    # Handle wrapped objects
    if isinstance(value, dict) and "__type" in value and "data" in value:
        obj_type = value["__type"]
        value = value["data"]
        # Convert Lua table to appropriate Python type if needed
        if hasattr(value, "keys"):
            if obj_type == "list":
                keys = list(value.keys())
                if keys and all(isinstance(k, int) and k > 0 for k in keys):
                    max_k = max(keys)
                    value = [value.get(k) for k in range(1, max_k + 1)]
                else:
                    value = list(value.values())
            else:  # dict type
                value = dict(value)

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
            # Use evaluate_expression for consistency and to support auto-wrap
            # functionality. Create a context where both dict property access AND
            # 'value' parameter work.
            context = {"value": value}
            if isinstance(value, dict):
                # Add dict keys as direct variables for convenience
                for key, val in value.items():
                    if (
                        isinstance(key, str)
                        and key.isidentifier()
                        and key
                        not in [
                            "and",
                            "or",
                            "not",
                            "if",
                            "then",
                            "else",
                            "end",
                            "value",
                        ]
                    ):
                        context[key] = val

            try:
                result = evaluate_expression(expression, value, context=context)
                return {"value": result}
            except Exception as e:
                return {"value": None, "error": f"Error in eval expression: {e}"}
        elif operation == "size":
            if hasattr(value, "__len__"):
                return {"value": len(value)}
            elif value is None:
                return {"value": 0}
            else:
                return {"value": 1}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}


@mcp.tool()
def generate(options: dict, operation: str) -> dict:
    """
    Generates sequences or derived data using the specified operation.

    Supported operations:
        - 'accumulate': Running totals. options: {'items': list, 'func':
          'add'/'mul'/'max'/'min'/'sub'/'div'/None}
        - 'cartesian_product': Cartesian product of multiple lists. options:
          {'lists': list_of_lists}
        - 'combinations': All combinations of a given length. options: {'items':
          list, 'length': int}
        - 'cycle': Repeat the sequence up to N times. options: {'items': list,
          'count': int}
        - 'permutations': All permutations of a given length. options: {'items':
          list, 'length': int (optional)}
        - 'powerset': All possible subsets of a list. options: {'items': list}
        - 'range': Generate a list of numbers. options: {'from': int, 'to': int,
          'step': int (optional)}
        - 'repeat': Repeat a value N times. options: {'value': any, 'count': int}
        - 'unique_pairs': All unique pairs from a list. options: {'items': list}
        - 'windowed': Sliding windows of a given size. options: {'items': list,
          'size': int}
        - 'zip_with_index': Tuples of (index, value). options: {'items': list}

    Returns:
        dict: Result with 'value' key containing a list (all operations return lists).
            On error, includes 'error' key.

    MCP Usage Examples:
        generate({'from': 0, 'to': 5}, 'range')  # => {'value': [0, 1, 2, 3, 4]}
        generate({'value': 'x', 'count': 3}, 'repeat')  # => {'value': ['x', 'x', 'x']}
        generate({'items': [1, 2, 3]}, 'powerset')
          # => {'value': [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]}
        generate({'lists': [[1, 2], ['a', 'b']]}, 'cartesian_product')
          # => {'value': [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]}

    Lua Function Call Examples:
        generate.range({from=0, to=5})  # => {0, 1, 2, 3, 4}
        generate['repeat']({value='x', count=3})  # => {'x', 'x', 'x'}
        generate.cartesian_product({lists={{1, 2}, {'a', 'b'}}})
          # => {{1, 'a'}, {1, 'b'}, {2, 'a'}, {2, 'b'}}
        generate.combinations({items={1, 2}, length=2, wrap=true})
          # => JSON: [[1, 2]], Lua: {'__type': 'list', 'data': [[1, 2]]}

    In Lua, an empty table represents an empty dict **OR** an empty list. Lever tools
    serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
    dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
    {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
    serialization. Use unwrap(o) to get the original table.
    """
    return _generate_impl(options, operation, wrap=False)


def _generate_impl(options: dict, operation: str, wrap: bool = False) -> dict:
    import itertools
    import operator

    # Unwrap input parameters
    options = _unwrap_input(options)

    try:
        if operation == "range":
            from_val = options.get("from")
            to_val = options.get("to")
            step = options.get("step", 1)

            if from_val is None or to_val is None:
                return {
                    "value": None,
                    "error": "range requires 'from' and 'to' in options dict",
                }
            result = list(range(from_val, to_val, step))
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "cartesian_product":
            lists = options.get("lists")
            if lists is None:
                return {
                    "value": None,
                    "error": "cartesian_product requires 'lists' in options dict",
                }
            result = list(itertools.product(*lists))
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "repeat":
            if "value" not in options or "count" not in options:
                return {
                    "value": None,
                    "error": "repeat requires 'value' and 'count' in options dict",
                }
            value = options["value"]
            count = options["count"]
            if not isinstance(count, int):
                return {
                    "value": None,
                    "error": "'count' must be an integer for 'repeat'",
                }
            result = list(itertools.repeat(value, count))
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "powerset":
            items = options.get("items")
            if items is None:
                return {
                    "value": None,
                    "error": "powerset requires 'items' in options dict",
                }
            s = list(items)
            if not s:
                result = [[]]
            else:
                result = [
                    list(combo)
                    for r in range(len(s) + 1)
                    for combo in itertools.combinations(s, r)
                ]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "windowed":
            items = options.get("items")
            size = options.get("size")

            if items is None or size is None:
                return {
                    "value": None,
                    "error": "windowed requires 'items' and 'size' in options dict",
                }
            if not isinstance(size, int) or size < 1:
                return {
                    "value": None,
                    "error": "'size' must be a positive integer for 'windowed'",
                }
            s = list(items)
            result = [list(s[i : i + size]) for i in range(len(s) - size + 1)]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "cycle":
            items = options.get("items")
            count = options.get("count")

            if items is None or count is None:
                return {
                    "value": None,
                    "error": "cycle requires 'items' and 'count' in options dict",
                }
            s = list(items)
            result = [s[i % len(s)] for i in range(count)] if s else []
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "accumulate":
            items = options.get("items")
            func = options.get("func")

            if items is None:
                return {
                    "value": None,
                    "error": "accumulate requires 'items' in options dict",
                }
            s = list(items)
            if func is None or func == "add":
                result = list(itertools.accumulate(s))  # Default is addition
            elif func == "mul":
                result = list(itertools.accumulate(s, operator.mul))
            elif func == "max":
                result = list(itertools.accumulate(s, max))
            elif func == "min":
                result = list(itertools.accumulate(s, min))
            elif func == "sub":
                result = list(itertools.accumulate(s, operator.sub))
            elif func == "div":
                result = list(itertools.accumulate(s, operator.truediv))
            else:
                return {
                    "value": None,
                    "error": "accumulate supports func: None, 'add', 'mul', "
                    "'max', 'min', 'sub', 'div'",
                }
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "zip_with_index":
            items = options.get("items")
            if items is None:
                return {
                    "value": None,
                    "error": "zip_with_index requires 'items' in options dict",
                }
            result = [[i, v] for i, v in enumerate(items)]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "unique_pairs":
            items = options.get("items")
            if items is None:
                return {
                    "value": None,
                    "error": "unique_pairs requires 'items' in options dict",
                }
            s = list(items)
            result = [list(pair) for pair in itertools.combinations(s, 2)]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "permutations":
            items = options.get("items")
            length = options.get("length")

            if items is None:
                return {
                    "value": None,
                    "error": "permutations requires 'items' in options dict",
                }
            s = list(items)
            if not s:
                result = [[]]
            else:
                result = [list(p) for p in itertools.permutations(s, length)]
            return {"value": _apply_wrapping(result, wrap)}
        elif operation == "combinations":
            items = options.get("items")
            length = options.get("length")

            if items is None or length is None:
                return {
                    "value": None,
                    "error": (
                        "combinations requires 'items' and 'length' in options dict"
                    ),
                }
            if not isinstance(length, int):
                return {
                    "value": None,
                    "error": "'length' must be an integer for 'combinations'",
                }
            s = list(items)
            if not s:
                result = []
            else:
                result = [list(c) for c in itertools.combinations(s, length)]
            return {"value": _apply_wrapping(result, wrap)}
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        return {"value": None, "error": str(e)}


@mcp.tool()
async def chain(input: Any, tool_calls: List[Dict[str, Any]]) -> dict:
    """
    Chains multiple tool calls, piping the output of one as the input to the next.

    Returns:
        dict: The result of the last tool in the chain, always wrapped in a
            dictionary with a 'value' key. If an error occurs, an 'error' key is
            also present.

    MCP Usage Examples:
        chain(
            [1, [2, [3, 4], 5]],
            [
                {'tool': 'lists', 'params': {'operation': 'flatten_deep'}},
                {'tool': 'lists', 'params': {'operation': 'compact'}},
                {
                    'tool': 'lists',
                    'params': {
                        'operation': 'sort_by',
                        'expression': 'item'
                    }
                }
            ]
        )
        # => {'value': [1, 2, 3, 4, 5]}

    Chaining Rule:
        The output from one tool is always used as the input to the next tool's primary
            parameter.
        You must not specify the primary parameter in params for any tool in the chain.

    Lua Function Call Examples:
        -- Note: chain is not exposed as a Lua function since it operates on tool calls
        -- Use direct tool function calls instead:
        local result = lists.sort_by(
            lists.compact(lists.flatten_deep({1, {2, {3, 4}, 5}}))
        )
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
        for p_name in ["text", "items", "obj", "value", "options"]:
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

        # Special handling for the generate tool
        if tool_name == "generate":
            if "options" in arguments:
                return {
                    "value": None,
                    "error": (
                        f"Step {i}: Chaining does not allow specifying the primary "
                        "parameter 'options' in params for generate tool."
                    ),
                }
            # For generate tool, construct the options dict based on operation
            operation = arguments.get("operation")
            unwrapped_value = unwrap_result(value)

            if operation == "repeat":
                count = arguments.get("count")
                if count is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'repeat' operation requires 'count' "
                            "parameter."
                        ),
                    }
                arguments["options"] = {"value": unwrapped_value, "count": count}
                arguments.pop("count", None)
            elif operation == "range":
                # Range doesn't use the input value, just pass the from/to/step
                # parameters
                from_val = arguments.get("from")
                to_val = arguments.get("to")
                step_val = arguments.get("step")
                if from_val is None or to_val is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'range' operation requires 'from' and "
                            "'to' parameters."
                        ),
                    }
                options = {"from": from_val, "to": to_val}
                if step_val is not None:
                    options["step"] = step_val
                arguments["options"] = options
                arguments.pop("from", None)
                arguments.pop("to", None)
                arguments.pop("step", None)
            elif operation == "cycle":
                count = arguments.get("count")
                if count is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'cycle' operation requires 'count' "
                            "parameter."
                        ),
                    }
                arguments["options"] = {"items": unwrapped_value, "count": count}
                arguments.pop("count", None)
            elif operation == "windowed":
                size = arguments.get("size")
                if size is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'windowed' operation requires 'size' "
                            "parameter."
                        ),
                    }
                arguments["options"] = {"items": unwrapped_value, "size": size}
                arguments.pop("size", None)
                arguments.pop("param", None)
            elif operation == "combinations":
                length = arguments.get("length")
                if length is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'combinations' operation requires "
                            "'length' parameter."
                        ),
                    }
                arguments["options"] = {"items": unwrapped_value, "length": length}
                arguments.pop("length", None)
                arguments.pop("param", None)
            elif operation == "permutations":
                length = arguments.get("length")
                # Length is optional for permutations
                options = {"items": unwrapped_value}
                if length is not None:
                    options["length"] = length
                arguments["options"] = options
                arguments.pop("length", None)
                arguments.pop("param", None)
            elif operation in [
                "powerset",
                "unique_pairs",
                "zip_with_index",
                "accumulate",
            ]:
                # These operations only need the items from the previous tool
                arguments["options"] = {"items": unwrapped_value}
            elif operation == "cartesian_product":
                # Cartesian product expects lists parameter
                lists = arguments.get("lists")
                if lists is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'cartesian_product' operation "
                            "requires 'lists' parameter."
                        ),
                    }
                arguments["options"] = {"lists": lists}
                arguments.pop("lists", None)
            else:
                return {
                    "value": None,
                    "error": (
                        f"Step {i}: Generate operation '{operation}' is not supported "
                        "in chains yet."
                    ),
                }
        elif primary_param:
            if primary_param in arguments:
                return {
                    "value": None,
                    "error": (
                        f"Step {i}: Chaining does not allow specifying the "
                        f"primary parameter '{primary_param}' in params. The "
                        "output from the previous tool is always used as input."
                    ),
                }
            # Unwrap the value before passing to the next tool
            arguments[primary_param] = unwrap_result(value)
        elif len(param_schema) == 1:
            only_param = next(iter(param_schema))
            if only_param in arguments:
                return {
                    "value": None,
                    "error": (
                        f"Step {i}: Chaining does not allow specifying the "
                        f"primary parameter '{only_param}' in params. The output "
                        "from the previous tool is always used as input."
                    ),
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


def _unwrap_input(value: Any) -> Any:
    """
    Unwrap input parameters for tool processing.
    Recursively unwraps wrapped lists/dicts to regular Python objects.
    """
    if isinstance(value, dict) and "__type" in value and "data" in value:
        # This is a wrapped object, unwrap it
        return _unwrap_input(value["data"])
    elif isinstance(value, list):
        # Recursively unwrap list contents
        return [_unwrap_input(item) for item in value]
    elif isinstance(value, dict):
        # Recursively unwrap dict contents
        return {k: _unwrap_input(v) for k, v in value.items()}
    else:
        return value


def _apply_wrapping(result: Any, wrap: bool) -> Any:
    """
    Apply wrapping to lists and dicts if wrap=True.
    Recursively wraps ALL nested structures.
    """
    if not wrap:
        return result

    if isinstance(result, list):
        # Wrap as list and recursively wrap ALL contents
        wrapped_items = [_apply_wrapping(item, wrap) for item in result]
        return {"__type": "list", "data": wrapped_items}
    elif isinstance(result, dict):
        # Check if it's already a wrapped object
        if "__type" in result and "data" in result:
            # Already wrapped, just wrap the data recursively
            return {
                "__type": result["__type"],
                "data": _apply_wrapping(result["data"], wrap),
            }
        else:
            # Wrap as dict and recursively wrap ALL contents
            wrapped_items = {k: _apply_wrapping(v, wrap) for k, v in result.items()}
            return {"__type": "dict", "data": wrapped_items}
    else:
        return result


def _wrap_result(result_dict: dict, wrap: bool) -> dict:
    """
    Apply wrapping to the result value if wrap=True and no error occurred.
    """
    if "error" in result_dict or not wrap:
        return result_dict

    wrapped_value = _apply_wrapping(result_dict.get("value"), wrap)
    return {"value": wrapped_value}


def _register_mcp_tools_in_lua(lua_runtime: lupa.LuaRuntime):
    """
    Register MCP tool functions in the Lua runtime to enable calling them as
    functions like strings.is_alpha(s) or lists.filter_by(items, expr).
    """

    def create_tool_wrapper(tool_name, operation_name):
        """Create a wrapper function for a specific tool operation."""

        def wrapper(*args):
            # Get null sentinel for proper conversion
            null_sentinel = lua_runtime.eval("null")
            # Support both positional args and table-based args
            if len(args) == 1 and hasattr(args[0], "values"):
                # Check if this is a parameter table or just data
                table_dict = dict(args[0])

                # Parameter tables have tool-specific parameter names as keys
                param_keys = set()
                if tool_name == "strings":
                    param_keys = {"text", "param", "data", "wrap"}
                elif tool_name == "lists":
                    param_keys = {"items", "param", "others", "expression", "wrap"}
                elif tool_name == "dicts":
                    param_keys = {
                        "obj",
                        "param",
                        "path",
                        "value",
                        "default",
                        "expression",
                        "wrap",
                    }
                elif tool_name == "any_tool":
                    param_keys = {"value", "param", "expression", "wrap"}
                elif tool_name == "generate":
                    param_keys = {"options", "wrap"}

                # If any table key matches parameter names, treat as parameter table
                is_param_table = bool(param_keys.intersection(table_dict.keys()))

                if is_param_table:
                    # Single table argument - extract named parameters
                    params_table = lua_to_python(table_dict)
                    if not isinstance(params_table, dict):
                        params_table = {}
                    # Call the tool function with named parameters from the table
                    if tool_name == "strings":
                        wrap_val = params_table.get("wrap", False)
                        result = _strings_impl(
                            text=params_table.get("text"),
                            operation=operation_name,
                            param=params_table.get("param"),
                            data=params_table.get("data"),
                            wrap=wrap_val,
                        )
                    elif tool_name == "lists":
                        wrap_val = params_table.get("wrap", False)
                        result = _lists_impl(
                            items=params_table.get("items"),
                            operation=operation_name,
                            param=params_table.get("param"),
                            others=params_table.get("others"),
                            expression=params_table.get("expression"),
                            wrap=wrap_val,
                        )
                    elif tool_name == "dicts":
                        wrap_val = params_table.get("wrap", False)
                        result = _dicts_impl(
                            obj=params_table.get("obj"),
                            operation=operation_name,
                            param=params_table.get("param"),
                            path=params_table.get("path"),
                            value=params_table.get("value"),
                            default=params_table.get("default"),
                            expression=params_table.get("expression"),
                            wrap=wrap_val,
                        )
                    elif tool_name == "any_tool":
                        wrap_val = params_table.get("wrap", False)
                        result = _any_impl(
                            value=params_table.get("value"),
                            operation=operation_name,
                            param=params_table.get("param"),
                            expression=params_table.get("expression"),
                            wrap=wrap_val,
                        )
                    elif tool_name == "generate":
                        wrap_val = params_table.get("wrap", False)
                        # Extract options from the table, excluding the wrap parameter
                        options = {k: v for k, v in params_table.items() if k != "wrap"}
                        result = _generate_impl(
                            options=options,
                            operation=operation_name,
                            wrap=wrap_val,
                        )
                    else:
                        return None
                else:
                    # Single table that's data, not parameters - treat as positional
                    data_table = lua_to_python(args[0], null_sentinel)

                    # Call with the table as the first positional argument
                    if tool_name == "strings":
                        result = strings.fn(text=data_table, operation=operation_name)
                    elif tool_name == "lists":
                        result = lists.fn(items=data_table, operation=operation_name)
                    elif tool_name == "dicts":
                        result = dicts.fn(obj=data_table, operation=operation_name)
                    elif tool_name == "any_tool":
                        result = any_tool.fn(value=data_table, operation=operation_name)
                    elif tool_name == "generate":
                        result = _generate_impl(
                            options=data_table, operation=operation_name, wrap=False
                        )
                    else:
                        return None
            else:
                # Positional arguments - convert and use positional mapping
                py_args = []
                for i, arg in enumerate(args):
                    if hasattr(arg, "values"):  # Lua table
                        # Check if this is the null sentinel
                        if arg is null_sentinel:
                            py_args.append(None)
                        else:
                            converted_table = lua_to_python(dict(arg))

                            # Special handling for first argument that might be a
                            # parameter table
                            if i == 0 and isinstance(converted_table, dict):
                                # Check if this looks like a parameter table for this
                                # tool
                                if tool_name == "lists" and "items" in converted_table:
                                    # Extract the items value for lists operations
                                    py_args.append(converted_table["items"])
                                elif (
                                    tool_name == "strings" and "text" in converted_table
                                ):
                                    # Extract the text value for strings operations
                                    py_args.append(converted_table["text"])
                                elif tool_name == "dicts" and "obj" in converted_table:
                                    # Extract the obj value for dicts operations
                                    py_args.append(converted_table["obj"])
                                elif (
                                    tool_name == "any_tool"
                                    and "value" in converted_table
                                ):
                                    # Extract the value for any_tool operations
                                    py_args.append(converted_table["value"])
                                elif tool_name == "generate":
                                    # For generate operations, the table itself is the
                                    # options
                                    py_args.append(converted_table)
                                else:
                                    # Not a parameter table, use as-is
                                    py_args.append(converted_table)
                            else:
                                py_args.append(converted_table)
                    elif hasattr(arg, "__iter__") and not isinstance(
                        arg, str
                    ):  # Other Lua tables
                        try:
                            py_args.append(lua_to_python(dict(arg)))
                        except Exception:
                            py_args.append(list(arg))
                    else:
                        py_args.append(arg)

                # Call the tool function directly using .fn to access the
                # underlying implementation
                if tool_name == "strings":
                    # Check for wrap parameter as last argument
                    # Only treat as wrap if: we have 4+ args AND last is boolean
                    # Expected: strings.upper_case(text, param, data, wrap)
                    wrap_arg = False
                    if len(py_args) >= 4 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        # Remove wrap from args for other parameter parsing
                        py_args = py_args[:-1]

                    # Some string operations use 'data' as second argument instead of
                    # 'param'
                    if operation_name in ["slice", "replace", "template"]:
                        result = _strings_impl(
                            text=py_args[0] if py_args else None,
                            operation=operation_name,
                            data=py_args[1] if len(py_args) > 1 else None,
                            wrap=wrap_arg,
                        )
                    else:
                        result = _strings_impl(
                            text=py_args[0] if py_args else None,
                            operation=operation_name,
                            param=py_args[1] if len(py_args) > 1 else None,
                            data=py_args[2] if len(py_args) > 2 else None,
                            wrap=wrap_arg,
                        )
                elif tool_name == "lists":
                    # Handle different argument patterns for lists operations
                    items_arg = py_args[0] if py_args else None

                    # Check for wrap parameter as last argument
                    # Only treat as wrap if: we have 5+ args AND last is boolean
                    # This ensures explicit intent: lists.map(items, expr, nil, nil,
                    # true)
                    wrap_arg = False
                    if len(py_args) >= 5 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        # Remove wrap from args for other parameter parsing
                        py_args = py_args[:-1]

                    # Operations that use 'param' as second or third argument
                    if operation_name in [
                        "join",
                        "min",
                        "max",
                        "sample_size",
                    ]:
                        param_arg = py_args[1] if len(py_args) > 1 else None
                        expression_arg = py_args[2] if len(py_args) > 2 else None
                        others_arg = py_args[3] if len(py_args) > 3 else None
                    elif operation_name in [
                        "contains",
                        "nth",
                        "take",
                        "take_right",
                        "drop",
                        "drop_right",
                        "chunk",
                    ]:
                        # These operations expect param as third argument
                        # (skip nil in second position)
                        param_arg = py_args[2] if len(py_args) > 2 else None
                        expression_arg = py_args[3] if len(py_args) > 3 else None
                        others_arg = py_args[4] if len(py_args) > 4 else None
                    elif operation_name in ["is_equal"]:
                        # is_equal expects the comparison value as param argument
                        # (third position)
                        param_arg = py_args[2] if len(py_args) > 2 else None
                        expression_arg = None
                        others_arg = None
                    elif operation_name in [
                        "difference_by",
                        "intersection_by",
                        "difference",
                        "intersection",
                        "union",
                        "xor",
                        "zip_with",
                    ]:
                        # Operations that use 'others' as second argument
                        others_arg = py_args[1] if len(py_args) > 1 else None
                        expression_arg = py_args[2] if len(py_args) > 2 else None
                        param_arg = py_args[3] if len(py_args) > 3 else None
                    else:
                        # Standard operations: items, expression, param, others
                        expression_arg = py_args[1] if len(py_args) > 1 else None
                        param_arg = py_args[2] if len(py_args) > 2 else None
                        others_arg = py_args[3] if len(py_args) > 3 else None

                    result = _lists_impl(
                        items=items_arg,
                        operation=operation_name,
                        param=param_arg,
                        expression=expression_arg,
                        others=others_arg,
                        wrap=wrap_arg,
                    )
                elif tool_name == "dicts":
                    # Check for wrap parameter as last argument.
                    # Only treat as wrap if: we have 7+ args AND last is boolean
                    # Expected:
                    #    dicts.keys(obj, param, path, value, default, expression, wrap)
                    wrap_arg = False
                    if len(py_args) >= 7 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        # Remove wrap from args for other parameter parsing
                        py_args = py_args[:-1]

                    # Handle different argument patterns for dicts operations
                    if operation_name in ["map_keys", "map_values"]:
                        # These operations use expression as second argument
                        result = _dicts_impl(
                            obj=py_args[0] if py_args else None,
                            operation=operation_name,
                            expression=py_args[1] if len(py_args) > 1 else None,
                            wrap=wrap_arg,
                        )
                    else:
                        # Standard operations: obj, param, path, value
                        result = _dicts_impl(
                            obj=py_args[0] if py_args else None,
                            operation=operation_name,
                            param=py_args[1] if len(py_args) > 1 else None,
                            path=py_args[2] if len(py_args) > 2 else None,
                            value=py_args[3] if len(py_args) > 3 else None,
                            wrap=wrap_arg,
                        )
                elif tool_name == "any_tool":
                    # Check for wrap parameter as last argument
                    # Only treat as wrap if: we have 4+ args AND last is boolean
                    # Expected: any.eval(value, expression, param, wrap)
                    wrap_arg = False
                    if len(py_args) >= 4 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        # Remove wrap from args for other parameter parsing
                        py_args = py_args[:-1]

                    # For any_tool, param vs expression depends on the operation
                    if operation_name in ["contains", "is_equal"]:
                        # These operations use param for second argument
                        result = _any_impl(
                            value=py_args[0] if py_args else None,
                            operation=operation_name,
                            param=py_args[1] if len(py_args) > 1 else None,
                            wrap=wrap_arg,
                        )
                    else:
                        # Operations like 'eval' use expression for second
                        # argument
                        result = _any_impl(
                            value=py_args[0] if py_args else None,
                            operation=operation_name,
                            expression=py_args[1] if len(py_args) > 1 else None,
                            param=py_args[2] if len(py_args) > 2 else None,
                            wrap=wrap_arg,
                        )
                elif tool_name == "generate":
                    # Check for wrap parameter as last argument
                    wrap_arg = False
                    if len(py_args) >= 2 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        py_args = py_args[:-1]
                    result = _generate_impl(
                        options=py_args[0] if py_args else {},
                        operation=operation_name,
                        wrap=wrap_arg,
                    )
                else:
                    return None

            # Return the value directly, or None if error
            if isinstance(result, dict) and "value" in result:
                value = result["value"]
                # If the value is wrapped (has __type), create a special Lua object
                # that preserves the wrapped format through evaluate_expression
                if isinstance(value, dict) and "__type" in value and "data" in value:
                    # Create a special wrapper that won't be unwrapped by lua_to_python
                    special_wrapper = {
                        "__wrapped_result": True,
                        "__type": value["__type"],
                        "data": value["data"],
                    }
                    return python_to_lua(special_wrapper, lua_runtime)
                else:
                    return python_to_lua(value, lua_runtime)
            return None

        # Store tool name as attribute for auto-wrap detection
        wrapper._mcp_tool_name = tool_name
        return wrapper

    # String operations
    string_ops = [
        "camel_case",
        "capitalize",
        "contains",
        "deburr",
        "ends_with",
        "is_alpha",
        "is_digit",
        "is_empty",
        "is_equal",
        "is_lower",
        "is_upper",
        "kebab_case",
        "lower_case",
        "replace",
        "reverse",
        "sample_size",
        "shuffle",
        "slice",
        "snake_case",
        "split",
        "starts_with",
        "template",
        "trim",
        "upper_case",
        "xor",
    ]

    # List operations
    list_ops = [
        "all_by",
        "every",
        "any_by",
        "some",
        "count_by",
        "difference_by",
        "filter_by",
        "find_by",
        "flat_map",
        "group_by",
        "intersection_by",
        "join",
        "key_by",
        "map",
        "max",
        "max_by",
        "min",
        "min_by",
        "partition",
        "pluck",
        "reduce",
        "remove_by",
        "sort_by",
        "uniq_by",
        "zip_with",
        "chunk",
        "compact",
        "contains",
        "drop",
        "drop_right",
        "flatten",
        "flatten_deep",
        "head",
        "index_of",
        "initial",
        "is_empty",
        "is_equal",
        "last",
        "nth",
        "random_except",
        "sample",
        "sample_size",
        "shuffle",
        "tail",
        "take",
        "take_right",
        "difference",
        "intersection",
        "union",
        "xor",
        "unzip_list",
        "zip_lists",
    ]

    # Dict operations
    dict_ops = [
        "flatten_keys",
        "get_value",
        "has_key",
        "invert",
        "is_empty",
        "is_equal",
        "items",
        "keys",
        "map_keys",
        "map_values",
        "merge",
        "omit",
        "pick",
        "set_value",
        "unflatten_keys",
        "values",
    ]

    # Any operations
    any_ops = ["contains", "eval", "is_empty", "is_equal", "is_nil", "size"]

    # Generate operations
    generate_ops = [
        "accumulate",
        "cartesian_product",
        "combinations",
        "cycle",
        "permutations",
        "powerset",
        "range",
        "repeat",
        "unique_pairs",
        "windowed",
        "zip_with_index",
    ]

    strings_table = {op: create_tool_wrapper("strings", op) for op in string_ops}
    lua_runtime.globals()["strings"] = lua_runtime.table_from(
        strings_table
    )  # type: ignore  # noqa

    lists_table = {op: create_tool_wrapper("lists", op) for op in list_ops}
    lua_runtime.globals()["lists"] = lua_runtime.table_from(lists_table)  # type: ignore

    dicts_table = {op: create_tool_wrapper("dicts", op) for op in dict_ops}
    lua_runtime.globals()["dicts"] = lua_runtime.table_from(dicts_table)  # type: ignore

    any_table = {op: create_tool_wrapper("any_tool", op) for op in any_ops}
    lua_runtime.globals()["any"] = lua_runtime.table_from(any_table)  # type: ignore

    generate_table = {op: create_tool_wrapper("generate", op) for op in generate_ops}
    lua_runtime.globals()["generate"] = lua_runtime.table_from(
        generate_table
    )  # type: ignore  # noqa


def create_lua_runtime(safe_mode: Optional[bool] = None) -> lupa.LuaRuntime:
    """
    Create a Lua runtime with optional sandboxing and MCP tool function
    registration.

    Args:
        safe_mode: If True, applies safety rails. If None, uses global SAFE_MODE
            setting.
    """
    if safe_mode is None:
        safe_mode = SAFE_MODE

    lua_runtime = lupa.LuaRuntime()

    # Always define a global 'null' table as the None sentinel with a unique marker
    lua_runtime.execute("null = {__null_sentinel = true}")

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

    # Register utility functions for type disambiguation
    def lua_list(table):
        """
        Creates a list-typed wrapper for explicit type disambiguation.

        Usage: list({1, 2, 3}) or list({})
        Returns: A wrapped object that will be converted to Python list

        Use this when you need to ensure an empty table {} becomes an empty list []
        in the JSON output, rather than an empty dict {}.
        """
        if table is None:
            return lua_runtime.table_from(
                {"__type": "list", "data": lua_runtime.table_from([])}
            )

        # Create wrapper with list type
        wrapper = {"__type": "list", "data": table}
        return lua_runtime.table_from(wrapper)

    def lua_dict(table):
        """
        Creates a dict-typed wrapper for explicit type disambiguation.

        Usage: dict({a=1, b=2}) or dict({})
        Returns: A wrapped object that will be converted to Python dict

        Use this when you need to ensure an empty table {} is explicitly
        treated as an empty dict {} in the JSON output.
        """
        if table is None:
            return lua_runtime.table_from(
                {"__type": "dict", "data": lua_runtime.table_from({})}
            )

        # Create wrapper with dict type
        wrapper = {"__type": "dict", "data": table}
        return lua_runtime.table_from(wrapper)

    def lua_unwrap(obj):
        """
        Unwraps a wrapped object to access the underlying data.

        Usage: unwrap(list({1, 2, 3})) or unwrap(dict({a=1}))
        Returns: The original Lua table without the wrapper

        Use this to extract the data from wrapped objects for further processing.
        For non-wrapped objects, returns the object unchanged.
        """
        if obj is None:
            return None

        # Convert to Python dict to check structure
        if hasattr(obj, "values"):
            obj_dict = dict(obj)
        else:
            obj_dict = obj if isinstance(obj, dict) else {}

        # Check if it's a wrapped object
        if "__type" in obj_dict and "data" in obj_dict:
            return obj_dict["data"]

        # If not wrapped, return as-is
        return obj

    # Register the functions in Lua runtime
    lua_runtime.globals()["list"] = lua_list
    lua_runtime.globals()["dict"] = lua_dict
    lua_runtime.globals()["unwrap"] = lua_unwrap

    return lua_runtime


def python_to_lua(obj, lua_runtime):
    """
    Convert Python data structures to Lua equivalents. Handles None values,
    lists, dicts, and wrapped list/dict formats. None values become 'null'
    sentinels, enabling consistent null checks with 'item == null'. Lists are
    converted to Lua tables, dicts as tables.
    """
    null_sentinel = lua_runtime.eval("null")
    if obj is None:
        return null_sentinel
    elif isinstance(obj, list):
        # Convert each element and then convert the whole list to a Lua
        # table
        converted_items = [python_to_lua(x, lua_runtime) for x in obj]
        return lua_runtime.table_from(converted_items)
    elif isinstance(obj, dict):
        # Check for special wrapped result marker first
        if "__wrapped_result" in obj and obj["__wrapped_result"] is True:
            # Preserve the special wrapper structure
            wrapper = {
                "__wrapped_result": True,
                "__type": obj["__type"],
                "data": python_to_lua(obj["data"], lua_runtime),
            }
            return lua_runtime.table_from(wrapper)
        # Check for wrapped list/dict format
        elif "__type" in obj and "data" in obj:
            # It's a wrapped object, preserve the wrapper structure
            obj_type = obj["__type"]
            data = obj["data"]

            # Recursively encode the data part
            encoded_data = python_to_lua(data, lua_runtime)

            # Return the wrapped structure
            wrapper = {"__type": obj_type, "data": encoded_data}
            return lua_runtime.table_from(wrapper)
        else:
            # Regular dict handling
            converted_dict = {}
            for k, v in obj.items():
                converted_dict[k] = python_to_lua(v, lua_runtime)
            return lua_runtime.table_from(converted_dict)
    else:
        return obj


def lua_to_python_preserve_wrapped(obj, null_sentinel=None):
    """
    Convert Lua data structures to Python equivalents, preserving wrapped objects.
    This version keeps wrapped list/dict objects in wrapped format instead of unwrapping
    them.
    """
    # Check for null sentinel - handle both identity and empty table cases
    if null_sentinel is not None and obj is null_sentinel:
        return None
    elif isinstance(obj, list):
        return [lua_to_python_preserve_wrapped(x, null_sentinel) for x in obj]
    elif isinstance(obj, dict):
        # Check for wrapped list/dict format - preserve them!
        if "__type" in obj and "data" in obj:
            # This is a wrapped object, preserve it but convert the data part
            obj_type = obj["__type"]
            data = obj["data"]

            # Convert the data part recursively, preserving any nested wrapped objects
            if obj_type == "list":
                # Force conversion to list but preserve wrapped objects within
                if hasattr(data, "keys"):
                    # It's a Lua table, convert to Python list
                    keys = list(data.keys())
                    if not keys:
                        converted_data = []
                    elif all(isinstance(k, int) and k > 0 for k in keys):
                        max_k = max(keys)
                        converted_data = [
                            lua_to_python_preserve_wrapped(
                                data[k] if k in keys else None, null_sentinel
                            )
                            for k in range(1, max_k + 1)
                        ]
                    else:
                        # Non-consecutive keys, convert to list of values
                        converted_data = [
                            lua_to_python_preserve_wrapped(v, null_sentinel)
                            for v in data.values()
                        ]
                elif isinstance(data, list):
                    converted_data = [
                        lua_to_python_preserve_wrapped(x, null_sentinel) for x in data
                    ]
                else:
                    converted_data = []
            elif obj_type == "dict":
                # Force conversion to dict but preserve wrapped objects within
                if hasattr(data, "items"):
                    converted_data = {
                        k: lua_to_python_preserve_wrapped(v, null_sentinel)
                        for k, v in data.items()
                    }
                elif isinstance(data, dict):
                    converted_data = {
                        k: lua_to_python_preserve_wrapped(v, null_sentinel)
                        for k, v in data.items()
                    }
                else:
                    converted_data = {}
            else:
                # Unknown type, use regular conversion
                converted_data = lua_to_python_preserve_wrapped(data, null_sentinel)

            return {"__type": obj_type, "data": converted_data}

        # Check for null sentinel marker first
        if "__null_sentinel" in obj and obj["__null_sentinel"] is True:
            return None

        # Regular dict handling (no wrapper)
        keys = list(obj.keys())
        if not keys:
            # Empty dict - ambiguous, keep as dict
            return {}
        elif all(isinstance(k, int) and k > 0 for k in keys):
            min_k, max_k = min(keys), max(keys)
            if min_k == 1 and max_k == len(keys):
                # Convert to list in order
                return [
                    lua_to_python_preserve_wrapped(obj[k], null_sentinel)
                    for k in range(1, max_k + 1)
                ]
            else:
                # Non-consecutive keys, convert to list of values
                return [
                    lua_to_python_preserve_wrapped(v, null_sentinel)
                    for v in obj.values()
                ]
        else:
            # Regular dict with string/mixed keys
            return {
                k: lua_to_python_preserve_wrapped(v, null_sentinel)
                for k, v in obj.items()
            }
    elif hasattr(obj, "keys"):
        # It's a Lua table, convert to dict first
        table_dict = dict(obj)
        return lua_to_python_preserve_wrapped(table_dict, null_sentinel)
    else:
        return obj


def lua_to_python(obj, null_sentinel=None):
    """
    Convert Lua data structures to Python equivalents. Converts Lua 'null' tables
    back to Python None. Handles wrapped list/dict formats and converts Lua tables
    with consecutive integer keys starting at 1 to lists. Ambiguous empty tables
    default to empty dicts.
    """
    # Check for null sentinel - handle both identity and empty table cases
    if null_sentinel is not None and obj is null_sentinel:
        return None
    elif isinstance(obj, list):
        return [lua_to_python(x, null_sentinel) for x in obj]
    elif isinstance(obj, dict):
        # Check for special wrapped result marker first
        if "__wrapped_result" in obj and obj["__wrapped_result"] is True:
            # This is a wrapped result that should be preserved
            obj_type = obj["__type"]
            data = obj["data"]

            # Use the preserve-wrapped conversion for the data
            if obj_type == "list":
                # Force conversion to list, preserving wrapped objects
                if hasattr(data, "keys"):
                    # It's a Lua table, convert to Python list preserving wrapped
                    # objects
                    keys = list(data.keys())
                    if not keys:
                        converted_data = []
                    elif all(isinstance(k, int) and k > 0 for k in keys):
                        max_k = max(keys)
                        converted_data = [
                            lua_to_python_preserve_wrapped(
                                data[k] if k in keys else None, null_sentinel
                            )
                            for k in range(1, max_k + 1)
                        ]
                    else:
                        # Non-consecutive keys, convert to list of values
                        converted_data = [
                            lua_to_python_preserve_wrapped(v, null_sentinel)
                            for v in data.values()
                        ]
                elif isinstance(data, list):
                    # Preserve wrapped objects within the list
                    converted_data = []
                    for x in data:
                        # Check if this is a Lua table that represents a wrapped object
                        if hasattr(x, "keys"):
                            x_dict = dict(x)
                            if "__type" in x_dict and "data" in x_dict:
                                # This is a wrapped object, preserve the wrapped format
                                # exactly. Convert the data part directly without
                                # unwrapping the whole object.
                                inner_type = x_dict["__type"]
                                inner_data_lua = x_dict["data"]

                                # Convert the inner data preserving its structure
                                if inner_type == "list":
                                    # Force list conversion
                                    if hasattr(inner_data_lua, "keys"):
                                        keys = list(inner_data_lua.keys())
                                        if not keys:
                                            inner_data = []
                                        else:
                                            # Convert Lua table to list, preserving
                                            # wrapped objects
                                            inner_data = []
                                            for k in range(1, max(keys) + 1):
                                                if k in keys:
                                                    item = inner_data_lua[k]
                                                    # Check if this item is a
                                                    # wrapped object
                                                    if hasattr(item, "keys"):
                                                        item_dict = dict(item)
                                                        if (
                                                            "__type" in item_dict
                                                            and "data" in item_dict
                                                        ):
                                                            # Preserve wrapped object
                                                            item_type = item_dict[
                                                                "__type"
                                                            ]
                                                            item_data = lua_to_python(
                                                                item_dict["data"],
                                                                null_sentinel,
                                                            )
                                                            inner_data.append(
                                                                {
                                                                    "__type": item_type,
                                                                    "data": item_data,
                                                                }
                                                            )
                                                        else:
                                                            # Regular item
                                                            inner_data.append(
                                                                lua_to_python(
                                                                    item, null_sentinel
                                                                )
                                                            )
                                                    else:
                                                        # Regular item
                                                        inner_data.append(
                                                            lua_to_python(
                                                                item, null_sentinel
                                                            )
                                                        )
                                    else:
                                        inner_data = []
                                elif inner_type == "dict":
                                    # Force dict conversion
                                    if hasattr(inner_data_lua, "items"):
                                        inner_data = {
                                            k: lua_to_python(v, null_sentinel)
                                            for k, v in inner_data_lua.items()
                                        }
                                    else:
                                        inner_data = {}
                                else:
                                    inner_data = lua_to_python(
                                        inner_data_lua, null_sentinel
                                    )

                                converted_data.append(
                                    {"__type": inner_type, "data": inner_data}
                                )
                            else:
                                # Regular Lua table, convert normally
                                converted_data.append(lua_to_python(x, null_sentinel))
                        else:
                            # Not a table, convert normally
                            converted_data.append(lua_to_python(x, null_sentinel))
                else:
                    converted_data = []
            elif obj_type == "dict":
                # Force conversion to dict
                if hasattr(data, "items"):
                    converted_data = {
                        k: lua_to_python(v, null_sentinel) for k, v in data.items()
                    }
                elif isinstance(data, dict):
                    # Preserve wrapped objects within the dict
                    converted_data = {}
                    for k, v in data.items():
                        # Check if this is a Lua table that represents a wrapped object
                        if hasattr(v, "keys"):
                            v_dict = dict(v)
                            if "__type" in v_dict and "data" in v_dict:
                                # This is a wrapped object, preserve the wrapped format
                                # Use lua_to_python on the whole wrapped object which
                                # will unwrap it, but since we know it's supposed to be
                                # wrapped, re-wrap it
                                unwrapped_inner = lua_to_python(v, null_sentinel)
                                # Re-wrap it with the original type
                                converted_data[k] = {
                                    "__type": v_dict["__type"],
                                    "data": unwrapped_inner,
                                }
                            else:
                                # Regular Lua table, convert normally
                                converted_data[k] = lua_to_python(v, null_sentinel)
                        else:
                            # Not a table, convert normally
                            converted_data[k] = lua_to_python(v, null_sentinel)
                else:
                    converted_data = {}
            else:
                # Unknown type, use regular conversion
                converted_data = lua_to_python(data, null_sentinel)

            return {"__type": obj_type, "data": converted_data}
        # Check for null sentinel marker
        elif "__null_sentinel" in obj and obj["__null_sentinel"] is True:
            return None
        # Check for wrapped list/dict format
        elif "__type" in obj and "data" in obj:
            obj_type = obj["__type"]
            data = obj["data"]

            if obj_type == "list":
                # Force conversion to list regardless of structure
                if hasattr(data, "keys"):
                    # It's a Lua table, convert to Python list
                    keys = list(data.keys())
                    if not keys:
                        return []
                    elif all(isinstance(k, int) and k > 0 for k in keys):
                        max_k = max(keys)
                        return [
                            lua_to_python(data[k] if k in keys else None, null_sentinel)
                            for k in range(1, max_k + 1)
                        ]
                    else:
                        # Non-consecutive keys, convert to list of values
                        return [lua_to_python(v, null_sentinel) for v in data.values()]
                elif isinstance(data, list):
                    return [lua_to_python(x, null_sentinel) for x in data]
                else:
                    return []
            elif obj_type == "dict":
                # Force conversion to dict regardless of structure
                if hasattr(data, "items"):
                    return {k: lua_to_python(v, null_sentinel) for k, v in data.items()}
                elif isinstance(data, dict):
                    return {k: lua_to_python(v, null_sentinel) for k, v in data.items()}
                else:
                    return {}

        # Regular dict handling (no wrapper)
        keys = list(obj.keys())
        if not keys:
            # Empty dict could be either empty list or empty dict
            # We can't determine this from structure alone, so keep as dict
            # The caller should handle type conversion if needed
            return {}
        elif all(isinstance(k, int) and k > 0 for k in keys):
            min_k, max_k = min(keys), max(keys)
            if min_k == 1 and max_k == len(keys):
                # Convert to list in order
                return [
                    lua_to_python(obj[k], null_sentinel) for k in range(1, max_k + 1)
                ]
        # Otherwise, keep as dict
        return {k: lua_to_python(v, null_sentinel) for k, v in obj.items()}
    # Check for LuaTable objects
    elif "LuaTable" in type(obj).__name__:
        try:
            keys = list(obj.keys())
            # Check if this is a null sentinel by looking for the marker
            lua_dict = {k: obj[k] for k in keys}
            if "__null_sentinel" in lua_dict and lua_dict["__null_sentinel"] is True:
                return None
            # Convert to dict and recurse to handle potential wrapped formats
            return lua_to_python(lua_dict, null_sentinel)
        except Exception:
            return obj
    else:
        return obj


def evaluate_expression_preserve_wrapped(
    expression: str,
    item: Any,
    safe_mode: Optional[bool] = None,
    context: Optional[Dict] = None,
) -> Any:
    """
    Evaluate a Lua expression against an item, preserving wrapped objects.
    This version preserves list({})/dict({}) wrapped objects instead of unwrapping them.
    """
    try:
        lua_runtime = create_lua_runtime(safe_mode)
        # Set up context - always make dict keys available for direct access
        if isinstance(item, dict):
            for key, value in item.items():
                if (
                    isinstance(key, str)
                    and key.isidentifier()
                    and key not in ["and", "or", "not", "if", "then", "else", "end"]
                ):
                    lua_runtime.globals()[key] = python_to_lua(
                        value, lua_runtime
                    )  # type: ignore  # noqa

        # Set up additional context variables (may override dict keys)
        if context is not None:
            for k, v in context.items():
                lua_runtime.globals()[k] = python_to_lua(
                    v, lua_runtime
                )  # type: ignore  # noqa
        # Evaluate the expression
        try:
            result = lua_runtime.execute("return (" + expression + ")")
        except lupa.LuaError:
            result = lua_runtime.execute(expression)

        # Convert result back to Python, preserving wrapped objects
        null_sentinel = lua_runtime.eval("null")
        return lua_to_python_preserve_wrapped(result, null_sentinel)
    except Exception:
        # Fallback to regular expression evaluation on error
        return evaluate_expression(expression, item, safe_mode, context)


def evaluate_expression(
    expression: str,
    item: Any,
    safe_mode: Optional[bool] = None,
    context: Optional[Dict] = None,
) -> Any:
    """
    Evaluate a Lua expression against an item. No default parameter name is set -
    callers must specify parameter names via context. Dict keys are directly accessible.
    All None (JSON null) values are converted to 'null' table for consistent
    null checks.

    Args:
        expression: Lua expression to evaluate (can return any value)
        item: The data item to evaluate against (None values become 'null')
        safe_mode: If True, applies safety rails. If None, uses global SAFE_MODE
            setting.
        context: Dict of variables to set in the Lua context (e.g., {"item": item}).
            Required for parameter access in expressions.
    """
    try:
        lua_runtime = create_lua_runtime(safe_mode)
        # Set up context - always make dict keys available for direct access
        if isinstance(item, dict):
            for key, value in item.items():
                if (
                    isinstance(key, str)
                    and key.isidentifier()
                    and key not in ["and", "or", "not", "if", "then", "else", "end"]
                ):
                    lua_runtime.globals()[key] = python_to_lua(
                        value, lua_runtime
                    )  # type: ignore  # noqa

        # Set up additional context variables (may override dict keys)
        if context is not None:
            for k, v in context.items():
                lua_runtime.globals()[k] = python_to_lua(
                    v, lua_runtime
                )  # type: ignore  # noqa
        # Evaluate the expression
        try:
            result = lua_runtime.execute("return (" + expression + ")")
        except lupa.LuaError:
            result = lua_runtime.execute(expression)

        # Check if the result is a Lua function - if so, call it with the item
        if callable(result):
            try:
                # Check if this is one of our MCP tool functions
                is_mcp_tool = False
                try:
                    # Check if the function is one of our registered MCP tool wrappers
                    # by examining if it has the characteristic wrapper function
                    # structure
                    func_str = str(result)
                    # Our tool wrappers are created by create_tool_wrapper and have
                    # this signature
                    if "create_tool_wrapper" in func_str and "wrapper" in func_str:
                        is_mcp_tool = True
                except Exception:
                    pass

                if is_mcp_tool:
                    # For MCP tool functions, pass a table with wrap=True to ensure
                    # proper JSON serialization. Map the generic "item" to the correct
                    # parameter name based on tool type.
                    tool_name = getattr(result, "_mcp_tool_name", None)

                    if tool_name == "strings":
                        param_table = {
                            "text": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }
                    elif tool_name == "lists":
                        param_table = {
                            "items": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }
                    elif tool_name == "dicts":
                        param_table = {
                            "obj": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }
                    elif tool_name == "any_tool":
                        param_table = {
                            "value": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }
                    else:
                        # Fallback to generic "item" parameter
                        param_table = {
                            "item": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }

                    result = result(lua_runtime.table_from(param_table))
                else:
                    # For regular functions, call with the item as argument
                    result = result(python_to_lua(item, lua_runtime))
            except Exception:
                # If calling the function fails, return the original result
                pass

        # Convert Lua results back to Python
        null_sentinel = lua_runtime.eval("null")
        return lua_to_python(result, null_sentinel)
    except Exception:
        return None


def unwrap_result(result):
    """
    Unwraps the result from a tool call. The result from the client is typically a
    list containing a single Content object. This function extracts the text from
    that object and decodes it from JSON.
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
                    # Check if this value is an empty LuaTable (null
                    # sentinel)
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
                    # Check if this value is an empty LuaTable (null
                    # sentinel)
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
            # The text attribute contains the JSON string of the actual return
            # value.
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
            k: (_convert_lua_table(v) if type(v).__name__ == "LuaTable" else v)
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
