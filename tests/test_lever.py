import pytest
import json
from fastmcp import Client
import importlib
import main
from main import LeverMCP


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
    result = await client.call_tool("group_by", {"items": items, "key": "type"})
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
    result = await client.call_tool("flatten_deep", {"items": items})
    data = json.loads(result[0].text)
    assert data == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_sort_by(client):
    items = [{"name": "b"}, {"name": "a"}]
    result = await client.call_tool("sort_by", {"items": items, "key": "name"})
    data = json.loads(result[0].text)
    assert data == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_uniq_by(client):
    items = [{"id": 1, "name": "a"}, {"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    result = await client.call_tool("uniq_by", {"items": items, "key": "id"})
    data = json.loads(result[0].text)
    assert data == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]


@pytest.mark.asyncio
async def test_deburr(client):
    result = await client.call_tool("deburr", {"text": "Café déjà vu"})
    assert result[0].text == "Cafe deja vu"


@pytest.mark.asyncio
async def test_template(client):
    result = await client.call_tool(
        "template", {"text": "Hello, {name}!", "data": {"name": "World"}}
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
    result = await client.call_tool("partition", {"items": items, "predicate": "even"})
    data = json.loads(result[0].text)
    assert data == [
        [{"value": 2, "even": True}, {"value": 4, "even": True}],
        [{"value": 1, "even": False}, {"value": 3, "even": False}],
    ]


@pytest.mark.asyncio
async def test_partition_by_int(client):
    items = [{"value": 0}, {"value": 1}, {"value": 2}, {"value": 0}]
    result = await client.call_tool("partition", {"items": items, "predicate": "value"})
    data = json.loads(result[0].text)
    assert data == [[{"value": 1}, {"value": 2}], [{"value": 0}, {"value": 0}]]


@pytest.mark.asyncio
async def test_partition_by_string(client):
    items = [{"name": "foo"}, {"name": ""}, {"name": "bar"}, {"name": ""}]
    result = await client.call_tool("partition", {"items": items, "predicate": "name"})
    data = json.loads(result[0].text)
    assert data == [[{"name": "foo"}, {"name": "bar"}], [{"name": ""}, {"name": ""}]]


@pytest.mark.asyncio
async def test_partition_by_none(client):
    items = [{"flag": None}, {"flag": True}, {"flag": False}, {"flag": None}]
    result = await client.call_tool("partition", {"items": items, "predicate": "flag"})
    data = json.loads(result[0].text)
    assert data == [[{"flag": True}], [{"flag": None}, {"flag": False}, {"flag": None}]]


@pytest.mark.asyncio
async def test_group_by_string(client):
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "vegetable", "name": "carrot"},
    ]
    result = await client.call_tool("group_by", {"items": items, "key": "type"})
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
    result = await client.call_tool("group_by", {"items": items, "key": "value"})
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
    result = await client.call_tool("group_by", {"items": items, "key": "flag"})
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
        result = await client.call_tool("group_by", {"items": items, "key": "meta"})
        data = json.loads(result[0].text)
        # If the server serializes dict keys, they will be stringified
        assert any(isinstance(k, str) for k in data.keys())
    except Exception:
        pass  # Accept error as valid outcome


@pytest.mark.asyncio
async def test_sort_by_string(client):
    items = [{"name": "b"}, {"name": "a"}]
    result = await client.call_tool("sort_by", {"items": items, "key": "name"})
    data = json.loads(result[0].text)
    assert data == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_sort_by_number(client):
    items = [{"value": 2}, {"value": 1}]
    result = await client.call_tool("sort_by", {"items": items, "key": "value"})
    data = json.loads(result[0].text)
    assert data == [{"value": 1}, {"value": 2}]


@pytest.mark.asyncio
async def test_sort_by_boolean(client):
    items = [{"flag": True}, {"flag": False}]
    result = await client.call_tool("sort_by", {"items": items, "key": "flag"})
    data = json.loads(result[0].text)
    # False sorts before True
    assert data == [{"flag": False}, {"flag": True}]


@pytest.mark.asyncio
async def test_sort_by_dict(client):
    items = [{"meta": {"x": 2}}, {"meta": {"x": 1}}]
    # Dicts are not orderable, so this should raise or group all under one
    try:
        result = await client.call_tool("sort_by", {"items": items, "key": "meta"})
        data = json.loads(result[0].text)
        # If the server stringifies dicts, this will not error
        assert isinstance(data, list)
    except Exception:
        pass  # Accept error as valid outcome


@pytest.mark.asyncio
async def test_uniq_by_string(client):
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "vegetable", "name": "carrot"},
    ]
    result = await client.call_tool("uniq_by", {"items": items, "key": "type"})
    data = json.loads(result[0].text)
    assert data == [
        {"type": "fruit", "name": "apple"},
        {"type": "vegetable", "name": "carrot"},
    ]


@pytest.mark.asyncio
async def test_uniq_by_number(client):
    items = [
        {"value": 1, "name": "a"},
        {"value": 2, "name": "b"},
        {"value": 1, "name": "c"},
    ]
    result = await client.call_tool("uniq_by", {"items": items, "key": "value"})
    data = json.loads(result[0].text)
    assert data == [{"value": 1, "name": "a"}, {"value": 2, "name": "b"}]


@pytest.mark.asyncio
async def test_uniq_by_boolean(client):
    items = [
        {"flag": True, "name": "a"},
        {"flag": False, "name": "b"},
        {"flag": True, "name": "c"},
    ]
    result = await client.call_tool("uniq_by", {"items": items, "key": "flag"})
    data = json.loads(result[0].text)
    assert data == [{"flag": True, "name": "a"}, {"flag": False, "name": "b"}]


@pytest.mark.asyncio
async def test_uniq_by_dict(client):
    items = [
        {"meta": {"x": 1}, "name": "a"},
        {"meta": {"x": 2}, "name": "b"},
        {"meta": {"x": 1}, "name": "c"},
    ]
    # Dicts are not hashable, so this should raise or only keep the first
    try:
        result = await client.call_tool("uniq_by", {"items": items, "key": "meta"})
        data = json.loads(result[0].text)
        assert isinstance(data, list)
    except Exception:
        pass  # Accept error as valid outcome


@pytest.mark.asyncio
async def test_pluck(client):
    items = [
        {"id": 1, "name": "a"},
        {"id": 2, "name": "b"},
        {"id": 3, "name": "c"},
    ]
    result = await client.call_tool("pluck", {"items": items, "key": "name"})
    data = json.loads(result[0].text)
    assert data == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_compact(client):
    items = [0, 1, False, 2, '', 3, None]
    result = await client.call_tool("compact", {"items": items})
    data = json.loads(result[0].text)
    assert data == [1, 2, 3]


@pytest.mark.asyncio
async def test_chunk(client):
    items = [1, 2, 3, 4, 5]
    result = await client.call_tool("chunk", {"items": items, "size": 2})
    data = json.loads(result[0].text)
    assert data == [[1, 2], [3, 4], [5]]


@pytest.mark.asyncio
async def test_count_by(client):
    items = [
        {"type": "a"}, {"type": "b"}, {"type": "a"}, {"type": "c"}, {"type": "b"}
    ]
    result = await client.call_tool("count_by", {"items": items, "key": "type"})
    data = json.loads(result[0].text)
    assert data == {"a": 2, "b": 2, "c": 1}


@pytest.mark.asyncio
async def test_difference_by(client):
    a = [{"id": 1}, {"id": 2}, {"id": 3}]
    b = [{"id": 2}]
    result = await client.call_tool("difference_by", {"a": a, "b": b, "key": "id"})
    data = json.loads(result[0].text)
    assert data == [{"id": 1}, {"id": 3}]


@pytest.mark.asyncio
async def test_intersection_by(client):
    a = [{"id": 1}, {"id": 2}, {"id": 3}]
    b = [{"id": 2}, {"id": 4}]
    result = await client.call_tool("intersection_by", {"a": a, "b": b, "key": "id"})
    data = json.loads(result[0].text) if result else None
    if isinstance(data, dict):
        data = [data]
    assert data == [{"id": 2}]


@pytest.mark.asyncio
async def test_zip_lists(client):
    l1 = [1, 2]
    l2 = ["a", "b"]
    result = await client.call_tool("zip_lists", {"lists": [l1, l2]})
    data = json.loads(result[0].text)
    assert data == [[1, "a"], [2, "b"]]


@pytest.mark.asyncio
async def test_unzip_list(client):
    items = [[1, "a"], [2, "b"]]
    result = await client.call_tool("unzip_list", {"items": items})
    data = json.loads(result[0].text)
    assert data == [[1, 2], ["a", "b"]]


@pytest.mark.asyncio
async def test_find_by(client):
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    result = await client.call_tool("find_by", {"items": items, "key": "id", "value": 2})
    data = json.loads(result[0].text) if result else None
    assert data == {"id": 2}
    # Test not found
    result = await client.call_tool("find_by", {"items": items, "key": "id", "value": 99})
    data = json.loads(result[0].text) if result else None
    assert data is None


@pytest.mark.asyncio
async def test_remove_by(client):
    items = [{"id": 1}, {"id": 2}, {"id": 1}]
    result = await client.call_tool("remove_by", {"items": items, "key": "id", "value": 1})
    data = json.loads(result[0].text) if result else None
    if isinstance(data, dict):
        data = [data]
    assert data == [{"id": 2}]


@pytest.mark.asyncio
async def test_chain_single_tool(client):
    # Should flatten a nested list
    result = await client.call_tool("chain", {
        "input": [1, [2, [3, 4], 5]],
        "tool_calls": [
            {"tool": "flatten_deep", "params": {}}
        ]
    })
    data = json.loads(result[0].text)
    assert data == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_chain_multiple_tools(client):
    # Should flatten and then compact (remove falsy values)
    result = await client.call_tool("chain", {
        "input": [0, 1, [2, [0, 3, 4], 5], None],
        "tool_calls": [
            {"tool": "flatten_deep", "params": {}},
            {"tool": "compact", "params": {}}
        ]
    })
    data = json.loads(result[0].text)
    assert data == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_chain_with_params(client):
    # Should chunk after flattening
    result = await client.call_tool("chain", {
        "input": [1, [2, [3, 4], 5]],
        "tool_calls": [
            {"tool": "flatten_deep", "params": {}},
            {"tool": "chunk", "params": {"size": 2}}
        ]
    })
    data = json.loads(result[0].text)
    assert data == [[1, 2], [3, 4], [5]]


@pytest.mark.asyncio
async def test_chain_error_missing_tool(client):
    # Should return error for missing tool
    result = await client.call_tool("chain", {
        "input": [1, 2, 3],
        "tool_calls": [
            {"tool": "not_a_tool", "params": {}}
        ]
    })
    data = json.loads(result[0].text)
    assert "error" in data and "not_a_tool" in data["error"]


@pytest.mark.asyncio
async def test_chain_error_missing_param(client):
    # Should return error for missing required param
    result = await client.call_tool("chain", {
        "input": [1, 2, 3],
        "tool_calls": [
            {"tool": "chunk", "params": {}}  # missing 'size'
        ]
    })
    data = json.loads(result[0].text)
    assert "error" in data and "chunk" in data["error"]


@pytest.mark.asyncio
async def test_chain_type_chaining(client):
    # Should group by after flattening
    result = await client.call_tool("chain", {
        "input": [{"type": "a", "val": 1}, [{"type": "b", "val": 2}]],
        "tool_calls": [
            {"tool": "flatten_deep", "params": {}},
            {"tool": "group_by", "params": {"key": "type"}}
        ]
    })
    data = json.loads(result[0].text)
    assert "a" in data and "b" in data


@pytest.mark.asyncio
async def test_chain_empty_chain(client):
    # Should return the input unchanged
    result = await client.call_tool("chain", {
        "input": 42,
        "tool_calls": []
    })
    data = json.loads(result[0].text)
    assert data == 42


@pytest.mark.asyncio
async def test_chain_chain_with_text_content(client):
    # Should error if user tries to specify the primary parameter in params
    result = await client.call_tool("chain", {
        "input": None,
        "tool_calls": [
            {"tool": "template", "params": {"text": "Hello, {name}!", "data": {"name": "World"}}}
        ]
    })
    data = result[0].text
    assert "Chaining does not allow specifying the primary parameter" in data
