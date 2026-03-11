from tests import make_tool_call
import pytest


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
async def test_generate_powerset_direct(client):
    value, error = await make_tool_call(
        client, "generate", {"options": {"items": []}, "operation": "powerset"}
    )
    assert error is None
    assert value == [[]]


@pytest.mark.asyncio
async def test_generate_permutations_direct(client):
    value, error = await make_tool_call(
        client, "generate", {"options": {"items": []}, "operation": "permutations"}
    )
    assert error is None
    assert value == [[]]


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
