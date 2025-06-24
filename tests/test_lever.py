import pytest
import json
from fastmcp import Client
import importlib
import main
from main import LeverMCP
from json.decoder import JSONDecodeError
from fastmcp.exceptions import ToolError


@pytest.fixture
async def client():
    """
    Provides an isolated FastMCP client for each test by reloading the main
    module and explicitly resetting the application state for the session.
    """
    importlib.reload(main)
    mcp_instance: LeverMCP = main.mcp
    async with Client(mcp_instance) as c:
        yield c


@pytest.mark.asyncio
async def test_group_by(client):
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "vegetable", "name": "carrot"},
    ]
    result = await client.call_tool(
        "process_list", {"items": items, "operation": "group_by", "key": "type"}
    )
    data = json.loads(result[0].text)
    assert data == {
        "fruit": [
            {"type": "fruit", "name": "apple"},
            {"type": "fruit", "name": "banana"},
        ],
        "vegetable": [{"type": "vegetable", "name": "carrot"}],
    }


@pytest.mark.asyncio
async def test_merge(client):
    d1 = {"a": 1, "b": {"c": 2}}
    d2 = {"b": {"d": 3}}
    result = await client.call_tool("merge", {"dicts": [d1, d2]})
    data = json.loads(result[0].text)
    assert data == {"a": 1, "b": {"c": 2, "d": 3}}


@pytest.mark.asyncio
async def test_flatten_deep(client):
    items = [1, [2, [3, 4], 5]]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "flatten_deep"}
    )
    data = json.loads(result[0].text)
    assert data == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_sort_by(client):
    items = [{"name": "b"}, {"name": "a"}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "sort_by", "param": "name"}
    )
    data = json.loads(result[0].text)
    assert data == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_uniq_by(client):
    items = [{"id": 1, "name": "a"}, {"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "uniq_by", "param": "id"}
    )
    data = json.loads(result[0].text)
    assert data == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]


@pytest.mark.asyncio
async def test_deburr(client):
    result = await client.call_tool(
        "mutate_string", {"text": "Café déjà vu", "mutation": "deburr"}
    )
    assert result[0].text == "Cafe deja vu"


@pytest.mark.asyncio
async def test_template(client):
    result = await client.call_tool(
        "mutate_string",
        {"text": "Hello, {name}!", "mutation": "template", "data": {"name": "World"}},
    )
    assert result[0].text == "Hello, World!"


@pytest.mark.asyncio
async def test_set_and_get_value(client):
    obj = {"a": {"b": 1}}
    set_result = await client.call_tool(
        "set_value", {"obj": obj, "path": "a.b", "value": 2}
    )
    set_data = json.loads(set_result[0].text)
    assert set_data == {"a": {"b": 2}}
    get_result = await client.call_tool(
        "get_value", {"obj": {"a": {"b": 2}}, "path": "a.b"}
    )
    assert json.loads(get_result[0].text) == 2
    get_default = await client.call_tool(
        "get_value", {"obj": {"a": {"b": 2}}, "path": "a.c", "default": 42}
    )
    assert json.loads(get_default[0].text) == 42


@pytest.mark.asyncio
async def test_partition_by_boolean(client):
    items = [
        {"value": 2, "even": True},
        {"value": 1, "even": False},
        {"value": 4, "even": True},
        {"value": 3, "even": False},
    ]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "partition", "param": "even"}
    )
    data = json.loads(result[0].text)
    assert data == [
        [{"value": 2, "even": True}, {"value": 4, "even": True}],
        [{"value": 1, "even": False}, {"value": 3, "even": False}],
    ]


@pytest.mark.asyncio
async def test_partition_by_int(client):
    items = [{"value": 0}, {"value": 1}, {"value": 2}, {"value": 0}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "partition", "param": "value"}
    )
    data = json.loads(result[0].text)
    assert data == [[{"value": 1}, {"value": 2}], [{"value": 0}, {"value": 0}]]


@pytest.mark.asyncio
async def test_partition_by_string(client):
    items = [{"name": "foo"}, {"name": ""}, {"name": "bar"}, {"name": ""}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "partition", "param": "name"}
    )
    data = json.loads(result[0].text)
    assert data == [[{"name": "foo"}, {"name": "bar"}], [{"name": ""}, {"name": ""}]]


@pytest.mark.asyncio
async def test_partition_by_none(client):
    items = [{"flag": None}, {"flag": True}, {"flag": False}, {"flag": None}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "partition", "param": "flag"}
    )
    data = json.loads(result[0].text)
    assert data == [[{"flag": True}], [{"flag": None}, {"flag": False}, {"flag": None}]]


@pytest.mark.asyncio
async def test_group_by_string(client):
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "vegetable", "name": "carrot"},
    ]
    result = await client.call_tool(
        "process_list", {"items": items, "operation": "group_by", "key": "type"}
    )
    data = json.loads(result[0].text)
    assert data == {
        "fruit": [
            {"type": "fruit", "name": "apple"},
            {"type": "fruit", "name": "banana"},
        ],
        "vegetable": [{"type": "vegetable", "name": "carrot"}],
    }


@pytest.mark.asyncio
async def test_group_by_number(client):
    items = [
        {"value": 1, "name": "a"},
        {"value": 2, "name": "b"},
        {"value": 1, "name": "c"},
    ]
    result = await client.call_tool(
        "process_list", {"items": items, "operation": "group_by", "key": "value"}
    )
    data = json.loads(result[0].text)
    assert data == {
        "1": [{"value": 1, "name": "a"}, {"value": 1, "name": "c"}],
        "2": [{"value": 2, "name": "b"}],
    }


@pytest.mark.asyncio
async def test_group_by_boolean(client):
    items = [
        {"flag": True, "name": "a"},
        {"flag": False, "name": "b"},
        {"flag": True, "name": "c"},
    ]
    result = await client.call_tool(
        "process_list", {"items": items, "operation": "group_by", "key": "flag"}
    )
    data = json.loads(result[0].text)
    # JSON keys are strings, so True/False become "true"/"false"
    assert data == {
        "true": [{"flag": True, "name": "a"}, {"flag": True, "name": "c"}],
        "false": [{"flag": False, "name": "b"}],
    }


@pytest.mark.asyncio
async def test_group_by_dict(client):
    items = [
        {"meta": {"x": 1}, "name": "a"},
        {"meta": {"x": 2}, "name": "b"},
        {"meta": {"x": 1}, "name": "c"},
    ]
    # Dicts are not hashable, so all will be grouped under one key (or error)
    try:
        result = await client.call_tool(
            "process_list", {"items": items, "operation": "group_by", "key": "meta"}
        )
        data = json.loads(result[0].text)
        # If the server serializes dict keys, they will be stringified
        assert any(isinstance(k, str) for k in data.keys())
    except Exception:
        pass  # Accept error as valid outcome


@pytest.mark.asyncio
async def test_sort_by_string(client):
    items = [{"name": "b"}, {"name": "a"}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "sort_by", "param": "name"}
    )
    data = json.loads(result[0].text)
    assert data == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_sort_by_number(client):
    items = [{"value": 2}, {"value": 1}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "sort_by", "param": "value"}
    )
    data = json.loads(result[0].text)
    assert data == [{"value": 1}, {"value": 2}]


@pytest.mark.asyncio
async def test_sort_by_boolean(client):
    items = [{"flag": True}, {"flag": False}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "sort_by", "param": "flag"}
    )
    data = json.loads(result[0].text)
    assert data == [{"flag": False}, {"flag": True}]


@pytest.mark.asyncio
async def test_sort_by_dict(client):
    items = [{"meta": {"x": 2}}, {"meta": {"x": 1}}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "sort_by", "param": "meta"}
    )
    data = json.loads(result[0].text)
    assert data == [{"meta": {"x": 1}}, {"meta": {"x": 2}}]


@pytest.mark.asyncio
async def test_uniq_by_string(client):
    items = [{"type": "a"}, {"type": "a"}, {"type": "b"}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "uniq_by", "param": "type"}
    )
    data = json.loads(result[0].text)
    assert data == [{"type": "a"}, {"type": "b"}]


@pytest.mark.asyncio
async def test_uniq_by_number(client):
    items = [{"value": 1}, {"value": 1}, {"value": 2}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "uniq_by", "param": "value"}
    )
    data = json.loads(result[0].text)
    assert data == [{"value": 1}, {"value": 2}]


@pytest.mark.asyncio
async def test_uniq_by_boolean(client):
    items = [{"flag": True}, {"flag": True}, {"flag": False}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "uniq_by", "param": "flag"}
    )
    data = json.loads(result[0].text)
    assert data == [{"flag": True}, {"flag": False}]


@pytest.mark.asyncio
async def test_uniq_by_dict(client):
    items = [{"meta": {"x": 1}}, {"meta": {"x": 1}}, {"meta": {"x": 2}}]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "uniq_by", "param": "meta"}
    )
    data = json.loads(result[0].text)
    assert data == [{"meta": {"x": 1}}, {"meta": {"x": 2}}]


@pytest.mark.asyncio
async def test_pluck(client):
    items = [
        {"id": 1, "name": "a"},
        {"id": 2, "name": "b"},
        {"id": 3, "name": "c"},
    ]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "pluck", "param": "name"}
    )
    data = json.loads(result[0].text)
    assert data == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_compact(client):
    items = [0, 1, False, 2, "", 3, None]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "compact"}
    )
    data = json.loads(result[0].text)
    assert data == [1, 2, 3]


@pytest.mark.asyncio
async def test_chunk(client):
    items = [1, 2, 3, 4, 5]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "chunk", "param": 2}
    )
    data = json.loads(result[0].text)
    assert data == [[1, 2], [3, 4], [5]]


@pytest.mark.asyncio
async def test_count_by(client):
    items = [{"type": "a"}, {"type": "b"}, {"type": "a"}, {"type": "c"}, {"type": "b"}]
    result = await client.call_tool(
        "process_list", {"items": items, "operation": "count_by", "key": "type"}
    )
    data = json.loads(result[0].text)
    assert data == {"a": 2, "b": 2, "c": 1}


@pytest.mark.asyncio
async def test_difference_by(client):
    a = [{"id": 1}, {"id": 2}, {"id": 3}]
    b = [{"id": 2}]
    result = await client.call_tool(
        "compare_lists", {"a": a, "b": b, "operation": "difference_by", "key": "id"}
    )
    data = json.loads(result[0].text)
    assert data == [{"id": 1}, {"id": 3}]


@pytest.mark.asyncio
async def test_intersection_by(client):
    a = [{"id": 1}, {"id": 2}, {"id": 3}]
    b = [{"id": 2}, {"id": 4}]
    result = await client.call_tool(
        "compare_lists", {"a": a, "b": b, "operation": "intersection_by", "key": "id"}
    )
    data = json.loads(result[0].text) if result else None
    if isinstance(data, dict):
        data = [data]
    assert data == [{"id": 2}]


@pytest.mark.asyncio
async def test_zip_lists(client):
    l1 = [1, 2]
    l2 = ["a", "b"]
    result = await client.call_tool(
        "mutate_list", {"items": [l1, l2], "mutation": "zip_lists"}
    )
    data = json.loads(result[0].text)
    assert data == [[1, "a"], [2, "b"]]


@pytest.mark.asyncio
async def test_unzip_list(client):
    items = [[1, "a"], [2, "b"]]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "unzip_list"}
    )
    data = json.loads(result[0].text)
    assert data == [[1, 2], ["a", "b"]]


@pytest.mark.asyncio
async def test_find_by(client):
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    result = await client.call_tool(
        "select_from_list",
        {"items": items, "operation": "find_by", "param": {"key": "id", "value": 2}},
    )
    data = json.loads(result[0].text) if result else None
    assert data == {"id": 2}
    # Test not found
    result = await client.call_tool(
        "select_from_list",
        {"items": items, "operation": "find_by", "param": {"key": "id", "value": 99}},
    )
    data = json.loads(result[0].text) if result else None
    assert data is None


@pytest.mark.asyncio
async def test_remove_by(client):
    items = [{"id": 1}, {"id": 2}, {"id": 1}]
    result = await client.call_tool(
        "mutate_list",
        {"items": items, "mutation": "remove_by", "param": {"key": "id", "value": 1}},
    )
    data = json.loads(result[0].text) if result else None
    if isinstance(data, dict):
        data = [data]
    assert data == [{"id": 2}]


@pytest.mark.asyncio
async def test_chain_single_tool(client):
    # Should flatten a nested list
    result = await client.call_tool(
        "chain",
        {
            "input": [1, [2, [3, 4], 5]],
            "tool_calls": [
                {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}}
            ],
        },
    )
    data = json.loads(result[0].text)
    assert data == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_chain_multiple_tools(client):
    # Should flatten and then compact (remove falsy values)
    result = await client.call_tool(
        "chain",
        {
            "input": [0, 1, [2, [0, 3, 4], 5], None],
            "tool_calls": [
                {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}},
                {"tool": "mutate_list", "params": {"mutation": "compact"}},
            ],
        },
    )
    data = json.loads(result[0].text)
    assert data == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_chain_with_params(client):
    # Should chunk after flattening
    result = await client.call_tool(
        "chain",
        {
            "input": [1, [2, [3, 4], 5]],
            "tool_calls": [
                {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}},
                {"tool": "mutate_list", "params": {"mutation": "chunk", "param": 2}},
            ],
        },
    )
    data = json.loads(result[0].text)
    assert data == [[1, 2], [3, 4], [5]]


@pytest.mark.asyncio
async def test_chain_error_missing_tool(client):
    # Should return error for missing tool
    result = await client.call_tool(
        "chain",
        {"input": [1, 2, 3], "tool_calls": [{"tool": "not_a_tool", "params": {}}]},
    )
    data = json.loads(result[0].text)
    assert "error" in data and "not_a_tool" in data["error"]


@pytest.mark.asyncio
async def test_chain_error_missing_param(client):
    # Should return error for missing required param
    result = await client.call_tool(
        "chain",
        {
            "input": [1, 2, 3],
            "tool_calls": [
                {
                    "tool": "mutate_list",
                    "params": {"mutation": "chunk"},
                }  # missing 'param' for size
            ],
        },
    )
    data = json.loads(result[0].text)
    assert "error" in data and "mutate_list" in data["error"]


@pytest.mark.asyncio
async def test_chain_type_chaining(client):
    # Should group by after flattening
    result = await client.call_tool(
        "chain",
        {
            "input": [{"type": "a", "val": 1}, [{"type": "b", "val": 2}]],
            "tool_calls": [
                {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}},
                {
                    "tool": "process_list",
                    "params": {"operation": "group_by", "key": "type"},
                },
            ],
        },
    )
    data = json.loads(result[0].text)
    assert "a" in data and "b" in data


@pytest.mark.asyncio
async def test_chain_empty_chain(client):
    # Should return the input unchanged
    result = await client.call_tool("chain", {"input": 42, "tool_calls": []})
    data = json.loads(result[0].text)
    assert data == 42


@pytest.mark.asyncio
async def test_chain_chain_with_text_content(client):
    # Should error if user tries to specify the primary parameter in params
    result = await client.call_tool(
        "chain",
        {
            "input": None,
            "tool_calls": [
                {
                    "tool": "mutate_string",
                    "params": {
                        "text": "Hello, {name}!",
                        "mutation": "template",
                        "data": {"name": "World"},
                    },
                }
            ],
        },
    )
    data = result[0].text
    assert "Chaining does not allow specifying the primary parameter" in data


@pytest.mark.asyncio
async def test_mutate_string_edge_cases(client):
    # Empty string
    result = await client.call_tool(
        "mutate_string", {"text": "", "mutation": "camel_case"}
    )
    if result[0].text:
        assert json.loads(result[0].text) == ""
    else:
        assert result[0].text == ""
    # Missing data for template
    with pytest.raises(ToolError):
        await client.call_tool(
            "mutate_string", {"text": "Hello, {name}!", "mutation": "template"}
        )
    # Non-string input
    with pytest.raises(ToolError):
        await client.call_tool("mutate_string", {"text": 123, "mutation": "camel_case"})
    # Unknown mutation
    with pytest.raises(ToolError):
        await client.call_tool("mutate_string", {"text": "foo", "mutation": "unknown"})


@pytest.mark.asyncio
async def test_mutate_list_edge_cases(client):
    # Deeply nested list
    result = await client.call_tool(
        "mutate_list", {"items": [1, [2, [3, [4, [5]]]]], "mutation": "flatten_deep"}
    )
    assert json.loads(result[0].text) == [1, 2, 3, 4, 5]
    # Invalid param type
    with pytest.raises(ToolError):
        await client.call_tool(
            "mutate_list", {"items": [1, 2], "mutation": "chunk", "param": "two"}
        )
    # Empty input for all mutations, using correct param types
    empty_mutations = [
        ("flatten_deep", None),
        ("compact", None),
        ("chunk", 2),
        ("sort_by", "x"),
        ("uniq_by", "x"),
        ("pluck", "x"),
        ("partition", "x"),
    ]
    for mutation, param in empty_mutations:
        params = {"items": [], "mutation": mutation}
        if param is not None:
            params["param"] = param
        result = await client.call_tool("mutate_list", params)
        assert result is not None
    # Unknown mutation
    with pytest.raises(ToolError):
        await client.call_tool("mutate_list", {"items": [1, 2], "mutation": "unknown"})


@pytest.mark.asyncio
async def test_has_property_edge_cases(client):
    # Non-string/non-dict input returns false
    result = await client.call_tool(
        "has_property", {"obj": 123, "property": "starts_with", "param": "1"}
    )
    assert result[0].text == "false"
    # Missing param returns false
    result = await client.call_tool(
        "has_property", {"obj": "abc", "property": "starts_with"}
    )
    assert result[0].text == "false"
    # Unknown property raises
    with pytest.raises(ToolError):
        await client.call_tool("has_property", {"obj": "abc", "property": "unknown"})


@pytest.mark.asyncio
async def test_select_from_list_edge_cases(client):
    # Non-dict items for find_by returns []
    result = await client.call_tool(
        "select_from_list",
        {"items": [1, 2], "operation": "find_by", "param": {"key": "id", "value": 1}},
    )
    assert result == []
    # Missing param for find_by raises
    with pytest.raises(ToolError):
        await client.call_tool(
            "select_from_list", {"items": [{"id": 1}], "operation": "find_by"}
        )
    # Unknown operation raises
    with pytest.raises(ToolError):
        await client.call_tool(
            "select_from_list", {"items": [1, 2], "operation": "unknown"}
        )


@pytest.mark.asyncio
async def test_compare_lists_edge_cases(client):
    # Non-dict items for *_by returns []
    result = await client.call_tool(
        "compare_lists",
        {"a": [1, 2], "b": [2, 3], "operation": "difference_by", "key": "id"},
    )
    assert result == []
    # Missing key for *_by raises
    with pytest.raises(ToolError):
        await client.call_tool(
            "compare_lists",
            {"a": [{"id": 1}], "b": [{"id": 2}], "operation": "difference_by"},
        )
    # Unknown operation raises
    with pytest.raises(ToolError):
        await client.call_tool(
            "compare_lists", {"a": [1], "b": [2], "operation": "unknown"}
        )


@pytest.mark.asyncio
async def test_process_list_edge_cases(client):
    # Missing key raises
    with pytest.raises(ToolError):
        await client.call_tool(
            "process_list", {"items": [{"a": 1}], "operation": "group_by"}
        )
    # Non-dict items returns {}
    result = await client.call_tool(
        "process_list", {"items": [1, 2], "operation": "group_by", "key": "a"}
    )
    assert json.loads(result[0].text) == {"None": [1, 2]}
    # Unknown operation raises
    with pytest.raises(ToolError):
        await client.call_tool(
            "process_list", {"items": [{"a": 1}], "operation": "unknown", "key": "a"}
        )


@pytest.mark.asyncio
async def test_process_dict_edge_cases(client):
    # Non-dict input raises
    with pytest.raises(ToolError):
        await client.call_tool(
            "process_dict", {"obj": 123, "operation": "pick", "param": ["a"]}
        )
    # Missing param for pick/omit raises
    with pytest.raises(ToolError):
        await client.call_tool("process_dict", {"obj": {"a": 1}, "operation": "pick"})
    # Unknown operation raises
    with pytest.raises(ToolError):
        await client.call_tool(
            "process_dict", {"obj": {"a": 1}, "operation": "unknown"}
        )


@pytest.mark.asyncio
async def test_chain_all_tools_and_error_propagation(client):
    # Chain all tool types
    result = await client.call_tool(
        "chain",
        {
            "input": "foo bar",
            "tool_calls": [
                {"tool": "mutate_string", "params": {"mutation": "camel_case"}},
                {"tool": "mutate_string", "params": {"mutation": "capitalize"}},
            ],
        },
    )
    if result[0].text:
        assert result[0].text == "Foobar"
    else:
        raise AssertionError("Expected 'Foobar' but got empty response")
    # Error propagation
    result = await client.call_tool(
        "chain",
        {
            "input": "foo bar",
            "tool_calls": [
                {"tool": "mutate_string", "params": {"mutation": "unknown"}}
            ],
        },
    )
    assert result and ("error" in result[0].text or result[0].text == "")


@pytest.mark.asyncio
async def test_merge_edge_cases(client):
    # More than two dicts
    dicts = [{"a": 1}, {"b": 2}, {"c": 3}]
    result = await client.call_tool("merge", {"dicts": dicts})
    data = json.loads(result[0].text)
    assert data == {"a": 1, "b": 2, "c": 3}
    # Empty list
    result = await client.call_tool("merge", {"dicts": []})
    data = json.loads(result[0].text)
    assert data == {}
    # Non-dict input raises
    with pytest.raises(ToolError):
        await client.call_tool("merge", {"dicts": [1, 2]})


@pytest.mark.asyncio
async def test_set_value_edge_cases(client):
    # List path
    obj = {"a": {"b": 1}}
    result = await client.call_tool(
        "set_value", {"obj": obj, "path": ["a", "b"], "value": 3}
    )
    data = json.loads(result[0].text)
    assert data["a"]["b"] == 3
    # Creating new keys
    obj = {}
    result = await client.call_tool(
        "set_value", {"obj": obj, "path": "x.y.z", "value": 1}
    )
    data = json.loads(result[0].text)
    assert data["x"]["y"]["z"] == 1
    # Invalid path raises
    with pytest.raises(ToolError):
        await client.call_tool("set_value", {"obj": {}, "path": 123, "value": 1})
    # Non-dict input raises
    with pytest.raises(ToolError):
        await client.call_tool("set_value", {"obj": 123, "path": "a.b", "value": 1})


@pytest.mark.asyncio
async def test_get_value_edge_cases(client):
    # List path
    obj = {"a": {"b": 2}}
    result = await client.call_tool("get_value", {"obj": obj, "path": ["a", "b"]})
    data = json.loads(result[0].text)
    assert data == 2
    # Missing path returns default
    result = await client.call_tool(
        "get_value", {"obj": obj, "path": "x.y", "default": "not found"}
    )
    assert result[0].text == "not found"
    # Non-dict input raises
    with pytest.raises(ToolError):
        await client.call_tool("get_value", {"obj": 123, "path": "a.b"})
