import importlib
import json
import main
import pytest
from fastmcp import Client
from main import LeverMCP
from . import make_tool_call


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
    value, error = await make_tool_call(
        client, "strings", {"text": input_str, "operation": "camel_case"}
    )
    assert value == expected or (isinstance(value, dict) and "error" in value)


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
    value, error = await make_tool_call(
        client, "strings", {"text": input_str, "operation": "kebab_case"}
    )
    assert value == expected or (isinstance(value, dict) and "error" in value)


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
    value, error = await make_tool_call(
        client, "strings", {"text": input_str, "operation": "snake_case"}
    )
    assert value == expected or (isinstance(value, dict) and "error" in value)


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
    value, error = await make_tool_call(
        client, "strings", {"text": input_str, "operation": "capitalize"}
    )
    assert value == expected or (isinstance(value, dict) and "error" in value)


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
    value, error = await make_tool_call(
        client,
        "strings",
        {"text": text, "operation": "starts_with", "param": target},
    )
    assert value is expected or (isinstance(value, dict) and "error" in value)


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
    value, error = await make_tool_call(
        client, "strings", {"text": text, "operation": "ends_with", "param": target}
    )
    assert value is expected or (isinstance(value, dict) and "error" in value)


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
    if isinstance(value, str):
        value_out, error = await make_tool_call(
            client, "strings", {"text": value, "operation": "is_empty"}
        )
    elif isinstance(value, list):
        value_out, error = await make_tool_call(
            client, "lists", {"items": value, "operation": "is_empty"}
        )
    elif isinstance(value, dict):
        value_out, error = await make_tool_call(
            client, "dicts", {"obj": value, "operation": "is_empty"}
        )
    else:
        value_out, error = await make_tool_call(
            client, "any", {"value": value, "operation": "is_empty"}
        )
    assert value_out is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("foo", "foo", True),
        (42, 42, True),
        (3.14, 3.14, True),
        (True, True, True),
        ([1, 2], [1, 2], True),
        ({"a": 1}, {"a": 1}, True),
        (None, None, True),
        ("foo", "bar", False),
        (42, 43, False),
        (3.14, 2.71, False),
        (True, False, False),
        ([1, 2], [2, 1], False),
        ({"a": 1}, {"a": 2}, False),
        (None, 0, False),
    ],
)
async def test_is_equal_all_types(client, a, b, expected):
    if isinstance(a, str) and isinstance(b, str):
        value_out, error = await make_tool_call(
            client, "strings", {"text": a, "operation": "is_equal", "param": b}
        )
    elif isinstance(a, list) and isinstance(b, list):
        value_out, error = await make_tool_call(
            client, "lists", {"items": a, "operation": "is_equal", "param": b}
        )
    elif isinstance(a, dict) and isinstance(b, dict):
        value_out, error = await make_tool_call(
            client, "dicts", {"obj": a, "operation": "is_equal", "param": b}
        )
    else:
        value_out, error = await make_tool_call(
            client, "any", {"value": a, "operation": "is_equal", "param": b}
        )
    assert value_out is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected",
    [
        (None, True),
        (0, False),
        (1, False),
        (3.14, False),
        ("", False),
        ("foo", False),
        ([], False),
        ([1, 2], False),
        ({}, False),
        ({"a": 1}, False),
        (False, False),
        (True, False),
    ],
)
async def test_any_is_nil(client, value, expected):
    value_out, error = await make_tool_call(
        client, "any", {"value": value, "operation": "is_nil"}
    )
    assert value_out is expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "head"}
    )
    if expected is None:
        assert value is None
    else:
        assert value is not None
        assert value == expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "tail"}
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "last"}
    )
    if not value:
        assert expected is None
    else:
        assert value == expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "initial"}
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "drop", "param": n}
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "drop_right", "param": n}
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "take", "param": n}
    )
    if not value:
        assert expected == []
    else:
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if len(expected) == 1 and not isinstance(value, list):
            assert [value] == expected
        else:
            assert value == expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "take_right", "param": n}
    )
    if not value:
        assert expected == []
    else:
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if len(expected) == 1 and not isinstance(value, list):
            assert [value] == expected
        else:
            assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([[], [1]], [1]),
        ([[]], []),
        ([], []),
        ([1, [2, 3]], [1, 2, 3]),  # Non-list elements preserved
        ([1, 2, [3, 4]], [1, 2, 3, 4]),  # Multiple non-list elements
    ],
)
async def test_flatten(client, items, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "flatten"}
    )
    if not value:
        assert expected == []
    else:
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if len(expected) == 1 and not isinstance(value, list):
            assert [value] == expected
        else:
            assert value == expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": lists, "operation": "union"}
    )
    if not value:
        assert expected == []
    else:
        if isinstance(value, list):
            assert sorted(value) == sorted(expected)
        else:
            assert [value] == expected


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
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": lists[0], "others": lists[1], "operation": "intersection"},
    )
    if not value:
        assert expected == []
    else:
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if not isinstance(value, list):
            value = [value]
        if (
            isinstance(value, list)
            and isinstance(expected, list)
            and value
            and expected
        ):
            primitive_types = (int, float, str, bool, type(None))
            t = type(value[0])
            if all(
                isinstance(x, primitive_types) and type(x) == t  # noqa
                for x in value + expected
            ):
                assert set(value) == set(expected)
            elif all(isinstance(x, dict) for x in value + expected):

                def dicts_to_set(lst):
                    return set(tuple(sorted(d.items())) for d in lst)

                assert dicts_to_set(value) == dicts_to_set(expected)
            elif all(isinstance(x, list) for x in value + expected):
                assert set(tuple(x) for x in value) == set(tuple(x) for x in expected)
            else:
                assert value == expected
        else:
            assert value == expected


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
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "others": others[0], "operation": "difference"},
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


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
    value, error = await make_tool_call(
        client, "lists", {"items": lists[0], "others": lists[1], "operation": "xor"}
    )
    if (
        isinstance(value, list)
        and value
        and all(isinstance(x, dict) and "value" in x for x in value)
    ):
        value = [x["value"] for x in value]
    assert value == expected


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
    value, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": "pick", "param": keys}
    )
    assert error is None
    assert value == expected


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
    value, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": "omit", "param": keys}
    )
    assert error is None
    assert value == expected


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
    value, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": "invert"}
    )
    assert error is None
    assert value == expected


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
    value, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": "has_key", "param": key}
    )
    assert error is None
    assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected",
    [
        (
            [{"id": "a", "v": 1}, {"id": "b", "v": 2}],
            "id",
            {"a": {"id": "a", "v": 1}, "b": {"id": "b", "v": 2}},
        ),
        ([], "id", {}),
    ],
)
async def test_key_by(client, items, expression, expected):
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "key_by", "expression": expression},
    )
    assert error is None
    assert value == expected


# --- Randomized Tests ---


@pytest.mark.asyncio
async def test_shuffle(client):
    items = [1, 2, 3, 4, 5]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "shuffle"}
    )
    assert value is not None
    assert len(value) == len(items)
    assert sorted(value) == sorted(items)


@pytest.mark.asyncio
async def test_sample(client):
    items = [1, 2, 3, 4, 5]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "sample"}
    )
    assert value is not None
    assert value in items
    value_empty, error = await make_tool_call(
        client, "lists", {"items": [], "operation": "sample"}
    )
    assert value_empty is None


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
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "sample_size", "param": n}
    )
    assert value is not None
    assert len(value) == min(n, len(items))
    assert all(item in items for item in value)


@pytest.mark.asyncio
async def test_sample_size_empty(client):
    value, error = await make_tool_call(
        client, "lists", {"items": [], "operation": "sample_size", "param": 3}
    )
    assert value == []


# --- Additional mutate_string tests ---
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_str, mutation, data, expected",
    [
        ("hello", "reverse", None, "olleh"),
        ("  hello  ", "trim", None, "hello"),
        ("Hello World", "lower_case", None, "hello world"),
        ("Hello World", "upper_case", None, "HELLO WORLD"),
        ("foo bar foo", "replace", {"old": "foo", "new": "baz"}, "baz bar baz"),
    ],
)
async def test_mutate_string_new_options(client, input_str, mutation, data, expected):
    params = {"text": input_str, "operation": mutation}
    if data is not None:
        params["data"] = data
    value, error = await make_tool_call(client, "strings", params)
    assert value == expected


# --- Additional has_property tests ---
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, property, param, expected",
    [
        ("hello world", "contains", "world", True),
        ([1, 2, 3], "contains", 2, True),
        ("12345", "is_digit", None, True),
        ("abcXYZ", "is_alpha", None, True),
        ("HELLO", "is_upper", None, True),
        ("hello", "is_lower", None, True),
        ("abc123", "is_digit", None, False),
        ("abc123", "is_alpha", None, False),
        ("Hello", "is_upper", None, False),
        ("Hello", "is_lower", None, False),
    ],
)
async def test_has_property_new_options(client, obj, property, param, expected):
    if isinstance(obj, str):
        params = {"text": obj, "operation": property}
        if param is not None:
            params["param"] = param
        value_out, error = await make_tool_call(client, "strings", params)
    elif isinstance(obj, list):
        params = {"items": obj, "operation": property}
        if param is not None:
            params["param"] = param
        value_out, error = await make_tool_call(client, "lists", params)
    elif isinstance(obj, dict):
        params = {"obj": obj, "operation": property}
        if param is not None:
            params["param"] = param
        value_out, error = await make_tool_call(client, "dicts", params)
    else:
        value_out, error = await make_tool_call(
            client, "any", {"value": obj, "operation": property, "param": param}
        )
    assert value_out is expected


# --- Additional select_from_list tests ---
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, operation, param, expected",
    [
        ([10, 20, 30], "nth", 1, 20),
        ([10, 20, 30], "nth", -1, 30),
        ([{"score": 5}, {"score": 2}, {"score": 8}], "min_by", "score", {"score": 2}),
        ([{"score": 5}, {"score": 2}, {"score": 8}], "max_by", "score", {"score": 8}),
        ([{"id": 1}, {"id": 2}, {"id": 3}], "index_of", "id == 2", 1),
        (
            [{"status": "active"}, {"status": "inactive"}, {"status": "active"}],
            "random_except",
            "status == 'inactive'",
            {"status": "active"},
        ),
    ],
)
async def test_select_from_list_new_options(client, items, operation, param, expected):
    params = {"items": items, "operation": operation}
    if param is not None:
        # For expression-based operations, use expression parameter
        if operation in ["index_of", "random_except"]:
            params["expression"] = param
        else:
            params["param"] = param
    value, error = await make_tool_call(client, "lists", params)
    if operation == "random_except":
        assert value is not None
        assert value in [i for i in items if i["status"] == "active"]
    else:
        if isinstance(expected, dict):
            assert value is not None
            assert value == expected
        else:
            assert value is not None
            assert value == expected


# --- Tests for generate tool ---
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input, operation, param, expected",
    [
        (None, "range", [0, 5], [0, 1, 2, 3, 4]),
        (None, "range", [1, 10, 3], [1, 4, 7]),
        (None, "range", [5, 5], []),
        (None, "range", [5, 1, -1], [5, 4, 3, 2]),
        (
            [[1, 2], ["a", "b"]],
            "cartesian_product",
            None,
            [(1, "a"), (1, "b"), (2, "a"), (2, "b")],
        ),
        ("x", "repeat", 3, ["x", "x", "x"]),
        ([1, 2], "powerset", None, [[], [1], [2], [1, 2]]),
        ([1, 2, 3, 4], "windowed", 2, [(1, 2), (2, 3), (3, 4)]),
        ([1, 2], "cycle", 5, [1, 2, 1, 2, 1]),
        ([1, 2, 3], "accumulate", None, [1, 3, 6]),
        ([1, 2, 3, 4], "accumulate", "mul", [1, 2, 6, 24]),
        (["a", "b", "c"], "zip_with_index", None, [(0, "a"), (1, "b"), (2, "c")]),
        ([1, 2, 3], "unique_pairs", None, [(1, 2), (1, 3), (2, 3)]),
        (
            [1, 2, 3],
            "permutations",
            None,
            [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]],
        ),
        (
            [1, 2, 3],
            "permutations",
            2,
            [[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]],
        ),
        (
            [1, 2, 3, 4],
            "combinations",
            2,
            [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]],
        ),
        ([], "powerset", None, [[]]),
        ([], "permutations", None, [[]]),
        ([], "combinations", 1, []),
        ([1, 2, 3], "windowed", 4, []),
        ([1, 2, 3], "windowed", 1, [(1,), (2,), (3,)]),
        ([1, 2, 3], "windowed", 0, ValueError),
        ([1, 2, 3], "cycle", None, ValueError),
        ([1, 2, 3], "accumulate", "invalid", ValueError),
        ([1, 2, 3], "combinations", None, ValueError),
        ([1, 2, 3], "not_a_real_op", None, ValueError),
    ],
)
async def test_generate(client, input, operation, param, expected):
    # Map old parameters to new options format
    options = {}

    if operation == "range":
        if isinstance(param, list) and len(param) >= 2:
            options["from"] = param[0]
            options["to"] = param[1]
            if len(param) > 2:
                options["step"] = param[2]
    elif operation == "cartesian_product":
        options["lists"] = input
    elif operation == "repeat":
        options["value"] = input
        options["count"] = param
    elif operation in ["powerset", "unique_pairs", "zip_with_index"]:
        options["items"] = input
    elif operation == "windowed":
        options["items"] = input
        options["size"] = param
    elif operation == "cycle":
        options["items"] = input
        options["count"] = param
    elif operation == "accumulate":
        options["items"] = input
        if param is not None:
            options["func"] = param
    elif operation == "permutations":
        options["items"] = input
        if param is not None:
            options["length"] = param
    elif operation == "combinations":
        options["items"] = input
        options["length"] = param

    params = {"options": options, "operation": operation}
    value, error = await make_tool_call(client, "generate", params)
    if expected is ValueError:
        assert error is not None
    else:

        def normalize(x):
            if isinstance(x, tuple):
                return list(x)
            if isinstance(x, list):
                return [normalize(i) for i in x]
            return x

        assert normalize(value) == normalize(expected)


# --- Direct function call tests for generate ---
@pytest.mark.asyncio
async def test_generate_powerset_direct():
    import main

    result = await main.generate.run(
        {"options": {"items": []}, "operation": "powerset"}
    )
    actual = json.loads(result[0].text)  # type: ignore
    assert actual["value"] == [[]]


@pytest.mark.asyncio
async def test_generate_permutations_direct():
    import main

    result = await main.generate.run(
        {"options": {"items": []}, "operation": "permutations"}
    )
    actual = json.loads(result[0].text)  # type: ignore
    assert actual["value"] == [[]]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input, param, expected",
    [
        ("foo", 2, ["foo", "foo"]),
        (42, 2, [42, 42]),
        (3.14, 2, [3.14, 3.14]),
        (True, 2, [True, True]),
        ([1, 2], 2, [[1, 2], [1, 2]]),
        ({"a": 1}, 2, [{"a": 1}, {"a": 1}]),
        (None, 2, [None, None]),
    ],
)
async def test_generate_repeat_all_types(client, input, param, expected):
    value, error = await make_tool_call(
        client,
        "generate",
        {"options": {"value": input, "count": param}, "operation": "repeat"},
    )
    assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, path, value, expected",
    [
        ({}, "x", "foo", {"x": "foo"}),
        ({}, "x", 42, {"x": 42}),
        ({}, "x", 3.14, {"x": 3.14}),
        ({}, "x", True, {"x": True}),
        ({}, "x", [1, 2], {"x": [1, 2]}),
        ({}, "x", {"a": 1}, {"x": {"a": 1}}),
        ({}, "x", None, {"x": None}),
    ],
)
async def test_set_value_all_types(client, obj, path, value, expected):
    value_out, error = await make_tool_call(
        client,
        "dicts",
        {"obj": obj, "operation": "set_value", "path": path, "value": value},
    )
    assert value_out == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, path, default, expected",
    [
        ({"x": "foo"}, "x", None, "foo"),
        ({"x": 42}, "x", None, 42),
        ({"x": 3.14}, "x", None, 3.14),
        ({"x": True}, "x", None, True),
        ({"x": [1, 2]}, "x", None, [1, 2]),
        ({"x": {"a": 1}}, "x", None, {"a": 1}),
        ({}, "x", None, None),
        ({}, "x", "foo", "foo"),
        ({}, "x", 42, 42),
        ({}, "x", 3.14, 3.14),
        ({}, "x", True, True),
        ({}, "x", [1, 2], [1, 2]),
        ({}, "x", {"a": 1}, {"a": 1}),
        ({}, "x", None, None),
    ],
)
async def test_get_value_all_types(client, obj, path, default, expected):
    args = {"obj": obj, "operation": "get_value", "path": path}
    if default is not None or (default is None and "x" not in obj):
        args["default"] = default
    value, error = await make_tool_call(client, "dicts", args)
    assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input, tool_calls, expected",
    [
        ("foo", [{"tool": "strings", "params": {"operation": "reverse"}}], "oof"),
        (
            42,
            [{"tool": "generate", "params": {"operation": "repeat", "count": 2}}],
            [42, 42],
        ),
        (
            3.14,
            [{"tool": "generate", "params": {"operation": "repeat", "count": 2}}],
            [3.14, 3.14],
        ),
        (
            True,
            [{"tool": "generate", "params": {"operation": "repeat", "count": 2}}],
            [True, True],
        ),
        (
            [1, 2],
            [{"tool": "generate", "params": {"operation": "repeat", "count": 2}}],
            [[1, 2], [1, 2]],
        ),
        (
            {"a": 1},
            [{"tool": "generate", "params": {"operation": "repeat", "count": 2}}],
            [{"a": 1}, {"a": 1}],
        ),
        (
            None,
            [{"tool": "generate", "params": {"operation": "repeat", "count": 2}}],
            [None, None],
        ),
    ],
)
async def test_chain_all_types(client, input, tool_calls, expected):
    value, error = await make_tool_call(
        client, "chain", {"input": input, "tool_calls": tool_calls}
    )
    assert value == expected
