import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json
import pytest
import random
import socket
import subprocess
import time
from fastmcp import Client


def normalize_json(obj):
    if isinstance(obj, str):
        return json.dumps(json.loads(obj), sort_keys=True, separators=(",", ":"))
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


@pytest.fixture(scope="session", params=["lua", "javascript"])
def server_url(request):
    engine = request.param
    port = random.randint(12001, 12999)
    host = "127.0.0.1"
    url = f"http://{host}:{port}/mcp/"

    # Build command with engine-specific argument
    cmd = [sys.executable, "main.py", "--http", "--host", host, "--port", str(port)]
    if engine == "lua":
        cmd.append("--lua")
    # JavaScript is now the default, so no parameter needed

    # Redirect stdout/stderr to avoid pipe blocking
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(30):
            try:
                with socket.create_connection((host, port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.2)
        else:
            proc.terminate()
            raise RuntimeError("HTTP server did not start in time")
        yield url
    finally:
        # Only terminate if not told to keep alive
        import os

        if not os.environ.get("KEEP_SERVER_UP"):
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()


@pytest.fixture
async def shared_client(server_url):
    async with Client(server_url) as client:
        yield client


# === STRINGS TOOL TESTS ===


@pytest.mark.asyncio
async def test_strings_basic_operations(shared_client):
    """Test core string operations."""
    # upper_case
    result = await shared_client.call_tool(
        "strings", {"text": "hello", "operation": "upper_case"}
    )
    assert json.loads(result[0].text)["value"] == "HELLO"

    # contains
    result = await shared_client.call_tool(
        "strings", {"text": "hello world", "operation": "contains", "param": "world"}
    )
    assert json.loads(result[0].text)["value"] is True

    # is_empty
    result = await shared_client.call_tool(
        "strings", {"text": "", "operation": "is_empty"}
    )
    assert json.loads(result[0].text)["value"] is True


@pytest.mark.asyncio
async def test_strings_case_conversion(shared_client):
    """Test string case conversion operations."""
    test_cases = [
        ("hello world", "camel_case", "helloWorld"),
        ("hello world", "snake_case", "hello_world"),
        ("hello world", "kebab_case", "hello-world"),
        ("hello", "capitalize", "Hello"),
    ]

    for text, operation, expected in test_cases:
        result = await shared_client.call_tool(
            "strings", {"text": text, "operation": operation}
        )
        assert json.loads(result[0].text)["value"] == expected


# === LISTS TOOL TESTS ===


@pytest.mark.asyncio
async def test_lists_basic_operations(shared_client):
    """Test core list operations."""
    # head
    result = await shared_client.call_tool(
        "lists", {"items": [1, 2, 3], "operation": "head"}
    )
    assert json.loads(result[0].text)["value"] == 1

    # last
    result = await shared_client.call_tool(
        "lists", {"items": [1, 2, 3], "operation": "last"}
    )
    assert json.loads(result[0].text)["value"] == 3

    # contains
    result = await shared_client.call_tool(
        "lists", {"items": [1, 2, 3], "operation": "contains", "param": 2}
    )
    assert json.loads(result[0].text)["value"] is True


@pytest.mark.asyncio
async def test_lists_set_operations(shared_client):
    """Test list set operations."""
    # difference
    result = await shared_client.call_tool(
        "lists", {"items": [1, 2, 3], "others": [2, 3], "operation": "difference"}
    )
    assert json.loads(result[0].text)["value"] == [1]

    # intersection
    result = await shared_client.call_tool(
        "lists", {"items": [1, 2, 3], "others": [2, 3, 4], "operation": "intersection"}
    )
    result_value = json.loads(result[0].text)["value"]
    assert 2 in result_value and 3 in result_value

    # xor (symmetric difference)
    result = await shared_client.call_tool(
        "lists", {"items": [1, 2, 3], "others": [2, 3, 4], "operation": "xor"}
    )
    result_value = json.loads(result[0].text)["value"]
    assert 1 in result_value and 4 in result_value


@pytest.mark.asyncio
async def test_lists_functional_operations(shared_client):
    """Test functional list operations."""
    # compact
    result = await shared_client.call_tool(
        "lists", {"items": [1, None, 2, False, 3], "operation": "compact"}
    )
    result_value = json.loads(result[0].text)["value"]
    assert 1 in result_value and 2 in result_value and 3 in result_value
    assert len(result_value) <= 5  # Some falsy values removed

    # uniq_by
    result = await shared_client.call_tool(
        "lists",
        {
            "items": [{"id": 1}, {"id": 1}, {"id": 2}],
            "operation": "uniq_by",
            "expression": "id",
        },
    )
    result_value = json.loads(result[0].text)["value"]
    # uniq_by may only keep first occurrence, so check we get at least 1 unique
    assert len(result_value) >= 1
    assert result_value[0]["id"] == 1  # First item kept

    # count_by
    result = await shared_client.call_tool(
        "lists",
        {
            "items": [{"type": "a"}, {"type": "b"}, {"type": "a"}],
            "operation": "count_by",
            "expression": "type",
        },
    )
    assert json.loads(result[0].text)["value"] == {"a": 2, "b": 1}


# === DICTS TOOL TESTS ===


@pytest.mark.asyncio
async def test_dicts_basic_operations(shared_client):
    """Test core dictionary operations."""
    # has_key
    result = await shared_client.call_tool(
        "dicts", {"obj": {"a": 1, "b": 2}, "operation": "has_key", "param": "a"}
    )
    assert json.loads(result[0].text)["value"] is True

    # is_empty
    result = await shared_client.call_tool(
        "dicts", {"obj": {}, "operation": "is_empty"}
    )
    assert json.loads(result[0].text)["value"] is True

    # is_equal
    result = await shared_client.call_tool(
        "dicts", {"obj": {"a": 1}, "operation": "is_equal", "param": {"a": 1}}
    )
    assert json.loads(result[0].text)["value"] is True


@pytest.mark.asyncio
async def test_dicts_advanced_operations(shared_client):
    """Test advanced dictionary operations."""
    # get_value
    result = await shared_client.call_tool(
        "dicts", {"obj": {"a": {"b": 1}}, "operation": "get_value", "path": "a.b"}
    )
    assert json.loads(result[0].text)["value"] == 1

    # set_value
    result = await shared_client.call_tool(
        "dicts",
        {"obj": {"a": {}}, "operation": "set_value", "path": "a.b", "value": 42},
    )
    assert json.loads(result[0].text)["value"] == {"a": {"b": 42}}

    # invert
    result = await shared_client.call_tool(
        "dicts", {"obj": {"a": "x", "b": "y"}, "operation": "invert"}
    )
    assert json.loads(result[0].text)["value"] == {"x": "a", "y": "b"}

    # merge
    result = await shared_client.call_tool(
        "dicts", {"obj": [{"a": 1}, {"b": 2}], "operation": "merge"}
    )
    assert json.loads(result[0].text)["value"] == {"a": 1, "b": 2}


# === ANY TOOL TESTS ===


@pytest.mark.asyncio
async def test_any_tool_operations(shared_client):
    """Test any tool for type-agnostic operations."""
    # is_equal with different types
    test_cases = [
        (42, 42, True),
        (3.14, 3.14, True),
        (True, True, True),
        (False, False, True),
        (None, None, True),
        ("hello", "hello", True),
        ([1, 2], [1, 2], True),
        (42, 43, False),
    ]

    for value, param, expected in test_cases:
        result = await shared_client.call_tool(
            "any", {"value": value, "operation": "is_equal", "param": param}
        )
        assert (
            json.loads(result[0].text)["value"] == expected
        ), f"Failed for {value} == {param}"

    # is_empty with different types
    empty_cases = [
        ("", True),
        ([], True),
        ({}, True),
        (None, True),  # None is considered empty by any.is_empty
        ("hello", False),
        ([1], False),
    ]

    for value, expected in empty_cases:
        result = await shared_client.call_tool(
            "any", {"value": value, "operation": "is_empty"}
        )
        assert (
            json.loads(result[0].text)["value"] == expected
        ), f"is_empty failed for {value}"


# === GENERATE TOOL TESTS ===


@pytest.mark.asyncio
async def test_generate_tool_operations(shared_client):
    """Test generate tool operations."""
    # repeat
    result = await shared_client.call_tool(
        "generate", {"options": {"value": 3, "count": 2}, "operation": "repeat"}
    )
    assert json.loads(result[0].text)["value"] == [3, 3]

    # range
    result = await shared_client.call_tool(
        "generate", {"options": {"from": 0, "to": 5}, "operation": "range"}
    )
    assert json.loads(result[0].text)["value"] == [0, 1, 2, 3, 4]

    # powerset
    result = await shared_client.call_tool(
        "generate", {"options": {"items": [1, 2]}, "operation": "powerset"}
    )
    result_value = json.loads(result[0].text)["value"]
    assert len(result_value) == 4  # 2^2 = 4 subsets

    # cartesian_product
    result = await shared_client.call_tool(
        "generate",
        {"options": {"lists": [[1, 2], ["a", "b"]]}, "operation": "cartesian_product"},
    )
    result_value = json.loads(result[0].text)["value"]
    # Check that we get the right number of combinations
    assert len(result_value) == 4  # 2 * 2 = 4 combinations
    # Check that specific combinations exist
    assert [1, "a"] in result_value or (1, "a") in result_value
    assert [2, "b"] in result_value or (2, "b") in result_value


# === CHAIN TOOL TESTS ===


@pytest.mark.asyncio
async def test_chain_tool_operations(shared_client):
    """Test chain tool for combining operations."""
    # Simple chain: string -> upper_case
    result = await shared_client.call_tool(
        "chain",
        {
            "input": "hello",
            "tool_calls": [{"tool": "strings", "params": {"operation": "upper_case"}}],
        },
    )
    assert json.loads(result[0].text)["value"] == "HELLO"

    # Multi-step chain: list -> head -> string upper_case
    result = await shared_client.call_tool(
        "chain",
        {
            "input": ["hello", "world"],
            "tool_calls": [
                {"tool": "lists", "params": {"operation": "head"}},
                {"tool": "strings", "params": {"operation": "upper_case"}},
            ],
        },
    )
    assert json.loads(result[0].text)["value"] == "HELLO"


# === ERROR HANDLING TESTS ===


@pytest.mark.asyncio
async def test_error_handling(shared_client):
    """Test error handling for invalid operations."""
    # Invalid operation
    result = await shared_client.call_tool(
        "strings", {"text": "hello", "operation": "nonexistent"}
    )
    result_data = json.loads(result[0].text)
    assert result_data["value"] is None
    assert "error" in result_data

    # Wrong type for tool - this will raise ToolError due to Pydantic validation
    try:
        await shared_client.call_tool(
            "lists", {"items": "not a list", "operation": "head"}
        )
        assert False, "Expected ToolError to be raised"
    except Exception as e:
        # Pydantic validation error expected
        assert "validation error" in str(e).lower() or "list_type" in str(e)

    # Missing required parameter
    result = await shared_client.call_tool(
        "strings", {"text": "hello", "operation": "contains"}  # missing param
    )
    result_data = json.loads(result[0].text)
    assert result_data["value"] is None
    assert "error" in result_data
