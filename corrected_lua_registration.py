#!/usr/bin/env python3
"""
Corrected Lua runtime registration that calls the complete MCP tool functions
instead of using incomplete fallback implementations.
"""

import asyncio
import lupa
from typing import Any, Optional, Dict
import main


def create_direct_tool_caller():
    """Create a tool caller that can access the full MCP functions synchronously."""
    
    _tool_cache = {}
    
    def get_tool_function(tool_name: str):
        """Get and cache the underlying function from a FastMCP tool."""
        if tool_name not in _tool_cache:
            # We need to run this in an async context
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're already in an async context, this is tricky
                    # For now, we'll use the cached version if available
                    # or fall back to a simple approach
                    raise RuntimeError("Cannot get tool in running loop")
                else:
                    tool = loop.run_until_complete(main.mcp._tool_manager.get_tool(tool_name))
            except RuntimeError:
                # No event loop or in running loop
                tool = asyncio.run(main.mcp._tool_manager.get_tool(tool_name))
            
            if hasattr(tool, 'fn'):
                _tool_cache[tool_name] = tool.fn
            else:
                raise ValueError(f"Tool '{tool_name}' does not have an accessible function")
        return _tool_cache[tool_name]
    
    def call_tool(tool_name: str, **kwargs) -> Dict:
        """Call a tool function with the given parameters."""
        try:
            tool_fn = get_tool_function(tool_name)
            return tool_fn(**kwargs)
        except Exception as e:
            return {"value": None, "error": str(e)}
    
    return call_tool


def _register_mcp_tools_in_lua_corrected(lua_runtime: lupa.LuaRuntime):
    """
    Register MCP tool functions in the Lua runtime to enable calling them
    as functions like strings.is_alpha(s) or lists.filter_by(items, expr).
    
    This version calls the COMPLETE function implementations, not just fallbacks.
    """
    
    # Create the direct tool caller
    call_tool = create_direct_tool_caller()
    
    def create_tool_wrapper(tool_name: str, operation_name: str):
        """Create a wrapper function for a specific tool operation."""
        def wrapper(*args):
            # Convert Lua arguments to Python
            py_args = []
            for arg in args:
                if hasattr(arg, 'values'):  # Lua table
                    py_args.append(main.decode_null_from_lua(dict(arg)))
                else:
                    py_args.append(arg)
            
            # Map arguments to the correct parameter names for each tool
            if tool_name == 'strings':
                kwargs = {
                    'text': py_args[0] if len(py_args) > 0 else None,
                    'operation': operation_name,
                    'param': py_args[1] if len(py_args) > 1 else None,
                    'data': py_args[2] if len(py_args) > 2 else None
                }
            elif tool_name == 'lists':
                kwargs = {
                    'items': py_args[0] if len(py_args) > 0 else None,
                    'operation': operation_name,
                    'param': py_args[1] if len(py_args) > 1 else None,
                    'others': py_args[2] if len(py_args) > 2 else None,
                    'key': py_args[3] if len(py_args) > 3 else "",
                    'expression': py_args[4] if len(py_args) > 4 else None
                }
            elif tool_name == 'dicts':
                kwargs = {
                    'obj': py_args[0] if len(py_args) > 0 else None,
                    'operation': operation_name,
                    'param': py_args[1] if len(py_args) > 1 else None,
                    'path': py_args[2] if len(py_args) > 2 else None,
                    'value': py_args[3] if len(py_args) > 3 else None,
                    'default': py_args[4] if len(py_args) > 4 else None
                }
            elif tool_name == 'any':
                kwargs = {
                    'value': py_args[0] if len(py_args) > 0 else None,
                    'operation': operation_name,
                    'param': py_args[1] if len(py_args) > 1 else None,
                    'expression': py_args[2] if len(py_args) > 2 else None
                }
            elif tool_name == 'generate':
                kwargs = {
                    'text': py_args[0] if len(py_args) > 0 else None,
                    'operation': operation_name,
                    'param': py_args[1] if len(py_args) > 1 else None
                }
            else:
                return None
            
            # Call the complete tool function
            result = call_tool(tool_name, **kwargs)
            
            # Return the value directly, or None if error
            if isinstance(result, dict) and "value" in result:
                return main.encode_null_for_lua(result["value"], lua_runtime)
            return None
        
        return wrapper

    # All operation lists (copied from original implementation)
    string_ops = [
        'camel_case', 'capitalize', 'contains', 'deburr', 'ends_with', 'is_alpha',
        'is_digit', 'is_empty', 'is_equal', 'is_lower', 'is_upper', 'kebab_case',
        'lower_case', 'replace', 'reverse', 'sample_size', 'shuffle', 'snake_case',
        'starts_with', 'template', 'trim', 'upper_case', 'xor'
    ]
    
    list_ops = [
        'all_by', 'every', 'any_by', 'some', 'count_by', 'difference_by', 'filter_by',
        'find_by', 'flat_map', 'group_by', 'intersection_by', 'key_by', 'map',
        'max_by', 'min_by', 'partition', 'pluck', 'reduce', 'remove_by', 'sort_by',
        'uniq_by', 'zip_with', 'chunk', 'compact', 'contains', 'drop', 'drop_right',
        'flatten', 'flatten_deep', 'head', 'index_of', 'initial', 'is_empty',
        'is_equal', 'last', 'nth', 'random_except', 'sample', 'sample_size',
        'shuffle', 'tail', 'take', 'take_right', 'difference', 'intersection',
        'union', 'xor', 'unzip_list', 'zip_lists'
    ]
    
    dict_ops = [
        'get_value', 'has_key', 'invert', 'is_empty', 'is_equal', 'merge',
        'omit', 'pick', 'set_value'
    ]
    
    any_ops = ['contains', 'eval', 'is_empty', 'is_equal', 'is_nil']
    
    generate_ops = [
        'accumulate', 'cartesian_product', 'combinations', 'cycle', 'permutations',
        'powerset', 'range', 'repeat', 'unique_pairs', 'windowed', 'zip_with_index'
    ]
    
    # Create string table with operations
    strings_table = {}
    for op in string_ops:
        strings_table[op] = create_tool_wrapper('strings', op)
    lua_runtime.globals()['strings'] = lua_runtime.table_from(strings_table)
    
    # Create lists table with operations
    lists_table = {}
    for op in list_ops:
        lists_table[op] = create_tool_wrapper('lists', op)
    lua_runtime.globals()['lists'] = lua_runtime.table_from(lists_table)
    
    # Create dicts table with operations
    dicts_table = {}
    for op in dict_ops:
        dicts_table[op] = create_tool_wrapper('dicts', op)
    lua_runtime.globals()['dicts'] = lua_runtime.table_from(dicts_table)
    
    # Create any table with operations
    any_table = {}
    for op in any_ops:
        any_table[op] = create_tool_wrapper('any', op)
    lua_runtime.globals()['any'] = lua_runtime.table_from(any_table)
    
    # Create generate table with operations
    generate_table = {}
    for op in generate_ops:
        generate_table[op] = create_tool_wrapper('generate', op)
    lua_runtime.globals()['generate'] = lua_runtime.table_from(generate_table)


def demo_corrected_lua_registration():
    """Demonstrate the corrected Lua registration calling complete functions."""
    
    print("=== Testing Corrected Lua Registration ===")
    
    # Create a Lua runtime
    lua_runtime = lupa.LuaRuntime()
    lua_runtime.execute("null = {}")  # Define null sentinel
    
    # Register the corrected MCP tools
    _register_mcp_tools_in_lua_corrected(lua_runtime)
    
    # Test string operations
    print("\n1. String operations in Lua:")
    lua_runtime.execute('''
        result1 = strings.camel_case("hello world")
        result2 = strings.xor("abc", "bcd")
        result3 = strings.template("Hello {name}!", {name = "Lua"})
    ''')
    print(f"camel_case('hello world') = {lua_runtime.globals()['result1']}")
    print(f"xor('abc', 'bcd') = {lua_runtime.globals()['result2']}")
    print(f"template('Hello {{name}}!', {{name='Lua'}}) = {lua_runtime.globals()['result3']}")
    
    # Test list operations with expressions
    print("\n2. List operations with expressions in Lua:")
    # Set up test data
    lua_runtime.execute('''
        items = {
            {age = 30, name = "Alice"},
            {age = 20, name = "Bob"},
            {age = 35, name = "Charlie"}
        }
    ''')
    
    # Test operations that should now work with expressions
    lua_runtime.execute('''
        filtered = lists.filter_by(items, nil, nil, nil, "age > 25")
        mapped = lists.map({1, 2, 3, 4}, nil, nil, nil, "item * item")
        grouped = lists.group_by(items, nil, nil, nil, "age >= 30 and 'senior' or 'junior'")
    ''')
    
    print(f"filter_by(items, 'age > 25') = {lua_runtime.globals()['filtered']}")
    print(f"map([1,2,3,4], 'item * item') = {lua_runtime.globals()['mapped']}")
    print(f"group_by(items, age grouping) = {lua_runtime.globals()['grouped']}")
    
    # Test generate operations
    print("\n3. Generate operations in Lua:")
    lua_runtime.execute('''
        range_result = generate.range(nil, {1, 10, 2})
        powerset_result = generate.powerset({1, 2, 3})
    ''')
    print(f"generate.range(1, 10, 2) = {lua_runtime.globals()['range_result']}")
    print(f"generate.powerset([1,2,3]) = {lua_runtime.globals()['powerset_result']}")


if __name__ == "__main__":
    demo_corrected_lua_registration()