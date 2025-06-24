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
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("foo bar", "fooBar"),
        ("Foo-Bar", "fooBar"),
        ("__FOO_BAR__", "fooBar"),
        ("foo_bar_baz", "fooBarBaz"),
        ("", ""),
        ("single", "single"),
    ],
)
async def test_camel_case(client, input_str, expected):
    result = await client.call_tool(
        "mutate_string", {"text": input_str, "mutation": "camel_case"}
    )
    assert result[0].text == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("foo bar", "foo-bar"),
        ("FooBar", "foo-bar"),
        ("foo_bar", "foo-bar"),
        ("__FOO_BAR__", "foo-bar"),
        ("fooBarBaz", "foo-bar-baz"),
        ("", ""),
    ],
)
async def test_kebab_case(client, input_str, expected):
    result = await client.call_tool(
        "mutate_string", {"text": input_str, "mutation": "kebab_case"}
    )
    assert result[0].text == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("foo bar", "foo_bar"),
        ("FooBar", "foo_bar"),
        ("foo-bar", "foo_bar"),
        ("--FOO-BAR--", "foo_bar"),
        ("fooBarBaz", "foo_bar_baz"),
        ("", ""),
    ],
)
async def test_snake_case(client, input_str, expected):
    result = await client.call_tool(
        "mutate_string", {"text": input_str, "mutation": "snake_case"}
    )
    assert result[0].text == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("foo bar", "Foo bar"),
        ("FOO BAR", "Foo bar"),
        (" foo bar", " foo bar"),
        ("", ""),
    ],
)
async def test_capitalize(client, input_str, expected):
    result = await client.call_tool(
        "mutate_string", {"text": input_str, "mutation": "capitalize"}
    )
    assert result[0].text == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, target, expected",
    [
        ("abc", "a", True),
        ("abc", "b", False),
        ("abc", "", True),
        ("", "", True),
    ],
)
async def test_starts_with(client, text, target, expected):
    result = await client.call_tool(
        "has_property", {"obj": text, "property": "starts_with", "param": target}
    )
    assert json.loads(result[0].text) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, target, expected",
    [
        ("abc", "c", True),
        ("abc", "b", False),
        ("abc", "", True),
        ("", "", True),
    ],
)
async def test_ends_with(client, text, target, expected):
    result = await client.call_tool(
        "has_property", {"obj": text, "property": "ends_with", "param": target}
    )
    assert json.loads(result[0].text) is expected


# --- General Utility Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected",
    [
        ([], True),
        ({}, True),
        ("", True),
        ([1], False),
        ({"a": 1}, False),
        ("a", False),
        (None, True),
        (0, True),
        (False, True),
    ],
)
async def test_is_empty(client, value, expected):
    result = await client.call_tool(
        "has_property", {"obj": value, "property": "is_empty"}
    )
    assert json.loads(result[0].text) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "a, b, expected",
    [
        ({"x": [1, 2]}, {"x": [1, 2]}, True),
        ({"x": [1, 2]}, {"x": [2, 1]}, False),
        (1, 1, True),
        (1, 2, False),
        (None, None, True),
        (None, 1, False),
    ],
)
async def test_is_equal(client, a, b, expected):
    result = await client.call_tool(
        "has_property", {"obj": a, "property": "is_equal", "param": b}
    )
    assert json.loads(result[0].text) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected",
    [
        (None, True),
        (1, False),
        ("", False),
        ([], False),
    ],
)
async def test_is_nil(client, value, expected):
    result = await client.call_tool(
        "has_property", {"obj": value, "property": "is_nil"}
    )
    assert json.loads(result[0].text) is expected


# --- List Manipulation Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([1, 2, 3], 1),
        ([None, 2, 3], None),
        ([], None),
    ],
)
async def test_head(client, items, expected):
    result = await client.call_tool(
        "select_from_list", {"items": items, "operation": "head"}
    )
    if not result:
        assert expected is None
    else:
        data = json.loads(result[0].text)
        assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([1, 2, 3], [2, 3]),
        ([1], []),
        ([], []),
    ],
)
async def test_tail(client, items, expected):
    result = await client.call_tool("mutate_list", {"items": items, "mutation": "tail"})
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([1, 2, 3], 3),
        ([1, 2, None], None),
        ([], None),
    ],
)
async def test_last(client, items, expected):
    result = await client.call_tool(
        "select_from_list", {"items": items, "operation": "last"}
    )
    if not result:
        assert expected is None
    else:
        data = json.loads(result[0].text)
        assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([1, 2, 3], [1, 2]),
        ([1], []),
        ([], []),
    ],
)
async def test_initial(client, items, expected):
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "initial"}
    )
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, n, expected",
    [
        ([1, 2, 3], 1, [2, 3]),
        ([1, 2, 3], 0, [1, 2, 3]),
        ([1, 2, 3], 5, []),
        ([], 2, []),
    ],
)
async def test_drop(client, items, n, expected):
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "drop", "param": n}
    )
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, n, expected",
    [
        ([1, 2, 3], 1, [1, 2]),
        ([1, 2, 3], 0, [1, 2, 3]),
        ([1, 2, 3], 5, []),
        ([], 2, []),
    ],
)
async def test_drop_right(client, items, n, expected):
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "drop_right", "param": n}
    )
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, n, expected",
    [
        ([1, 2, 3], 2, [1, 2]),
        ([1, 2, 3], 0, []),
        ([1, 2, 3], 5, [1, 2, 3]),
        ([], 2, []),
    ],
)
async def test_take(client, items, n, expected):
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "take", "param": n}
    )
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        if len(expected) == 1 and not isinstance(data, list):
            assert [data] == expected
        else:
            assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, n, expected",
    [
        ([1, 2, 3], 2, [2, 3]),
        ([1, 2, 3], 0, []),
        ([1, 2, 3], 5, [1, 2, 3]),
        ([], 2, []),
    ],
)
async def test_take_right(client, items, n, expected):
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "take_right", "param": n}
    )
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        if len(expected) == 1 and not isinstance(data, list):
            assert [data] == expected
        else:
            assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([[], [1]], [1]),
        ([[]], []),
        ([], []),
    ],
)
async def test_flatten(client, items, expected):
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "flatten"}
    )
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        if len(expected) == 1 and not isinstance(data, list):
            assert [data] == expected
        else:
            assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lists, expected",
    [
        ([[1, 2], [2, 3]], [1, 2, 3]),
        ([[], [1]], [1]),
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([], []),
    ],
)
async def test_union(client, lists, expected):
    result = await client.call_tool(
        "mutate_list", {"items": lists, "mutation": "union"}
    )
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        if isinstance(data, list):
            assert sorted(data) == sorted(expected)
        else:
            assert [data] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lists, expected",
    [
        ([[1, 2, 3], [2, 3, 4], [2, 5]], [2, 3]),
        ([[1, 2], [3, 4]], []),
        ([[], [1, 2]], []),
        ([], []),
    ],
)
async def test_intersection(client, lists, expected):
    if len(lists) < 2:
        assert expected == []
        return
    result = await client.call_tool(
        "compare_lists", {"a": lists[0], "b": lists[1], "operation": "intersection"}
    )
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        if not isinstance(data, list):
            data = [data]
        assert sorted(data) == sorted(expected)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, others, expected",
    [
        ([1, 2, 3], [[2, 4]], [1, 3]),
        ([1, 2, 3], [[4, 5]], [1, 2, 3]),
        ([], [[1]], []),
    ],
)
async def test_difference(client, items, others, expected):
    if not others or not others[0]:
        assert expected == []
        return
    result = await client.call_tool(
        "compare_lists", {"a": items, "b": others[0], "operation": "difference"}
    )
    if not result:
        assert expected == []
    else:
        data = json.loads(result[0].text)
        assert sorted(data) == sorted(expected)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lists, expected",
    [
        ([[1, 2], [2, 3]], [1, 3]),
        ([[1, 2, 3], [2, 4, 5]], [1, 3, 4, 5]),
        ([[], [1, 2]], [1, 2]),
    ],
)
async def test_xor(client, lists, expected):
    result = await client.call_tool("mutate_list", {"items": lists, "mutation": "xor"})
    data = json.loads(result[0].text)
    assert data == expected


# --- Object/Dict Manipulation Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, keys, expected",
    [
        ({"a": 1, "b": 2}, ["a"], {"a": 1}),
        ({"a": 1, "b": 2}, ["a", "c"], {"a": 1}),
        ({}, ["a"], {}),
    ],
)
async def test_pick(client, obj, keys, expected):
    result = await client.call_tool(
        "process_dict", {"obj": obj, "operation": "pick", "param": keys}
    )
    data = json.loads(result[0].text)
    assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, keys, expected",
    [
        ({"a": 1, "b": 2}, ["a"], {"b": 2}),
        ({"a": 1, "b": 2}, ["c"], {"a": 1, "b": 2}),
        ({}, ["a"], {}),
    ],
)
async def test_omit(client, obj, keys, expected):
    result = await client.call_tool(
        "process_dict", {"obj": obj, "operation": "omit", "param": keys}
    )
    data = json.loads(result[0].text)
    assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, expected",
    [
        ({"a": "x", "b": "y"}, {"x": "a", "y": "b"}),
        ({"a": 1}, {"1": "a"}),
        ({}, {}),
    ],
)
async def test_invert(client, obj, expected):
    result = await client.call_tool("process_dict", {"obj": obj, "operation": "invert"})
    data = json.loads(result[0].text)
    assert data == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, key, expected",
    [
        ({"a": 1}, "a", True),
        ({"a": 1}, "b", False),
        ({}, "a", False),
    ],
)
async def test_has(client, obj, key, expected):
    result = await client.call_tool(
        "has_property", {"obj": obj, "property": "has_key", "param": key}
    )
    data = json.loads(result[0].text)
    assert data is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, key, expected",
    [
        (
            [{"id": "a", "v": 1}, {"id": "b", "v": 2}],
            "id",
            {"a": {"id": "a", "v": 1}, "b": {"id": "b", "v": 2}},
        ),
        ([], "id", {}),
    ],
)
async def test_key_by(client, items, key, expected):
    result = await client.call_tool(
        "process_list", {"items": items, "operation": "key_by", "key": key}
    )
    assert json.loads(result[0].text) == expected


# --- Randomized Tests ---


@pytest.mark.asyncio
async def test_shuffle(client):
    items = [1, 2, 3, 4, 5]
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "shuffle"}
    )
    data = json.loads(result[0].text)
    assert len(data) == len(items)
    assert sorted(data) == sorted(items)


@pytest.mark.asyncio
async def test_sample(client):
    items = [1, 2, 3, 4, 5]
    result = await client.call_tool(
        "select_from_list", {"items": items, "operation": "sample"}
    )
    if not result:
        assert False, "Should return a sample from non-empty list"
    else:
        data = json.loads(result[0].text)
        assert data in items
    result_empty = await client.call_tool(
        "select_from_list", {"items": [], "operation": "sample"}
    )
    if not result_empty:
        assert True
    else:
        data_empty = json.loads(result_empty[0].text)
        assert data_empty is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, n",
    [
        ([1, 2, 3, 4, 5], 3),
        ([1, 2, 3], 5),  # n > len(items)
        ([1, 2, 3], 3),  # n == len(items)
    ],
)
async def test_sample_size(client, items, n):
    result = await client.call_tool(
        "mutate_list", {"items": items, "mutation": "sample_size", "param": n}
    )
    data = json.loads(result[0].text)
    assert len(data) == min(n, len(items))
    assert all(item in items for item in data)


@pytest.mark.asyncio
async def test_sample_size_empty(client):
    result = await client.call_tool(
        "mutate_list", {"items": [], "mutation": "sample_size", "param": 3}
    )
    assert not result
