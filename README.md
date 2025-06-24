# Lever MCP

Lever MCP is a Python-based server that exposes a set of powerful data utility functions as Model Context Protocol (MCP) tools. It is designed to be used with an MCP-compatible client or LLM, providing a suite of functions for manipulating lists, dictionaries, and strings in a consistent, server-based way.

## Purpose

The primary purpose of Lever MCP is to provide a robust set of data transformation and utility tools, accessible via MCP, for use in AI coding assistants, automation, and data workflows.

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/Voidious/lever-mcp.git
    cd lever-mcp
    ```

2. **Create and Activate a Virtual Environment:**
    For macOS/Linux:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    For Windows:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Lever MCP is designed to be used as a server with an MCP-compatible client, such as an AI coding assistant in an editor like Cursor or VS Code.

To configure the server, add a new server configuration block in your editor's MCP settings:

**For macOS/Linux/Windows (Git Bash/WSL/Cygwin):**
```json
"lever": {
  "command": "/path/to/your/clone/of/lever-mcp/run.sh"
}
```
**For Windows (Command Prompt or PowerShell):**
```json
"lever": {
  "command": "C:\\path\\to\\your\\clone\\of\\lever-mcp\\run.bat"
}
```

Once configured, your AI coding assistant will be able to use the Lever MCP tools.

## Data Utility Tools

All tools accept only property names (strings) for keys/predicates, not function names or callables. Each tool is exposed as an MCP tool with the following parameters and return types:

### groupBy
Groups items by a property name (string key).

**Parameters:**
- `items` (List[Any]): The list of items (dicts or objects) to group.
- `key` (str): The property name to group by.

**Returns:**
- `Dict[Any, List[Any]]`: A dictionary mapping each unique property value to a list of items with that value.

### merge
Deep merges a list of dictionaries.

**Parameters:**
- `dicts` (List[Dict[Any, Any]]): A list of dictionaries to merge.

**Returns:**
- `Dict[Any, Any]`: A single dictionary containing the merged keys and values.

### flattenDeep
Fully flattens a nested list.

**Parameters:**
- `items` (List[Any]): The nested list to flatten.

**Returns:**
- `List[Any]`: A single, flat list containing all values from the nested structure.

### sortBy
Sorts a list by a property name (string key).

**Parameters:**
- `items` (List[Any]): The list of items (dicts or objects) to sort.
- `key` (str): The property name to sort by.

**Returns:**
- `List[Any]`: The sorted list of items.

### uniqBy
Returns unique items in a list by a property name (string key).

**Parameters:**
- `items` (List[Any]): The list of items (dicts or objects) to filter.
- `key` (str): The property name to determine uniqueness.

**Returns:**
- `List[Any]`: A list of unique items based on the property value.

### deburr
Removes accents/diacritics from a string.

**Parameters:**
- `text` (str): The input string to deburr.

**Returns:**
- `str`: The deburred string with accents removed.

### template
Interpolates variables in a string using {var} syntax.

**Parameters:**
- `text` (str): The template string containing {var} placeholders.
- `data` (Dict[str, Any]): A dictionary of values to substitute into the template.

**Returns:**
- `str`: The interpolated string with variables replaced.

### cloneDeep
Performs a deep copy of a dictionary or list.

**Parameters:**
- `obj` (Any): The object (dict or list) to deep copy.

**Returns:**
- `Any`: A deep copy of the input object.

### set_value
Sets a deep property in a dictionary by path (dot/bracket notation or list).

**Parameters:**
- `obj` (Dict[Any, Any]): The dictionary to modify.
- `path` (Union[str, List[Any]]): The property path as a dot/bracket string or list of keys.
- `value` (Any): The value to set at the specified path.

**Returns:**
- `Dict[Any, Any]`: The modified dictionary with the value set.

### get_value
Gets a deep property from a dictionary by path (dot/bracket notation or list).

**Parameters:**
- `obj` (Dict[Any, Any]): The dictionary to access.
- `path` (Union[str, List[Any]]): The property path as a dot/bracket string or list of keys.
- `default` (Any, optional): The value to return if the path does not exist. Defaults to None.

**Returns:**
- `Any`: The value at the specified path, or the default if not found.

### partition
Splits a list into two lists: [items where item[predicate] is truthy, items where it is falsy]. Predicate is a property name only.

**Parameters:**
- `items` (List[Any]): The list of items (dicts or objects) to partition.
- `predicate` (str): The property name to test for truthiness.

**Returns:**
- `List[List[Any]]`: A list containing two lists: [truthy_items, falsy_items].

## Running Tests

This project includes a test suite to verify its functionality. The tests use `pytest` and run in-memory without needing to keep the server running in a separate process.

To run the tests, execute the following command from the root directory:

```bash
pytest
``` 
