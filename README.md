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
- `--unsafe`: Disable Lua safety rails (allows file I/O and system commands)

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

### Lua Safety Configuration

By default, Lever MCP runs Lua predicates in **safe mode**, which blocks potentially dangerous operations:
- **Blocked**: File I/O (`io.*`), system commands (`os.execute`), module loading (`require`)
- **Allowed**: Math operations, string functions, time/date functions, comparisons

To disable safety rails for trusted environments:
```bash
./run.sh --unsafe
python main.py --unsafe
```

This enables full Lua access, including file operations and system commands.

### Usage in AI Coding Editors

If you are integrating Lever MCP with an AI-assisted coding editor (such as Cursor or Windsurf), be sure to load the [lever-rules.md](./docs/lever-rules.md) file into your editor's rules for the coding agent/AI assistant. This file provides best practices and guidance for the agent, ensuring it uses Lever MCP tools efficiently and according to recommended patterns:
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
    - 'replace': Replaces all occurrences of a substring (requires data={'old': 'x', 'new': 'y'}).
    - 'reverse': Reverses the string (e.g., 'hello' → 'olleh').
    - 'sample_size': Returns n random characters (param: int).
    - 'shuffle': Randomly shuffles string characters.
    - 'snake_case': Converts to snake_case (e.g., 'foo bar' → 'foo_bar').
    - 'starts_with': Checks if string starts with substring (param: str).
    - 'template': Interpolates variables using {var} syntax (requires data dict).
    - 'trim': Removes leading and trailing whitespace.
    - 'upper_case': Converts to uppercase (e.g., 'Hello' → 'HELLO').
    - 'xor': String-specific XOR operation (param: str).
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
Performs list operations, including merge, set/get value, and property checks.

**Note:** For details on using Lua expressions in filtering, grouping, sorting, and extraction, see the [Lua Expressions](#lua-expressions) section below.

**Parameters:**
- `items` (list): The input list to operate on.
- `operation` (str): The operation to perform. Key operations include:
    - 'chunk': Split into chunks (param: int)
    - 'compact': Remove falsy values
    - 'contains': Check if item exists (param: value)
    - 'count_by': Count occurrences by expression result/key
    - 'difference': Items in first not in second (others: list)
    - 'difference_by': Items in first list not matching expression in second
    - 'drop': Drop n elements from start (param: int)
    - 'drop_right': Drop n elements from end (param: int)
    - 'find_by': Find first item matching expression/key-value
    - 'flatten': Flatten one level
    - 'flatten_deep': Flatten completely
    - 'group_by': Group items by expression result/key value
    - 'head': First element
    - 'index_of': Find index of item (param: dict with 'key' and 'value')
    - 'initial': All but last element
    - 'intersection': Items in both lists (others: list)
    - 'intersection_by': Items in first list matching expression in second
    - 'is_empty': Check if list is empty
    - 'is_equal': Check if lists are equal (param: list)
    - 'key_by': Create dict keyed by expression result/field
    - 'last': Last element
    - 'max_by': Find max by expression result/key
    - 'min_by': Find min by expression result/key
    - 'nth': Get nth element (param: int, supports negative indexing)
    - 'partition': Split by expression result/boolean key
    - 'pluck': Extract values by expression/key (expression: any value)
    - 'random_except': Random item excluding condition (param: dict with 'key' and 'value')
    - 'remove_by': Remove items matching expression/key-value
    - 'sample': Get one random item
    - 'sample_size': Get n random items (param: int)
    - 'shuffle': Randomize order
    - 'sort_by': Sort by expression result/key (expression: any comparable value)
    - 'tail': All but first element
    - 'take': Take n elements from start (param: int)
    - 'take_right': Take n elements from end (param: int)
    - 'union': Unique values from all lists (others: list)
    - 'uniq_by': Remove duplicates by expression result/key
    - 'unzip_list': Unzip list of tuples
    - 'xor': Symmetric difference (others: list)
    - 'zip_lists': Zip multiple lists
- `param` (Any, optional): Parameter for operations (int for take/drop, str for sort_by)
- `others` (list, optional): Second list for set operations like difference/intersection
- `key` (str, optional): Property name for *_by operations (faster, alternative to expression)
- `expression` (str, optional): Lua expression for advanced filtering/grouping/sorting/extraction

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Examples:**
```python
# Basic operations
lists([[1, [2, 3], 4], 5], 'flatten_deep')  # => {'value': [1, 2, 3, 4, 5]}
lists([1, 2, 3], 'difference', others=[2, 3])  # => {'value': [1]}

# Using key parameter for *_by operations
lists([{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}, {'id': 1, 'name': 'Alice'}], 'uniq_by', key='id')  # => {'value': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}

# Expression-based operations
lists([{'age': 30, 'score': 85}, {'age': 20, 'score': 95}], 'find_by', expression="age > 25")
# => {'value': {'age': 30, 'score': 85}}

lists([{'score': 90}, {'score': 70}], 'remove_by', expression="score < 80")
# => {'value': [{'score': 90}]}

lists([{'age': 30}, {'age': 20}], 'group_by', expression="age >= 25 and 'adult' or 'young'")
# => {'value': {'adult': [{'age': 30}], 'young': [{'age': 20}]}}

# Advanced expression examples
lists([{'name': 'bob'}, {'name': 'Alice'}], 'sort_by', expression="string.lower(name)")
# => {'value': [{'name': 'Alice'}, {'name': 'bob'}]}

lists([{'x': 1, 'y': 2}, {'x': 3, 'y': 4}], 'pluck', expression="x + y")
# => {'value': [3, 7]}
```

---

### dicts
Performs dictionary operations, including merge, set/get value, and property checks.

**Parameters:**
- `obj` (dict or list): The source dictionary, or a list of dicts for 'merge'. Must be a dict for all operations except 'merge'.
- `operation` (str): The operation to perform. One of:
    - 'get_value': Gets a deep property by path (path: str or list, default: any).
    - 'has_key': Checks if a dict has a given key (param: str).
    - 'invert': Swaps keys and values.
    - 'is_empty': Checks if the dict is empty.
    - 'is_equal': Checks if two dicts are deeply equal (param: dict to compare).
    - 'merge': Deep merges a list of dictionaries (obj must be a list of dicts).
    - 'omit': Omits specified keys (param: list of keys).
    - 'pick': Picks specified keys (param: list of keys).
    - 'set_value': Sets a deep property by path (path: str or list, value: any).
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
Performs type-agnostic property checks, comparisons, and expression evaluation.

**Note:** For details on using Lua expressions in evaluation, see the [Lua Expressions](#lua-expressions) section below.

**Parameters:**
- `value` (Any): The value to check or use as context for expression evaluation.
- `operation` (str): The operation to perform. One of:
    - 'contains': Checks if a string or list contains a value (param: value to check).
    - 'eval': Evaluate a Lua expression with value as context (expression: Lua code).
    - 'is_empty': Checks if the value is empty.
    - 'is_equal': Checks if two values are deeply equal (param: value to compare).
    - 'is_nil': Checks if the value is None.
- `param` (Any, optional): The parameter for the operation, if required.
- `expression` (str, optional): Lua expression to evaluate (for 'eval' operation).

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Example:**
```python
# Basic operations
any('abc', 'contains', 'b')  # => {'value': True}
any([1, 2, 3], 'contains', 2)  # => {'value': True}
any({'a': 1}, 'contains', 'a')  # => {'value': False}
any([], 'is_empty')  # => {'value': True}
any(None, 'is_nil')  # => {'value': True}
any(42, 'is_equal', 42)  # => {'value': True}

# Expression evaluation
any({'age': 30, 'name': 'Alice'}, 'eval', expression="age > 25")  # => {'value': True}
any({'x': 3, 'y': 4}, 'eval', expression="math.sqrt(x*x + y*y)")  # => {'value': 5.0}
any("hello", 'eval', expression="string.upper(item)")  # => {'value': 'HELLO'}
any([1, 2, 3, 4, 5], 'eval', expression="#item")  # => {'value': 5} (length)
any(42, 'eval', expression="item * 2 + 1")  # => {'value': 85}

# Null handling (important: null is truthy!)
any(None, 'eval', expression="item == null")  # => {'value': True}
any({'score': None}, 'eval', expression="score ~= null and 'has score' or 'no score'")  # => {'value': 'no score'}
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

## Lua Expressions

Enable powerful filtering, grouping, sorting, and extraction with Lua expressions:
- **Filtering**: `"age > 25"`, `"score >= 80"`, `"name == 'Alice'"`
- **Complex conditions**: `"age > 25 and score >= 80"`, `"status == 'active' or priority == 'high'"`
- **Grouping**: `"age >= 30 and 'senior' or 'junior'"` (returns group key)
- **Sorting**: `"age * -1"` (reverse age), `"string.lower(name)"` (case-insensitive)
- **Extraction**: `"string.upper(name)"`, `"age > 18 and name or 'minor'"`
- **Math**: `"math.abs(score - 50)"`, `"x*x + y*y"` (distance squared)
- **Null handling**: `"item == null"`, `"age ~= null"`, `"item[2] == null"` (JSON null becomes `null`)

You can pass either a single Lua expression (e.g., `"age > 25"`) or a block of Lua code with one or more statements. For multi-line code, use the `return` statement to specify the value to return. For example:

```lua
if age > 25 then
  return 'adult'
end
return 'young'
```

Available functions: `math.*`, `string.*`, `os.time/date/clock`, `type()`, `tonumber()`, `tostring()`. Dictionary keys accessible directly (`age`, `name`) or via `item.key`.

In all Lua expressions, the special variable `item` is always available and refers to the current object (which may be a dictionary, string, number, or other value).

**Null Handling**: JSON null values become `null` table (not Lua `nil`). This is because Lua does not support `nil` as a list value—using `nil` would remove the element from the list. Important: `null` is truthy, use `== null` for null checks, `type(null)` returns "table". This preserves array indices and enables consistent null checking.

## Error Handling

All tools return a dictionary with a 'value' key. If an error occurs (e.g., invalid input type, missing parameter, unknown operation), the dictionary will also include an 'error' key with a descriptive message.

## Type Handling

All tools only accept JSON-serializable types. For type-agnostic checks (e.g., is_empty, is_equal, contains), use the `any` tool.

## License

Lever MCP is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
