from tests import make_tool_call
import pytest


@pytest.mark.asyncio
async def test_dict_map_values_expression(client):
    obj = {"a": 1, "b": 2, "c": 3}

    result, error = await make_tool_call(
        client,
        "dicts",
        {"obj": obj, "operation": "map_values", "expression": "value * 2"},
    )
    assert error is None
    assert result == {"a": 2, "b": 4, "c": 6}


@pytest.mark.asyncio
async def test_dict_map_keys_expression(client):
    obj = {"firstName": "John", "lastName": "Doe"}

    result, error = await make_tool_call(
        client,
        "dicts",
        {"obj": obj, "operation": "map_keys", "expression": "key.toLowerCase()"},
    )
    assert error is None
    assert result == {"firstname": "John", "lastname": "Doe"}


@pytest.mark.asyncio
async def test_dicts_map_keys_js(client):
    """Test dicts.map_keys operation with JavaScript expressions."""
    # Transform keys to uppercase
    value, error = await make_tool_call(
        client,
        "dicts",
        {
            "obj": {"a": 1, "b": 2},
            "operation": "map_keys",
            "expression": "key.toUpperCase()",
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
            "expression": "'user_' + key",
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
async def test_dicts_map_values_js(client):
    """Test dicts.map_values operation with JavaScript expressions."""
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
            "expression": "value.toUpperCase()",
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_values",
    [
        ([{"x": 1, "y": 2}, {"x": 3, "y": 4}], "item.x + item.y", [3, 7]),
        (
            [{"name": "alice"}, {"name": "bob"}],
            "item.name.toUpperCase()",
            ["ALICE", "BOB"],
        ),
        (
            [{"age": 25}, {"age": 30}],
            "item.age >= 30 ? 'adult' : 'young'",
            ["young", "adult"],
        ),
        # Conditional expression
        (
            [{"score": 95}, {"score": 85}, {"score": 75}, {"score": 92}],
            "item.score >= 90 ? 'high' : 'normal'",
            ["high", "normal", "normal", "high"],
        ),
    ],
)
async def test_pluck_expression(client, items, expression, expected_values):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "pluck", "expression": expression},
    )
    assert error is None
    assert result == expected_values
