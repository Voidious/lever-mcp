from tests import make_tool_call
import pytest


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
async def test_dicts_map_keys(client):
    """Test dicts.map_keys operation with Lua expressions."""
    # Transform keys to uppercase
    value, error = await make_tool_call(
        client,
        "dicts",
        {
            "obj": {"a": 1, "b": 2},
            "operation": "map_keys",
            "expression": "string.upper(key)",
        },
    )
    assert error is None
    assert value == {"A": 1, "B": 2}

    # Add prefix to keys
    value, error = await make_tool_call(
        client,
        "dicts",
        {
            "obj": {"name": "John", "age": 30},
            "operation": "map_keys",
            "expression": "'user_' .. key",
        },
    )
    assert error is None
    assert value == {"user_name": "John", "user_age": 30}

    # Missing expression should error
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a": 1}, "operation": "map_keys"}
    )
    assert error is not None
    assert "expression is required for map_keys operation" in error

    # Non-dict should error
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": "not_a_dict", "operation": "map_keys", "expression": "key"},
    )
    assert error is not None
    assert "Dict operation 'map_keys' requires a dictionary input" in error


@pytest.mark.asyncio
async def test_dicts_map_values(client):
    """Test dicts.map_values operation with Lua expressions."""
    # Double all values
    value, error = await make_tool_call(
        client,
        "dicts",
        {
            "obj": {"a": 1, "b": 2, "c": 3},
            "operation": "map_values",
            "expression": "value * 2",
        },
    )
    assert error is None
    assert value == {"a": 2, "b": 4, "c": 6}

    # Transform strings to uppercase
    value, error = await make_tool_call(
        client,
        "dicts",
        {
            "obj": {"name": "john", "city": "tokyo"},
            "operation": "map_values",
            "expression": "string.upper(value)",
        },
    )
    assert error is None
    assert value == {"name": "JOHN", "city": "TOKYO"}

    # Missing expression should error
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a": 1}, "operation": "map_values"}
    )
    assert error is not None
    assert "expression is required for map_values operation" in error

    # Non-dict should error
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": "not_a_dict", "operation": "map_values", "expression": "value"},
    )
    assert error is not None
    assert "Dict operation 'map_values' requires a dictionary input" in error
