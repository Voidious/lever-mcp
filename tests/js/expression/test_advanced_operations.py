from tests import make_tool_call
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, operation, expected_value",
    [
        (
            [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 0, "y": 1}],
            "item.x*item.x + item.y*item.y",
            "min_by",
            {"x": 0, "y": 1},
        ),  # Closest to origin
        (
            [{"age": 25}, {"age": 30}, {"age": 35}],
            "item.age * -1",
            "max_by",
            {"age": 25},
        ),  # Max of negative age = youngest
        (
            [{"score": 85}, {"score": 92}, {"score": 78}],
            "item.score",
            "max_by",
            {"score": 92},
        ),
        (
            [{"score": 85}, {"score": 92}, {"score": 78}],
            "item.score",
            "min_by",
            {"score": 78},
        ),
        # Best score/age ratio
        (
            [
                {"name": "Alice", "age": 25, "score": 95},
                {"name": "Bob", "age": 30, "score": 85},
                {"name": "Charlie", "age": 35, "score": 75},
                {"name": "Diana", "age": 28, "score": 92},
            ],
            "item.score / item.age",
            "max_by",
            {
                "name": "Alice",
                "age": 25,
                "score": 95,
            },  # Highest score/age ratio: 95/25=3.8
        ),
    ],
)
async def test_min_max_by_expression(
    client, items, expression, operation, expected_value
):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": operation, "expression": expression},
    )
    assert error is None
    assert result == expected_value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, others, expression, operation, expected_count",
    [
        (
            [{"id": 1, "category": "fruit"}, {"id": 2, "category": "vegetable"}],
            [{"id": 3, "category": "vegetable"}],
            "item.category === 'fruit'",
            "difference_by",
            1,  # Only the fruit item (True) since vegetable item matches others (False)
        ),
        (
            [{"id": 1, "category": "fruit"}, {"id": 2, "category": "vegetable"}],
            [{"id": 3, "category": "vegetable"}],
            "item.category === 'vegetable'",
            "intersection_by",
            1,  # Only vegetables that match
        ),
    ],
)
async def test_difference_intersection_by_expression(
    client, items, others, expression, operation, expected_count
):
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "others": others,
            "operation": operation,
            "expression": expression,
        },
    )
    assert error is None
    assert result is not None
    assert len(result) == expected_count


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_count",
    [
        (
            [{"score": 85}, {"score": 70}, {"score": 90}],
            "item.score < 80",
            2,
        ),  # Remove score < 80, keep 2
        (
            [{"age": 25}, {"age": 35}, {"age": 20}],
            "item.age < 30",
            1,
        ),  # Remove age < 30, keep 1
        (
            [{"status": "active"}, {"status": "inactive"}, {"status": "active"}],
            "item.status === 'inactive'",
            2,
        ),  # Remove inactive, keep 2
    ],
)
async def test_remove_by_expression(client, items, expression, expected_count):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "remove_by", "expression": expression},
    )
    assert error is None
    assert result is not None
    assert len(result) == expected_count


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
            "item.age > 30",
            "Charlie",
        ),
        (
            [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
                {"name": "Charlie", "age": 35, "score": 78},
            ],
            "find_by",
            "item.score > 90",
            "Bob",
        ),
        (
            [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
                {"name": "Charlie", "age": 35, "score": 78},
            ],
            "find_by",
            "item.age > 25 && item.score > 80",
            "Alice",
        ),
        # Engineering department filtering
        (
            [
                {"name": "Alice", "department": "engineering"},
                {"name": "Bob", "department": "marketing"},
            ],
            "find_by",
            "item.department === 'engineering'",
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
