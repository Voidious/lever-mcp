from tests import make_tool_call
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_name",
    [
        (
            [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
            "age > 27",
            "Alice",
        ),
        (
            [{"name": "Alice", "score": 85}, {"name": "Bob", "score": 92}],
            "score > 90",
            "Bob",
        ),
        (
            [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
            ],
            "age > 25 and score > 80",
            "Alice",
        ),
        (
            [
                {"name": "Alice", "status": "active"},
                {"name": "Bob", "status": "inactive"},
            ],
            "status == 'active'",
            "Alice",
        ),
    ],
)
async def test_find_by_expression(client, items, expression, expected_name):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "find_by", "expression": expression},
    )
    assert error is None
    assert result is not None
    assert result["name"] == expected_name


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_count",
    [
        (
            [{"score": 85}, {"score": 70}, {"score": 90}],
            "score < 80",
            2,
        ),  # Remove score < 80, keep 2
        (
            [{"age": 25}, {"age": 35}, {"age": 20}],
            "age < 30",
            1,
        ),  # Remove age < 30, keep 1
        (
            [{"status": "active"}, {"status": "inactive"}, {"status": "active"}],
            "status == 'inactive'",
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
    "items, expression, expected_groups",
    [
        (
            [{"age": 30}, {"age": 25}, {"age": 35}],
            "age >= 30 and 'senior' or 'junior'",
            ["senior", "junior"],
        ),
        (
            [{"score": 90}, {"score": 70}, {"score": 85}],
            "score >= 80 and 'high' or 'low'",
            ["high", "low"],
        ),
        ([{"dept": "eng"}, {"dept": "mkt"}, {"dept": "eng"}], "dept", ["eng", "mkt"]),
        # Complex grouping from test_expressions.py
        (
            [
                {"name": "Alice", "age": 25, "department": "engineering"},
                {"name": "Bob", "age": 30, "department": "marketing"},
                {"name": "Charlie", "age": 35, "department": "engineering"},
                {"name": "Diana", "age": 28, "department": "design"},
            ],
            "age >= 30 and department or 'junior_' .. department",
            ["engineering", "marketing", "junior_engineering", "junior_design"],
        ),
    ],
)
async def test_group_by_expression(client, items, expression, expected_groups):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "group_by", "expression": expression},
    )
    assert error is None
    for group in expected_groups:
        assert group in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_order",
    [
        (
            [{"name": "bob"}, {"name": "Alice"}, {"name": "charlie"}],
            "string.lower(name)",
            ["Alice", "bob", "charlie"],
        ),
        (
            [{"age": 30}, {"age": 25}, {"age": 35}],
            "age * -1",
            [35, 30, 25],
        ),  # Reverse order
        ([{"score": 85}, {"score": 92}, {"score": 78}], "score", [78, 85, 92]),
        # Complex expression from test_expressions.py
        (
            [
                {"name": "Alice", "age": 25, "score": 95},
                {"name": "Bob", "age": 30, "score": 85},
                {"name": "Charlie", "age": 35, "score": 75},
                {"name": "Diana", "age": 28, "score": 92},
            ],
            "score * age",
            [
                "Alice",
                "Bob",
                "Diana",
                "Charlie",
            ],  # Sort by score*age: 2375, 2550, 2576, 2625
        ),
    ],
)
async def test_sort_by_expression(client, items, expression, expected_order):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "sort_by", "expression": expression},
    )
    assert error is None
    assert result is not None
    if "name" in items[0]:
        actual_order = [item["name"] for item in result]
    elif "age" in items[0]:
        actual_order = [item["age"] for item in result]
    else:
        actual_order = [item["score"] for item in result]
    assert actual_order == expected_order


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_values",
    [
        ([{"x": 1, "y": 2}, {"x": 3, "y": 4}], "x + y", [3, 7]),
        ([{"name": "alice"}, {"name": "bob"}], "string.upper(name)", ["ALICE", "BOB"]),
        (
            [{"age": 25}, {"age": 30}],
            "age >= 30 and 'adult' or 'young'",
            ["young", "adult"],
        ),
        # Conditional expression from test_expressions.py
        (
            [{"score": 95}, {"score": 85}, {"score": 75}, {"score": 92}],
            "score >= 90 and 'high' or 'normal'",
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, operation, expected_value",
    [
        (
            [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 0, "y": 1}],
            "x*x + y*y",
            "min_by",
            {"x": 0, "y": 1},
        ),  # Closest to origin
        (
            [{"age": 25}, {"age": 30}, {"age": 35}],
            "age * -1",
            "max_by",
            {"age": 25},
        ),  # Max of negative age = youngest
        (
            [{"score": 85}, {"score": 92}, {"score": 78}],
            "score",
            "max_by",
            {"score": 92},
        ),
        (
            [{"score": 85}, {"score": 92}, {"score": 78}],
            "score",
            "min_by",
            {"score": 78},
        ),
        # Additional test from test_expressions.py - best score/age ratio
        (
            [
                {"name": "Alice", "age": 25, "score": 95},
                {"name": "Bob", "age": 30, "score": 85},
                {"name": "Charlie", "age": 35, "score": 75},
                {"name": "Diana", "age": 28, "score": 92},
            ],
            "score / age",
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
            "category == 'fruit'",
            "difference_by",
            1,  # Only the fruit item (True) since vegetable item matches others (False)
        ),
        (
            [{"id": 1, "category": "fruit"}, {"id": 2, "category": "vegetable"}],
            [{"id": 3, "category": "vegetable"}],
            "category == 'vegetable'",
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
    "items, operation, expression, expected_count",
    [
        # Test lists.min_by with new items
        (
            [{"score": 85}, {"score": 92}, {"score": 78}],
            "min_by",
            "score",
            1,  # One result: the minimum item
        ),
        # Test lists.max_by with new items
        (
            [{"age": 25}, {"age": 30}, {"age": 20}],
            "max_by",
            "age",
            1,  # One result: the maximum item
        ),
    ],
)
async def test_complex_expressions_with_new_operations(
    client, items, operation, expression, expected_count
):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": operation, "expression": expression},
    )
    assert error is None
    if expected_count == 1:
        assert result is not None  # Should return a single item, not a list
    else:
        assert len(result) == expected_count
