# Expression Test Coverage

This document outlines comprehensive test coverage for all expression-based operations in Lever MCP.

## Operations Supporting Expressions

### Lists Tool Operations (9 total)

#### ✅ Fully Tested Operations

1. **`find_by`** - Find first item matching expression
   - Basic comparison: `"age > 30"`
   - Score filtering: `"score > 90"`
   - Complex conditions: `"age > 25 and score > 80"`

2. **`remove_by`** - Remove items matching expression
   - Score filtering: `"score < 80"`

3. **`group_by`** - Group items by expression result
   - Age-based grouping: `"age >= 30 and 'senior' or 'junior'"`
   - Complex departmental grouping: `"age >= 30 and department or 'junior_' .. department"`

4. **`sort_by`** - Sort by expression result
   - Case-insensitive: `"string.lower(name)"`
   - Mathematical: `"score * age"`

5. **`pluck`** - Extract values using expression
   - Mathematical: `"x + y"`
   - Conditional: `"score >= 90 and 'high' or 'normal'"`

6. **`min_by`** - Find minimum by expression
   - Distance calculation: `"x*x + y*y"`
   - Simple field: `"age"`

7. **`max_by`** - Find maximum by expression
   - Reverse sorting: `"age * -1"`
   - Ratio calculation: `"score / age"`

8. **`difference_by`** - Set difference using expression
   - Category filtering: `"category == 'fruit'"`

9. **`intersection_by`** - Set intersection using expression
   - Category matching: `"category == 'vegetable'"`

### Any Tool Operations (1 total)

#### ✅ Fully Tested Operations

10. **`eval`** - Standalone expression evaluation
    - Boolean logic: `"age > 25"`
    - Mathematical: `"math.sqrt(x*x + y*y)"`
    - String operations: `"string.upper(item)"`
    - Data access: `"items[3]"`
    - Calculations: `"item * 2 + 1"`
    - Nested access: `"config.port > 8000"`

## Test Categories Covered

### 1. Basic Expression Types
- **Comparison operators**: `>`, `<`, `>=`, `<=`, `==`, `~=`
- **Logical operators**: `and`, `or`, `not`
- **Mathematical operators**: `+`, `-`, `*`, `/`, `%`, `^`

### 2. Data Types Tested
- **Numbers**: integers, floats
- **Strings**: text manipulation, concatenation
- **Booleans**: true/false conditions
- **Objects**: nested property access
- **Arrays**: indexed access

### 3. Function Categories
- **Math functions**: `math.sqrt()`, `math.pi`
- **String functions**: `string.upper()`, `string.lower()`, `string.len()`
- **Type functions**: `type()`, `tonumber()`, `tostring()`

### 4. Complex Scenarios
- **Conditional expressions**: ternary-like operations
- **String concatenation**: `".."` operator
- **Nested object access**: `object.property.subproperty`
- **Mathematical formulas**: distance, ratios, products
- **Multi-criteria sorting**: composite expressions
- **Dynamic grouping**: computed group keys

### 5. Edge Cases
- **Error handling**: malformed expressions
- **Type conversion**: automatic type coercion
- **Null/nil handling**: graceful degradation
- **Security**: sandboxed execution

## Test Data Patterns

### Simple Objects
```lua
{"name": "Alice", "age": 30, "score": 85}
```

### Complex Nested Objects
```lua
{
  "name": "Alice",
  "age": 25,
  "score": 95,
  "department": "engineering",
  "config": {"port": 8080, "host": "localhost"}
}
```

### Arrays and Lists
```lua
{"items": [1, 2, 3, 4, 5]}
{"users": [{"name": "Alice"}, {"name": "Bob"}]}
```

## Performance Considerations Tested

1. **Key vs Expression**: Tests verify both `key` and `expression` parameters work
2. **Backward Compatibility**: Existing `key` usage continues to work
3. **Error Resilience**: Failed expressions return sensible defaults
4. **Type Safety**: Mixed data types handled gracefully

## Security Testing

1. **Safe Mode**: Dangerous operations blocked (`os.execute`, `io.*`)
2. **Allowed Functions**: Math, string, time functions work
3. **Configurable Safety**: Server-level `--unsafe` flag tested
4. **Sandbox Boundaries**: File system access properly restricted

## Test Organization

All expression tests are now consolidated in a single, granular test file: **`tests/test_expression.py`**

This file follows the established testing patterns in the codebase with:
- Focused, parametrized test functions
- Clear test case descriptions
- Organized sections by operation type
- Easy identification of failing scenarios

## Coverage Summary

- **Total Operations with Expressions**: 10 (9 in lists + 1 in any)
- **Test Functions**: 15 focused, granular test suites
- **Test Cases**: 58 individual expression tests
- **Test File**: Single consolidated `test_expression.py`
- **Expression Types**: Simple, complex, mathematical, conditional, string-based, null handling
- **Data Scenarios**: Objects, arrays, nested structures, primitives, null values
- **Security Scenarios**: Safe and unsafe modes tested
- **Null Handling**: Comprehensive tests for JSON null conversion, null sentinel behavior, and edge cases

### Test Categories in test_expression.py
- **find_by expressions**: 4 test cases
- **remove_by expressions**: 3 test cases
- **group_by expressions**: 4 test cases
- **sort_by expressions**: 4 test cases
- **pluck expressions**: 4 test cases
- **min/max_by expressions**: 5 test cases
- **difference/intersection_by expressions**: 2 test cases
- **any.eval expressions**: 8 test cases
- **null handling expressions**: 6 test cases
- **null sentinel behavior**: 5 test cases
- **multiline expressions**: 3 test cases
- **safety mode**: 2 test cases
- **complex expressions**: 4 test cases
- **complex null handling**: 4 test cases

### Null Handling Test Coverage
- **Direct null values**: Input/output null handling
- **Null in arrays**: Position preservation and iteration
- **Null in objects**: Field null checking
- **Nested null values**: Deep structure null handling
- **Null sentinel nuances**: Truthiness, type checking, equality behavior
- **Complex null operations**: Filtering, grouping, and transformation with nulls

✅ **100% Coverage**: All expression-supporting operations have comprehensive tests covering basic usage, edge cases, complex scenarios, security considerations, and complete null handling behavior in a single, well-organized test file.
