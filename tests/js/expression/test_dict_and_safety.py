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
