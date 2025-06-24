import unicodedata
import re
from fastmcp import FastMCP, Context
from typing import Any, Callable, Dict, List, Optional, Union
import copy
import inspect
from typing import get_origin, get_args
from mcp.types import TextContent, ImageContent, AudioContent, EmbeddedResource
import json

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


@mcp.tool()
def pluck(items: List[Any], key: str) -> List[Any]:
    """
    Extracts a list of values for a given property from a list of dicts/objects.

    Parameters:
        items (List[Any]): The list of items (dicts or objects).
        key (str): The property name to extract.

    Returns:
        List[Any]: A list of values for the given property.
    
    Usage Example:
        pluck([
            {"id": 1, "name": "a"},
            {"id": 2, "name": "b"}
        ], "name")
        # => ["a", "b"]
    """
    return [item.get(key) if isinstance(item, dict) else getattr(item, key, None) for item in items]


@mcp.tool()
def compact(items: List[Any]) -> List[Any]:
    """
    Removes falsy values from a list.

    Parameters:
        items (List[Any]): The list to compact.

    Returns:
        List[Any]: A list with all falsy values removed.
    
    Usage Example:
        compact([0, 1, False, 2, '', 3, None])
        # => [1, 2, 3]
    """
    return [item for item in items if item]


@mcp.tool()
def chunk(items: List[Any], size: int) -> List[List[Any]]:
    """
    Splits a list into chunks of a specified size.

    Parameters:
        items (List[Any]): The list to split.
        size (int): The chunk size.

    Returns:
        List[List[Any]]: A list of chunks (sublists).
    
    Usage Example:
        chunk([1, 2, 3, 4, 5], 2)
        # => [[1, 2], [3, 4], [5]]
    """
    return [items[i:i + size] for i in range(0, len(items), size)]


@mcp.tool()
def count_by(items: List[Any], key: str) -> Dict[Any, int]:
    """
    Counts occurrences of values for a given property in a list of dicts/objects.

    Parameters:
        items (List[Any]): The list of items (dicts or objects).
        key (str): The property name to count by.

    Returns:
        Dict[Any, int]: A dictionary mapping property values to their counts.
    
    Usage Example:
        count_by([
            {"type": "a"}, {"type": "b"}, {"type": "a"}
        ], "type")
        # => {"a": 2, "b": 1}
    """
    result = {}
    for item in items:
        k = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
        result[k] = result.get(k, 0) + 1
    return result


@mcp.tool()
def difference_by(a: List[Any], b: List[Any], key: str) -> List[Any]:
    """
    Returns items from the first list whose property value is not present in the second list.

    Parameters:
        a (List[Any]): The list to filter.
        b (List[Any]): The list of items to exclude by property value.
        key (str): The property name to compare.

    Returns:
        List[Any]: Filtered list of items from 'a'.
    
    Usage Example:
        difference_by([
            {"id": 1}, {"id": 2}, {"id": 3}
        ], [
            {"id": 2}
        ], "id")
        # => [{"id": 1}, {"id": 3}]
    """
    b_keys = set(item.get(key) if isinstance(item, dict) else getattr(item, key, None) for item in b)
    return [item for item in a if (item.get(key) if isinstance(item, dict) else getattr(item, key, None)) not in b_keys]


@mcp.tool()
def intersection_by(a: List[Any], b: List[Any], key: str) -> List[Any]:
    """
    Returns items from the first list whose property value is present in the second list.

    Parameters:
        a (List[Any]): The list to filter.
        b (List[Any]): The list of items to include by property value.
        key (str): The property name to compare.

    Returns:
        List[Any]: Filtered list of items from 'a'.
    
    Usage Example:
        intersection_by([
            {"id": 1}, {"id": 2}, {"id": 3}
        ], [
            {"id": 2}, {"id": 4}
        ], "id")
        # => [{"id": 2}]
    """
    b_keys = set(item.get(key) if isinstance(item, dict) else getattr(item, key, None) for item in b)
    result = [item for item in a if (item.get(key) if isinstance(item, dict) else getattr(item, key, None)) in b_keys]
    return list(result)


@mcp.tool()
def zip_lists(lists: List[List[Any]]) -> List[List[Any]]:
    """
    Zips multiple lists into a list of tuples (as lists).

    Parameters:
        lists (List[List[Any]]): The lists to zip (pass as a list of lists).

    Returns:
        List[List[Any]]: A list of zipped tuples (as lists).
    
    Usage Example:
        zip_lists([[1, 2], ["a", "b"]])
        # => [[1, "a"], [2, "b"]]
    """
    return [list(t) for t in zip(*lists)]


@mcp.tool()
def unzip_list(items: List[List[Any]]) -> List[List[Any]]:
    """
    Unzips a list of tuples (as lists) into separate lists.

    Parameters:
        items (List[List[Any]]): The list of tuples (as lists) to unzip.

    Returns:
        List[List[Any]]: A list of lists, one for each position in the tuples.
    
    Usage Example:
        unzip_list([[1, "a"], [2, "b"]])
        # => [[1, 2], ["a", "b"]]
    """
    return [list(t) for t in zip(*items)] if items else []


@mcp.tool()
def find_by(items: List[Any], key: str, value: Any) -> Optional[Any]:
    """
    Finds the first item in a list where a property matches a value.

    Parameters:
        items (List[Any]): The list of items (dicts or objects).
        key (str): The property name to check.
        value (Any): The value to match.

    Returns:
        Optional[Any]: The first matching item, or None if not found.
    
    Usage Example:
        find_by([
            {"id": 1}, {"id": 2}
        ], "id", 2)
        # => {"id": 2}
    """
    for item in items:
        v = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
        if v == value:
            return item
    return None


@mcp.tool()
def remove_by(items: List[Any], key: str, value: Any) -> List[Any]:
    """
    Removes all items from a list where a property matches a value.

    Parameters:
        items (List[Any]): The list of items (dicts or objects).
        key (str): The property name to check.
        value (Any): The value to match for removal.

    Returns:
        List[Any]: The list with matching items removed.
    
    Usage Example:
        remove_by([
            {"id": 1}, {"id": 2}, {"id": 1}
        ], "id", 1)
        # => [{"id": 2}]
    """
    result = [item for item in items if (item.get(key) if isinstance(item, dict) else getattr(item, key, None)) != value]
    return list(result)


def unwrap_result(result):
    # If result is a list of content objects, extract their values
    if isinstance(result, list) and result and all(
        isinstance(x, (TextContent, ImageContent, AudioContent, EmbeddedResource)) for x in result
    ):
        values = []
        for content in result:
            if isinstance(content, TextContent):
                try:
                    values.append(json.loads(content.text))
                except Exception:
                    values.append(content.text)
            elif isinstance(content, (ImageContent, AudioContent)):
                values.append(content.data)
            elif isinstance(content, EmbeddedResource):
                values.append(content.resource)
            else:
                values.append(content)
        return values if len(values) > 1 else values[0]
    # If result is a single content object
    if isinstance(result, (TextContent, ImageContent, AudioContent, EmbeddedResource)):
        if isinstance(result, TextContent):
            try:
                return json.loads(result.text)
            except Exception:
                return result.text
        elif isinstance(result, (ImageContent, AudioContent)):
            return result.data
        elif isinstance(result, EmbeddedResource):
            return result.resource
    # Otherwise, return as is
    return result


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
        Any: The result of the last tool in the chain, or a descriptive error message if a tool is missing, incompatible, or if the primary parameter is specified in params.

    Chaining Rule:
        The output from one tool is always used as the input to the next tool's primary parameter. You must not specify the primary parameter in params for any tool in the chain.

    Usage Example:
        chain(
            [1, [2, [3, 4], 5]],
            [
                {"tool": "flatten_deep", "params": {}},
                {"tool": "compact", "params": {}}
            ]
        )
    # Or as a JSON payload:
    # {
    #   "input": [1, [2, [3, 4], 5]],
    #   "tool_calls": [
    #     {"tool": "flatten_deep", "params": {}},
    #     {"tool": "compact", "params": {}}
    #   ]
    # }
    """
    value = input
    for i, step in enumerate(tool_calls):
        tool_name = step.get("tool")
        params = step.get("params", {})
        if not tool_name:
            return {"error": f"Step {i}: Missing 'tool' name."}
        # Get the tool (support both sync and async)
        try:
            tool_coro = mcp._tool_manager.get_tool(tool_name)
        except Exception as e:
            return {"error": f"Step {i}: Tool '{tool_name}' not found: {e}"}
        # Await if coroutine, else use directly
        if hasattr(tool_coro, "__await__"):
            try:
                tool = await tool_coro
            except Exception as e:
                return {"error": f"Step {i}: Tool '{tool_name}' not found: {e}"}
        else:
            tool = tool_coro
        # Now 'tool' is always the resolved object, safe to access attributes
        if not hasattr(tool, "run") or not callable(getattr(tool, "run", None)):
            return {"error": f"Step {i}: Tool '{tool_name}' is not a valid tool object."}
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
                return {"error": f"Step {i}: Chaining does not allow specifying the primary parameter '{primary_param}' in params. The output from the previous tool is always used as input."}
            arguments[primary_param] = value
        elif len(param_schema) == 1:
            only_param = next(iter(param_schema))
            if only_param in arguments:
                return {"error": f"Step {i}: Chaining does not allow specifying the primary parameter '{only_param}' in params. The output from the previous tool is always used as input."}
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


if __name__ == "__main__":
    mcp.run()
