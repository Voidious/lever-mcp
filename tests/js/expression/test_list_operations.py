from tests import make_tool_call
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_name",
    [
        (
            [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
            "item.age > 27",
            "Alice",
        ),
        (
            [{"name": "Alice", "score": 85}, {"name": "Bob", "score": 92}],
            "item.score > 90",
            "Bob",
        ),
        (
            [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
            ],
            "item.age > 25 && item.score > 80",
            "Alice",
        ),
        (
            [
                {"name": "Alice", "status": "active"},
                {"name": "Bob", "status": "inactive"},
            ],
            "item.status === 'active'",
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
            "item.score >= 80",
            2,
        ),  # Keep items with score >= 80
        (
            [{"age": 25}, {"age": 35}, {"age": 20}],
            "item.age > 30",
            1,
        ),  # Keep items with age > 30
        (
            [{"active": True}, {"active": False}, {"active": True}],
            "item.active",
            2,
        ),  # Keep active items
    ],
)
async def test_filter_by_expression(client, items, expression, expected_count):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "filter_by", "expression": expression},
    )
    assert error is None
    assert len(result) == expected_count


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_result",
    [
        (
            [{"name": "alice"}, {"name": "bob"}],
            "item.name.toUpperCase()",
            ["ALICE", "BOB"],
        ),
        (
            [{"value": 1}, {"value": 2}, {"value": 3}],
            "item.value * 2",
            [2, 4, 6],
        ),
        (
            [{"first": "John", "last": "Doe"}, {"first": "Jane", "last": "Smith"}],
            "item.first + ' ' + item.last",
            ["John Doe", "Jane Smith"],
        ),
    ],
)
async def test_map_expression(client, items, expression, expected_result):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "map", "expression": expression},
    )
    assert error is None
    assert result == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_keys",
    [
        (
            [
                {"name": "Alice", "department": "Engineering"},
                {"name": "Bob", "department": "Sales"},
                {"name": "Charlie", "department": "Engineering"},
            ],
            "item.department",
            ["Engineering", "Sales"],
        ),
        (
            [{"age": 25}, {"age": 35}, {"age": 20}, {"age": 40}],
            "item.age >= 30 ? 'senior' : 'junior'",
            ["junior", "senior"],
        ),
    ],
)
async def test_group_by_expression(client, items, expression, expected_keys):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "group_by", "expression": expression},
    )
    assert error is None
    assert isinstance(result, dict)
    assert set(result.keys()) == set(expected_keys)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_order",
    [
        (
            [{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}],
            "item.name",
            [{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}],
        ),
        (
            [{"age": 30}, {"age": 20}, {"age": 25}],
            "item.age",
            [{"age": 20}, {"age": 25}, {"age": 30}],
        ),
        (
            [{"score": 85}, {"score": 95}, {"score": 75}],
            "-item.score",  # Reverse sort
            [{"score": 95}, {"score": 85}, {"score": 75}],
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
    assert result == expected_order


@pytest.mark.asyncio
async def test_any_by_expression(client):
    items = [{"score": 85}, {"score": 70}, {"score": 95}]

    # Test any_by - should find at least one item with score > 90
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "any_by", "expression": "item.score > 90"},
    )
    assert error is None
    assert result is True

    # Test all_by - should NOT find all items with score > 80
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "all_by", "expression": "item.score > 80"},
    )
    assert error is None
    assert result is False


@pytest.mark.asyncio
async def test_uniq_by_expression(client):
    items = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 1, "name": "Alice Duplicate"},
    ]

    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "uniq_by", "expression": "item.id"},
    )
    assert error is None
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2


@pytest.mark.asyncio
async def test_count_by_expression(client):
    items = [
        {"status": "active"},
        {"status": "inactive"},
        {"status": "active"},
        {"status": "pending"},
    ]

    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "count_by", "expression": "item.status"},
    )
    assert error is None
    assert isinstance(result, dict)
    assert result["active"] == 2
    assert result["inactive"] == 1
    assert result["pending"] == 1


@pytest.mark.asyncio
async def test_partition_expression(client):
    items = [{"age": 25}, {"age": 35}, {"age": 20}, {"age": 40}]

    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "partition", "expression": "item.age >= 30"},
    )
    assert error is None
    assert len(result) == 2
    assert len(result[0]) == 2  # Items with age >= 30
    assert len(result[1]) == 2  # Items with age < 30


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
            "item.score",
            {"score": 78},
        ),
        (
            [
                {"age": 25, "name": "Alice"},
                {"age": 30, "name": "Bob"},
                {"age": 20, "name": "Charlie"},
            ],
            "min_by",
            "item.age",
            {"age": 20, "name": "Charlie"},
        ),
        # lists.max_by operation
        (
            [{"score": 85}, {"score": 92}, {"score": 78}],
            "max_by",
            "item.score",
            {"score": 92},
        ),
        (
            [
                {"age": 25, "name": "Alice"},
                {"age": 30, "name": "Bob"},
                {"age": 20, "name": "Charlie"},
            ],
            "max_by",
            "item.age",
            {"age": 30, "name": "Bob"},
        ),
        # Complex expressions for min_by/max_by
        (
            [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 0, "y": 1}],
            "min_by",
            "item.x*item.x + item.y*item.y",  # Distance from origin
            {"x": 0, "y": 1},
        ),
        (
            [
                {"score": 90, "age": 25},
                {"score": 85, "age": 30},
                {"score": 95, "age": 28},
            ],
            "max_by",
            "item.score / item.age",  # Best score-to-age ratio
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
