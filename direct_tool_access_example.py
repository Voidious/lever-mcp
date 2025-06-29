#!/usr/bin/env python3
"""
Example demonstrating the correct way to call MCP tool functions directly from Python code,
bypassing the FastMCP decorator while accessing the complete function implementations.
"""

import asyncio
import main
from typing import Any, Dict, Optional

class DirectToolCaller:
    """
    Helper class to call MCP tool functions directly from Python code.
    This bypasses the FastMCP decorator system while accessing the complete implementations.
    """
    
    def __init__(self):
        self._tool_cache = {}
    
    async def _get_tool_function(self, tool_name: str):
        """Get the underlying function from a FastMCP tool."""
        if tool_name not in self._tool_cache:
            tool = await main.mcp._tool_manager.get_tool(tool_name)
            if hasattr(tool, 'fn'):
                self._tool_cache[tool_name] = tool.fn
            else:
                raise ValueError(f"Tool '{tool_name}' does not have an accessible function")
        return self._tool_cache[tool_name]
    
    async def call_strings(self, text: str, operation: str, param: Any = None, data: Optional[Dict] = None) -> Dict:
        """Call the strings tool function directly."""
        strings_fn = await self._get_tool_function('strings')
        return strings_fn(text=text, operation=operation, param=param, data=data)
    
    async def call_lists(self, items: list, operation: str, param: Any = None, others: Optional[list] = None, 
                        key: str = "", expression: Optional[str] = None) -> Dict:
        """Call the lists tool function directly."""
        lists_fn = await self._get_tool_function('lists')
        return lists_fn(items=items, operation=operation, param=param, others=others, 
                       key=key, expression=expression)
    
    async def call_dicts(self, obj: Any, operation: str, param: Any = None, path: Any = None, 
                        value: Any = None, default: Any = None) -> Dict:
        """Call the dicts tool function directly."""
        dicts_fn = await self._get_tool_function('dicts')
        return dicts_fn(obj=obj, operation=operation, param=param, path=path, value=value, default=default)
    
    async def call_any(self, value: Any, operation: str, param: Any = None, expression: Optional[str] = None) -> Dict:
        """Call the any tool function directly."""
        any_fn = await self._get_tool_function('any')
        return any_fn(value=value, operation=operation, param=param, expression=expression)
    
    async def call_generate(self, text: Any, operation: str, param: Any = None) -> Dict:
        """Call the generate tool function directly."""
        generate_fn = await self._get_tool_function('generate')
        return generate_fn(text=text, operation=operation, param=param)


def create_sync_tool_caller():
    """
    Create synchronous wrappers for tool functions.
    This is useful when you need to call tools from synchronous contexts like Lua.
    """
    
    # Cache for async tool caller
    _caller = None
    
    def get_caller():
        nonlocal _caller
        if _caller is None:
            _caller = DirectToolCaller()
        return _caller
    
    def call_strings_sync(text: str, operation: str, param: Any = None, data: Optional[Dict] = None) -> Dict:
        """Synchronous wrapper for strings tool."""
        caller = get_caller()
        
        # Create new event loop if none exists
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to use a different approach
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, caller.call_strings(text, operation, param, data))
                    return future.result()
            else:
                return loop.run_until_complete(caller.call_strings(text, operation, param, data))
        except RuntimeError:
            # No event loop
            return asyncio.run(caller.call_strings(text, operation, param, data))
    
    def call_lists_sync(items: list, operation: str, param: Any = None, others: Optional[list] = None, 
                       key: str = "", expression: Optional[str] = None) -> Dict:
        """Synchronous wrapper for lists tool."""
        caller = get_caller()
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, caller.call_lists(items, operation, param, others, key, expression))
                    return future.result()
            else:
                return loop.run_until_complete(caller.call_lists(items, operation, param, others, key, expression))
        except RuntimeError:
            return asyncio.run(caller.call_lists(items, operation, param, others, key, expression))
    
    def call_dicts_sync(obj: Any, operation: str, param: Any = None, path: Any = None, 
                       value: Any = None, default: Any = None) -> Dict:
        """Synchronous wrapper for dicts tool."""
        caller = get_caller()
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, caller.call_dicts(obj, operation, param, path, value, default))
                    return future.result()
            else:
                return loop.run_until_complete(caller.call_dicts(obj, operation, param, path, value, default))
        except RuntimeError:
            return asyncio.run(caller.call_dicts(obj, operation, param, path, value, default))
    
    def call_any_sync(value: Any, operation: str, param: Any = None, expression: Optional[str] = None) -> Dict:
        """Synchronous wrapper for any tool."""
        caller = get_caller()
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, caller.call_any(value, operation, param, expression))
                    return future.result()
            else:
                return loop.run_until_complete(caller.call_any(value, operation, param, expression))
        except RuntimeError:
            return asyncio.run(caller.call_any(value, operation, param, expression))
    
    def call_generate_sync(text: Any, operation: str, param: Any = None) -> Dict:
        """Synchronous wrapper for generate tool."""
        caller = get_caller()
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, caller.call_generate(text, operation, param))
                    return future.result()
            else:
                return loop.run_until_complete(caller.call_generate(text, operation, param))
        except RuntimeError:
            return asyncio.run(caller.call_generate(text, operation, param))
    
    return {
        'call_strings': call_strings_sync,
        'call_lists': call_lists_sync, 
        'call_dicts': call_dicts_sync,
        'call_any': call_any_sync,
        'call_generate': call_generate_sync
    }


async def demo_direct_calls():
    """Demonstrate calling MCP tools directly."""
    caller = DirectToolCaller()
    
    print("=== Direct MCP Tool Calls Demo ===")
    
    # Test strings operations
    print("\n1. Strings operations:")
    result = await caller.call_strings("hello world", "camel_case")
    print(f"camel_case('hello world') = {result}")
    
    result = await caller.call_strings("abc", "xor", param="bcd")
    print(f"xor('abc', 'bcd') = {result}")
    
    # Test lists operations with expressions
    print("\n2. Lists operations with expressions:")
    items = [{"age": 30, "name": "Alice"}, {"age": 20, "name": "Bob"}, {"age": 35, "name": "Charlie"}]
    
    result = await caller.call_lists(items, "filter_by", expression="age > 25")
    print(f"filter_by(items, 'age > 25') = {result}")
    
    result = await caller.call_lists(items, "sort_by", expression="string.lower(name)")
    print(f"sort_by(items, 'string.lower(name)') = {result}")
    
    result = await caller.call_lists([1, 2, 3, 4], "map", expression="item * item")
    print(f"map([1,2,3,4], 'item * item') = {result}")
    
    # Test complex operations
    print("\n3. Complex operations:")
    result = await caller.call_lists(items, "group_by", expression="age >= 30 and 'senior' or 'junior'")
    print(f"group_by(items, age >= 30 grouping) = {result}")
    
    result = await caller.call_generate(None, "range", param=[1, 10, 2])
    print(f"generate range(1, 10, 2) = {result}")


def demo_sync_calls():
    """Demonstrate synchronous tool calls."""
    print("\n=== Synchronous Tool Calls Demo ===")
    
    sync_tools = create_sync_tool_caller()
    
    # Test synchronous calls
    result = sync_tools['call_strings']("Hello World", "snake_case")
    print(f"sync strings.snake_case('Hello World') = {result}")
    
    result = sync_tools['call_lists']([3, 1, 4, 1, 5], "sort_by", param=None)
    print(f"sync lists.sort([3,1,4,1,5]) = {result}")
    
    result = sync_tools['call_generate'](None, "range", param=[0, 5])
    print(f"sync generate.range(0, 5) = {result}")


if __name__ == "__main__":
    # Demo async calls
    asyncio.run(demo_direct_calls())
    
    # Demo sync calls
    demo_sync_calls()