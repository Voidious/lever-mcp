import unicodedata
import re
from fastmcp import FastMCP, Context
from typing import Any, Callable, Dict, List, Optional, Union
import copy
import inspect
from typing import get_origin, get_args

# --- MCP Server Setup ---


class LeverMCP(FastMCP):
    pass


mcp = LeverMCP("Lever MCP")

# --- Utility Functions ---


@mcp.tool()
def group_by(items: List[Any], key: str) -> Dict[Any, List[Any]]:
    """
    Groups items by a property name (string key).

    Parameters:
        items (List[Any]): The list of items (dicts or objects) to group.
        key (str): The property name to group by.

    Returns:
        Dict[Any, List[Any]]: A dictionary mapping each unique property value to a list of items with that value.
    
    Usage Example:
        group_by([
            {"type": "fruit", "name": "apple"},
            {"type": "fruit", "name": "banana"},
            {"type": "vegetable", "name": "carrot"}
        ], "type")
        # => {'fruit': [{...}, {...}], 'vegetable': [{...}]}
    """
    result = {}
    for item in items:
        k = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
        result.setdefault(k, []).append(item)
    return result


@mcp.tool()
def merge(dicts: List[Dict[Any, Any]]) -> Dict[Any, Any]:
    """
    Deep merges a list of dictionaries.

    Parameters:
        dicts (List[Dict[Any, Any]]): A list of dictionaries to merge.

    Returns:
        Dict[Any, Any]: A single dictionary containing the merged keys and values.
    
    Usage Example:
        merge([
            {"a": 1, "b": {"c": 2}},
            {"b": {"d": 3}}
        ])
        # => {'a': 1, 'b': {'c': 2, 'd': 3}}
    """

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
def flatten_deep(items: List[Any]) -> List[Any]:
    """
    Fully flattens a nested list.

    Parameters:
        items (List[Any]): The nested list to flatten.

    Returns:
        List[Any]: A single, flat list containing all values from the nested structure.
    
    Usage Example:
        flatten_deep([1, [2, [3, 4], 5], 6])
        # => [1, 2, 3, 4, 5, 6]
    """
    result = []

    def _flatten(lst):
        for i in lst:
            if isinstance(i, list):
                _flatten(i)
            else:
                result.append(i)

    _flatten(items)
    return result


@mcp.tool()
def sort_by(items: List[Any], key: str) -> List[Any]:
    """
    Sorts a list by a property name (string key).

    Parameters:
        items (List[Any]): The list of items (dicts or objects) to sort.
        key (str): The property name to sort by.

    Returns:
        List[Any]: The sorted list of items.
    
    Usage Example:
        sort_by([
            {"age": 30, "name": "Alice"},
            {"age": 25, "name": "Bob"}
        ], "age")
        # => [{"age": 25, "name": "Bob"}, {"age": 30, "name": "Alice"}]
    """
    return sorted(
        items,
        key=lambda x: x.get(key, "") if isinstance(x, dict) else getattr(x, key, ""),
    )


@mcp.tool()
def uniq_by(items: List[Any], key: str) -> List[Any]:
    """
    Returns unique items in a list by a property name (string key).

    Parameters:
        items (List[Any]): The list of items (dicts or objects) to filter.
        key (str): The property name to determine uniqueness.

    Returns:
        List[Any]: A list of unique items based on the property value.
    
    Usage Example:
        uniq_by([
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 1, "name": "Alice"}
        ], "id")
        # => [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    """
    seen = set()
    result = []
    for item in items:
        k = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result


@mcp.tool()
def deburr(text: str) -> str:
    """
    Removes accents/diacritics from a string.

    Parameters:
        text (str): The input string to deburr.

    Returns:
        str: The deburred string with accents removed.
    
    Usage Example:
        deburr("Café déjà vu")
        # => 'Cafe deja vu'
    """
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )


@mcp.tool()
def template(text: str, data: Dict[str, Any]) -> str:
    """
    Interpolates variables in a string using {var} syntax.

    Parameters:
        text (str): The template string containing {var} placeholders.
        data (Dict[str, Any]): A dictionary of values to substitute into the template.

    Returns:
        str: The interpolated string with variables replaced.
    
    Usage Example:
        template("Hello, {name}!", {"name": "World"})
        # => 'Hello, World!'
    """

    def replacer(match):
        key = match.group(1)
        return str(data.get(key, match.group(0)))

    return re.sub(r"\{(\w+)\}", replacer, text)


@mcp.tool()
def clone_deep(obj: Any) -> Any:
    """
    Performs a deep copy of a dictionary or list.

    Parameters:
        obj (Any): The object (dict or list) to deep copy.

    Returns:
        Any: A deep copy of the input object.
    
    Usage Example:
        clone_deep({"a": [1, 2, 3]})
        # => {'a': [1, 2, 3]} (deep copy)
    """
    return copy.deepcopy(obj)


@mcp.tool()
def set_value(obj: Dict[Any, Any], path: Union[str, List[Any]], value: Any) -> Dict[Any, Any]:
    """
    Sets a deep property in a dictionary by path (dot/bracket notation or list).

    Parameters:
        obj (Dict[Any, Any]): The dictionary to modify.
        path (Union[str, List[Any]]): The property path as a dot/bracket string or list of keys.
        value (Any): The value to set at the specified path.

    Returns:
        Dict[Any, Any]: The modified dictionary with the value set.
    
    Usage Example:
        set_value({"a": {"b": 1}}, "a.b", 2)
        # => {'a': {'b': 2}}
    """
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
def get_value(obj: Dict[Any, Any], path: Union[str, List[Any]], default: Any = None) -> Any:
    """
    Gets a deep property from a dictionary by path (dot/bracket notation or list).

    Parameters:
        obj (Dict[Any, Any]): The dictionary to access.
        path (Union[str, List[Any]]): The property path as a dot/bracket string or list of keys.
        default (Any, optional): The value to return if the path does not exist. Defaults to None.

    Returns:
        Any: The value at the specified path, or the default if not found.
    
    Usage Example:
        get_value({"a": {"b": 2}}, "a.b")
        # => 2
        get_value({"a": {"b": 2}}, "a.c", 42)
        # => 42
    """
    if isinstance(path, str):
        path = re.findall(r"[^.\[\]]+", path)
    d = obj
    for p in path:
        if isinstance(d, dict) and p in d:
            d = d[p]
        else:
            return default
    return d


@mcp.tool()
def partition(items: List[Any], predicate: str) -> List[List[Any]]:
    """
    Splits a list into two lists: [items where item[predicate] is truthy, items where it is falsy]. Predicate is a property name only.

    Parameters:
        items (List[Any]): The list of items (dicts or objects) to partition.
        predicate (str): The property name to test for truthiness.

    Returns:
        List[List[Any]]: A list containing two lists: [truthy_items, falsy_items].
    
    Usage Example:
        partition([
            {"active": True, "name": "Alice"},
            {"active": False, "name": "Bob"}
        ], "active")
        # => [[{"active": True, "name": "Alice"}], [{"active": False, "name": "Bob"}]]
    """
    trues, falses = [], []
    for item in items:
        result = (
            item.get(predicate)
            if isinstance(item, dict)
            else getattr(item, predicate, False)
        )
        (trues if result else falses).append(item)
    return [trues, falses]


if __name__ == "__main__":
    mcp.run()
