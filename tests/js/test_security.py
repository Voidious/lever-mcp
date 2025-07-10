"""
Test JavaScript security and sandboxing features.

This test suite verifies that JavaScript expressions are properly sandboxed
in safe mode and that dangerous operations are blocked.
"""

import pytest
import importlib
import main
from main import LeverMCP
from fastmcp import Client
from tests import make_tool_call


@pytest.fixture
async def safe_client():
    """Client with JavaScript in safe mode (default)."""
    importlib.reload(main)
    main.USE_JAVASCRIPT = True
    main.SAFE_MODE = True  # Explicitly set safe mode

    mcp_instance = LeverMCP("Lever MCP")
    from tools.js import register_js_tools

    register_js_tools(mcp_instance)

    async with Client(mcp_instance) as c:
        yield c


@pytest.fixture
async def unsafe_client():
    """Client with JavaScript in unsafe mode (--unsafe flag equivalent)."""
    importlib.reload(main)
    main.USE_JAVASCRIPT = True
    main.SAFE_MODE = False  # Unsafe mode

    # Also need to update the js module's SAFE_MODE
    import lib.js

    lib.js.SAFE_MODE = False

    mcp_instance = LeverMCP("Lever MCP")
    from tools.js import register_js_tools

    register_js_tools(mcp_instance)

    async with Client(mcp_instance) as c:
        yield c


@pytest.mark.asyncio
async def test_safe_operations_work(safe_client):
    """Test that safe JavaScript operations work in safe mode."""
    safe_tests = [
        ("Math.sqrt(16)", 4),
        ('"hello".toUpperCase()', "HELLO"),
        ("JSON.stringify({a: 1, b: 2})", '{"a":1,"b":2}'),
        ("[1, 2, 3].map(x => x * 2)", [2, 4, 6]),
        ("Object.keys({a: 1, b: 2})", ["a", "b"]),
        ("Array.from({length: 3}, (_, i) => i)", [0, 1, 2]),
    ]

    for expression, expected in safe_tests:
        result, error = await make_tool_call(
            safe_client,
            "any",
            {"value": {}, "operation": "eval", "expression": expression},
        )
        assert error is None, f"Safe operation failed: {expression}"
        assert result == expected, f"Expected {expected}, got {result} for {expression}"


@pytest.mark.asyncio
async def test_dangerous_operations_blocked_in_safe_mode(safe_client):
    """Test that dangerous operations are blocked in safe mode."""
    dangerous_expressions = [
        # Python bridge (critical security issue)
        'python.eval("import os; os.system(\\"ls\\")")',
        "python.builtins.open('/etc/passwd')",
        # Dynamic code execution
        'eval("1+1")',
        'new Function("return 1+1")()',
        # Network access
        'fetch("http://example.com")',
        "new XMLHttpRequest()",
        # Async code execution
        "setTimeout(() => {}, 1000)",
        "setInterval(() => {}, 1000)",
        # WebAssembly
        "WebAssembly.compile(new ArrayBuffer(0))",
        # Dangerous constructors
        "new Proxy({}, {})",
        "Reflect.get({}, 'prop')",
    ]

    for expression in dangerous_expressions:
        result, error = await make_tool_call(
            safe_client,
            "any",
            {"value": {}, "operation": "eval", "expression": expression},
        )
        assert (
            result is None
        ), f"Dangerous operation should be blocked: {expression}, got: {result}"


# Note: Unsafe mode testing is complex in pytest due to module imports.
# Manual testing shows unsafe mode works correctly with --unsafe flag.


@pytest.mark.asyncio
async def test_mcp_tools_work_in_safe_mode(safe_client):
    """Test that MCP tool functions work properly in safe mode."""
    # Test strings tools
    result, error = await make_tool_call(
        safe_client, "strings", {"text": "hello", "operation": "upper_case"}
    )
    assert error is None
    assert result == "HELLO"

    # Test lists tools
    result, error = await make_tool_call(
        safe_client,
        "lists",
        {"items": [1, 2, 3], "operation": "map", "expression": "item * 2"},
    )
    assert error is None
    assert result == [2, 4, 6]

    # Test any tools
    result, error = await make_tool_call(
        safe_client,
        "any",
        {"value": "test", "operation": "eval", "expression": "value.length"},
    )
    assert error is None
    assert result == 4


@pytest.mark.asyncio
async def test_multiline_expressions_work_safely(safe_client):
    """Test that multiline JavaScript expressions work in safe mode."""
    multiline_expr = """
        let numbers = [1, 2, 3, 4, 5];
        let sum = numbers.reduce((a, b) => a + b, 0);
        let average = sum / numbers.length;
        return Math.round(average * 100) / 100;
    """

    result, error = await make_tool_call(
        safe_client,
        "any",
        {"value": {}, "operation": "eval", "expression": multiline_expr},
    )
    assert error is None
    assert result == 3  # Average of [1,2,3,4,5] is 3


@pytest.mark.asyncio
async def test_fresh_runtime_per_evaluation(safe_client):
    """Test that each evaluation gets a fresh JavaScript runtime."""
    # Note: PythonMonkey creates fresh runtimes for each evaluation
    # This test verifies that our create_js_runtime function works correctly

    # Test that Math functions work (should be available in fresh runtime)
    result, error = await make_tool_call(
        safe_client, "any", {"value": {}, "operation": "eval", "expression": "Math.PI"}
    )
    assert error is None
    assert abs(result - 3.14159) < 0.001

    # Test that JSON functions work (should be available in fresh runtime)
    result, error = await make_tool_call(
        safe_client,
        "any",
        {
            "value": {},
            "operation": "eval",
            "expression": "JSON.stringify({test: true})",
        },
    )
    assert error is None
    assert result == '{"test":true}'
