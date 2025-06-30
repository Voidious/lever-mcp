import importlib
import pytest
import main
from main import LeverMCP
from fastmcp import Client
from . import make_tool_call


@pytest.fixture
async def client():
    """
    Provides an isolated FastMCP client for each test by reloading the main
    module and explicitly resetting the application state for the session.
    """
    importlib.reload(main)
    mcp_instance: LeverMCP = main.mcp
    async with Client(mcp_instance) as c:
        yield c


# --- Find By Expression Tests ---


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


# --- Remove By Expression Tests ---


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


# --- Group By Expression Tests ---


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


# --- Sort By Expression Tests ---


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


# --- Pluck Expression Tests ---


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


# --- Min/Max By Expression Tests ---


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


# --- Difference/Intersection By Expression Tests ---


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


# --- Any Eval Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result",
    [
        ({"age": 30, "name": "Alice"}, "age > 25", True),
        ({"x": 3, "y": 4}, "math.sqrt(x*x + y*y)", 5.0),
        ("hello", "string.upper(item)", "HELLO"),
        ([1, 2, 3, 4, 5], "#item", 5),
        (42, "item * 2 + 1", 85),
        ({"config": {"port": 8080}}, "config.port > 8000", True),
        # Additional test cases from test_expressions.py
        ({"items": [1, 2, 3, 4, 5]}, "items[4]", 4),  # 1-indexed access
        ({"config": {"port": 8080, "host": "localhost"}}, "config.port > 8000", True),
    ],
)
async def test_any_eval_expression(client, value, expression, expected_result):
    result, error = await make_tool_call(
        client, "any", {"value": value, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result


# --- Null Handling Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result",
    [
        (None, "item == null", True),
        ([1, None, 3], "item[2] == null", True),
        ({"name": "Alice", "age": None}, "age == null", True),
        ({"user": {"metadata": None}}, "user.metadata == null", True),
        ([None, 2, None], "item[1] == null and item[3] == null", True),
        ({"score": None}, "score ~= null and 'has score' or 'no score'", "no score"),
    ],
)
async def test_null_handling_expression(client, value, expression, expected_result):
    result, error = await make_tool_call(
        client, "any", {"value": value, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result


# --- Null Sentinel Behavior Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result, description",
    [
        (None, 'item and "truthy" or "falsy"', "truthy", "null is truthy"),
        (None, "type(item)", "table", "null type is table"),
        ([None, None], "item[1] == item[2]", True, "null equality works"),
        ([1, None, 3], "#item", 3, "arrays with null preserve length"),
        (
            [1, None, 3],
            "local count = 0; for i, v in ipairs(item) do count = count + 1 end; "
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


# --- Multi-line Expression Tests ---


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


# --- Safety Mode Tests ---


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


# --- Complex Expression Tests ---


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


# --- Complex Null Handling Tests ---


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
            "item[2].score == null",  # Find Bob with null score
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
