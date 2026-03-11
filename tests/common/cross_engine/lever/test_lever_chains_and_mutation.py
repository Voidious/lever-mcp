from fastmcp.exceptions import ToolError
from tests import make_tool_call
import pytest


@pytest.mark.asyncio
async def test_chain_single_tool(client):
    # Should flatten a nested list
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [1, [2, [3, 4], 5]],
            "tool_calls": [{"tool": "lists", "params": {"operation": "flatten_deep"}}],
        },
    )
    assert value == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_chain_multiple_tools(client):
    # Should flatten and then compact (remove falsy values)
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [0, 1, [2, [0, 3, 4], 5], None],
            "tool_calls": [
                {"tool": "lists", "params": {"operation": "flatten_deep"}},
                {"tool": "lists", "params": {"operation": "compact"}},
            ],
        },
    )
    assert value == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_chain_with_params(client):
    # Should chunk after flattening
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [1, [2, [3, 4], 5]],
            "tool_calls": [
                {"tool": "lists", "params": {"operation": "flatten_deep"}},
                {"tool": "lists", "params": {"operation": "chunk", "param": 2}},
            ],
        },
    )
    assert value == [[1, 2], [3, 4], [5]]


@pytest.mark.asyncio
async def test_chain_error_missing_tool(client):
    # Should return error for missing tool
    value, error = await make_tool_call(
        client,
        "chain",
        {"input": [1, 2, 3], "tool_calls": [{"tool": "not_a_tool", "params": {}}]},
    )
    assert error is not None


@pytest.mark.asyncio
async def test_chain_error_missing_param(client):
    # Should return error for missing required param
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [1, 2, 3],
            "tool_calls": [{"tool": "lists", "params": {"operation": "chunk"}}],
        },
    )
    assert error is not None


@pytest.mark.asyncio
async def test_chain_type_chaining(client):
    # Should group by after flattening
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [{"type": "a", "val": 1}, [{"type": "b", "val": 2}]],
            "tool_calls": [
                {"tool": "lists", "params": {"operation": "flatten_deep"}},
                {
                    "tool": "lists",
                    "params": {"operation": "group_by", "expression": "type"},
                },
            ],
        },
    )
    assert value is not None and "a" in value and "b" in value


@pytest.mark.asyncio
async def test_chain_empty_chain(client):
    # Should return the input unchanged
    value, error = await make_tool_call(
        client, "chain", {"input": 42, "tool_calls": []}
    )
    assert value == 42


@pytest.mark.asyncio
async def test_chain_chain_with_text_content(client):
    # Should error if user tries to specify the primary parameter in params
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": None,
            "tool_calls": [
                {
                    "tool": "strings",
                    "params": {
                        "text": "Hello, {name}!",
                        "operation": "template",
                        "data": {"name": "World"},
                    },
                }
            ],
        },
    )
    assert error is not None


@pytest.mark.asyncio
async def test_mutate_string_edge_cases(client):
    # Empty string
    value, error = await make_tool_call(
        client, "strings", {"text": "", "operation": "camel_case"}
    )
    assert value == ""
    # Missing data for template
    value, error = await make_tool_call(
        client, "strings", {"text": "Hello, {name}!", "operation": "template"}
    )
    assert error is not None
    # Non-string input
    with pytest.raises(ToolError):
        await make_tool_call(
            client, "strings", {"text": 123, "operation": "camel_case"}
        )
    # Unknown operation
    value, error = await make_tool_call(
        client, "strings", {"text": "foo", "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_mutate_list_edge_cases(client):
    # Deeply nested list
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": [1, [2, [3, [4, [5]]]]], "operation": "flatten_deep"},
    )
    assert value == [1, 2, 3, 4, 5]
    # Invalid param type
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2], "operation": "chunk", "param": "two"}
    )
    assert error is not None
    # Empty input for all operations, using correct param types
    empty_operations = [
        ("flatten_deep", None),
        ("compact", None),
        ("chunk", 2),
        ("sort_by", "x"),
        ("uniq_by", "x"),
        ("pluck", "x"),
        ("partition", "x"),
    ]
    for operation, param in empty_operations:
        params = {"items": [], "operation": operation}
        if param is not None:
            params["param"] = param
        value, error = await make_tool_call(client, "lists", params)
        # Partition returns a pair of empty lists
        if operation == "partition":
            assert value == [[], []]
        else:
            assert value == []

    # Unknown operation
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2], "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_has_property_edge_cases(client):
    # Non-string/non-dict input returns false
    value, error = await make_tool_call(
        client, "dicts", {"obj": 123, "operation": "has_key", "param": "1"}
    )
    assert (value or False) is False

    # Missing param returns false
    value, error = await make_tool_call(
        client, "dicts", {"obj": "abc", "operation": "has_key"}
    )
    assert (value or False) is False

    # Unknown property returns error
    value, error = await make_tool_call(
        client, "dicts", {"obj": "abc", "operation": "unknown"}
    )
    assert error is not None
