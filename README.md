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
- `mutation` (str): The type of mutation to perform. One of:
    - 'camel_case': Converts the string to camelCase (e.g., 'foo bar' → 'fooBar').
    - 'capitalize': Converts the first character to upper case and the rest to lower case (e.g., 'foo bar' → 'Foo bar').
    - 'deburr': Removes accents/diacritics from the string (e.g., 'Café' → 'Cafe').
    - 'kebab_case': Converts the string to kebab-case (e.g., 'foo bar' → 'foo-bar').
    - 'lower_case': Converts the string to all lowercase (e.g., 'Hello' → 'hello').
    - 'replace': Replaces all occurrences of a substring with another (requires data={'old': 'x', 'new': 'y'}). (e.g., 'foo bar foo', data={'old': 'foo', 'new': 'baz'} → 'baz bar baz')
    - 'reverse': Reverses the string (e.g., 'hello' → 'olleh').
    - 'snake_case': Converts the string to snake_case (e.g., 'foo bar' → 'foo_bar').
    - 'upper_case': Converts the string to all uppercase (e.g., 'Hello' → 'HELLO').
    - 'template': Interpolates variables in the string using {var} syntax. Requires 'data' dict (e.g., 'Hello, {name}!' with data={'name': 'World'} → 'Hello, World!').
    - 'trim': Removes leading and trailing whitespace (e.g., '  hello  ' → 'hello').
- `data` (Dict[str, Any], optional): Data for 'template' and 'replace' mutations.

**Returns:**
- `str`: The mutated string.

**Usage Example:**
```python
mutate_string('foo bar', 'camel_case')  # => 'fooBar'
mutate_string('Hello, {name}!', 'template', {'name': 'World'})  # => 'Hello, World!'
mutate_string('foo bar foo', 'replace', {'old': 'foo', 'new': 'baz'})  # => 'baz bar baz'
```

### mutate_list
Mutates a list according to the specified mutation type.

**Parameters:**
- `items` (List[Any]): The input list to mutate.
- `mutation` (str): The type of mutation to perform. One of:
    - 'chunk': Splits a list into chunks of a given size (param: int).
    - 'compact': Removes falsy values from a list.
    - 'drop': Drops n elements from the beginning (param: int).
    - 'drop_right': Drops n elements from the end (param: int).
    - 'flatten': Flattens a list one level deep.
    - 'flatten_deep': Flattens a nested list completely.
    - 'initial': Gets all but the last element.
    - 'partition': Splits a list into two lists based on a predicate key (param: str).
    - 'pluck': Extracts a list of values for a given key (param: str).
    - 'remove_by': Removes items where a property matches a value (param: {'key': str, 'value': Any}).
    - 'sample_size': Gets n random elements from the list (param: int).
    - 'shuffle': Shuffles the list.
    - 'sort_by': Sorts a list of objects by a key (param: str).
    - 'tail': Gets all but the first element.
    - 'take': Takes n elements from the beginning (param: int).
    - 'take_right': Takes n elements from the end (param: int).
    - 'union': Creates a list of unique values from all given lists.
    - 'uniq_by': Removes duplicates from a list of objects based on a key (param: str).
    - 'unzip_list': Unzips a list of tuples into separate lists.
    - 'xor': Creates a list of unique values that is the symmetric difference of the given lists.
    - 'zip_lists': Zips multiple lists into a list of tuples.
- `param` (Any, optional): A parameter for mutations that require one.

**Returns:**
- `List[Any]`: The mutated list.

**Usage Example:**
```python
mutate_list([[1, [2, 3], 4], 5], 'flatten_deep')  # => [1, 2, 3, 4, 5]
mutate_list([{'id': 1}, {'id': 2}], 'pluck', 'id')  # => [1, 2]
```

### has_property
Checks a property or relationship for the given object.

**Parameters:**
- `obj` (Any): The object or value to check.
- `property` (str): The property or operation to check. One of:
    - 'contains': Checks if a string contains a substring or a list contains an element (param: value to check).
    - 'ends_with': Checks if a string ends with the given target (param: str).
    - 'has_key': Checks if a dict has a given key (param: str).
    - 'is_alpha': Checks if a string consists only of alphabetic characters.
    - 'is_digit': Checks if a string consists only of digits.
    - 'is_empty': Checks if the value is empty.
    - 'is_equal': Checks if two values are deeply equal (param: value to compare).
    - 'is_lower': Checks if a string is all lowercase.
    - 'is_nil': Checks if the value is None.
    - 'is_upper': Checks if a string is all uppercase.
    - 'starts_with': Checks if a string starts with the given target (param: str).
- `param` (Any, optional): The parameter for the operation, if required.

**Returns:**
- `bool`: The result of the check.

**Usage Example:**
```python
has_property('abc', 'ends_with', 'c')  # => True
has_property({'a': 1}, 'has_key', 'a')  # => True
has_property('12345', 'is_digit')  # => True
```

### select_from_list
Selects an element from a list using various operations.

**Parameters:**
- `items` (list): The list to select from.
- `operation` (str): The operation to perform. One of:
    - 'find_by': Finds the first item where a property matches a value (param: {'key': str, 'value': Any}).
    - 'head': Gets the first element.
    - 'index_of': Returns the index of the first item where a property matches a value (param: {'key': str, 'value': Any}), or -1 if not found.
    - 'last': Gets the last element.
    - 'max_by': Gets the item with the maximum value for a property (param: property name).
    - 'min_by': Gets the item with the minimum value for a property (param: property name).
    - 'nth': Gets the nth element (param: integer index, supports negative for reverse).
    - 'random_except': Returns a random element from the list, excluding any that match a given property value (param: {'key': str, 'value': Any}).
    - 'sample': Gets a random element.
- `param` (Any, optional): Parameter for the operation (required for some operations).

**Returns:**
- `any`: The selected element or None if not found.

**Usage Example:**
```python
select_from_list([1, 2, 3], 'head')  # => 1
select_from_list([10, 20, 30], 'nth', 1)  # => 20
select_from_list([{'id': 1}, {'id': 2}], 'find_by', {'key': 'id', 'value': 2}) # => {'id': 2}
```

### compare_lists
Compares two lists using various set-like operations.

**Parameters:**
- `a` (list): The first list.
- `b` (list): The second list.
- `operation` (str): The operation to perform. One of:
    - 'difference': Values in a not in b (ignores key).
    - 'difference_by': Items in a not in b by property (requires key).
    - 'intersection': Unique values in both lists (ignores key).
    - 'intersection_by': Items in a also in b by property (requires key).
- `key` (str, optional): The property name for *_by operations.

**Returns:**
- `list`: The result of the comparison.

**Usage Example:**
```python
compare_lists([1, 2, 3], [2, 4], 'difference')  # => [1, 3]
compare_lists([{'id': 1}, {'id': 2}], [{'id': 2}], 'difference_by', 'id')  # => [{'id': 1}]
```

### process_list
Processes a list into a dictionary using grouping, counting, or keying by a property.

**Parameters:**
- `items` (list): The list of items (dicts or objects).
- `operation` (str): The operation to perform. One of:
    - 'count_by': Counts occurrences of property values.
    - 'group_by': Groups items by a property value.
    - 'key_by': Creates a dictionary with keys from a property.
- `key` (str): The property name to use.

**Returns:**
- `dict`: The resulting dictionary.

**Usage Example:**
```python
process_list([{'type': 'a'}, {'type': 'b'}, {'type': 'a'}], 'count_by', 'type')  # => {'a': 2, 'b': 1}
process_list([{'id': 'a'}, {'id': 'b'}], 'key_by', 'id')  # => {'a': {'id': 'a'}, 'b': {'id': 'b'}}
```

### process_dict
Performs dictionary operations.

**Parameters:**
- `obj` (dict): The source dictionary.
- `operation` (str): The operation to perform. One of:
    - 'invert': Swaps keys and values.
    - 'omit': Omits specified keys (param: list of keys).
    - 'pick': Picks specified keys (param: list of keys).
- `param` (list, optional): Keys to pick or omit (required for 'pick' and 'omit').

**Returns:**
- `dict`: The resulting dictionary.

**Usage Example:**
```python
process_dict({'a': 'x', 'b': 'y'}, 'invert')  # => {'x': 'a', 'y': 'b'}
process_dict({'a': 1, 'b': 2}, 'omit', ['a'])  # => {'b': 2}
process_dict({'a': 1, 'b': 2}, 'pick', ['a'])  # => {'a': 1}
```

### generate
Generates sequences or derived data from input using the specified operation.

**Parameters:**
- `input` (Any): The input list or value.
- `operation` (str): The operation to perform. One of:
    - 'accumulate': Running totals (or with a binary function if param is provided).
    - 'cartesian_product': Cartesian product of multiple input lists.
    - 'combinations': All combinations of a given length.
    - 'cycle': Repeat the sequence infinitely or up to param times.
    - 'permutations': All permutations of a given length.
    - 'powerset': All possible subsets of a list.
    - 'range': Generate a list of numbers from start to end.
    - 'repeat': Repeat a value or sequence a specified number of times.
    - 'unique_pairs': All unique pairs from a list.
    - 'windowed': Sliding windows of a given size.
    - 'zip_with_index': Tuples of (index, value).
- `param` (Any, optional): Parameter for the operation, if required.

**Returns:**
- `Any`: The generated sequence or result.

**Usage Example:**
```python
generate(None, 'range', [0, 5])  # => [0, 1, 2, 3, 4]
generate('x', 'repeat', 3)  # => ['x', 'x', 'x']
generate([1, 2, 3], 'powerset') # => [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
generate([[1, 2], ['a', 'b']], 'cartesian_product') # => [[1, 'a'], [1, 'b'], [2, 'a'], [2, 'b']]
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
        {"tool": "mutate_list", "params": {"mutation": "compact"}},
        {"tool": "mutate_list", "params": {"mutation": "sort_by", "param": None}}
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
merge([{"a": 1, "b": {"c": 2}}, {"b": {"d": 3}}])
# => {'a': 1, 'b': {'c': 2, 'd': 3}}
```

### set_value
Sets a deep property in a dictionary by path (dot/bracket notation or list).

**Parameters:**
- `obj` (dict): The dictionary to modify.
- `path` (str or list): The property path.
- `value` (any): The value to set.

**Returns:**
- `dict`: The modified dictionary.

**Usage Example:**
```python
set_value({"a": {"b": 1}}, "a.b", 2)  # => {'a': {'b': 2}}
```

### get_value
Gets a deep property from a dictionary by path (dot/bracket notation or list).

**Parameters:**
- `obj` (dict): The dictionary to access.
- `path` (str or list): The property path.
- `default` (any, optional): The value to return if the path does not exist.

**Returns:**
- `any`: The value at the specified path, or the default.

**Usage Example:**
```python
get_value({"a": {"b": 2}}, "a.b")  # => 2
get_value({"a": {"b": 2}}, "a.c", 42)  # => 42
```

## Contributing

Contributions are welcome! If you have ideas for new tools or improvements, please open an issue or submit a pull request.

## License

Lever MCP is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
