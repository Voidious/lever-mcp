# Test Organization

This directory contains tests organized by scope and execution context:

## Directory Structure

### `tests/lua/`
Tests that specifically target Lua-based tools with Lua expressions:
- `test_expression.py` - Tests using Lua expressions for filtering, mapping, etc.
- `test_lua_tool_calls.py` - Tests for Lua function call syntax and features
- `test_wrap_comprehensive.py` - Tests for Lua wrap/unwrap functionality

### `tests/js/`
**[Future]** Tests that specifically target JavaScript-based tools with JavaScript expressions:
- Will mirror the Lua tools but use JavaScript expressions
- Currently empty as JavaScript implementations don't exist yet

### `tests/common/`
Tests for shared functionality in `lib/` and `tools/common/`:
- `test_real_server.py` - Integration tests for the MCP server

### `tests/common/cross-engine/`
Tests that run against both Lua and JavaScript engines using common functionality (no expressions):
- `test_lever.py` - Basic tool operations without expressions
- `test_chain_pairings.py` - Chain tool functionality tests
- `test_extended.py` - Extended functionality tests
- `test_lists_index_items.py` - Basic list operations

## Test Categories

1. **Engine-specific tests** (`lua/`, `js/`): Use expressions and engine-specific features
2. **Common library tests** (`common/`): Test shared infrastructure code
3. **Cross-engine tests** (`common/cross-engine/`): Test basic operations that work the same across engines

## Future Plans

When JavaScript implementations are added:
- Copy tests from `tests/lua/` to `tests/js/`
- Replace Lua expressions with JavaScript expressions
- Parametrize `tests/common/cross-engine/` tests to run against both engines
- JavaScript tools will not have wrap/unwrap functionality like Lua tools
