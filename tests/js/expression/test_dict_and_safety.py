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
    "value, expression, expected_result",
    [
        (None, "value === null", True),  # Python None becomes JS null
        ([1, None, 3], "value[1] === null", True),  # Array element None becomes null
        (
            {"name": "Alice", "age": None},
            "value.age === null",
            True,
        ),  # Object property None becomes null
        (
            {"user": {"metadata": None}},
            "value.user.metadata === null",
            True,
        ),  # Nested property None becomes null
        (
            [None, 2, None],
            "value[0] === null && value[2] === null",
            True,
        ),  # Multiple null checks
        (
            {"score": None},
            "value.score !== null ? 'has score' : 'no score'",
            "no score",
        ),  # Ternary with null
    ],
)
async def test_null_handling_expression(client, value, expression, expected_result):
    result, error = await make_tool_call(
        client, "any", {"value": value, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result, description",
    [
        (None, 'value ? "truthy" : "falsy"', "falsy", "null is falsy in JS"),
        (None, "typeof value", "object", "None type is object (null) in JS"),
        ([None, None], "value[0] === value[1]", True, "null equality works"),
        ([1, None, 3], "value.length", 3, "arrays with null preserve length"),
        (
            [1, None, 3],
            "value.length",
            3,
            "array length works with null",
        ),
    ],
)
async def test_null_sentinel_behavior(
    client, value, expression, expected_result, description
):
    result, error = await make_tool_call(
        client, "any", {"value": value, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result, f"Failed: {description}"


@pytest.mark.asyncio
async def test_safe_mode_blocks_dangerous_operations(client):
    # Test that dangerous operations are blocked
    result, error = await make_tool_call(
        client,
        "any",
        {
            "value": {"test": "data"},
            "operation": "eval",
            "expression": "typeof require !== 'undefined' ? 'dangerous' : 'safe'",
        },
    )
    assert error is None
    assert result == "safe"


@pytest.mark.asyncio
async def test_safe_mode_allows_safe_operations(client):
    # Test that safe operations work
    result, error = await make_tool_call(
        client,
        "any",
        {
            "value": {"test": "data"},
            "operation": "eval",
            "expression": "Date.now() > 0",
        },
    )
    assert error is None
    assert result is True
