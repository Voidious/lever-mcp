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

# --- String Manipulation Tests ---

@pytest.mark.asyncio
@pytest.mark.parametrize("input_str, expected", [
    ("foo bar", "fooBar"),
    ("Foo-Bar", "fooBar"),
    ("__FOO_BAR__", "fooBar"),
    ("foo_bar_baz", "fooBarBaz"),
    ("", ""),
    ("single", "single"),
])
async def test_camel_case(client, input_str, expected):
    result = await client.call_tool("camel_case", {"text": input_str})
    assert result[0].text == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("input_str, expected", [
    ("foo bar", "foo-bar"),
    ("FooBar", "foo-bar"),
    ("foo_bar", "foo-bar"),
    ("__FOO_BAR__", "foo-bar"),
    ("fooBarBaz", "foo-bar-baz"),
    ("", ""),
])
async def test_kebab_case(client, input_str, expected):
    result = await client.call_tool("kebab_case", {"text": input_str})
    assert result[0].text == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("input_str, expected", [
    ("foo bar", "foo_bar"),
    ("FooBar", "foo_bar"),
    ("foo-bar", "foo_bar"),
    ("--FOO-BAR--", "foo_bar"),
    ("fooBarBaz", "foo_bar_baz"),
    ("", ""),
])
async def test_snake_case(client, input_str, expected):
    result = await client.call_tool("snake_case", {"text": input_str})
    assert result[0].text == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("input_str, expected", [
    ("foo bar", "Foo bar"),
    ("FOO BAR", "Foo bar"),
    (" foo bar", " foo bar"),
    ("", ""),
])
async def test_capitalize(client, input_str, expected):
    result = await client.call_tool("capitalize", {"text": input_str})
    assert result[0].text == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("text, target, expected", [
    ("abc", "a", True),
    ("abc", "b", False),
    ("abc", "", True),
    ("", "", True),
])
async def test_starts_with(client, text, target, expected):
    result = await client.call_tool("starts_with", {"text": text, "target": target})
    assert json.loads(result[0].text) is expected

@pytest.mark.asyncio
@pytest.mark.parametrize("text, target, expected", [
    ("abc", "c", True),
    ("abc", "b", False),
    ("abc", "", True),
    ("", "", True),
])
async def test_ends_with(client, text, target, expected):
    result = await client.call_tool("ends_with", {"text": text, "target": target})
    assert json.loads(result[0].text) is expected


# --- General Utility Tests ---

@pytest.mark.asyncio
@pytest.mark.parametrize("value, expected", [
    ([], True),
    ({}, True),
    ("", True),
    ([1], False),
    ({"a": 1}, False),
    ("a", False),
    (None, True),
    (0, True),
    (False, True),
])
async def test_is_empty(client, value, expected):
    result = await client.call_tool("is_empty", {"value": value})
    assert json.loads(result[0].text) is expected

@pytest.mark.asyncio
@pytest.mark.parametrize("a, b, expected", [
    ({"x": [1, 2]}, {"x": [1, 2]}, True),
    ({"x": [1, 2]}, {"x": [2, 1]}, False),
    (1, 1, True),
    (1, 2, False),
    (None, None, True),
    (None, 1, False),
])
async def test_is_equal(client, a, b, expected):
    result = await client.call_tool("is_equal", {"a": a, "b": b})
    assert json.loads(result[0].text) is expected

@pytest.mark.asyncio
@pytest.mark.parametrize("value, expected", [
    (None, True),
    (1, False),
    ("", False),
    ([], False),
])
async def test_is_nil(client, value, expected):
    result = await client.call_tool("is_nil", {"value": value})
    assert json.loads(result[0].text) is expected


# --- List Manipulation Tests ---

@pytest.mark.asyncio
@pytest.mark.parametrize("items, expected", [
    ([1, 2, 3], 1),
    ([None, 2, 3], None),
    ([], None),
])
async def test_head(client, items, expected):
    result = await client.call_tool("head", {"items": items})
    if not result:
        assert expected is None
    else:
        data = json.loads(result[0].text)
        assert data == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("items, expected", [
    ([1, 2, 3], [2, 3]),
    ([1], []),
    ([], []),
])
async def test_tail(client, items, expected):
    result = await client.call_tool("tail", {"items": items})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert data == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("items, expected", [
    ([1, 2, 3], 3),
    ([1, 2, None], None),
    ([], None),
])
async def test_last(client, items, expected):
    result = await client.call_tool("last", {"items": items})
    if not result:
        assert expected is None
    else:
        data = json.loads(result[0].text)
        assert data == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("items, expected", [
    ([1, 2, 3], [1, 2]),
    ([1], []),
    ([], []),
])
async def test_initial(client, items, expected):
    result = await client.call_tool("initial", {"items": items})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert data == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("items, n, expected", [
    ([1, 2, 3], 1, [2, 3]),
    ([1, 2, 3], 0, [1, 2, 3]),
    ([1, 2, 3], 5, []),
    ([], 2, []),
])
async def test_drop(client, items, n, expected):
    result = await client.call_tool("drop", {"items": items, "n": n})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert data == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("items, n, expected", [
    ([1, 2, 3], 1, [1, 2]),
    ([1, 2, 3], 0, [1, 2, 3]),
    ([1, 2, 3], 5, []),
    ([], 2, []),
])
async def test_drop_right(client, items, n, expected):
    result = await client.call_tool("drop_right", {"items": items, "n": n})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert data == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("items, n, expected", [
    ([1, 2, 3], 2, [1, 2]),
    ([1, 2, 3], 0, []),
    ([1, 2, 3], 5, [1, 2, 3]),
    ([], 2, []),
])
async def test_take(client, items, n, expected):
    result = await client.call_tool("take", {"items": items, "n": n})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        # Handle single-element list unwrap
        if len(expected) == 1 and not isinstance(data, list):
            assert [data] == expected
        else:
            assert data == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("items, n, expected", [
    ([1, 2, 3], 2, [2, 3]),
    ([1, 2, 3], 0, []),
    ([1, 2, 3], 5, [1, 2, 3]),
    ([], 2, []),
])
async def test_take_right(client, items, n, expected):
    result = await client.call_tool("take_right", {"items": items, "n": n})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert data == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("items, expected", [
    ([[1, 2], [3, 4]], [1, 2, 3, 4]),
    ([[], [1]], [1]),
    ([[]], []),
    ([], []),
])
async def test_flatten(client, items, expected):
    result = await client.call_tool("flatten", {"items": items})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        if len(expected) == 1 and not isinstance(data, list):
             assert [data] == expected
        else:
            assert data == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("lists, expected", [
    ([[1, 2], [2, 3]], [1, 2, 3]),
    ([[], [1]], [1]),
    ([[1, 2], [3, 4]], [1, 2, 3, 4]),
    ([], []),
])
async def test_union(client, lists, expected):
    result = await client.call_tool("union", {"lists": lists})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        if isinstance(data, list):
            assert sorted(data) == sorted(expected)
        else:
            assert [data] == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("lists, expected", [
    ([[1, 2, 3], [2, 3, 4], [2, 5]], [2]),
    ([[1, 2], [3, 4]], []),
    ([[], [1, 2]], []),
    ([], []),
])
async def test_intersection(client, lists, expected):
    result = await client.call_tool("intersection", {"lists": lists})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        if len(expected) <= 1:
            assert data == (expected[0] if expected else [])
        else:
            assert sorted(data) == sorted(expected)


@pytest.mark.asyncio
@pytest.mark.parametrize("items, others, expected", [
    ([1, 2, 3], [[2, 4]], [1, 3]),
    ([1, 2, 3], [[4, 5]], [1, 2, 3]),
    ([], [[1]], []),
])
async def test_difference(client, items, others, expected):
    result = await client.call_tool("difference", {"items": items, "others": others})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert sorted(data) == sorted(expected)

@pytest.mark.asyncio
@pytest.mark.parametrize("lists, expected", [
    ([[1, 2], [2, 3]], [1, 3]),
    ([[1, 2, 3], [2, 4, 5]], [1, 3, 4, 5]),
    ([[], [1, 2]], [1, 2]),
])
async def test_xor(client, lists, expected):
    result = await client.call_tool("xor", {"lists": lists})
    data = json.loads(result[0].text)
    assert sorted(data) == sorted(expected)


# --- Object/Dict Manipulation Tests ---

@pytest.mark.asyncio
@pytest.mark.parametrize("obj, keys, expected", [
    ({"a": 1, "b": 2}, ["a"], {"a": 1}),
    ({"a": 1, "b": 2}, ["a", "c"], {"a": 1}),
    ({}, ["a"], {}),
])
async def test_pick(client, obj, keys, expected):
    result = await client.call_tool("pick", {"obj": obj, "keys": keys})
    assert json.loads(result[0].text) == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("obj, keys, expected", [
    ({"a": 1, "b": 2}, ["a"], {"b": 2}),
    ({"a": 1, "b": 2}, ["c"], {"a": 1, "b": 2}),
    ({}, ["a"], {}),
])
async def test_omit(client, obj, keys, expected):
    result = await client.call_tool("omit", {"obj": obj, "keys": keys})
    assert json.loads(result[0].text) == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("obj, expected", [
    ({"a": "x", "b": "y"}, {"x": "a", "y": "b"}),
    ({"a": 1}, {"1": "a"}),
    ({}, {}),
])
async def test_invert(client, obj, expected):
    result = await client.call_tool("invert", {"obj": obj})
    assert json.loads(result[0].text) == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("obj, key, expected", [
    ({"a": 1}, "a", True),
    ({"a": 1}, "b", False),
    ({}, "a", False),
])
async def test_has(client, obj, key, expected):
    result = await client.call_tool("has", {"obj": obj, "key": key})
    assert json.loads(result[0].text) is expected

@pytest.mark.asyncio
@pytest.mark.parametrize("items, key, expected", [
    ([{"id": "a", "v": 1}, {"id": "b", "v": 2}], "id", {"a": {"id": "a", "v": 1}, "b": {"id": "b", "v": 2}}),
    ([], "id", {}),
])
async def test_key_by(client, items, key, expected):
    result = await client.call_tool("key_by", {"items": items, "key": key})
    assert json.loads(result[0].text) == expected


# --- Randomized Tests ---

@pytest.mark.asyncio
async def test_shuffle(client):
    items = list(range(100))
    result = await client.call_tool("shuffle", {"items": items})
    data = json.loads(result[0].text)
    assert sorted(data) == items
    # Could still fail with a very low probability
    assert data != items

@pytest.mark.asyncio
async def test_sample(client):
    items = [1, 2, 3]
    result = await client.call_tool("sample", {"items": items})
    data = json.loads(result[0].text)
    assert data in items
    
    # Test empty list
    result_empty = await client.call_tool("sample", {"items": []})
    assert not result_empty

@pytest.mark.asyncio
@pytest.mark.parametrize("items, n", [
    ([1, 2, 3, 4, 5], 3),
    ([1, 2, 3], 5), # n > len(items)
    ([1, 2, 3], 3), # n == len(items)
])
async def test_sample_size(client, items, n):
    result = await client.call_tool("sample_size", {"items": items, "n": n})
    data = json.loads(result[0].text)
    expected_len = min(n, len(items))
    assert len(data) == expected_len
    assert all(item in items for item in data)

@pytest.mark.asyncio
async def test_sample_size_empty(client):
    result = await client.call_tool("sample_size", {"items": [], "n": 3})
    assert not result 