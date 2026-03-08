from tests import make_tool_call
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, operation, param, data, expected_result",
    [
        # strings.split operation
        ("a,b,c", "split", ",", None, ["a", "b", "c"]),
        ("hello world test", "split", " ", None, ["hello", "world", "test"]),
        ("one|two|three", "split", "|", None, ["one", "two", "three"]),
        ("no_delimiter", "split", ",", None, ["no_delimiter"]),
        ("", "split", ",", None, [""]),
        # strings.slice operation
        ("hello world", "slice", None, {"from": 0, "to": 5}, "hello"),
        ("testing", "slice", None, {"from": 1, "to": 4}, "est"),
        ("python", "slice", None, {"from": 2}, "thon"),  # from to end
        ("slice", "slice", None, {"from": 0, "to": 3}, "sli"),  # from start to index 3
    ],
)
async def test_new_string_operations_expressions(
    client, text, operation, param, data, expected_result
):
    call_params = {"text": text, "operation": operation}
    if param is not None:
        call_params["param"] = param
    if data is not None:
        call_params["data"] = data

    result, error = await make_tool_call(client, "strings", call_params)
    assert error is None
    assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, operation, param, expected_result",
    [
        # lists.min operation
        ([1, 3, 2, 5, 4], "min", None, 1),
        ([10, 5, 15, 3], "min", None, 3),
        (["apple", "banana", "cherry"], "min", None, "apple"),  # alphabetical
        # lists.max operation
        ([1, 3, 2, 5, 4], "max", None, 5),
        ([10, 5, 15, 3], "max", None, 15),
        (["apple", "banana", "cherry"], "max", None, "cherry"),  # alphabetical
        # lists.join operation
        (["a", "b", "c"], "join", ",", "a,b,c"),
        (["hello", "world"], "join", " ", "hello world"),
        (["one", "two", "three"], "join", "|", "one|two|three"),
        (["single"], "join", ",", "single"),
        ([], "join", ",", ""),
    ],
)
async def test_new_list_operations_expressions(
    client, items, operation, param, expected_result
):
    call_params = {"items": items, "operation": operation}
    if param is not None:
        call_params["param"] = param

    result, error = await make_tool_call(client, "lists", call_params)
    assert error is None
    assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, operation, expression, expected_result",
    [
        # lists.min_by operation
        (
            [{"score": 85}, {"score": 92}, {"score": 78}],
            "min_by",
            "score",
            {"score": 78},
        ),
        (
            [
                {"age": 25, "name": "Alice"},
                {"age": 30, "name": "Bob"},
                {"age": 20, "name": "Charlie"},
            ],
            "min_by",
            "age",
            {"age": 20, "name": "Charlie"},
        ),
        # lists.max_by operation
        (
            [{"score": 85}, {"score": 92}, {"score": 78}],
            "max_by",
            "score",
            {"score": 92},
        ),
        (
            [
                {"age": 25, "name": "Alice"},
                {"age": 30, "name": "Bob"},
                {"age": 20, "name": "Charlie"},
            ],
            "max_by",
            "age",
            {"age": 30, "name": "Bob"},
        ),
        # Complex expressions for min_by/max_by
        (
            [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 0, "y": 1}],
            "min_by",
            "x*x + y*y",  # Distance from origin
            {"x": 0, "y": 1},
        ),
        (
            [
                {"score": 90, "age": 25},
                {"score": 85, "age": 30},
                {"score": 95, "age": 28},
            ],
            "max_by",
            "score / age",  # Best score-to-age ratio
            {"score": 90, "age": 25},
        ),
    ],
)
async def test_new_list_by_operations_expressions(
    client, items, operation, expression, expected_result
):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": operation, "expression": expression},
    )
    assert error is None
    assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, operation, expected_result",
    [
        # dicts.keys operation
        ({"a": 1, "b": 2, "c": 3}, "keys", ["a", "b", "c"]),
        ({"name": "Alice", "age": 30}, "keys", ["name", "age"]),
        ({}, "keys", []),
        # dicts.values operation
        ({"a": 1, "b": 2, "c": 3}, "values", [1, 2, 3]),
        ({"name": "Alice", "age": 30}, "values", [30, "Alice"]),
        ({}, "values", []),
        # dicts.items operation
        ({"a": 1, "b": 2}, "items", [["a", 1], ["b", 2]]),
        ({"name": "Alice", "age": 30}, "items", [["name", "Alice"], ["age", 30]]),
        ({}, "items", []),
    ],
)
async def test_new_dict_operations_expressions(client, obj, operation, expected_result):
    result, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": operation}
    )
    assert error is None
    if operation == "values" and any(isinstance(x, str) for x in expected_result):
        # Handle mixed types - sort separately by type then combine
        assert len(result) == len(expected_result)
        assert set(result) == set(expected_result)
    else:
        assert sorted(result) == sorted(expected_result)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, operation, expression, expected_result",
    [
        # dicts.map_keys operation
        (
            {"name": "Alice", "age": 30},
            "map_keys",
            "string.upper(key)",
            {"NAME": "Alice", "AGE": 30},
        ),
        (
            {"first": "John", "last": "Doe"},
            "map_keys",
            "key .. '_field'",
            {"first_field": "John", "last_field": "Doe"},
        ),
        # dicts.map_values operation
        (
            {"a": 1, "b": 2, "c": 3},
            "map_values",
            "value * 2",
            {"a": 2, "b": 4, "c": 6},
        ),
        (
            {"greeting": "hello", "name": "world"},
            "map_values",
            "string.upper(value)",
            {"greeting": "HELLO", "name": "WORLD"},
        ),
    ],
)
async def test_new_dict_transformation_expressions(
    client, obj, operation, expression, expected_result
):
    result, error = await make_tool_call(
        client,
        "dicts",
        {"obj": obj, "operation": operation, "expression": expression},
    )
    assert error is None
    assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, operation, expected_result",
    [
        # dicts.flatten_keys operation
        (
            {"a": {"b": {"c": 1}}, "d": 2},
            "flatten_keys",
            {"a.b.c": 1, "d": 2},
        ),
        (
            {"user": {"name": "Alice", "profile": {"age": 30}}},
            "flatten_keys",
            {"user.name": "Alice", "user.profile.age": 30},
        ),
        # dicts.unflatten_keys operation
        (
            {"a.b.c": 1, "a.b.d": 2, "e": 3},
            "unflatten_keys",
            {"a": {"b": {"c": 1, "d": 2}}, "e": 3},
        ),
        (
            {"user.name": "Alice", "user.age": 30, "status": "active"},
            "unflatten_keys",
            {"user": {"name": "Alice", "age": 30}, "status": "active"},
        ),
    ],
)
async def test_new_dict_structure_expressions(client, obj, operation, expected_result):
    result, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": operation}
    )
    assert error is None
    assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected_result",
    [
        # any.size operation
        ("hello", 5),
        ([1, 2, 3, 4], 4),
        ({"a": 1, "b": 2}, 2),
        ("", 0),
        ([], 0),
        ({}, 0),
        (42, 1),  # scalar values have size 1
        (None, 0),  # null has size 0
        (True, 1),  # boolean has size 1
    ],
)
async def test_new_any_size_expressions(client, value, expected_result):
    result, error = await make_tool_call(
        client, "any", {"value": value, "operation": "size"}
    )
    assert error is None
    assert result == expected_result
