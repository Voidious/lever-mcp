import unicodedata
import re
from fastmcp import FastMCP
from typing import Any, Dict, List, Optional
import inspect
import json
import random

# --- MCP Server Setup ---


class LeverMCP(FastMCP):
    pass


mcp = LeverMCP("Lever MCP")


@mcp.tool()
def mutate_string(text: str, mutation: str, data: Dict[str, Any] = {}) -> str:
    """
    Mutates a string according to the specified mutation type.

    Parameters:
        text (str): The input string to mutate.
        mutation (str): The type of mutation to perform. One of:
            - 'camel_case': Converts the string to camelCase (e.g.,
              'foo bar' → 'fooBar').
            - 'capitalize': Converts the first character to upper case and the rest to
              lower case (e.g., 'foo bar' → 'Foo bar').
            - 'deburr': Removes accents/diacritics from the string (e.g.,
              'Café' → 'Cafe').
            - 'kebab_case': Converts the string to kebab-case (e.g.,
              'foo bar' → 'foo-bar').
            - 'lower_case': Converts the string to all lowercase (e.g.,
              'Hello' → 'hello').
            - 'replace': Replaces all occurrences of a substring with another (requires
              data={'old': 'x', 'new': 'y'}). (e.g., 'foo bar foo',
              data={'old': 'foo', 'new': 'baz'} → 'baz bar baz')
            - 'reverse': Reverses the string (e.g., 'hello' → 'olleh').
            - 'snake_case': Converts the string to snake_case (e.g.,
              'foo bar' → 'foo_bar').
            - 'upper_case': Converts the string to all uppercase (e.g.,
              'Hello' → 'HELLO').
            - 'template': Interpolates variables in the string using {var} syntax.
              Requires 'data' dict (e.g., 'Hello, {name}!' with
              data={'name': 'World'} → 'Hello, World!').
            - 'trim': Removes leading and trailing whitespace (e.g., '
              hello  ' → 'hello').
        data (Dict[str, Any], optional): Data for 'template' and 'replace' mutations.

    Returns:
        str: The mutated string.

    Usage Example:
        mutate_string('foo bar', 'camel_case')  # => 'fooBar'
        mutate_string(
            'Hello, {name}!', 'template', {'name': 'World'}
        )  # => 'Hello, World!'
        mutate_string(
            'foo bar foo', 'replace', {'old': 'foo', 'new': 'baz'
        })  # => 'baz bar baz'
    """
    if mutation == "deburr":
        return "".join(
            c
            for c in unicodedata.normalize("NFKD", text)
            if not unicodedata.combining(c)
        )
    elif mutation == "template":
        if not data:
            raise ValueError("'data' argument is required for 'template' mutation.")

        def replacer(match):
            key = match.group(1)
            return str(data.get(key, match.group(0)))

        return re.sub(r"\{(\w+)\}", replacer, text)
    elif mutation == "camel_case":
        s = re.sub(r"(_|-)+", " ", text).title().replace(" ", "")
        return s[0].lower() + s[1:] if s else ""
    elif mutation == "kebab_case":
        s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
        return re.sub(r"(\s|_|-)+", "-", s).lower().strip("-_")
    elif mutation == "snake_case":
        s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
        return re.sub(r"(\s|-)+", "_", s).lower().strip("-_")
    elif mutation == "capitalize":
        return text.capitalize()
    elif mutation == "reverse":
        return text[::-1]
    elif mutation == "trim":
        return text.strip()
    elif mutation == "lower_case":
        return text.lower()
    elif mutation == "upper_case":
        return text.upper()
    elif mutation == "replace":
        if not data or "old" not in data or "new" not in data:
            raise ValueError(
                "'data' with 'old' and 'new' is required for 'replace' mutation."
            )
        return text.replace(data["old"], data["new"])
    else:
        raise ValueError(f"Unknown mutation type: {mutation}")


@mcp.tool()
def mutate_list(
    items: List[Any],
    mutation: str,
    param: Any = None,
) -> List[Any]:
    """
    Mutates a list according to the specified mutation type.

    Parameters:
        items (List[Any]): The input list to mutate.
        mutation (str): The type of mutation to perform. One of:
            - 'chunk': Splits a list into chunks of a given size (param: int).
            - 'compact': Removes falsy values from a list.
            - 'drop': Drops n elements from the beginning (param: int).
            - 'drop_right': Drops n elements from the end (param: int).
            - 'flatten': Flattens a list one level deep.
            - 'flatten_deep': Flattens a nested list completely.
            - 'initial': Gets all but the last element.
            - 'partition': Splits a list into two lists based on a predicate key
              (param: str).
            - 'pluck': Extracts a list of values for a given key (param: str).
            - 'remove_by': Removes items where a property matches a value (param:
              {'key': str, 'value': Any}).
            - 'sample_size': Gets n random elements from the list (param: int).
            - 'shuffle': Shuffles the list.
            - 'sort_by': Sorts a list of objects by a key (param: str).
            - 'tail': Gets all but the first element.
            - 'take': Takes n elements from the beginning (param: int).
            - 'take_right': Takes n elements from the end (param: int).
            - 'union': Creates a list of unique values from all given lists.
            - 'uniq_by': Removes duplicates from a list of objects based on a key
              (param: str).
            - 'unzip_list': Unzips a list of tuples into separate lists.
            - 'xor': Creates a list of unique values that is the symmetric difference of
              the given lists.
            - 'zip_lists': Zips multiple lists into a list of tuples.
        param (Any, optional): A parameter for mutations that require one.

    Returns:
        List[Any]: The mutated list.

    Usage Example:
        mutate_list([[1, [2, 3], 4], 5], 'flatten_deep')  # => [1, 2, 3, 4, 5]
        mutate_list(
            [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}], 'pluck', 'name'
        )  # => ['Alice', 'Bob']
    """
    if mutation == "flatten_deep":
        result = []

        def _flatten(lst):
            for i in lst:
                if isinstance(i, list):
                    _flatten(i)
                else:
                    result.append(i)

        _flatten(items)
        return result
    elif mutation == "sort_by":

        def get_sort_key(x):
            v = x.get(param, "") if isinstance(x, dict) else getattr(x, param, "")
            if isinstance(v, dict):
                return json.dumps(v, sort_keys=True)
            return v

        return sorted(items, key=get_sort_key)
    elif mutation == "uniq_by":
        seen = set()
        result = []
        for item in items:
            k = (
                item.get(param)
                if isinstance(item, dict)
                else getattr(item, param, None)
            )
            if isinstance(k, dict):
                k_hash = json.dumps(k, sort_keys=True)
            else:
                k_hash = k
            if k_hash not in seen:
                seen.add(k_hash)
                result.append(item)
        return result
    elif mutation == "partition":
        trues, falses = [], []
        for item in items:
            result = (
                item.get(param)
                if isinstance(item, dict)
                else getattr(item, param, False)
            )
            (trues if result else falses).append(item)
        return [trues, falses]
    elif mutation == "pluck":
        return [
            item.get(param) if isinstance(item, dict) else getattr(item, param, None)
            for item in items
        ]
    elif mutation == "compact":
        return [item for item in items if item]
    elif mutation == "chunk":
        size = int(param)
        return [items[i : i + size] for i in range(0, len(items), size)]
    elif mutation == "zip_lists":
        return [list(t) for t in zip(*items)]
    elif mutation == "unzip_list":
        return [list(t) for t in zip(*items)]
    elif mutation == "remove_by":
        key = param["key"]
        value = param["value"]
        return [
            item
            for item in items
            if (item.get(key) if isinstance(item, dict) else getattr(item, key, None))
            != value
        ]
    elif mutation == "tail":
        return items[1:] if len(items) > 1 else []
    elif mutation == "initial":
        return items[:-1] if items else []
    elif mutation == "drop":
        return items[int(param) :]
    elif mutation == "drop_right":
        return items[: -int(param)] if int(param) > 0 else items[:]
    elif mutation == "take":
        return items[: int(param)]
    elif mutation == "take_right":
        return items[-int(param) :] if int(param) > 0 else []
    elif mutation == "flatten":
        return [item for sublist in items for item in sublist]
    elif mutation == "union":
        result = []
        seen = set()
        for sublist in items:
            for item in sublist:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
        return result
    elif mutation == "xor":
        counts = {}
        for sublist in items:
            for item in sublist:
                counts[item] = counts.get(item, 0) + 1
        return [item for item, count in counts.items() if count == 1]
    elif mutation == "shuffle":
        result = list(items)
        random.shuffle(result)
        return result
    elif mutation == "sample_size":
        return random.sample(items, min(int(param), len(items)))
    else:
        raise ValueError(f"Unknown mutation type: {mutation}")


@mcp.tool()
def has_property(obj: Any, property: str, param: Optional[Any] = None) -> bool:
    """
    Checks a property or relationship for the given object.

    Parameters:
        obj (Any): The object or value to check.
        property (str): The property or operation to check. One of:
            - 'contains': Checks if a string contains a substring or a list contains an
              element (param: value to check).
            - 'ends_with': Checks if a string ends with the given target (param: str).
            - 'has_key': Checks if a dict has a given key (param: str).
            - 'is_alpha': Checks if a string consists only of alphabetic characters.
            - 'is_digit': Checks if a string consists only of digits.
            - 'is_empty': Checks if the value is empty.
            - 'is_equal': Checks if two values are deeply equal (param: value to
              compare).
            - 'is_lower': Checks if a string is all lowercase.
            - 'is_nil': Checks if the value is None.
            - 'is_upper': Checks if a string is all uppercase.
            - 'starts_with': Checks if a string starts with the given target
              (param: str).
        param (Any, optional): The parameter for the operation, if required.

    Returns:
        bool: The result of the check.

    Usage Example:
        has_property('abc', 'ends_with', 'c')  # => True
        has_property({'a': 1}, 'has_key', 'a')  # => True
        has_property('12345', 'is_digit')  # => True
    """
    if property == "starts_with":
        if not isinstance(obj, str) or param is None:
            return False
        return obj.startswith(param)
    elif property == "ends_with":
        if not isinstance(obj, str) or param is None:
            return False
        return obj.endswith(param)
    elif property == "is_empty":
        if hasattr(obj, "__len__"):
            return len(obj) == 0
        return not bool(obj)
    elif property == "is_equal":
        return obj == param
    elif property == "is_nil":
        return obj is None
    elif property == "has_key":
        if not isinstance(obj, dict) or param is None:
            return False
        return param in obj
    elif property == "contains":
        if isinstance(obj, str) and param is not None:
            return param in obj
        elif isinstance(obj, list) and param is not None:
            return param in obj
        return False
    elif property == "is_digit":
        return isinstance(obj, str) and obj.isdigit()
    elif property == "is_alpha":
        return isinstance(obj, str) and obj.isalpha()
    elif property == "is_upper":
        return isinstance(obj, str) and obj.isupper()
    elif property == "is_lower":
        return isinstance(obj, str) and obj.islower()
    else:
        raise ValueError(f"Unknown property: {property}")


@mcp.tool()
def select_from_list(items: list, operation: str, param: Optional[Any] = None) -> Any:
    """
    Selects an element from a list using various operations.

    Parameters:
        items (list): The list to select from.
        operation (str): The operation to perform. One of:
            - 'find_by': Finds the first item where a property matches a value (param:
              {'key': str, 'value': Any}).
            - 'head': Gets the first element.
            - 'index_of': Returns the index of the first item where a property matches a
              value (param: {'key': str, 'value': Any}), or -1 if not found.
            - 'last': Gets the last element.
            - 'max_by': Gets the item with the maximum value for a property (param:
              property name).
            - 'min_by': Gets the item with the minimum value for a property (param:
              property name).
            - 'nth': Gets the nth element (param: integer index, supports negative for
              reverse).
            - 'random_except': Returns a random element from the list, excluding any
              that match a given property value (param: {'key': str, 'value': Any}).
            - 'sample': Gets a random element.
        param (Any, optional): Parameter for the operation (required for some
            operations).

    Returns:
        Any: The selected element or None if not found.

    Usage Example:
        select_from_list([1, 2, 3], 'head')  # => 1
        select_from_list([10, 20, 30], 'nth', 1)  # => 20
        select_from_list([{'id': 1}, {'id': 2}], 'find_by', {'key': 'id', 'value': 2})
        # => {'id': 2}
    """
    if operation == "find_by":
        if not param or "key" not in param or "value" not in param:
            raise ValueError(
                "'param' with 'key' and 'value' is required for 'find_by'."
            )
        key = param["key"]
        value = param["value"]
        for item in items:
            v = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
            if v == value:
                return item
        return None
    elif operation == "head":
        return items[0] if items else None
    elif operation == "last":
        return items[-1] if items else None
    elif operation == "sample":
        if not items:
            return None
        import random

        return random.choice(items)
    elif operation == "nth":
        if not isinstance(param, int):
            raise ValueError("'param' must be an integer for 'nth'.")
        if not items:
            return None
        idx = param
        if -len(items) <= idx < len(items):
            return items[idx]
        return None
    elif operation == "min_by":
        if not items or not param:
            return None
        key = param

        def min_key(x):
            v = x.get(key) if isinstance(x, dict) else getattr(x, key, None)
            return v if v is not None else float("inf")

        return min(items, key=min_key)
    elif operation == "max_by":
        if not items or not param:
            return None
        key = param

        def max_key(x):
            v = x.get(key) if isinstance(x, dict) else getattr(x, key, None)
            return v if v is not None else float("-inf")

        return max(items, key=max_key)
    elif operation == "index_of":
        if not param or "key" not in param or "value" not in param:
            raise ValueError(
                "'param' with 'key' and 'value' is required for 'index_of'."
            )
        key = param["key"]
        value = param["value"]
        for idx, item in enumerate(items):
            v = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
            if v == value:
                return idx
        return -1
    elif operation == "random_except":
        if not items or not param or "key" not in param or "value" not in param:
            return None
        key = param["key"]
        value = param["value"]
        filtered = [
            item
            for item in items
            if (item.get(key) if isinstance(item, dict) else getattr(item, key, None))
            != value
        ]
        if not filtered:
            return None
        import random

        return random.choice(filtered)
    else:
        raise ValueError(f"Unknown operation: {operation}")


@mcp.tool()
def compare_lists(a: list, b: list, operation: str, key: Optional[str] = None) -> list:
    """
    Compares two lists using various set-like operations.

    Parameters:
        a (list): The first list.
        b (list): The second list.
        operation (str): The operation to perform. One of:
            - 'difference': Values in a not in b (ignores key).
            - 'difference_by': Items in a not in b by property (requires key).
            - 'intersection': Unique values in both lists (ignores key).
            - 'intersection_by': Items in a also in b by property (requires key).
        key (str, optional): The property name for *_by operations.

    Returns:
        list: The result of the comparison.

    Usage Example:
        compare_lists([1, 2, 3], [2, 4], 'difference')  # => [1, 3]
        compare_lists(
            [{'id': 1}, {'id': 2}, {'id': 3}], [{'id': 2}], 'difference_by', 'id'
        )  # => [{'id': 1}, {'id': 3}]
    """
    if operation == "difference_by":
        if key is None:
            raise ValueError("'key' is required for 'difference_by'.")
        b_keys = set(
            item.get(key) if isinstance(item, dict) else getattr(item, key, None)
            for item in b
        )
        return [
            item
            for item in a
            if (item.get(key) if isinstance(item, dict) else getattr(item, key, None))
            not in b_keys
        ]
    elif operation == "intersection_by":
        if key is None:
            raise ValueError("'key' is required for 'intersection_by'.")
        b_keys = set(
            item.get(key) if isinstance(item, dict) else getattr(item, key, None)
            for item in b
        )
        return [
            item
            for item in a
            if (item.get(key) if isinstance(item, dict) else getattr(item, key, None))
            in b_keys
        ]
    elif operation == "intersection":
        return list(set(a) & set(b))
    elif operation == "difference":
        return [item for item in a if item not in b]
    else:
        raise ValueError(f"Unknown operation: {operation}")


@mcp.tool()
def process_list(items: list, operation: str, key: str) -> dict:
    """
    Processes a list into a dictionary using grouping, counting, or keying by a
    property.

    Parameters:
        items (list): The list of items (dicts or objects).
        operation (str): The operation to perform. One of:
            - 'count_by': Counts occurrences of property values.
            - 'group_by': Groups items by a property value.
            - 'key_by': Creates a dictionary with keys from a property.
        key (str): The property name to use.

    Returns:
        dict: The resulting dictionary.

    Usage Example:
        process_list(
            [{'type': 'a'}, {'type': 'b'}, {'type': 'a'}], 'count_by', 'type'
        )  # => {'a': 2, 'b': 1}
        process_list(
            [
                {'type': 'fruit', 'name': 'apple'},
                {'type': 'fruit', 'name': 'banana'},
                {'type': 'vegetable', 'name': 'carrot'}
            ],
            'group_by',
            'type'
        )  # => {'fruit': [...], 'vegetable': [...]}
        process_list(
            [{'id': 'a', 'val': 1}, {'id': 'b', 'val': 2}], 'key_by', 'id'
        )  # => {'a': {...}, 'b': {...}}
    """
    if operation == "group_by":
        result = {}
        for item in items:
            k = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
            result.setdefault(k, []).append(item)
        return result
    elif operation == "count_by":
        result = {}
        for item in items:
            k = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
            result[k] = result.get(k, 0) + 1
        return result
    elif operation == "key_by":
        return {item[key]: item for item in items}
    else:
        raise ValueError(f"Unknown operation: {operation}")


@mcp.tool()
def process_dict(obj: dict, operation: str, param: Optional[list] = None) -> dict:
    """
    Performs dictionary operations.

    Parameters:
        obj (dict): The source dictionary.
        operation (str): The operation to perform. One of:
            - 'invert': Swaps keys and values.
            - 'omit': Omits specified keys (param: list of keys).
            - 'pick': Picks specified keys (param: list of keys).
        param (list, optional): Keys to pick or omit (required for 'pick' and 'omit').

    Returns:
        dict: The resulting dictionary.

    Usage Example:
        process_dict({'a': 'x', 'b': 'y'}, 'invert')  # => {'x': 'a', 'y': 'b'}
        process_dict({'a': 1, 'b': 2}, 'omit', ['a'])  # => {'b': 2}
        process_dict({'a': 1, 'b': 2}, 'pick', ['a'])  # => {'a': 1}
    """
    if operation == "invert":
        return {str(value): key for key, value in obj.items()}
    elif operation == "pick":
        if param is None:
            raise ValueError("'param' (list of keys) is required for 'pick' operation.")
        return {key: obj[key] for key in param if key in obj}
    elif operation == "omit":
        if param is None:
            raise ValueError("'param' (list of keys) is required for 'omit' operation.")
        return {key: value for key, value in obj.items() if key not in param}
    else:
        raise ValueError(f"Unknown operation: {operation}")


@mcp.tool()
def generate(input: Any, operation: str, param: Any = None) -> Any:
    """
    Generates sequences or derived data from input using the specified operation.

    Parameters:
        input (Any): The input list or value.
        operation (str): The operation to perform. One of:
            - 'accumulate': Running totals (or with a binary function if param is
              provided). param: None or a supported function name (e.g., 'mul')
            - 'cartesian_product': Cartesian product of multiple input lists.
              param: None
            - 'combinations': All combinations of a given length (param: int, required)
            - 'cycle': Repeat the sequence infinitely or up to param times.
              param: int (max length, optional)
            - 'permutations': All permutations of a given length (param: int, optional,
              default=len(input))
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
        Any: The generated sequence or result.

    Usage Example:
        generate(None, 'range', [0, 5])  # => [0, 1, 2, 3, 4]
        generate('x', 'repeat', 3)  # => ['x', 'x', 'x']
        generate([1, 2, 3], 'powerset')
        # => [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
        generate([[1, 2], ['a', 'b']], 'cartesian_product')
        # => [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
    """
    import itertools
    import operator

    if operation == "range":
        # param: [start, end, step?]
        if not isinstance(param, list) or len(param) < 2:
            raise ValueError(
                "'param' must be [start, end] or [start, end, step] for 'range'."
            )
        start, end = param[0], param[1]
        step = param[2] if len(param) > 2 else 1
        return list(range(start, end, step))
    elif operation == "cartesian_product":
        # input: list of lists
        return list(itertools.product(*input))
    elif operation == "repeat":
        # input: value or list, param: int
        if not isinstance(param, int):
            raise ValueError("'param' must be an integer for 'repeat'.")
        return list(itertools.repeat(input, param))
    elif operation == "powerset":
        s = list(input)
        if not s:
            # Workaround for fastmcp bug that converts [[]] to []
            return [[""]]
        return [
            list(combo)
            for r in range(len(s) + 1)
            for combo in itertools.combinations(s, r)
        ]
    elif operation == "windowed":
        # input: list, param: int (window size)
        if not isinstance(param, int) or param < 1:
            raise ValueError("'param' must be a positive integer for 'windowed'.")
        s = list(input)
        return [tuple(s[i : i + param]) for i in range(len(s) - param + 1)]
    elif operation == "cycle":
        # input: list, param: int (max length, optional)
        s = list(input)
        if param is not None:
            return [x for _, x in zip(range(param), itertools.cycle(s))]
        else:
            raise ValueError("'cycle' without a length limit is not supported.")
    elif operation == "accumulate":
        # input: list, param: None or function name
        s = list(input)
        if param is None:
            return list(itertools.accumulate(s))
        elif param == "mul":
            return list(itertools.accumulate(s, operator.mul))
        else:
            raise ValueError("'accumulate' only supports param=None or 'mul'.")
    elif operation == "zip_with_index":
        # input: list
        return list(enumerate(input))
    elif operation == "unique_pairs":
        # input: list
        s = list(input)
        return [tuple(pair) for pair in itertools.combinations(s, 2)]
    elif operation == "permutations":
        s = list(input)
        r = param if isinstance(param, int) else None
        if not s:
            if r is None or r == 0:
                # Workaround for fastmcp bug that converts [[]] to []
                return [[""]]
            else:
                return []
        return [list(p) for p in itertools.permutations(s, r)]
    elif operation == "combinations":
        s = list(input)
        if not isinstance(param, int):
            raise ValueError("'param' must be an integer for 'combinations'.")
        # Special case: combinations([], n) is [] for n > 0
        if not s:
            return []
        return [list(c) for c in itertools.combinations(s, param)]
    else:
        raise ValueError(f"Unknown operation: {operation}")


@mcp.tool()
async def chain(input: Any, tool_calls: List[Dict[str, Any]]) -> Any:
    """
    Chains multiple tool calls, piping the output of one as the input to the next.

    Parameters:
        input (Any): The initial input to the chain.
        tool_calls (List[Dict[str, Any]]): Each dict must have:
            - 'tool': the tool name (str)
            - 'params': dict of additional parameters (optional, default empty)

    Returns:
        Any: The result of the last tool in the chain, or a descriptive error message
        if a tool is missing, incompatible, or if the primary parameter is specified in
        params.

    Chaining Rule:
        The output from one tool is always used as the input to the next tool's primary
        parameter. You must not specify the primary parameter in params for any tool in
        the chain.

    Usage Example:
        chain(
            [1, [2, [3, 4], 5]],
            [
                {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}},
                {"tool": "mutate_list", "params": {"mutation": "compact"}},
                {
                    "tool": "mutate_list",
                    "params": {"mutation": "sort_by", "param": None}
                }
            ]
        )
        # => [1, 2, 3, 4, 5]
    """
    value = input
    for i, step in enumerate(tool_calls):
        tool_name = step.get("tool")
        params = step.get("params", {})
        if not tool_name:
            return {"error": f"Step {i}: Missing 'tool' name."}

        # Get the tool (it may be a coroutine)
        try:
            tool_or_coro = mcp._tool_manager.get_tool(tool_name)
            if inspect.isawaitable(tool_or_coro):
                tool = await tool_or_coro
            else:
                tool = tool_or_coro
        except Exception as e:
            return {"error": f"Step {i}: Tool '{tool_name}' not found: {e}"}

        # Now 'tool' is always the resolved object, safe to access attributes
        if not hasattr(tool, "run") or not callable(getattr(tool, "run", None)):
            return {
                "error": f"Step {i}: Tool '{tool_name}' is not a valid tool object."
            }

        param_schema = tool.parameters.get("properties", {})
        required = tool.parameters.get("required", [])

        # Find the first required param not in params, or just the first param
        primary_param = None
        for k in required:
            primary_param = k
            break
        if not primary_param and param_schema:
            for k in param_schema:
                primary_param = k
                break
        arguments = dict(params)
        if primary_param:
            if primary_param in arguments:
                return {
                    "error": f"Step {i}: Chaining does not allow specifying the "
                    f"primary parameter '{primary_param}' in params. The output from "
                    "the previous tool is always used as input."
                }
            arguments[primary_param] = value
        elif len(param_schema) == 1:
            only_param = next(iter(param_schema))
            if only_param in arguments:
                return {
                    "error": f"Step {i}: Chaining does not allow specifying the "
                    f"primary parameter '{only_param}' in params. The output from the "
                    "previous tool is always used as input."
                }
            arguments[only_param] = value
        elif not param_schema:
            arguments = {}
        # Call the tool's run method (must be awaited)
        try:
            result = await tool.run(arguments)
        except Exception as e:
            return {"error": f"Step {i}: Error calling tool '{tool_name}': {e}"}
        value = unwrap_result(result)
    return value


def unwrap_result(result):
    import json

    # If result is a list of content objects, extract their values
    if isinstance(result, list) and result:
        if all(hasattr(x, "text") for x in result):
            values = []
            for content in result:
                if hasattr(content, "text"):
                    try:
                        values.append(json.loads(content.text))  # type: ignore[attr-defined]  # noqa
                    except Exception:
                        values.append(content.text)  # type: ignore[attr-defined]
                else:
                    values.append(content)
            return values if len(values) > 1 else values[0]
    # If result is a single content object
    if hasattr(result, "text"):
        try:
            return json.loads(result.text)  # type: ignore[attr-defined]
        except Exception:
            return result.text  # type: ignore[attr-defined]
    # Otherwise, return as is
    return result


@mcp.tool()
def merge(dicts: list) -> dict:
    """
    Deep merges a list of dictionaries.

    Parameters:
        dicts (List[Dict[Any, Any]]): A list of dictionaries to merge.

    Returns:
        Dict[Any, Any]: A single dictionary containing the merged keys and values.

    Usage Example:
        merge([{"a": 1, "b": {"c": 2}}, {"b": {"d": 3}}])
        # => {'a': 1, 'b': {'c': 2, 'd': 3}}
    """
    import copy

    def deep_merge(a, b):
        for k, v in b.items():
            if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                a[k] = deep_merge(a[k], v)
            else:
                a[k] = copy.deepcopy(v)
        return a

    result = {}
    for d in dicts:
        result = deep_merge(result, d)
    return result


@mcp.tool()
def set_value(obj: dict, path, value):
    """
    Sets a deep property in a dictionary by path (dot/bracket notation or list).

    Parameters:
        obj (Dict[Any, Any]): The dictionary to modify.
        path (Union[str, List[Any]]): The property path as a dot/bracket string or list
            of keys.
        value (Any): The value to set at the specified path.

    Returns:
        Dict[Any, Any]: The modified dictionary with the value set.

    Usage Example:
        set_value({"a": {"b": 1}}, "a.b", 2)  # => {'a': {'b': 2}}
    """
    import re

    if isinstance(path, str):
        path = re.findall(r"[^.\[\]]+", path)
    d = obj
    for p in path[:-1]:
        if p not in d or not isinstance(d[p], dict):
            d[p] = {}
        d = d[p]
    d[path[-1]] = value
    return obj


@mcp.tool()
def get_value(obj: dict, path, default=None):
    """
    Gets a deep property from a dictionary by path (dot/bracket notation or list).

    Parameters:
        obj (Dict[Any, Any]): The dictionary to access.
        path (Union[str, List[Any]]): The property path as a dot/bracket string or list
            of keys.
        default (Any, optional): The value to return if the path does not exist.
            Defaults to None.

    Returns:
        Any: The value at the specified path, or the default if not found.

    Usage Example:
        get_value({"a": {"b": 2}}, "a.b")  # => 2
        get_value({"a": {"b": 2}}, "a.c", 42)  # => 42
    """
    import re

    if isinstance(path, str):
        path = re.findall(r"[^.\[\]]+", path)
    d = obj
    for p in path:
        if isinstance(d, dict) and p in d:
            d = d[p]
        else:
            return default
    return d


if __name__ == "__main__":
    mcp.run()
