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

If you are integrating Lever MCP with an AI-assisted coding editor (such as Cursor or Windsurf), be sure to load the [lever-rules.md](./docs/lever-rules.md) file into your editor's rules for the coding agent/AI assistant. This file provides best practices and guidance for the agent, ensuring it uses Lever MCP tools efficiently and according to recommended patterns:
- Prefer built-in Lever MCP tools for data operations
- Apply best practices for data transformation, list/set operations, and more
- Use efficient, maintainable patterns for code generation
- Handle errors and edge cases appropriately

While human users and contributors may also find the document informative, its primary audience is the coding agent. Loading these rules is recommended for anyone developing or configuring an AI coding assistant to ensure high-quality, consistent use of Lever MCP's capabilities.

### Expression Engine Configuration

Lever MCP supports two expression engines: **JavaScript (default)** and **Lua**. Both run in **safe mode** by default, which blocks potentially dangerous operations:

**JavaScript (Default Engine):**
- **Blocked**: Python bridge, eval(), Function(), WebAssembly, file I/O, network access
- **Allowed**: Modern JavaScript syntax, JSON operations, math functions, string methods, array methods

**Lua Engine:**
- **Blocked**: File I/O (`io.*`), system commands (`os.execute`), module loading (`require`)
- **Allowed**: Math operations, string functions, time/date functions, comparisons

**Switching Expression Engines:**
```bash
# Use JavaScript expressions (default)
python main.py

# Use Lua expressions instead
python main.py --lua
./run.sh --lua
```

**Disabling Safety Rails:**
```bash
# Disable safety for trusted environments (both JavaScript and Lua)
python main.py --unsafe
./run.sh --unsafe

# Combine with engine selection
python main.py --lua --unsafe
```

This enables full access to dangerous operations in both engines.

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
- `--unsafe`: Disable safety rails for both Lua and JavaScript (allows file I/O, system commands, and dangerous operations)
- `--lua`: Use Lua expressions instead of JavaScript expressions (default is JavaScript)

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
    - 'slice': Extracts substring (requires data={'from': int, 'to': int}).
    - 'snake_case': Converts to snake_case (e.g., 'foo bar' → 'foo_bar').
    - 'split': Splits string into array by delimiter (param: str delimiter).
    - 'starts_with': Checks if string starts with substring (param: str).
    - 'template': Interpolates variables using {var} syntax (requires data dict with variable mappings).
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
strings('a,b,c', 'split', ',')  # => {'value': ['a', 'b', 'c']}
strings('hello', 'slice', data={'from': 1, 'to': 4})  # => {'value': 'ell'}
```

---

### lists
Performs list operations, including merge, set/get value, and property checks.

**Note:** For details on using expressions in filtering, grouping, sorting, and extraction, see the [JavaScript Expressions](#javascript-expressions) and [Lua Expressions](#lua-expressions) sections below.

**Parameters:**
- `items` (list): The input list to operate on.
- `operation` (str): The operation to perform. Key operations include:
    - 'all_by'/'every': Return True if all items satisfy the expression
    - 'any_by'/'some': Return True if any item satisfies the expression
    - 'chunk': Split into chunks (param: int)
    - 'compact': Remove falsy values
    - 'contains': Check if item exists (param: value)
    - 'count_by': Count occurrences by expression result
    - 'difference': Items in first not in second (others: list)
    - 'difference_by': Items in first list not matching expression in second
    - 'drop': Drop n elements from start (param: int)
    - 'drop_right': Drop n elements from end (param: int)
    - 'filter_by': Return all items matching the expression (predicate)
    - 'find_by': Find first item matching expression
    - 'flat_map': Like map, but flattens one level if the mapping returns lists
    - 'flatten': Flatten one level (non-list elements are preserved as-is)
    - 'flatten_deep': Flatten completely
    - 'group_by': Group items by expression result
    - 'head': First element
    - 'index_of': Find index of item (expression: Lua expression)
    - 'initial': All but last element
    - 'intersection': Items in both lists (others: list)
    - 'intersection_by': Items in first list matching expression in second
    - 'is_empty': Check if list is empty
    - 'is_equal': Check if lists are equal (param: list)
    - 'join': Join list items into string with delimiter (param: str delimiter)
    - 'key_by': Create dict keyed by expression result
    - 'last': Last element
    - 'map': Apply a Lua expression to each item and return the transformed list
    - 'max': Find maximum value in list
    - 'max_by': Find max by expression result
    - 'min': Find minimum value in list
    - 'min_by': Find min by expression result
    - 'nth': Get nth element (param: int, supports negative indexing)
    - 'partition': Split by expression result/boolean
    - 'pluck': Extract values by expression (expression: any value)
    - 'random_except': Random item excluding condition (expression: Lua expression)
    - 'reduce': Aggregate the list using a binary Lua expression (uses 'acc' and 'item') with optional initial accumulator value (param)
    - 'remove_by': Remove items matching expression
    - 'sample': Get one random item
    - 'sample_size': Get n random items (param: int)
    - 'shuffle': Randomize order
    - 'sort_by': Sort by expression result (expression: any comparable value)
    - 'tail': All but first element
    - 'take': Take n elements from start (param: int)
    - 'take_right': Take n elements from end (param: int)
    - 'union': Unique values from all lists (items: list of lists)
    - 'uniq_by': Remove duplicates by expression result
    - 'unzip_list': Unzip list of lists (items: list of lists)
    - 'xor': Symmetric difference (others: list)
    - 'zip_lists': Zip multiple lists (items: list of lists)
    - 'zip_with': Combine two lists element-wise using a binary Lua expression (others: list, expression: uses 'item' and 'other')
- `others` (list, optional): Second list for set operations like difference/intersection
- `expression` (str, optional): JavaScript or Lua expression for advanced filtering/grouping/sorting/extraction

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Examples:**
```python
# Basic operations
lists([[1, [2, 3], 4], 5], 'flatten_deep')  # => {'value': [1, 2, 3, 4, 5]}
lists([1, 2, 3], 'difference', others=[2, 3])  # => {'value': [1]}
lists([3, 1, 4, 1, 5], 'min')  # => {'value': 1}
lists([3, 1, 4, 1, 5], 'max')  # => {'value': 5}
lists(['a', 'b', 'c'], 'join', param=',')  # => {'value': 'a,b,c'}

# Operations that take list of lists
lists([[1, 2], [3, 4]], 'zip_lists')  # => {'value': [[1, 3], [2, 4]]}
lists([[[1, 'a'], [2, 'b']], [[3, 'c']]], 'unzip_list')  # => {'value': [[1, 2], ['a', 'b']]}
lists([[1, 2], [2, 3], [3, 4]], 'union')  # => {'value': [1, 2, 3, 4]}

# Using expression for *_by operations
lists([{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}, {'id': 1, 'name': 'Alice'}], 'uniq_by', expression='id')  # => {'value': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}

# Expression-based operations (JavaScript syntax)
lists([{'age': 30, 'score': 85}, {'age': 20, 'score': 95}], 'find_by', expression="age > 25")
# => {'value': {'age': 30, 'score': 85}}

lists([{'score': 90}, {'score': 70}], 'filter_by', expression="score >= 80")
# => {'value': [{'score': 90}]}

lists([{'age': 30}, {'age': 20}], 'group_by', expression="age >= 25 ? 'adult' : 'young'")
# => {'value': {'adult': [{'age': 30}], 'young': [{'age': 20}]}}

# Modern JavaScript features
lists([{'name': 'bob'}, {'name': 'Alice'}], 'sort_by', expression="name.toLowerCase()")
# => {'value': [{'name': 'Alice'}, {'name': 'bob'}]}

lists([{'x': 1, 'y': 2}, {'x': 3, 'y': 4}], 'map', expression="x + y")
# => {'value': [3, 7]}

# Using index and items parameters (JavaScript 0-based indexing)
lists(['a', 'b', 'c'], 'map', expression="`${item}${index}`")
# => {'value': ['a0', 'b1', 'c2']}

lists(['x', 'y', 'z'], 'filter_by', expression="index < 2")
# => {'value': ['x', 'y']}

lists([10, 20, 30], 'map', expression="item / items.length")
# => {'value': [0.333..., 0.666..., 1.0]}
```

---

### dicts
Performs dictionary operations, including merge, set/get value, and property checks.

**Parameters:**
- `obj` (dict or list): The source dictionary, or a list of dicts for 'merge'. Must be a dict for all operations except 'merge'.
- `operation` (str): The operation to perform. One of:
    - 'flatten_keys': Flattens nested dict with dot notation (e.g., {'a': {'b': 1}} → {'a.b': 1}).
    - 'get_value': Gets a deep property by path (path: str dot-notation like "a.b.c" or list like ["a","b","c"], default: any).
    - 'has_key': Checks if a dict has a given key (param: str).
    - 'invert': Swaps keys and values.
    - 'is_empty': Checks if the dict is empty.
    - 'is_equal': Checks if two dicts are deeply equal (param: dict to compare).
    - 'items': Gets key-value pairs as list of tuples.
    - 'keys': Gets all dictionary keys as list.
    - 'map_keys': Transforms all keys with JavaScript or Lua expression (expression: str).
    - 'map_values': Transforms all values with JavaScript or Lua expression (expression: str).
    - 'merge': Deep merges a list of dictionaries (obj must be a list of dicts).
    - 'omit': Omits specified keys (param: list of keys).
    - 'pick': Picks specified keys (param: list of keys).
    - 'set_value': Sets a deep property by path (path: str dot-notation like "a.b.c" or list like ["a","b","c"], value: any).
    - 'unflatten_keys': Unflattens dot-notation keys to nested dict (e.g., {'a.b': 1} → {'a': {'b': 1}}).
    - 'values': Gets all dictionary values as list.
- `param` (Any, optional): Used for 'pick', 'omit', 'has_key', 'is_equal'.
- `path` (str or list, optional): Used for 'set_value' and 'get_value'.
- `value` (Any, optional): Used for 'set_value'.
- `default` (Any, optional): Used for 'get_value'.
- `expression` (str, optional): JavaScript or Lua expression for 'map_keys' and 'map_values'.

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Example:**
```python
# Basic operations
dicts({'a': 1, 'b': 2}, 'pick', ['a'])  # => {'value': {'a': 1}}
dicts({'a': {'b': 1}}, 'set_value', path=['a', 'b'], value=2)  # => {'value': {'a': {'b': 2}}}
dicts({'a': 1}, 'get_value', path='b', default=42)  # => {'value': 42}

# New operations
dicts({'a': 1, 'b': 2, 'c': 3}, 'keys')  # => {'value': ['a', 'b', 'c']}
dicts({'a': 1, 'b': 2, 'c': 3}, 'values')  # => {'value': [1, 2, 3]}
dicts({'a': 1, 'b': 2}, 'items')  # => {'value': [['a', 1], ['b', 2]]}

# Transformation operations with JavaScript expressions
dicts({'name': 'john', 'age': 30}, 'map_keys', expression="key.toUpperCase()")  # => {'value': {'NAME': 'john', 'AGE': 30}}
dicts({'a': 1, 'b': 2}, 'map_values', expression="value * 2")  # => {'value': {'a': 2, 'b': 4}}

# Flattening operations
dicts({'a': {'b': {'c': 1}}, 'd': 2}, 'flatten_keys')  # => {'value': {'a.b.c': 1, 'd': 2}}
dicts({'a.b.c': 1, 'd': 2}, 'unflatten_keys')  # => {'value': {'a': {'b': {'c': 1}}, 'd': 2}}
```

---

### any
Performs type-agnostic property checks, comparisons, and expression evaluation.

**Note:** For details on using expressions in evaluation, see the [JavaScript Expressions](#javascript-expressions) and [Lua Expressions](#lua-expressions) sections below.

**Parameters:**
- `value` (Any): The value to check or use as context for expression evaluation.
- `operation` (str): The operation to perform. One of:
    - 'contains': Checks if a string or list contains a value (param: value to check).
    - 'eval': Evaluate a JavaScript or Lua expression with value as context (expression: code).
    - 'is_empty': Checks if the value is empty.
    - 'is_equal': Checks if two values are deeply equal (param: value to compare).
    - 'is_nil': Checks if the value is None.
    - 'size': Gets the size/length of any collection type (strings, lists, dicts) or 1 for scalars.
- `param` (Any, optional): The parameter for the operation, if required.
- `expression` (str, optional): JavaScript or Lua expression to evaluate (for 'eval' operation).

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

# Size operations
any('hello', 'size')  # => {'value': 5}
any([1, 2, 3, 4], 'size')  # => {'value': 4}
any({'a': 1, 'b': 2}, 'size')  # => {'value': 2}
any(42, 'size')  # => {'value': 1}
any(None, 'size')  # => {'value': 0}

# Expression evaluation (JavaScript syntax)
any({'age': 30, 'name': 'Alice'}, 'eval', expression="age > 25")  # => {'value': True}
any({'x': 3, 'y': 4}, 'eval', expression="Math.sqrt(x*x + y*y)")  # => {'value': 5.0}
any("hello", 'eval', expression="value.toUpperCase()")  # => {'value': 'HELLO'}
any([1, 2, 3, 4, 5], 'eval', expression="value.length")  # => {'value': 5} (length)
any(42, 'eval', expression="value * 2 + 1")  # => {'value': 85}

# Null handling (important: null is falsy in JavaScript!)
any(None, 'eval', expression="value === null")  # => {'value': True}
any({'score': None}, 'eval', expression="score !== null ? 'has score' : 'no score'")  # => {'value': 'no score'}
```

---

### generate
Generates sequences or derived data using the specified operation.

**Parameters:**
- `options` (dict): Configuration options for the operation (parameter names vary by operation).
- `operation` (str): The operation to perform. Supported operations:
    - 'accumulate': Running totals. options: {'items': list, 'func': 'add'/'mul'/'max'/'min'/'sub'/'div'/None (default: addition)}
    - 'cartesian_product': Cartesian product of multiple lists. options: {'lists': list_of_lists}
    - 'combinations': All combinations of a given length. options: {'items': list, 'length': int}
    - 'cycle': Cycle through the sequence repeatedly to produce exactly count elements. options: {'items': list, 'count': int}
    - 'permutations': All permutations of a given length. options: {'items': list, 'length': int (optional)}
    - 'powerset': All possible subsets of a list. options: {'items': list}
    - 'range': Generate a list of numbers from start to end. options: {'from': int, 'to': int, 'step': int (optional)}
    - 'repeat': Repeat a value a specified number of times. options: {'value': any, 'count': int}
    - 'unique_pairs': All unique pairs from a list. options: {'items': list}
    - 'windowed': Sliding windows of a given size. options: {'items': list, 'size': int}
    - 'zip_with_index': Tuples of (index, value). options: {'items': list}

**Returns:**
- `dict`: Always returns a dictionary with a 'value' key containing the result. If an error occurs, the dict will also have an 'error' key.

**Usage Example:**
```python
generate({'from': 0, 'to': 5}, 'range')  # => {'value': [0, 1, 2, 3, 4]}
generate({'value': 'x', 'count': 3}, 'repeat')  # => {'value': ['x', 'x', 'x']}
generate({'items': [1, 2, 3], 'func': None}, 'accumulate')  # => {'value': [1, 3, 6]} (running sum)
generate({'items': [1, 2], 'count': 5}, 'cycle')  # => {'value': [1, 2, 1, 2, 1]}
generate({'items': [1, 2, 3], 'length': 2}, 'combinations')  # => {'value': [[1, 2], [1, 3], [2, 3]]}
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
        {"tool": "lists", "params": {"operation": "sort_by", "expression": "id"}}
    ]
)
# => {'value': [{"id": 1}, {"id": 2}}
```

---

## JavaScript Expressions

Enable powerful filtering, grouping, sorting, and extraction with modern JavaScript syntax:

**Basic Operations:**
- **Filtering**: `age > 25`, `score >= 80`, `name === 'Alice'`
- **Complex conditions**: `age > 25 && score >= 80`, `status === 'active' || priority === 'high'`
- **Grouping**: `age >= 30 ? 'senior' : 'junior'` (returns group key)
- **Sorting**: `age * -1` (reverse age), `name.toLowerCase()` (case-insensitive)
- **Extraction**: `name.toUpperCase()`, `age > 18 ? name : 'minor'`
- **Math**: `Math.abs(score - 50)`, `x*x + y*y` (distance squared)
- **Null handling**: `item === null`, `age !== null`, `item[2] === null`

**Modern JavaScript Features:**
- **Arrow functions**: `[1,2,3].map(x => x * 2)`, `users.filter(u => u.age > 25)`
- **Template literals**: `` `Hello ${name}!` ``, `` `Score: ${Math.round(score)}` ``
- **Destructuring**: `const {name, age} = user; return name + age`
- **Spread operator**: `[...arr1, ...arr2]`, `{...obj1, ...obj2}`
- **Modern array methods**: `array.includes(item)`, `array.find(x => x.id === 1)`

**Expression Context:**
In JavaScript expressions, the parameter name varies by tool:
- **lists operations**: `item` (current element), `index` (0-based position), `items` (full array)
- **lists.zip_with**: `item` (from first array), `other` (from second array)
- **dicts.map_keys**: `key` (current key), `value` (current value), `obj` (original object)
- **dicts.map_values**: `value` (current value), `key` (current key), `obj` (original object)
- **any.eval**: `value` (input value being evaluated)

**Type System:**
- `typeof value`, `Array.isArray(value)`, `value instanceof Array`
- `Number.isInteger(value)`, `Number.isFinite(value)`
- JavaScript truthy/falsy behavior: `!!value`, `value || 'default'`, `value && 'exists'`

**Examples:**
```javascript
// Arrow functions in list operations
[1, 2, 3].map(x => x * 2)  // => [2, 4, 6]
users.filter(u => u.age > 25 && u.active)

// Template literals with expressions
`User ${name.toUpperCase()} scored ${score}/100`

// Modern destructuring and spread
const {name, ...rest} = user; return {...rest, fullName: name}

// Complex filtering with chaining
items.filter(item => item.price > 10)
     .map(item => ({...item, discounted: item.price * 0.9}))
     .sort((a, b) => a.name.localeCompare(b.name))

// Error handling with try/catch
try { return user.profile.settings.theme; }
catch (e) { return 'default'; }

// JSON operations
JSON.stringify(data)
JSON.parse(jsonString)
```

You can pass either a single JavaScript expression or a block of JavaScript code. For multi-line code, use `return` to specify the value:

```javascript
if (age >= 18) {
  return status === 'student' ? 'student_adult' : 'adult';
} else {
  return 'minor';
}
```

**Available APIs**: `Math.*`, `String.prototype.*`, `Array.prototype.*`, `Object.*`, `JSON.*`, `Date.*`, standard JavaScript operators and control flow.

### Tool Function References in Expressions

You can use tool functions directly as expressions, enabling powerful functional programming patterns:

**Basic function references:**
```javascript
// Partition strings by whether they're all digits
lists.partition(["123", "abc", "456", "def"], "strings.is_digit")
// => [["123", "456"], ["abc", "def"]]

// Filter to keep only alphabetic strings
lists.filter_by(["hello", "world123", "test"], "strings.is_alpha")
// => ["hello", "test"]

// Transform all strings to uppercase
lists.map(["hello", "world"], "strings.upper_case")
// => ["HELLO", "WORLD"]
```

**Advanced function reference patterns:**
```javascript
// Group by result of function call
lists.group_by(["123", "abc", "456"], "strings.is_digit")
// => {true: ["123", "456"], false: ["abc"]}

// Check if all items satisfy a condition
lists.all_by(["hello", "world", "test"], "strings.is_alpha")
// => true

// Check if any items satisfy a condition
lists.any_by(["hello", "123", "world"], "strings.is_digit")
// => true

// Sort using function transformation
lists.sort_by(["  hello  ", "  world  "], "strings.trim")
// => ["  hello  ", "  world  "] (sorted by trimmed values)
```

**Nested function calls in expressions:**
```javascript
// Chain multiple functions within expressions
lists.map(["  HELLO  ", "  WORLD  "], "strings.lower_case(strings.trim(item))")
// => ["hello", "world"]

// Use tool functions in complex expressions
lists.filter_by(users, "strings.contains(email, '@gmail.com')")
// Filter users with Gmail addresses
```

---

## JavaScript Function Calls

Lever MCP tools are exposed as JavaScript functions, enabling powerful expression-based data transformations. You can call tools directly from JavaScript expressions using either positional or object syntax.

### Function Call Syntax

**Positional syntax:**
```javascript
strings.upper_case("hello")  // => "HELLO"
lists.head([1, 2, 3])       // => 1
dicts.has_key({a: 1}, "a")   // => true
any.is_equal(42, 42)         // => true
```

**Object syntax (recommended for complex parameters):**
```javascript
strings.replace({text: "hello world", data: {old: "world", new: "JavaScript"}})  // => "hello JavaScript"
lists.filter_by({items: [{age: 25}, {age: 30}], expression: "age > 25"})  // => [{age: 30}]
dicts.get_value({obj: {a: {b: 1}}, path: "a.b"})  // => 1
```

### Function Returns

Functions return their direct values when called (not wrapped in `{value: ...}`):
```javascript
// In JavaScript expressions, functions return the value directly
const name = strings.upper_case("alice")  // name = "ALICE"
const first = lists.head(["a", "b", "c"]) // first = "a"
const empty = any.is_empty("")           // empty = true

// You can chain function calls
const result = strings.upper_case(lists.head(["hello", "world"]))  // => "HELLO"
```

### Advanced Examples

**Nested tool calls in expressions:**
```javascript
// Use lists functions in expressions
lists.map({items: [{name: "alice"}, {name: "bob"}], expression: "strings.upper_case(name)"})
// => ["ALICE", "BOB"]

// Complex data transformations
lists.filter_by({
  items: [{name: "Alice", age: 25}, {name: "Bob", age: 17}],
  expression: "age >= 18"
})
// => [{name: "Alice", age: 25}]

// String processing in list operations
lists.sort_by({
  items: [{name: "charlie"}, {name: "alice"}, {name: "bob"}],
  expression: "strings.lower_case(name)"
})
// => [{name: "alice"}, {name: "bob"}, {name: "charlie"}]
```

**Using any.eval for complex logic:**
```javascript
any.eval({score: 85, passed: true}, `
  if (passed && score >= 80) {
    return "excellent";
  } else if (passed) {
    return "good";
  } else {
    return "needs improvement";
  }
`)
// => "excellent"
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

Available functions: `math.*`, `string.*`, `os.time/date/clock`, `type()`, `tonumber()`, `tostring()`. Dictionary keys accessible directly (`age`, `name`) or via property access.

In Lua expressions, the parameter name varies by tool:
- **lists operations**: `item` refers to the current list element, `index` refers to the current position (1-based), `items` refers to the full list
- **lists.zip_with**: `item` refers to the current element from the first list, `other` refers to the current element from the second list
- **dicts.map_keys**: `key` refers to the current dictionary key (string), `value` refers to the current dictionary value, `obj` refers to the original dictionary
- **dicts.map_values**: `value` refers to the current dictionary value, `key` refers to the current dictionary key (string), `obj` refers to the original dictionary. If `value` is a dict, its properties are accessible directly
- **any.eval**: `value` refers to the input value being evaluated

**Null Handling**: JSON null values become `null` table (not Lua `nil`). This is because Lua does not support `nil` as a list value—using `nil` would remove the element from the list. Important: `null` is truthy, use `== null` for null checks, `type(null)` returns "table". This preserves array indices and enables consistent null checking.

### Tool Function References in Expressions

You can use tool functions directly as expressions, enabling powerful functional programming patterns:

**Basic function references:**
```lua
-- Partition strings by whether they're all digits
lists.partition({"123", "abc", "456", "def"}, "strings.is_digit")
-- => [["123", "456"], ["abc", "def"]]

-- Filter to keep only alphabetic strings
lists.filter_by({"hello", "world123", "test"}, "strings.is_alpha")
-- => ["hello", "test"]

-- Transform all strings to uppercase
lists.map({"hello", "world"}, "strings.upper_case")
-- => ["HELLO", "WORLD"]
```

**Advanced function reference patterns:**
```lua
-- Group by result of function call
lists.group_by({"123", "abc", "456"}, "strings.is_digit")
-- => {"True": ["123", "456"], "False": ["abc"]}

-- Check if all items satisfy a condition
lists.all_by({"hello", "world", "test"}, "strings.is_alpha")
-- => true

-- Check if any items satisfy a condition
lists.any_by({"hello", "123", "world"}, "strings.is_digit")
-- => true

-- Sort using function transformation
lists.sort_by({"  hello  ", "  world  "}, "strings.trim")
-- => ["  hello  ", "  world  "] (sorted by trimmed values)
```

**Nested function calls in expressions:**
```lua
-- Chain multiple functions within expressions
lists.map({"  HELLO  ", "  WORLD  "}, "strings.lower_case(strings.trim(item))")
-- => ["hello", "world"]

-- Use tool functions in complex expressions
lists.filter_by(users, "strings.contains(email, '@gmail.com')")
-- Filter users with Gmail addresses
```

---

## Lua Function Calls

Lever MCP tools are exposed as Lua functions, enabling powerful expression-based data transformations. You can call tools directly from Lua expressions using either positional or table syntax.

### Function Call Syntax

**Positional syntax:**
```lua
strings.upper_case("hello")  -- => "HELLO"
lists.head({1, 2, 3})       -- => 1
dicts.has_key({a=1}, "a")   -- => true
any.is_equal(42, 42)        -- => true
```

**Table syntax (recommended for complex parameters):**
```lua
strings.replace({text="hello world", data={old="world", new="Lua"}})  -- => "hello Lua"
lists.filter_by({items={{age=25}, {age=30}}, expression="age > 25"})  -- => [{"age": 30}]
dicts.get_value({obj={a={b=1}}, path="a.b"})  -- => 1
```

### Type Disambiguation and Wrapping

In Lua, empty tables `{}` are ambiguous—they could represent empty lists or empty dictionaries. For proper JSON serialization, Lever MCP provides wrapper functions and a `wrap` parameter:

**Wrapper Functions:**
```lua
-- Type disambiguation for empty collections
list({})    -- => {"__type": "list", "data": []}
dict({})    -- => {"__type": "dict", "data": {}}

-- Unwrap wrapped objects
unwrap(list({}))  -- => {} (gets original table)
unwrap(dict({}))  -- => {} (gets original table)
```

**Wrap Parameter:**
```lua
-- Use wrap=true to get wrapped lists/dicts in results
lists.map({items={1, 2}, expression="{}", wrap=true})
-- => {"__type": "list", "data": [{"__type": "dict", "data": {}}, {"__type": "dict", "data": {}}]}

-- Without wrap parameter, results are unwrapped
lists.map({items={1, 2}, expression="{}"})
-- => [{}, {}]
```

The `wrap` parameter is available for all tools (`strings`, `lists`, `dicts`, `any`, `generate`) in the Lua implementation. When `wrap=true`, all lists and dictionaries in the result are recursively wrapped with type information.

### Function Returns

Functions return their direct values when called (not wrapped in `{value: ...}`):
```lua
-- In Lua expressions, functions return the value directly
local name = strings.upper_case("alice")  -- name = "ALICE"
local first = lists.head({"a", "b", "c"}) -- first = "a"
local empty = any.is_empty("")           -- empty = true

-- You can chain function calls
local result = strings.upper_case(lists.head({"hello", "world"}))  -- => "HELLO"
```

### Advanced Examples

**Nested tool calls in expressions:**
```lua
-- Use lists functions in expressions
lists.map({items={{"name": "alice"}, {"name": "bob"}}, expression="strings.upper_case(name)"})
-- => ["ALICE", "BOB"]

-- Complex data transformations
lists.filter_by({
  items={{name="Alice", age=25}, {name="Bob", age=17}},
  expression="age >= 18"
})
-- => [{"name": "Alice", "age": 25}]

-- String processing in list operations
lists.sort_by({
  items={{"name": "charlie"}, {"name": "alice"}, {"name": "bob"}},
  expression="strings.lower_case(name)"
})
-- => [{"name": "alice"}, {"name": "bob"}, {"name": "charlie"}]
```

**Using any.eval for complex logic:**
```lua
any.eval({score=85, passed=true}, [[
  if passed and score >= 80 then
    return "excellent"
  elseif passed then
    return "good"
  else
    return "needs improvement"
  end
]])
-- => "excellent"
```

---

## All Available Functions

- **strings**: `camel_case`, `capitalize`, `contains`, `deburr`, `ends_with`, `is_alpha`, `is_digit`, `is_empty`, `is_equal`, `is_lower`, `is_upper`, `kebab_case`, `lower_case`, `replace`, `reverse`, `sample_size`, `shuffle`, `snake_case`, `starts_with`, `template`, `trim`, `upper_case`, `xor`

- **lists**: `all_by`, `any_by`, `chunk`, `compact`, `contains`, `count_by`, `difference`, `difference_by`, `drop`, `drop_right`, `every`, `filter_by`, `find_by`, `flat_map`, `flatten`, `flatten_deep`, `group_by`, `head`, `index_of`, `initial`, `intersection`, `intersection_by`, `is_empty`, `is_equal`, `key_by`, `last`, `map`, `max_by`, `min_by`, `nth`, `partition`, `pluck`, `random_except`, `reduce`, `remove_by`, `sample`, `sample_size`, `shuffle`, `some`, `sort_by`, `tail`, `take`, `take_right`, `union`, `uniq_by`, `unzip_list`, `xor`, `zip_lists`, `zip_with`

- **dicts**: `get_value`, `has_key`, `invert`, `is_empty`, `is_equal`, `merge`, `omit`, `pick`, `set_value`

- **any**: `contains`, `eval`, `is_empty`, `is_equal`, `is_nil`

- **generate**: `accumulate`, `cartesian_product`, `combinations`, `cycle`, `permutations`, `powerset`, `range`, `repeat`, `unique_pairs`, `windowed`, `zip_with_index`

---

## Error Handling

All tools return a dictionary with a 'value' key. If an error occurs (e.g., invalid input type, missing parameter, unknown operation), the dictionary will also include an 'error' key with a descriptive message.

## Type Handling

All tools only accept JSON-serializable types. For type-agnostic checks (e.g., is_empty, is_equal, contains), use the `any` tool.

## License

Lever MCP is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
