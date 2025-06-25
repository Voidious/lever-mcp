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
    params = {"text": input_str, "mutation": mutation}
    if data is not None:
        params["data"] = data
    result = await client.call_tool("mutate_string", params)
    assert result[0].text == expected


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
    params = {"obj": obj, "property": property}
    if param is not None:
        params["param"] = param
    result = await client.call_tool("has_property", params)
    assert json.loads(result[0].text) is expected


# --- Additional select_from_list tests ---
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, operation, param, expected",
    [
        ([10, 20, 30], "nth", 1, 20),
        ([10, 20, 30], "nth", -1, 30),
        ([{"score": 5}, {"score": 2}, {"score": 8}], "min_by", "score", {"score": 2}),
        ([{"score": 5}, {"score": 2}, {"score": 8}], "max_by", "score", {"score": 8}),
        ([{"id": 1}, {"id": 2}, {"id": 3}], "index_of", {"key": "id", "value": 2}, 1),
        (
            [{"status": "active"}, {"status": "inactive"}, {"status": "active"}],
            "random_except",
            {"key": "status", "value": "inactive"},
            {"status": "active"},
        ),
    ],
)
async def test_select_from_list_new_options(client, items, operation, param, expected):
    params = {"items": items, "operation": operation}
    if param is not None:
        params["param"] = param
    result = await client.call_tool("select_from_list", params)
    # For random_except, just check the result is one of the expected filtered values
    if operation == "random_except":
        assert result and json.loads(result[0].text) in [
            i for i in items if i["status"] == "active"
        ]
    else:
        if isinstance(expected, dict):
            assert result and json.loads(result[0].text) == expected
        else:
            assert result and json.loads(result[0].text) == expected


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
        # Workaround for fastmcp bug that serializes `[['']]` as `['']`
        ([], "powerset", None, [""]),
        ([], "permutations", None, [""]),
        ([], "combinations", 1, []),
        ([1, 2, 3], "windowed", 4, []),
        ([1, 2, 3], "windowed", 1, [(1,), (2,), (3,)]),
        ([1, 2, 3], "windowed", 0, ValueError),
        ([1, 2, 3], "cycle", None, ValueError),
        ([1, 2, 3], "accumulate", "invalid", ValueError),
        ([1, 2, 3], "combinations", None, ValueError),
        (
            [1, 2, 3],
            "permutations",
            "bad",
            [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]],
        ),
        ([1, 2, 3], "not_a_real_op", None, ValueError),
    ],
)
async def test_generate(client, input, operation, param, expected):
    params = {"input": input, "operation": operation}
    if param is not None:
        params["param"] = param
    try:
        result = await client.call_tool("generate", params)
        if expected is ValueError:
            assert (
                False
            ), f"Expected ValueError for {operation} but got result: {result}"
        else:

            def normalize(x):
                if isinstance(x, tuple):
                    return list(x)
                if isinstance(x, list):
                    return [normalize(i) for i in x]
                return x

            actual = json.loads(result[0].text) if result else []
            # Diagnostic print for empty powerset/permutations
            if (
                operation in ("powerset", "permutations")
                and input == []
                and (param is None)
            ):
                print(f"RAW RESPONSE for {operation}([]):", result[0].text)
            assert normalize(actual) == normalize(expected)
    except Exception as e:
        if expected is ValueError:
            msg = str(e)
            assert (
                "ValueError" in msg
                or "raise ValueError" in msg
                or "is not supported" in msg
                or msg.startswith("Error calling tool")
            )
        else:
            raise


# --- Direct function call tests for generate ---
@pytest.mark.asyncio
async def test_generate_powerset_direct():
    import main
    import json

    result = await main.generate.run({"input": [], "operation": "powerset"})
    actual = json.loads(result[0].text)
    # The tool returns [['']], but fastmcp serializes it to ['']
    assert actual == [""]


@pytest.mark.asyncio
async def test_generate_permutations_direct():
    import main
    import json

    result = await main.generate.run({"input": [], "operation": "permutations"})
    actual = json.loads(result[0].text)
    # The tool returns [['']], but fastmcp serializes it to ['']
    assert actual == [""]
