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

### Usage in AI Coding Editors

If you are integrating Lever MCP with an AI-assisted coding editor (such as Cursor or Windsurf), be sure to load the [lever-rules.md](./lever-rules.md) file into your editor's rules for the coding agent/AI assistant. This file provides best practices and guidance for the agent, ensuring it uses Lever MCP tools efficiently and according to recommended patterns:
- Prefer built-in Lever MCP tools for data operations
- Apply best practices for data transformation, list/set operations, and more
- Use efficient, maintainable patterns for code generation
- Handle errors and edge cases appropriately

While human users and contributors may also find the document informative, its primary audience is the coding agent. Loading these rules is recommended for anyone developing or configuring an AI coding assistant to ensure high-quality, consistent use of Lever MCP's capabilities.

## Data Utility Tools

All tools accept only property names (strings) for keys/predicates, not function names or callables. Each tool is exposed as an MCP tool with the following parameters and return types:

### mutate_string
Mutates a string according to the specified mutation type.

**Parameters:**
- `text` (str): The input string to mutate.
- `mutation` (str): The type of mutation to perform. One of: 'deburr', 'template', 'camel_case', 'kebab_case', 'snake_case', 'capitalize'.
- `data` (dict, optional): Data for 'template' mutation.

**Returns:**
- `str`: The mutated string.

**Usage Example:**
```python
mutate_string('foo bar', 'camel_case')
# => 'fooBar'
mutate_string('Café déjà vu', 'deburr')
# => 'Cafe deja vu'
mutate_string('Hello, {name}!', 'template', {'name': 'World'})
# => 'Hello, World!'
```

### mutate_list
Mutates a list according to the specified mutation type.

**Parameters:**
- `items` (list): The input list to mutate.
- `mutation` (str): The type of mutation to perform. See main.py for full list (e.g., 'flatten_deep', 'sort_by', 'uniq_by', 'partition', 'pluck', 'compact', 'chunk', 'zip_lists', 'unzip_list', 'remove_by', 'tail', 'initial', 'drop', 'drop_right', 'take', 'take_right', 'flatten', 'union', 'xor', 'shuffle', 'sample_size').
- `param` (any, optional): A parameter for mutations that require one.

**Returns:**
- `list`: The mutated list.

**Usage Example:**
```python
mutate_list([[1, [2, 3], 4], 5], 'flatten_deep')
# => [1, 2, 3, 4, 5]
mutate_list([{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}, {'id': 1, 'name': 'Alice'}], 'uniq_by', 'id')
# => [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
mutate_list([1, 2, 3, 4, 5], 'chunk', 2)
# => [[1, 2], [3, 4], [5]]
```

### has_property
Checks a property or relationship for the given object.

**Parameters:**
- `obj` (any): The object or value to check.
- `property` (str): One of: 'starts_with', 'ends_with', 'is_empty', 'is_equal', 'is_nil', 'has_key'.
- `param` (any, optional): The parameter for the operation, if required.

**Returns:**
- `bool`: The result of the check.

**Usage Example:**
```python
has_property('abc', 'starts_with', 'a')
# => True
has_property({'a': 1}, 'has_key', 'a')
# => True
has_property([], 'is_empty')
# => True
```

### select_from_list
Selects an element from a list using various operations.

**Parameters:**
- `items` (list): The list to select from.
- `operation` (str): One of: 'find_by', 'head', 'last', 'sample'.
- `param` (any, optional): Parameter for the operation (required for 'find_by').

**Returns:**
- `any`: The selected element or None if not found.

**Usage Example:**
```python
select_from_list([{'id': 1}, {'id': 2}], 'find_by', {'key': 'id', 'value': 2})
# => {'id': 2}
select_from_list([1, 2, 3], 'head')
# => 1
select_from_list([1, 2, 3], 'sample')
# => 2 (example output)
```

### compare_lists
Compares two lists using various set-like operations.

**Parameters:**
- `a` (list): The first list.
- `b` (list): The second list.
- `operation` (str): One of: 'difference_by', 'intersection_by', 'intersection', 'difference'.
- `key` (str, optional): The property name for *_by operations.

**Returns:**
- `list`: The result of the comparison.

**Usage Example:**
```python
compare_lists([1, 2, 3], [2, 4], 'difference')
# => [1, 3]
compare_lists([{'id': 1}, {'id': 2}, {'id': 3}], [{'id': 2}], 'difference_by', 'id')
# => [{'id': 1}, {'id': 3}]
compare_lists([1, 2, 3], [2, 3, 4], 'intersection')
# => [2, 3]
```

### process_list
Processes a list into a dictionary using grouping, counting, or keying by a property.

**Parameters:**
- `items` (list): The list of items (dicts or objects).
- `operation` (str): One of: 'group_by', 'count_by', 'key_by'.
- `key` (str): The property name to use.

**Returns:**
- `dict`: The resulting dictionary.

**Usage Example:**
```python
process_list([
    {'type': 'fruit', 'name': 'apple'},
    {'type': 'fruit', 'name': 'banana'},
    {'type': 'vegetable', 'name': 'carrot'}
], 'group_by', 'type')
# => {'fruit': [...], 'vegetable': [...]}
process_list([
    {'type': 'a'}, {'type': 'b'}, {'type': 'a'}
], 'count_by', 'type')
# => {'a': 2, 'b': 1}
```

### process_dict
Performs dictionary operations: invert, pick, or omit.

**Parameters:**
- `obj` (dict): The source dictionary.
- `operation` (str): One of: 'invert', 'pick', 'omit'.
- `param` (list, optional): Keys to pick or omit (required for 'pick' and 'omit').

**Returns:**
- `dict`: The resulting dictionary.

**Usage Example:**
```python
process_dict({'a': 1, 'b': 2}, 'pick', ['a'])
# => {'a': 1}
process_dict({'a': 1, 'b': 2}, 'omit', ['a'])
# => {'b': 2}
process_dict({'a': 'x', 'b': 'y'}, 'invert')
# => {'x': 'a', 'y': 'b'}
```

### chain
Chains multiple tool calls, piping the output of one as the input to the next.

**Parameters:**
- `input` (any): The initial input to the chain.
- `tool_calls` (list): Each dict must have:
  - `tool` (str): The tool name
  - `params` (dict, optional): Additional parameters

**Returns:**
- `any`: The result of the last tool in the chain.

**Usage Example:**
```python
chain(
    [1, [2, [3, 4], 5]],
    [
        {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}},
        {"tool": "mutate_list", "params": {"mutation": "compact"}}
    ]
)
# => [1, 2, 3, 4, 5]
```

### merge
Deep merges a list of dictionaries.

**Parameters:**
- `dicts` (list): A list of dictionaries to merge.

**Returns:**
- `dict`: A single dictionary containing the merged keys and values.

**Usage Example:**
```python
merge([
    {"a": 1, "b": {"c": 2}},
    {"b": {"d": 3}}
])
# => {'a': 1, 'b': {'c': 2, 'd': 3}}
```

### set_value
Sets a deep property in a dictionary by path (dot/bracket notation or list).

**Parameters:**
- `obj` (dict): The dictionary to modify.
- `path` (str or list): The property path as a dot/bracket string or list of keys.
- `value` (any): The value to set at the specified path.

**Returns:**
- `dict`: The modified dictionary with the value set.

**Usage Example:**
```python
set_value({"a": {"b": 1}}, "a.b", 2)
# => {'a': {'b': 2}}
```

### get_value
Gets a deep property from a dictionary by path (dot/bracket notation or list).

**Parameters:**
- `obj` (dict): The dictionary to access.
- `path` (str or list): The property path as a dot/bracket string or list of keys.
- `default` (any, optional): The value to return if the path does not exist. Defaults to None.

**Returns:**
- `any`: The value at the specified path, or the default if not found.

**Usage Example:**
```python
get_value({"a": {"b": 2}}, "a.b")
# => 2
get_value({"a": {"b": 2}}, "a.c", 42)
# => 42
```

## Contributing

Contributions are welcome! If you have ideas for new tools or improvements, please open an issue or submit a pull request.

## License

Lever MCP is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
