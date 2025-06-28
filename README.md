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

### Starting the Server with Streamable HTTP

By default, the server runs using stdio transport (suitable for local tools and editor integration). To run the server as a Streamable HTTP service (recommended for web-based deployments or remote access), use the `--http` flag:

```bash
python main.py --http
```

You can also specify a custom host and port:

```bash
python main.py --http --host 0.0.0.0 --port 9000
```

- `--http`: Start the server with Streamable HTTP (instead of stdio)
- `--host`: Host for HTTP server (default: 127.0.0.1)
- `--port`: Port for HTTP server (default: 8000)

**Note:** The `run.sh` and `run.bat` scripts also support these arguments and will pass them to `main.py`. For example:

```bash
./run.sh --http --host 0.0.0.0 --port 9000
```

or on Windows:

```bat
run.bat --http --host 0.0.0.0 --port 9000
```

If you omit `--http`, the server will use stdio transport (default behavior):

```bash
python main.py
```

### Usage in AI Coding Editors

If you are integrating Lever MCP with an AI-assisted coding editor (such as Cursor or Windsurf), be sure to load the [lever-rules.md](./lever-rules.md) file into your editor's rules for the coding agent/AI assistant. This file provides best practices and guidance for the agent, ensuring it uses Lever MCP tools efficiently and according to recommended patterns:
- Prefer built-in Lever MCP tools for data operations
- Apply best practices for data transformation, list/set operations, and more
- Use efficient, maintainable patterns for code generation
- Handle errors and edge cases appropriately

While human users and contributors may also find the document informative, its primary audience is the coding agent. Loading these rules is recommended for anyone developing or configuring an AI coding assistant to ensure high-quality, consistent use of Lever MCP's capabilities.

## Data Utility Tools

All tools accept only JSON-serializable types (str, int, float, bool, None, list, dict). Each tool is exposed as an MCP tool with the following parameters and return types:

---

### strings
Performs string operations and mutations.

**Parameters:**
- `text` (str): The input string to operate on.
- `operation` (str): The operation to perform. One of:
    - 'camel_case': Converts to camelCase (e.g., 'foo bar' → 'fooBar').
    - 'capitalize': Capitalizes the first character (e.g., 'foo bar' → 'Foo bar').
    - 'deburr': Removes accents/diacritics (e.g., 'Café' → 'Cafe').
    - 'kebab_case': Converts to kebab-case (e.g., 'foo bar' → 'foo-bar').
    - 'lower_case': Converts to lowercase (e.g., 'Hello' → 'hello').
    - 'replace': Replaces all occurrences of a substring (requires data={'old': 'x', 'new': 'y'}).
    - 'reverse': Reverses the string (e.g., 'hello' → 'olleh').
    - 'snake_case': Converts to snake_case (e.g., 'foo bar' → 'foo_bar').
    - 'upper_case': Converts to uppercase (e.g., 'Hello' → 'HELLO').
    - 'template': Interpolates variables using {var} syntax (requires data dict).
    - 'trim': Removes leading and trailing whitespace.
    - 'starts_with', 'ends_with', 'contains', 'is_equal', 'is_empty', 'is_digit', 'is_alpha', 'is_upper', 'is_lower', 'xor', 'shuffle', 'sample_size'.
- `param` (Any, optional): Parameter for operations that require one.
- `data` (dict, optional): Data for 'template' and 'replace' operations.

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Example:**
```python
strings('foo bar', 'camel_case')  # => {'value': 'fooBar'}
strings('Hello, {name}!', 'template', data={'name': 'World'})  # => {'value': 'Hello, World!'}
strings('foo bar foo', 'replace', data={'old': 'foo', 'new': 'baz'})  # => {'value': 'baz bar baz'}
```

---

### lists
Performs list operations and mutations.

**Parameters:**
- `items` (list): The input list to operate on.
- `operation` (str): The operation to perform. One of:
    - 'chunk': Splits a list into chunks of a given size (param: int).
    - 'compact': Removes falsy values from a list.
    - 'drop': Drops n elements from the beginning (param: int).
    - 'drop_right': Drops n elements from the end (param: int).
    - 'flatten': Flattens a list one level deep.
    - 'flatten_deep': Flattens a nested list completely.
    - 'initial': Gets all but the last element.
    - 'partition': Splits a list into two lists based on a property (param: str).
    - 'pluck': Extracts a list of values for a given key (param: str).
    - 'remove_by': Removes items where a property matches a value (param: {'key': str, 'value': Any}).
    - 'sample_size': Gets n random elements (param: int).
    - 'shuffle': Shuffles the list.
    - 'sort_by': Sorts a list of objects by a key (param: str).
    - 'tail': Gets all but the first element.
    - 'take': Takes n elements from the beginning (param: int).
    - 'take_right': Takes n elements from the end (param: int).
    - 'union': Unique values from all given lists.
    - 'uniq_by': Removes duplicates by a key (param: str).
    - 'unzip_list': Unzips a list of tuples into separate lists.
    - 'xor': Symmetric difference of the given lists.
    - 'zip_lists': Zips multiple lists into a list of tuples.
    - 'is_empty', 'difference', 'intersection', 'difference_by', 'intersection_by', 'group_by', 'count_by', 'key_by', 'find_by', 'head', 'last', 'sample', 'nth', 'min_by', 'max_by', 'index_of', 'random_except', 'contains', 'is_equal', 'is_empty'.
- `param` (Any, optional): Parameter for operations that require one.
- `others` (list, optional): Second list for set-like operations.
- `key` (str, optional): Property name for *_by operations.

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Example:**
```python
lists([[1, [2, 3], 4], 5], 'flatten_deep')  # => {'value': [1, 2, 3, 4, 5]}
lists([{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}], 'pluck', 'name')  # => {'value': ['Alice', 'Bob']}
lists([1, 2, 3], 'difference', others=[2, 3])  # => {'value': [1]}
lists([{'id': 1}, {'id': 2}], 'uniq_by', key='id')  # => {'value': [{'id': 1}]}
```

---

### dicts
Performs dictionary operations, including merge, set/get value, and property checks.

**Parameters:**
- `obj` (dict or list): The source dictionary, or a list of dicts for 'merge'. Must be a dict for all operations except 'merge'.
- `operation` (str): The operation to perform. One of:
    - 'merge': Deep merges a list of dictionaries (obj must be a list of dicts).
    - 'invert': Swaps keys and values.
    - 'pick': Picks specified keys (param: list of keys).
    - 'omit': Omits specified keys (param: list of keys).
    - 'set_value': Sets a deep property by path (path: str or list, value: any).
    - 'get_value': Gets a deep property by path (path: str or list, default: any).
    - 'has_key': Checks if a dict has a given key (param: str).
    - 'is_equal': Checks if two dicts are deeply equal (param: dict to compare).
    - 'is_empty': Checks if the dict is empty.
- `param` (Any, optional): Used for 'pick', 'omit', 'has_key', 'is_equal'.
- `path` (str or list, optional): Used for 'set_value' and 'get_value'.
- `value` (Any, optional): Used for 'set_value'.
- `default` (Any, optional): Used for 'get_value'.

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Example:**
```python
dicts({'a': 1, 'b': 2}, 'pick', ['a'])  # => {'value': {'a': 1}}
dicts({'a': {'b': 1}}, 'set_value', path=['a', 'b'], value=2)  # => {'value': {'a': {'b': 2}}}
dicts({'a': 1}, 'get_value', path='b', default=42)  # => {'value': 42}
```

---

### any
Performs type-agnostic property checks and comparisons.

**Parameters:**
- `value` (Any): The value to check.
- `operation` (str): The operation to perform. One of:
    - 'is_equal': Checks if two values are deeply equal (param: value to compare).
    - 'is_empty': Checks if the value is empty.
    - 'is_nil': Checks if the value is None.
    - 'contains': Checks if a string or list contains a value (param: value to check).
- `param` (Any, optional): The parameter for the operation, if required.

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Example:**
```python
any('abc', 'contains', 'b')  # => {'value': True}
any([1, 2, 3], 'contains', 2)  # => {'value': True}
any({'a': 1}, 'contains', 'a')  # => {'value': False}
any([], 'is_empty')  # => {'value': True}
any(None, 'is_nil')  # => {'value': True}
any(42, 'is_equal', 42)  # => {'value': True}
any(True, 'is_equal', True)  # => {'value': True}
any(3.14, 'is_equal', 3.14)  # => {'value': True}
```

---

### generate
Generates sequences or derived data from input using the specified operation.

**Parameters:**
- `text` (Any): The input list or value.
- `operation` (str): The operation to perform. One of:
    - 'accumulate': Running totals (or with a binary function if param is provided). param: None or a supported function name (e.g., 'mul')
    - 'cartesian_product': Cartesian product of multiple input lists. param: None
    - 'combinations': All combinations of a given length (param: int, required)
    - 'cycle': Repeat the sequence up to param times. param: int (max length, optional)
    - 'permutations': All permutations of a given length (param: int, optional, default=len(input))
    - 'powerset': All possible subsets of a list. param: None
    - 'range': Generate a list of numbers from start to end (optionally step). param: [start, end, step?]
    - 'repeat': Repeat a value or sequence a specified number of times. param: int (number of times)
    - 'unique_pairs': All unique pairs from a list. param: None
    - 'windowed': Sliding windows of a given size. param: int (window size)
    - 'zip_with_index': Tuples of (index, value). param: None
- `param` (Any, optional): Parameter for the operation, if required.

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Example:**
```python
generate(None, 'range', [0, 5])  # => {'value': [0, 1, 2, 3, 4]}
generate('x', 'repeat', 3)  # => {'value': ['x', 'x', 'x']}
```

---

### chain
Chains multiple tool calls, piping the output of one as the input to the next.

**Parameters:**
- `input` (Any): The initial input to the chain.
- `tool_calls` (List[Dict[str, Any]]): Each dict must have:
    - 'tool': the tool name (str)
    - 'params': dict of additional parameters (optional, default empty)

**Returns:**
- `dict`: The result of the last tool in the chain, always wrapped in a dictionary with a 'value' key. If an error occurs, an 'error' key is also present.

**Usage Example:**
```python
chain(
    [[{"id": 2}], [{"id": 1}], [None]],
    [
        {"tool": "lists", "params": {"operation": "flatten"}},
        {"tool": "lists", "params": {"operation": "compact"}},
        {"tool": "lists", "params": {"operation": "sort_by", "param": "id"}}
    ]
)
# => {'value': [{"id": 1}, {"id": 2}}
```

---

## Error Handling

All tools return a dictionary with a 'value' key. If an error occurs (e.g., invalid input type, missing parameter, unknown operation), the dictionary will also include an 'error' key with a descriptive message.

## Type Handling

All tools only accept JSON-serializable types. For type-agnostic checks (e.g., is_empty, is_equal, contains), use the `any` tool.

## License

Lever MCP is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
