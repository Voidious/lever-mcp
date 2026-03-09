from tests import make_tool_call
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result",
    [
        (None, "value == null", True),
        ([1, None, 3], "value[2] == null", True),
        ({"name": "Alice", "age": None}, "age == null", True),
        ({"user": {"metadata": None}}, "user.metadata == null", True),
        ([None, 2, None], "value[1] == null and value[3] == null", True),
        ({"score": None}, "score ~= null and 'has score' or 'no score'", "no score"),
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
        (None, 'value and "truthy" or "falsy"', "truthy", "null is truthy"),
        (None, "type(value)", "table", "null type is table"),
        ([None, None], "value[1] == value[2]", True, "null equality works"),
        ([1, None, 3], "#value", 3, "arrays with null preserve length"),
        (
            [1, None, 3],
            "local count = 0; for i, v in ipairs(value) do count = count + 1 end; "
            "return count",
            3,
            "ipairs works with null",
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
        ({"score": 85}, "local new_score = score + 5\nreturn new_score", 90),
        (
            {"name": "Alice", "age": 30},
            "if age > 25 then\n  return name .. ' is a senior'\nelse\n  return name .. "
            "' is a junior'\nend",
            "Alice is a senior",
        ),
        (
            {"data": [10, 20, 30]},
            "local total = 0\nfor i, v in ipairs(data) do\n  total = total + "
            "v\nend\nreturn total",
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
    # Test that os.execute is blocked in safe mode
    result, error = await make_tool_call(
        client,
        "any",
        {
            "value": {"test": "data"},
            "operation": "eval",
            "expression": "os.execute and 'dangerous' or 'safe'",
        },
    )
    assert error is None
    assert result == "safe"


@pytest.mark.asyncio
async def test_safe_mode_allows_safe_operations(client):
    # Test that safe os functions work
    result, error = await make_tool_call(
        client,
        "any",
        {"value": {"test": "data"}, "operation": "eval", "expression": "os.time() > 0"},
    )
    assert error is None
    assert result is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, operation, expression, expected_result",
    [
        # Complex conditional expressions
        (
            [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
                {"name": "Charlie", "age": 35, "score": 78},
            ],
            "find_by",
            "age > 30",
            "Charlie",
        ),
        (
            [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
                {"name": "Charlie", "age": 35, "score": 78},
            ],
            "find_by",
            "score > 90",
            "Bob",
        ),
        (
            [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
                {"name": "Charlie", "age": 35, "score": 78},
            ],
            "find_by",
            "age > 25 and score > 80",
            "Alice",
        ),
        # Engineering department filtering
        (
            [
                {"name": "Alice", "department": "engineering"},
                {"name": "Bob", "department": "marketing"},
            ],
            "find_by",
            "department == 'engineering'",
            "Alice",
        ),
    ],
)
async def test_complex_expressions(
    client, items, operation, expression, expected_result
):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": operation, "expression": expression},
    )
    assert error is None
    assert result is not None
    if isinstance(expected_result, str):
        assert result["name"] == expected_result
    else:
        assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result, description",
    [
        # Complex null filtering
        (
            [
                {"name": "Alice", "score": 85, "metadata": None},
                {"name": "Bob", "score": None, "metadata": {"priority": "high"}},
            ],
            "value[2].score == null",  # Find Bob with null score
            True,
            "Complex null filtering in nested structures",
        ),
        # Return null values from expressions
        ({"test": "data"}, "null", None, "Return direct null from expression"),
        ({"test": "data"}, "{1, null, 3}", [1, None, 3], "Return list with null"),
        (
            {"test": "data"},
            "{a = 1, b = null, c = 3}",
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
