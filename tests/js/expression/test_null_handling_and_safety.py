from tests import make_tool_call
import pytest


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
@pytest.mark.parametrize(
    "value, expression, expected_result",
    [
        (
            {"score": 85},
            # Multiline with let and return
            "let newScore = value.score + 5; return newScore;",
            90,
        ),
        (
            {"name": "Alice", "age": 30},
            # Proper if/else statement
            (
                "if (value.age > 25) { return value.name + ' is a senior'; } "
                "else { return value.name + ' is a junior'; }"
            ),
            "Alice is a senior",
        ),
        (
            {"data": [10, 20, 30]},
            # Proper for loop
            (
                "let total = 0; for (let item of value.data) { total += item; } "
                "return total;"
            ),
            60,
        ),
    ],
)
async def test_multiline_expression(client, value, expression, expected_result):
    result, error = await make_tool_call(
        client, "any", {"value": value, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result, description",
    [
        # Complex null filtering (since Python None becomes JS null)
        (
            [
                {"name": "Alice", "score": 85, "metadata": None},
                {"name": "Bob", "score": None, "metadata": {"priority": "high"}},
            ],
            "value[1].score === null",  # Find Bob with null score
            True,
            "Complex null filtering in nested structures",
        ),
        # Return null values from expressions - these should be converted to Python None
        ({"test": "data"}, "null", None, "Return direct null from expression"),
        ({"test": "data"}, "[1, null, 3]", [1, None, 3], "Return list with null"),
        (
            {"test": "data"},
            "({a: 1, b: null, c: 3})",
            {"a": 1, "b": None, "c": 3},
            "Return dict with null",
        ),
    ],
)
async def test_complex_null_handling(
    client, value, expression, expected_result, description
):
    if isinstance(value, list):
        # For list operations, use the first item
        result, error = await make_tool_call(
            client,
            "any",
            {"value": value, "operation": "eval", "expression": expression},
        )
    else:
        result, error = await make_tool_call(
            client,
            "any",
            {"value": value, "operation": "eval", "expression": expression},
        )
    assert error is None
    assert result == expected_result, f"Failed: {description}"
