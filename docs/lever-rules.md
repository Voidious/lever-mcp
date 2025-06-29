# Lever MCP Tool Usage Rules

**Purpose:**
These rules are designed to be loaded into the rules of an AI-assisted coding editor (such as Cursor or Windsurf). They provide best practices and examples for using Lever MCP tools efficiently, encouraging maintainable, high-quality code by leveraging built-in utilities for data transformation, list/set operations, and more.

## 1. Prefer Built-in Lever Utilities
- Always use the provided Lever MCP tools for data operations (e.g., grouping, sorting, flattening, extracting, set operations) instead of custom code.
- Lever tools are optimized for batch processing and clarity.

*Example:*
```python
# Instead of manual iteration:
result = [x['id'] for x in items]
# Use:
result = pluck(items, 'id')
```

## 2. Data Transformation
- Use `group_by` to organize items by a property.
- Use `sort_by` to sort lists of objects by a property.
- Use `pluck` to extract a list of values for a property from a list of objects.
- Use `flatten` for one-level flattening, and `flatten_deep` for deeply nested lists.
- Use `compact` to remove falsy values (`None`, `False`, `0`, `''`, etc.).

*Example:*
```python
# Group users by role:
grouped = group_by(users, 'role')
# Sort by score:
sorted_items = sort_by(items, 'score')
```

## 3. List Operations
- Use `chunk` to split a list into fixed-size chunks.
- Use `partition` to split a list into two lists based on a property's truthiness.
- Use `zip_lists` to combine lists element-wise, and `unzip_list` to separate them.

*Example:*
```python
# Chunk a list into groups of 3:
chunks = chunk(items, 3)
# Partition by active status:
active, inactive = partition(users, 'is_active')
```

## 4. Set-Like Operations
- Use `uniq_by` to remove duplicates from a list based on a property.
- Use `difference_by` to find items in one list not present in another, by property.
- Use `intersection_by` to find items present in both lists, by property.
- Use `union` to combine lists with unique values.
- Use `xor` for the symmetric difference of lists.

*Example:*
```python
# Remove duplicate users by id:
unique_users = uniq_by(users, 'id')
# Find new users:
new_users = difference_by(all_users, old_users, 'id')
```

## 5. Dictionary Utilities
- Use `set_value` to set a value at a deep path in a dictionary.
- Use `get_value` to retrieve a value from a deep path, with optional default.
- Use `invert` to swap keys and values.
- Use `pick` and `omit` to select or exclude keys from a dictionary.

*Example:*
```python
# Set a nested value:
set_value(config, 'db.host', 'localhost')
# Get a nested value with default:
host = get_value(config, 'db.host', '127.0.0.1')
```

## 6. String Utilities
- Use `deburr` to remove accents/diacritics from strings.
- Use `camel_case`, `snake_case`, `kebab_case`, and `capitalize` for string formatting.
- Use `template` to interpolate variables into a string using `{var}` syntax.

*Example:*
```python
# Convert to snake_case:
snake = snake_case('Hello World!')
# Interpolate variables:
greeting = template('Hello, {name}!', {'name': 'Alice'})
```

## 7. Counting and Filtering
- Use `count_by` to count occurrences of property values in a list.
- Use `find_by` to find the first item in a list matching a property value.
- Use `remove_by` to remove all items from a list matching a property value.

*Example:*
```python
# Count users by role:
role_counts = count_by(users, 'role')
# Find user by email:
user = find_by(users, {'key': 'email', 'value': 'a@b.com'})
```

## 8. Chaining Operations
- Use `chain` to compose multiple Lever operations in sequence for complex transformations.
- Ensure output types are compatible between chained operations.

*Example:*
```python
# Chain: pluck, compact, uniq_by
result = chain(users, [
    {'tool': 'pluck', 'params': {'param': 'email'}},
    {'tool': 'compact', 'params': {}},
    {'tool': 'uniq_by', 'params': {'param': 'email'}}
])
```

## 9. Efficiency
- Prefer Lever tools for batch operations over manual iteration.
- Combine operations using chaining to avoid redundancy.

## 10. Error Handling
- Validate input data types and property names before calling Lever tools.
- Handle empty or unexpected results gracefully, especially when chaining.
