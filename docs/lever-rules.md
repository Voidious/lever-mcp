# Lever MCP Tool Usage Rules

**Purpose:**
These rules are designed to be loaded into the rules of an AI-assisted coding editor (such as Cursor or Windsurf). They provide best practices and examples for using Lever MCP tools efficiently, encouraging maintainable, high-quality code by leveraging built-in utilities for data transformation, list/set operations, and more.

## 1. Prefer Built-in Lever MCP Tools
- Always use the provided Lever MCP tools for data operations (e.g., grouping, sorting, flattening, extracting, set operations) instead of custom code.
- Lever tools are optimized for batch processing and clarity.
- Use the correct MCP tool syntax with named parameters.

*MCP Tool Example:*
```python
# Instead of manual iteration:
result = [x['id'] for x in items]
# Use MCP tool:
result = lists(items, 'pluck', key='id')['value']
```

*Lua Function Example:*
```lua
-- In Lua expressions, use direct function calls:
local result = lists.pluck(items, "id")
```

## 2. Data Transformation with Lists Tool
- Use `lists` tool with `group_by` operation to organize items by a property.
- Use `sort_by` to sort lists of objects by a property or expression.
- Use `pluck` to extract values from objects using a key or expression.
- Use `flatten` for one-level flattening, and `flatten_deep` for deeply nested lists.
- Use `compact` to remove falsy values (`None`, `False`, `0`, `''`, etc.).

*MCP Tool Examples:*
```python
# Group users by role:
grouped = lists(users, 'group_by', key='role')['value']
# Sort by score (descending):
sorted_items = lists(items, 'sort_by', expression='score * -1')['value']
# Extract names with transformation:
names = lists(users, 'pluck', expression='string.upper(name)')['value']
```

*Lua Function Examples:*
```lua
-- Group users by role:
local grouped = lists.group_by(users, "role")
-- Sort by score (descending):
local sorted_items = lists.sort_by(users, "score * -1")
-- Extract and transform names:
local names = lists.pluck(users, "strings.upper_case(name)")
```

## 3. List Operations
- Use `chunk` to split a list into fixed-size chunks.
- Use `partition` to split a list into two lists based on an expression.
- Use `zip_lists` to combine lists element-wise, and `unzip_list` to separate them.
- Use `take`, `drop`, `head`, `last`, `tail` for list slicing and access.

*MCP Tool Examples:*
```python
# Chunk a list into groups of 3:
chunks = lists(items, 'chunk', param=3)['value']
# Partition by active status:
result = lists(users, 'partition', key='is_active')['value']
active, inactive = result[True], result[False]
# Take first 5 items:
first_five = lists(items, 'take', param=5)['value']
```

*Lua Function Examples:*
```lua
-- Chunk a list into groups of 3:
local chunks = lists.chunk(items, 3)
-- Partition by active status:
local partitioned = lists.partition(users, "is_active")
-- Take first 5 items:
local first_five = lists.take(items, 5)
```

## 4. Set-Like Operations
- Use `uniq_by` to remove duplicates from a list based on a property.
- Use `difference`, `intersection`, `union`, `xor` for set operations.
- Use `difference_by`, `intersection_by` for property-based set operations.

*MCP Tool Examples:*
```python
# Remove duplicate users by id:
unique_users = lists(users, 'uniq_by', key='id')['value']
# Find items in first list but not second:
diff = lists(all_items, 'difference', others=excluded_items)['value']
# Find new users not in old list:
new_users = lists(all_users, 'difference_by', others=old_users, key='id')['value']
```

*Lua Function Examples:*
```lua
-- Remove duplicate users by id:
local unique_users = lists.uniq_by(users, "id")
-- Find set difference:
local diff = lists.difference(all_items, excluded_items)
-- Find new users:
local new_users = lists.difference_by(all_users, old_users, "id")
```

## 5. Dictionary Utilities with Dicts Tool
- Use `dicts` tool with `set_value` to set a value at a deep path.
- Use `get_value` to retrieve a value from a deep path, with optional default.
- Use `invert` to swap keys and values.
- Use `pick` and `omit` to select or exclude keys from a dictionary.
- Use `merge` to deep merge multiple dictionaries.

*MCP Tool Examples:*
```python
# Set a nested value:
config = dicts(config, 'set_value', path=['db', 'host'], value='localhost')['value']
# Get a nested value with default:
host = dicts(config, 'get_value', path='db.host', default='127.0.0.1')['value']
# Pick specific keys:
subset = dicts(user, 'pick', param=['name', 'email'])['value']
```

*Lua Function Examples:*
```lua
-- Set a nested value:
local config = dicts.set_value(config, {"db", "host"}, "localhost")
-- Get a nested value with default:
local host = dicts.get_value(config, "db.host", "127.0.0.1")
-- Pick specific keys:
local subset = dicts.pick(user, {"name", "email"})
```

## 6. String Utilities with Strings Tool
- Use `strings` tool for case conversion, formatting, and validation.
- Use `template` to interpolate variables into a string using `{var}` syntax.
- Use `replace` for substring replacement with data parameter.

*MCP Tool Examples:*
```python
# Convert to snake_case:
snake = strings('Hello World!', 'snake_case')['value']
# Interpolate variables:
greeting = strings('Hello, {name}!', 'template', data={'name': 'Alice'})['value']
# Replace text:
result = strings('hello world', 'replace', data={'old': 'world', 'new': 'universe'})['value']
```

*Lua Function Examples:*
```lua
-- Convert to snake_case:
local snake = strings.snake_case("Hello World!")
-- Interpolate variables:
local greeting = strings.template("Hello, {name}!", {name="Alice"})
-- Replace text:
local result = strings.replace("hello world", {old="world", new="universe"})
```

## 7. Functional Operations with Expressions
- Use Lua expressions for complex filtering, mapping, and transformations.
- Use `filter_by`, `map`, `reduce` with expressions for powerful data processing.
- Use `all_by`, `any_by` to test conditions across lists.

*MCP Tool Examples:*
```python
# Filter users over 18:
adults = lists(users, 'filter_by', expression='age >= 18')['value']
# Transform with complex logic:
processed = lists(items, 'map', expression='score > 80 and "pass" or "fail"')['value']
# Check if all items meet condition:
all_valid = lists(items, 'all_by', expression='price > 0 and quantity > 0')['value']
```

*Lua Function Examples:*
```lua
-- Filter users over 18:
local adults = lists.filter_by(users, "age >= 18")
-- Transform with complex logic:
local processed = lists.map(items, 'score > 80 and "pass" or "fail"')
-- Check if all items meet condition:
local all_valid = lists.all_by(items, "price > 0 and quantity > 0")
```

## 8. Type-Agnostic Operations with Any Tool
- Use `any` tool for operations that work on any data type.
- Use `eval` for complex expression evaluation with custom context.
- Use `is_equal`, `is_empty`, `is_nil` for type-safe comparisons.

*MCP Tool Examples:*
```python
# Evaluate complex expression:
result = any({'score': 85, 'passed': True}, 'eval',
             expression='score >= 80 and passed and "excellent" or "needs work"')['value']
# Type-safe equality:
equal = any(value1, 'is_equal', param=value2)['value']
```

*Lua Function Examples:*
```lua
-- Evaluate complex expression:
local result = any.eval({score=85, passed=true},
                       'score >= 80 and passed and "excellent" or "needs work"')
-- Type-safe equality:
local equal = any.is_equal(value1, value2)
```

## 9. Chaining Operations
- Use `chain` tool to compose multiple operations in sequence for complex transformations.
- Ensure output types are compatible between chained operations.
- Consider using Lua function chaining for simpler cases.

*MCP Tool Example:*
```python
# Chain multiple operations:
result = chain(users, [
    {'tool': 'lists', 'params': {'operation': 'filter_by', 'expression': 'age >= 18'}},
    {'tool': 'lists', 'params': {'operation': 'pluck', 'key': 'email'}},
    {'tool': 'lists', 'params': {'operation': 'compact'}}
])['value']
```

*Lua Function Example:*
```lua
-- Chain functions directly:
local result = lists.compact(lists.pluck(lists.filter_by(users, "age >= 18"), "email"))
```

## 10. Error Handling and Best Practices
- Always check for the 'error' key in MCP tool responses before using 'value'.
- Handle empty or unexpected results gracefully, especially when chaining.
- Use appropriate tools for data types (strings for strings, lists for lists, etc.).
- Prefer key-based operations over expressions when simple property access is sufficient.

*Example:*
```python
# Safe MCP tool usage:
result = lists(items, 'filter_by', expression='score > 80')
if 'error' in result:
    print(f"Error: {result['error']}")
else:
    filtered_items = result['value']
```

## 11. Lua Expression Best Practices
- Use `item` to refer to the current object in expressions.
- Use `null` (not `nil`) for null checks: `item == null`.
- Access nested properties: `item.user.name` or `user.name` (when item has user property).
- Use math and string functions: `math.abs(score)`, `string.upper(name)`.
- Combine conditions: `age >= 18 and score > 80`.

## 12. Tool Function References in Expressions
- Use tool functions directly as expressions for powerful functional programming.
- Pass function names as strings to operations like `filter_by`, `map`, `partition`.
- Combine tool functions within expressions for complex transformations.

*MCP Tool Examples:*
```python
# Partition strings by whether they're all digits
result = lists(items, 'partition', expression='strings.is_digit')['value']
# Filter to keep only alphabetic strings
filtered = lists(items, 'filter_by', expression='strings.is_alpha')['value']
# Transform using function reference
transformed = lists(items, 'map', expression='strings.upper_case')['value']
```

*Lua Function Examples:*
```lua
-- Partition by digit check
local partitioned = lists.partition(items, "strings.is_digit")
-- Filter alphabetic only
local filtered = lists.filter_by(items, "strings.is_alpha")
-- Transform to uppercase
local transformed = lists.map(items, "strings.upper_case")
-- Complex nested function calls
local cleaned = lists.map(items, "strings.lower_case(strings.trim(item))")
```

## 13. Performance Tips
- Use key-based operations when possible (faster than expressions).
- Prefer built-in operations over complex expressions.
- Use `compact` to remove null/empty values before further processing.
- Consider using `chunk` for processing large datasets in batches.
- Use tool function references for cleaner, more readable functional code.
