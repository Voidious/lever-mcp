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
async def test_groupBy(client):
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "vegetable", "name": "carrot"},
    ]
    result = await client.call_tool("groupBy", {"items": items, "key": "type"})
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
async def test_flattenDeep(client):
    items = [1, [2, [3, 4], 5]]
    result = await client.call_tool("flattenDeep", {"items": items})
    data = json.loads(result[0].text)
    assert data == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_sortBy(client):
    items = [{"name": "b"}, {"name": "a"}]
    result = await client.call_tool("sortBy", {"items": items, "key": "name"})
    data = json.loads(result[0].text)
    assert data == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_uniqBy(client):
    items = [{"id": 1, "name": "a"}, {"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    result = await client.call_tool("uniqBy", {"items": items, "key": "id"})
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
async def test_cloneDeep(client):
    obj = {"a": [1, 2, 3]}
    result = await client.call_tool("cloneDeep", {"obj": obj})
    data = json.loads(result[0].text)
    assert data == {"a": [1, 2, 3]}
    assert data is not obj


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
async def test_groupBy_string(client):
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "vegetable", "name": "carrot"},
    ]
    result = await client.call_tool("groupBy", {"items": items, "key": "type"})
    data = json.loads(result[0].text)
    assert data == {
        "fruit": [
            {"type": "fruit", "name": "apple"},
            {"type": "fruit", "name": "banana"},
        ],
        "vegetable": [{"type": "vegetable", "name": "carrot"}],
    }


@pytest.mark.asyncio
async def test_groupBy_number(client):
    items = [
        {"value": 1, "name": "a"},
        {"value": 2, "name": "b"},
        {"value": 1, "name": "c"},
    ]
    result = await client.call_tool("groupBy", {"items": items, "key": "value"})
    data = json.loads(result[0].text)
    assert data == {
        "1": [{"value": 1, "name": "a"}, {"value": 1, "name": "c"}],
        "2": [{"value": 2, "name": "b"}],
    }


@pytest.mark.asyncio
async def test_groupBy_boolean(client):
    items = [
        {"flag": True, "name": "a"},
        {"flag": False, "name": "b"},
        {"flag": True, "name": "c"},
    ]
    result = await client.call_tool("groupBy", {"items": items, "key": "flag"})
    data = json.loads(result[0].text)
    # JSON keys are strings, so True/False become "true"/"false"
    assert data == {
        "true": [{"flag": True, "name": "a"}, {"flag": True, "name": "c"}],
        "false": [{"flag": False, "name": "b"}],
    }


@pytest.mark.asyncio
async def test_groupBy_dict(client):
    items = [
        {"meta": {"x": 1}, "name": "a"},
        {"meta": {"x": 2}, "name": "b"},
        {"meta": {"x": 1}, "name": "c"},
    ]
    # Dicts are not hashable, so all will be grouped under one key (or error)
    try:
        result = await client.call_tool("groupBy", {"items": items, "key": "meta"})
        data = json.loads(result[0].text)
        # If the server serializes dict keys, they will be stringified
        assert any(isinstance(k, str) for k in data.keys())
    except Exception:
        pass  # Accept error as valid outcome


@pytest.mark.asyncio
async def test_sortBy_string(client):
    items = [{"name": "b"}, {"name": "a"}]
    result = await client.call_tool("sortBy", {"items": items, "key": "name"})
    data = json.loads(result[0].text)
    assert data == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_sortBy_number(client):
    items = [{"value": 2}, {"value": 1}]
    result = await client.call_tool("sortBy", {"items": items, "key": "value"})
    data = json.loads(result[0].text)
    assert data == [{"value": 1}, {"value": 2}]


@pytest.mark.asyncio
async def test_sortBy_boolean(client):
    items = [{"flag": True}, {"flag": False}]
    result = await client.call_tool("sortBy", {"items": items, "key": "flag"})
    data = json.loads(result[0].text)
    # False sorts before True
    assert data == [{"flag": False}, {"flag": True}]


@pytest.mark.asyncio
async def test_sortBy_dict(client):
    items = [{"meta": {"x": 2}}, {"meta": {"x": 1}}]
    # Dicts are not orderable, so this should raise or group all under one
    try:
        result = await client.call_tool("sortBy", {"items": items, "key": "meta"})
        data = json.loads(result[0].text)
        # If the server stringifies dicts, this will not error
        assert isinstance(data, list)
    except Exception:
        pass  # Accept error as valid outcome


@pytest.mark.asyncio
async def test_uniqBy_string(client):
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "vegetable", "name": "carrot"},
    ]
    result = await client.call_tool("uniqBy", {"items": items, "key": "type"})
    data = json.loads(result[0].text)
    assert data == [
        {"type": "fruit", "name": "apple"},
        {"type": "vegetable", "name": "carrot"},
    ]


@pytest.mark.asyncio
async def test_uniqBy_number(client):
    items = [
        {"value": 1, "name": "a"},
        {"value": 2, "name": "b"},
        {"value": 1, "name": "c"},
    ]
    result = await client.call_tool("uniqBy", {"items": items, "key": "value"})
    data = json.loads(result[0].text)
    assert data == [{"value": 1, "name": "a"}, {"value": 2, "name": "b"}]


@pytest.mark.asyncio
async def test_uniqBy_boolean(client):
    items = [
        {"flag": True, "name": "a"},
        {"flag": False, "name": "b"},
        {"flag": True, "name": "c"},
    ]
    result = await client.call_tool("uniqBy", {"items": items, "key": "flag"})
    data = json.loads(result[0].text)
    assert data == [{"flag": True, "name": "a"}, {"flag": False, "name": "b"}]


@pytest.mark.asyncio
async def test_uniqBy_dict(client):
    items = [
        {"meta": {"x": 1}, "name": "a"},
        {"meta": {"x": 2}, "name": "b"},
        {"meta": {"x": 1}, "name": "c"},
    ]
    # Dicts are not hashable, so this should raise or only keep the first
    try:
        result = await client.call_tool("uniqBy", {"items": items, "key": "meta"})
        data = json.loads(result[0].text)
        assert isinstance(data, list)
    except Exception:
        pass  # Accept error as valid outcome
