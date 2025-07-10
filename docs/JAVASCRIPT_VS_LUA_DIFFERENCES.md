# JavaScript vs Lua: Implementation Differences

This document outlines the key differences between the JavaScript and Lua implementations in the Lever MCP project.

## Test Coverage Summary

| Engine | Test Files | Test Methods | Total Test Executions |
|--------|------------|--------------|----------------------|
| **Lua** | 5 files | 237 methods | ~468 total executions |
| **JavaScript** | 6 files | 138 methods | ~434 total executions |

### Test Coverage by Category

| Category | Lua Tests | JavaScript Tests | Status |
|----------|-----------|------------------|---------|
| Expression Tests | ✅ 25 methods | ✅ 33 methods | **JS has more** |
| Tool Call Tests | ✅ 184 methods | ✅ 75 methods | **Lua has more** |
| Chain Tests | ✅ 1 method | ✅ 1 method | **Equivalent** |
| Index/Items Tests | ✅ 12 methods | ✅ 13 methods | **Equivalent** |
| Wrap Tests | ✅ 15 methods | ❌ **N/A** | **Lua only** |
| Security Tests | ❌ **N/A** | ✅ 5 methods | **JS only** |
| Language Features | ❌ **N/A** | ✅ 11 methods | **JS only** |

## Key Architectural Differences

### 1. **Wrap Parameter Support** 🚨

**Most significant difference:**

- **Lua**: Full support for `wrap=true` parameter across all tools
- **JavaScript**: No wrap parameter support

```lua
-- Lua (supported)
lists.map({items={1,2,3}, expression="item * 2", wrap=true})
-- Returns: {__type="list", data={2,4,6}}
```

```javascript
// JavaScript (not supported)
lists.map({items:[1,2,3], expression:"item * 2", wrap:true})
// Error: Unexpected keyword argument 'wrap'
```

**Impact**: This means JavaScript tools always return unwrapped JSON-compatible results, while Lua tools can return wrapped structures for explicit type preservation.

### 2. **Security and Sandboxing**

- **Lua**: Built-in safe mode with granular security controls
- **JavaScript**: Enhanced security implementation (added in this project)

**Lua Security (existing):**
- Disables `io`, `os.execute`, `require`, `debug`
- Preserves safe functions: `os.time`, `math.*`, `string.*`
- Controlled via `--unsafe` flag

**JavaScript Security (newly implemented):**
- Disables `python` bridge, `eval`, `Function`, network access
- Preserves safe functions: `Math.*`, `JSON.*`, array methods
- Controlled via same `--unsafe` flag

### 3. **Language Syntax Differences**

| Feature | Lua | JavaScript |
|---------|-----|------------|
| **Logical Operators** | `and`, `or`, `not` | `&&`, `\|\|`, `!` |
| **Equality** | `==`, `~=` | `===`, `!==` |
| **String Concatenation** | `..` | `+` |
| **Conditional** | `condition and 'yes' or 'no'` | `condition ? 'yes' : 'no'` |
| **Arrays** | `{1, 2, 3}` (1-indexed) | `[1, 2, 3]` (0-indexed) |
| **Objects** | `{key = value}` | `{key: value}` |

### 4. **Type System Differences**

| Concept | Lua | JavaScript |
|---------|-----|------------|
| **Null Values** | `nil` | `null` and `undefined` |
| **Falsy Values** | `false`, `nil` | `false`, `null`, `undefined`, `0`, `""`, `NaN` |
| **Arrays** | Tables with numeric indices | Native array objects |
| **Type Coercion** | More permissive | Strict equality with `===` |

### 5. **Index Numbering**

- **Lua**: 1-based indexing (`index` starts at 1)
- **JavaScript**: 0-based indexing (`index` starts at 0)

```lua
-- Lua: index 1, 2, 3 for items
lists.map({items={10, 20, 30}, expression="item .. index"})
-- Returns: {"101", "202", "303"}
```

```javascript
// JavaScript: index 0, 1, 2 for items
lists.map({items:[10, 20, 30], expression:"item + index"})
// Returns: ["100", "211", "322"]
```

### 6. **Error Handling Patterns**

**Lua Error Handling:**
- Returns `nil` for most errors
- Type coercion attempts (e.g., `string.upper(123)` → `"123"`)

**JavaScript Error Handling:**
- Returns `None` (Python None) for most errors
- Stricter type checking (e.g., `item.toUpperCase()` on number → `None`)

### 7. **Expression Evaluation Features**

**JavaScript Advantages:**
- ✅ Arrow functions: `x => x * 2`
- ✅ Template literals: `` `Hello ${name}` ``
- ✅ Destructuring: `const {a, b} = obj`
- ✅ Spread operator: `[...arr1, ...arr2]`
- ✅ Modern array methods: `filter`, `map`, `reduce`
- ✅ Try/catch error handling
- ✅ Regular expressions: `/pattern/g`
- ✅ JSON operations: `JSON.stringify/parse`

**Lua Advantages:**
- ✅ Wrap parameter for type preservation
- ✅ More permissive type coercion
- ✅ Simpler syntax for basic operations
- ✅ Better integration with table structures

## Performance Characteristics

### Memory Usage
- **Lua**: Lower memory overhead for basic operations
- **JavaScript**: Higher memory overhead due to PythonMonkey bridge

### Execution Speed
- **Lua**: Generally faster for simple expressions
- **JavaScript**: Comparable performance for complex operations

### Runtime Creation
- **Both**: Create fresh runtime per evaluation for security isolation

## Compatibility Matrix

| Feature | Lua Support | JS Support | Notes |
|---------|-------------|------------|-------|
| Basic expressions | ✅ Full | ✅ Full | Syntax differs |
| Tool function calls | ✅ Full | ✅ Full | Same functionality |
| Wrap parameter | ✅ Full | ❌ None | Major difference |
| Security sandboxing | ✅ Full | ✅ Full | Similar implementation |
| Modern language features | ❌ Limited | ✅ Extensive | JS advantage |
| Type preservation | ✅ Via wrap | ✅ Via JSON | Different approaches |

## Migration Considerations

### From Lua to JavaScript
1. **Remove wrap parameters** - JavaScript doesn't support them
2. **Update syntax** - Change operators, indexing, object notation
3. **Handle type differences** - Be aware of null/undefined distinctions
4. **Leverage JS features** - Can use modern JavaScript syntax

### From JavaScript to Lua
1. **Add wrap parameters** - If type preservation needed
2. **Update syntax** - Change to Lua operators and table notation
3. **Adjust indexing** - Convert from 0-based to 1-based
4. **Simplify expressions** - Lua has simpler syntax for basic operations

## Recommendations

### Use Lua When:
- Type preservation with wrap parameter is needed
- Working with table-heavy data structures
- Preferring simpler, more readable syntax
- Memory efficiency is important

### Use JavaScript When:
- Need modern language features (arrow functions, destructuring, etc.)
- Working with JSON-heavy data
- Team has strong JavaScript background
- Want extensive built-in method support

### Tool Selection Strategy:
- **Default to JavaScript** for new projects (better feature set)
- **Use Lua** when wrap parameter functionality is required
- **Both engines** are equally secure and performant for basic operations
