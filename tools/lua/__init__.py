from fastmcp import FastMCP
from typing import Any, Dict, List, Optional

# Import extracted tool functions
from .strings import strings_tool
from .lists import lists_tool
from .dicts import dicts_tool
from .any import any_tool as any_tool_impl
from .generate import generate_tool
from .chain import chain_tool


# Common Lua unwrapping functions
def unwrap_input(value):
    """
    Standard Lua unwrapping - preserves empty dicts as empty dicts.
    """
    from lib.lua import _unwrap_input

    return _unwrap_input(value)


def unwrap_list_input(value):
    """
    Lua unwrapping for list parameters - converts empty dicts to empty lists.
    Used when we know the input should be a list and want to handle
    empty Lua tables {} as empty lists.
    """
    unwrapped = unwrap_input(value)

    # Handle empty dict as empty list (for empty Lua tables in list contexts)
    if isinstance(unwrapped, dict) and len(unwrapped) == 0:
        return []

    return unwrapped


# MCP Parameter Description Monkey Patch
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


def apply_param_descriptions_patch():
    """Apply the parameter descriptions patch to FastMCP"""
    try:
        from fastmcp.tools.tool import ParsedFunction

        # Only store the original if not already stored
        if not hasattr(apply_param_descriptions_patch, "_original_from_function"):
            apply_param_descriptions_patch._original_from_function = (
                ParsedFunction.from_function
            )

        def patched_from_function(fn, exclude_args=None, validate=True):
            parsed = apply_param_descriptions_patch._original_from_function(
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


def register_lua_tools(mcp: FastMCP):
    """Register all Lua-based tools with the MCP server"""
    apply_param_descriptions_patch()

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
            - 'capitalize': Capitalizes the first character
              (e.g., 'foo bar' → 'Foo bar').
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
            - 'template': Interpolates variables using {var} syntax
              (requires data dict).
            - 'trim': Removes leading and trailing whitespace.
            - 'upper_case': Converts to uppercase (e.g., 'Hello' → 'HELLO').
            - 'xor': String-specific XOR operation (param: str).

        Returns:
            dict: The result, always wrapped in a dictionary with a 'value' key
                containing
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

        In Lua, an empty table represents an empty dict **OR** an empty list.
        Lever tools
        serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
        dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
        {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
        serialization. Use unwrap(o) to get the original table.
        """
        return strings_tool(text, operation, param, data)

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
            - 'key_by': Create dict keyed by expression result
              (expression: Lua expression)
            - 'last': Last element
            - 'map': Apply a Lua expression to each item (expression: Lua expression)
            - 'max': Find maximum value in list
            - 'max_by': Find item with maximum property value
              (expression: Lua expression)
            - 'min': Find minimum value in list
            - 'min_by': Find item with minimum property value
              (expression: Lua expression)
            - 'nth': Get nth element (param: int, supports negative indexing)
            - 'partition': Split by expression result/boolean
              (expression: Lua expression)
            - 'pluck': Extract values by expression (expression: Lua expression)
            - 'random_except': Random item excluding condition
              (expression: Lua expression)
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
            - 'uniq_by': Remove duplicates by expression result
              (expression: Lua expression)
            - 'unzip_list': Unzip list of lists
            - 'xor': Symmetric difference
            - 'zip_lists': Zip multiple lists
            - 'zip_with': Combine two lists element-wise using a binary
              Lua expression
              (requires others: list, expression: Lua expression using
              'item' and 'other')

        Returns:
            dict: Result with 'value' key containing a list (most operations),
                single value
                ('head', 'last', 'nth', 'sample', 'max', 'min', etc.), dict ('group_by',
                'key_by'), string ('join'), or boolean
                ('is_empty', 'is_equal', 'contains').
                On error, includes 'error' key.

        Expression Examples:
            - Filtering: 'age > 25', 'score >= 80', 'name == 'Alice''
            - Grouping: 'age >= 30 and 'senior' or 'junior''
            - Sorting: 'age * -1' (reverse age), 'string.lower(name)' (case-insensitive)
            - Extraction: 'string.upper(name)', 'age > 18 and name or 'minor''
            - Math: 'math.abs(score - 50)', 'x*x + y*y' (distance squared)
            - Functional programming: Use tool functions as expressions
              (e.g.,
              `lists.map(items, 'strings.upper_case')`).

        In Lua expressions, item refers to the current list element, index
        (1-based) refers
        to the current position, and items refers to the full list. For
        zip_with, item
        refers to the current element from the first list and other refers to the
        current
        element from the second list. Available in expressions: math.*,
        string.*,
        os.time/date/clock, type(), tonumber(), tostring(). Dictionary keys
        accessible
        directly (age, name, etc.) or via item.key. You may pass a single Lua
        expression or
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
                {items={{age=30}, {age=20}},
                 expression='age >= 25 and "adult" or "young"'}
            )  # => {'adult': [{age=30}], 'young': [{age=20}]}
            lists.difference({items={1, 2, 3}, others={2, 3}, wrap=true})
              # => JSON: [1], Lua: {'__type': 'list', 'data': {1}}

        In Lua, an empty table represents an empty dict **OR** an empty list.
        Lever tools
        serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
        dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
        {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
        serialization. Use unwrap(o) to get the original table.
        """
        return lists_tool(items, operation, param, others, expression)

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
        Performs dictionary operations, including merge, set/get value, and
        property checks.

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
            - Functional programming: Use tool functions as expressions
              (e.g.,
              `lists.map(items, 'strings.upper_case')`).

        In Lua expressions for map_keys: key (current key string), value
        (current value),
        obj (original dict). For map_values: value (current value), key
        (current key
        string), obj (original dict). For map_values, if value is a dict,
        its
        properties are
        also accessible directly (age, name, etc.). Available in
        expressions:
        math.*,
        string.*, os.time/date/clock, type(), tonumber(), tostring().
        You may pass a single
        Lua expression or a block of Lua code. For multi-line code, use
        return to specify
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
                {obj={user={profile={name='bob'}}},
                 path='user.profile.name'}
            )  # => 'bob'
            dicts.pick(
                {obj={id=1, name='alice',
                      email='alice@test.com'},
                 param={'id', 'name'}}
            )  # => {'id': 1, 'name': 'alice'}
            dicts.omit({obj={password='secret', name='alice', age=30},
                        param={'password'}})
              # => {'name': 'alice', 'age': 30}
            dicts.merge({obj={{config={debug=true}}, {config={port=8080}}}, wrap=true})
              # => JSON: {'config': {'port': 8080}},
                Lua: {'__type': 'dict', 'data': {...}}

        In Lua, an empty table represents an empty dict **OR** an empty list.
        Lever tools
        serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
        dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
        {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
        serialization. Use unwrap(o) to get the original table.
        """
        return dicts_tool(obj, operation, param, path, value, default, expression)

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
            - 'is_equal': Checks if two values are deeply equal
              (param: value to compare)
            - 'is_nil': Checks if the value is None
            - 'size': Gets the size/length of any collection type
              (strings, lists, dicts)
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
            - Functional programming: Use tool functions as expressions
              (e.g.,
              `lists.map(items, 'strings.upper_case')`).

        In Lua expressions, value refers to the input value being evaluated.
        Available in
        expressions: math.*, string.*, os.time/date/clock, type(), tonumber(),
        tostring().
        Dictionary keys accessible directly (age, name, etc.) or via value.key.
        You may pass
        a single Lua expression or a block of Lua code. For multi-line code, use
        return to
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

        In Lua, an empty table represents an empty dict **OR** an empty list.
        Lever tools
        serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
        dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
        {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
        serialization. Use unwrap(o) to get the original table.
        """
        return any_tool_impl(value, operation, param, expression)

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
            - 'zip_with_index': Tuples of (index, value). options:
              {'items': list}

        Returns:
            dict: Result with 'value' key containing a list
                (all operations return lists).
                On error, includes 'error' key.

        MCP Usage Examples:
            generate({'from': 0, 'to': 5}, 'range')
              # => {'value': [0, 1, 2, 3, 4]}
            generate({'value': 'x', 'count': 3}, 'repeat')
              # => {'value': ['x', 'x', 'x']}
            generate({'items': [1, 2, 3]}, 'powerset')
              # => {'value': [[], [1], [2], [1, 2], [3], [1, 3], [2, 3],
                [1, 2, 3]]}
            generate({'lists': [[1, 2], ['a', 'b']]}, 'cartesian_product')
              # => {'value': [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]}

        Lua Function Call Examples:
            generate.range({from=0, to=5})  # => {0, 1, 2, 3, 4}
            generate['repeat']({value='x', count=3})  # => {'x', 'x', 'x'}
            generate.cartesian_product({lists={{1, 2}, {'a', 'b'}}})
              # => {{1, 'a'}, {1, 'b'}, {2, 'a'}, {2, 'b'}}
            generate.combinations({items={1, 2}, length=2, wrap=true})
              # => JSON: [[1, 2]], Lua: {'__type': 'list', 'data': [[1, 2]]}

        In Lua, an empty table represents an empty dict **OR** an empty list.
        Lever tools
        serialize an empty Lua table to JSON as an empty dict/object ({}). Use list(t),
        dict(t), or pass wrap=true to Lua tool calls to get wrapped lists and dicts:
        {'__type'= '{list|dict}', 'data'=t}. This format ensures proper JSON
        serialization. Use unwrap(o) to get the original table.
        """
        return generate_tool(options, operation)

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
            The output from one tool is always used as the input to the next
                tool's primary
                parameter.
            You must not specify the primary parameter in params for any tool
                in the chain.

        Lua Function Call Examples:
            -- Note: chain is not exposed as a Lua function since it
            -- operates on tool calls
            -- Use direct tool function calls instead:
            local result = lists.sort_by(
                lists.compact(lists.flatten_deep({1, {2, {3, 4}, 5}}))
            )
            -- => [1, 2, 3, 4, 5]
        """
        return await chain_tool(input, tool_calls, mcp)
