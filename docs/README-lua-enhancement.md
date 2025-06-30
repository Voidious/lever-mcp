# Enhanced Lua Integration for Lever MCP

This enhancement allows calling MCP tools as functions directly within Lua expressions, supporting both positional and table-based argument syntax.

## Features

### 1. Function Call Syntax
Call MCP operations as Lua functions:
```lua
strings.is_alpha("hello")           -- true
lists.head({1, 2, 3})              -- 1
dicts.has_key({obj={a=1}, param="a"}) -- true
```

### 2. Table-Based Arguments (Recommended for Complex Operations)
Use named parameters in a table for clarity:
```lua
-- Instead of error-prone positional args:
strings.replace("hello world", nil, {old="world", new="Lua"})

-- Use clear table syntax:
strings.replace({
    text = "hello world",
    data = {old = "world", new = "Lua"}
})
```

### 3. Function Returns
Return functions that apply to the current item:
```lua
strings.upper_case  -- applies upper_case to current item
lists.head         -- gets first element of current item
```

## Supported Tools

All MCP tools are available with their complete functionality:

- **strings**: All 20+ string operations (is_alpha, upper_case, replace, template, etc.)
- **lists**: All 35+ list operations (filter_by, map, sort_by, group_by, etc.)
- **dicts**: All dictionary operations (merge, get_value, set_value, etc.)
- **any**: Type checking and evaluation operations
- **generate**: Sequence generation operations (range, combinations, etc.)

## Syntax Comparison

### Simple Operations
```lua
-- Positional (concise for simple cases)
strings.upper_case("hello")
lists.head({1, 2, 3})

-- Table-based (more explicit)
strings.upper_case({text = "hello"})
lists.head({items = {1, 2, 3}})
```

### Complex Operations
```lua
-- Table-based (recommended for operations with multiple parameters)
lists.filter_by({
    items = {{age = 20}, {age = 30}},
    expression = "age >= 25"
})

lists.sort_by({
    items = {{name = "Charlie"}, {name = "Alice"}},
    expression = "string.lower(name)"
})

dicts.get_value({
    obj = {user = {profile = {name = "Alice"}}},
    path = {"user", "profile", "name"}
})
```

## Benefits

1. **Type Safety**: Named parameters prevent argument order mistakes
2. **Readability**: Clear intent with named parameters
3. **Maintainability**: Easy to modify without breaking argument order
4. **Full Functionality**: Access to all MCP tool features
5. **Nested Operations**: Tools can call other tools in expressions

## Implementation

The enhancement works by:
1. Registering Lua functions for each MCP tool operation
2. Supporting both positional and table-based argument patterns
3. Converting between Lua and Python data types automatically
4. Using `.fn` to access the underlying tool implementations directly

This provides a powerful and intuitive way to use MCP tools within Lua expressions while maintaining the flexibility of both simple and complex usage patterns.
