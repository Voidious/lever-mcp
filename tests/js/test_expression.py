from typing import Any
from dataclasses import dataclass
@dataclass
class TestFindByExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestFilterByExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestMapExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestGroupByExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestSortByExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestPluckExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestMinMaxByExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
@dataclass
class TestDifferenceIntersectionByExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
    field_4: Any
@dataclass
class TestRemoveByExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestNullHandlingExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestNullSentinelBehaviorResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
@dataclass
class TestMultilineExpressionResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestComplexExpressionsResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
@dataclass
class TestNewStringOperationsExpressionsResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
    field_4: Any
@dataclass
class TestNewListOperationsExpressionsResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
@dataclass
class TestNewListByOperationsExpressionsResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
@dataclass
class TestNewDictOperationsExpressionsResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestNewDictTransformationExpressionsResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
@dataclass
class TestNewDictStructureExpressionsResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestComplexExpressionsWithNewOperationsResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
@dataclass
class TestComplexNullHandlingResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
def assert_result_count(result, error, expected_count):
    assert error is None
    assert result is not None
    assert len(result) == expected_count


import importlib
import pytest
import main
from main import LeverMCP
from fastmcp import Client
from tests import make_tool_call


@pytest.fixture
async def client():
    """
    Provides an isolated FastMCP client for each test by reloading the main
    module and explicitly configuring it for JavaScript expressions.
    """
    importlib.reload(main)
    main.USE_JAVASCRIPT = True

    # Create fresh MCP instance with JavaScript tools
    mcp_instance = LeverMCP("Lever MCP")
    from tools.js import register_js_tools

    register_js_tools(mcp_instance)

    async with Client(mcp_instance) as c:
        yield c


# --- Find By Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_name",
    [
        TestFindByExpressionResult(field_0 = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}], field_1 = "item.age > 27", field_2 = "Alice"),
        TestFindByExpressionResult(field_0 = [{"name": "Alice", "score": 85}, {"name": "Bob", "score": 92}], field_1 = "item.score > 90", field_2 = "Bob"),
        TestFindByExpressionResult(field_0 = [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
            ], field_1 = "item.age > 25 && item.score > 80", field_2 = "Alice"),
        TestFindByExpressionResult(field_0 = [
                {"name": "Alice", "status": "active"},
                {"name": "Bob", "status": "inactive"},
            ], field_1 = "item.status === 'active'", field_2 = "Alice"),
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


# --- Filter By Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_count",
    [
        TestFilterByExpressionResult(field_0 = [{"score": 85}, {"score": 70}, {"score": 90}], field_1 = "item.score >= 80", field_2 = 2),  # Keep items with score >= 80
        TestFilterByExpressionResult(field_0 = [{"age": 25}, {"age": 35}, {"age": 20}], field_1 = "item.age > 30", field_2 = 1),  # Keep items with age > 30
        TestFilterByExpressionResult(field_0 = [{"active": True}, {"active": False}, {"active": True}], field_1 = "item.active", field_2 = 2),  # Keep active items
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


# --- Map Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_result",
    [
        TestMapExpressionResult(field_0 = [{"name": "alice"}, {"name": "bob"}], field_1 = "item.name.toUpperCase()", field_2 = ["ALICE", "BOB"]),
        TestMapExpressionResult(field_0 = [{"value": 1}, {"value": 2}, {"value": 3}], field_1 = "item.value * 2", field_2 = [2, 4, 6]),
        TestMapExpressionResult(field_0 = [{"first": "John", "last": "Doe"}, {"first": "Jane", "last": "Smith"}], field_1 = "item.first + ' ' + item.last", field_2 = ["John Doe", "Jane Smith"]),
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


# --- Group By Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_keys",
    [
        TestGroupByExpressionResult(field_0 = [
                {"name": "Alice", "department": "Engineering"},
                {"name": "Bob", "department": "Sales"},
                {"name": "Charlie", "department": "Engineering"},
            ], field_1 = "item.department", field_2 = ["Engineering", "Sales"]),
        TestGroupByExpressionResult(field_0 = [{"age": 25}, {"age": 35}, {"age": 20}, {"age": 40}], field_1 = "item.age >= 30 ? 'senior' : 'junior'", field_2 = ["junior", "senior"]),
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


# --- Sort By Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_order",
    [
        TestSortByExpressionResult(field_0 = [{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}], field_1 = "item.name", field_2 = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}]),
        TestSortByExpressionResult(field_0 = [{"age": 30}, {"age": 20}, {"age": 25}], field_1 = "item.age", field_2 = [{"age": 20}, {"age": 25}, {"age": 30}]),
        TestSortByExpressionResult(field_0 = [{"score": 85}, {"score": 95}, {"score": 75}], field_1 = "-item.score", field_2 = [{"score": 95}, {"score": 85}, {"score": 75}]),
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


# --- Any/Every Expression Tests ---


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


# --- Unique By Expression Tests ---


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


# --- Count By Expression Tests ---


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


# --- Partition Expression Tests ---


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


# --- Dictionary Expression Tests ---


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


# --- Any Tool Expression Tests ---


@pytest.mark.asyncio
async def test_any_eval_expression(client):
    value = {"name": "Alice", "age": 30, "scores": [85, 90, 88]}

    # Test simple property access
    result, error = await make_tool_call(
        client,
        "any",
        {"value": value, "operation": "eval", "expression": "value.name"},
    )
    assert error is None
    assert result == "Alice"

    # Test computation
    result, error = await make_tool_call(
        client,
        "any",
        {"value": value, "operation": "eval", "expression": "value.age * 2"},
    )
    assert error is None
    assert result == 60

    # Test array operations
    result, error = await make_tool_call(
        client,
        "any",
        {
            "value": value,
            "operation": "eval",
            "expression": "value.scores.reduce((a, b) => a + b, 0)",
        },
    )
    assert error is None
    assert result == 263  # Sum of scores


# --- Dictionary Expression Tests with JavaScript Syntax ---


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


# --- Pluck Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_values",
    [
        TestPluckExpressionResult(field_0 = [{"x": 1, "y": 2}, {"x": 3, "y": 4}], field_1 = "item.x + item.y", field_2 = [3, 7]),
        TestPluckExpressionResult(field_0 = [{"name": "alice"}, {"name": "bob"}], field_1 = "item.name.toUpperCase()", field_2 = ["ALICE", "BOB"]),
        TestPluckExpressionResult(field_0 = [{"age": 25}, {"age": 30}], field_1 = "item.age >= 30 ? 'adult' : 'young'", field_2 = ["young", "adult"]),
        # Conditional expression
        TestPluckExpressionResult(field_0 = [{"score": 95}, {"score": 85}, {"score": 75}, {"score": 92}], field_1 = "item.score >= 90 ? 'high' : 'normal'", field_2 = ["high", "normal", "normal", "high"]),
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
        TestMinMaxByExpressionResult(field_0 = [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 0, "y": 1}], field_1 = "item.x*item.x + item.y*item.y", field_2 = "min_by", field_3 = {"x": 0, "y": 1}),  # Closest to origin
        TestMinMaxByExpressionResult(field_0 = [{"age": 25}, {"age": 30}, {"age": 35}], field_1 = "item.age * -1", field_2 = "max_by", field_3 = {"age": 25}),  # Max of negative age = youngest
        TestMinMaxByExpressionResult(field_0 = [{"score": 85}, {"score": 92}, {"score": 78}], field_1 = "item.score", field_2 = "max_by", field_3 = {"score": 92}),
        TestMinMaxByExpressionResult(field_0 = [{"score": 85}, {"score": 92}, {"score": 78}], field_1 = "item.score", field_2 = "min_by", field_3 = {"score": 78}),
        # Best score/age ratio
        TestMinMaxByExpressionResult(field_0 = [
                {"name": "Alice", "age": 25, "score": 95},
                {"name": "Bob", "age": 30, "score": 85},
                {"name": "Charlie", "age": 35, "score": 75},
                {"name": "Diana", "age": 28, "score": 92},
            ], field_1 = "item.score / item.age", field_2 = "max_by", field_3 = {
                "name": "Alice",
                "age": 25,
                "score": 95,
            }),
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
        TestDifferenceIntersectionByExpressionResult(field_0 = [{"id": 1, "category": "fruit"}, {"id": 2, "category": "vegetable"}], field_1 = [{"id": 3, "category": "vegetable"}], field_2 = "item.category === 'fruit'", field_3 = "difference_by", field_4 = 1),
        TestDifferenceIntersectionByExpressionResult(field_0 = [{"id": 1, "category": "fruit"}, {"id": 2, "category": "vegetable"}], field_1 = [{"id": 3, "category": "vegetable"}], field_2 = "item.category === 'vegetable'", field_3 = "intersection_by", field_4 = 1),
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
    assert_result_count(result, error, expected_count)


# --- Remove By Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected_count",
    [
        TestRemoveByExpressionResult(field_0 = [{"score": 85}, {"score": 70}, {"score": 90}], field_1 = "item.score < 80", field_2 = 2),  # Remove score < 80, keep 2
        TestRemoveByExpressionResult(field_0 = [{"age": 25}, {"age": 35}, {"age": 20}], field_1 = "item.age < 30", field_2 = 1),  # Remove age < 30, keep 1
        TestRemoveByExpressionResult(field_0 = [{"status": "active"}, {"status": "inactive"}, {"status": "active"}], field_1 = "item.status === 'inactive'", field_2 = 2),  # Remove inactive, keep 2
    ],
)
async def test_remove_by_expression(client, items, expression, expected_count):
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "remove_by", "expression": expression},
    )
    assert_result_count(result, error, expected_count)


# --- Null Handling Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result",
    [
        TestNullHandlingExpressionResult(field_0 = None, field_1 = "value === null", field_2 = True),  # Python None becomes JS null
        TestNullHandlingExpressionResult(field_0 = [1, None, 3], field_1 = "value[1] === null", field_2 = True),  # Array element None becomes null
        TestNullHandlingExpressionResult(field_0 = {"name": "Alice", "age": None}, field_1 = "value.age === null", field_2 = True),  # Object property None becomes null
        TestNullHandlingExpressionResult(field_0 = {"user": {"metadata": None}}, field_1 = "value.user.metadata === null", field_2 = True),  # Nested property None becomes null
        TestNullHandlingExpressionResult(field_0 = [None, 2, None], field_1 = "value[0] === null && value[2] === null", field_2 = True),  # Multiple null checks
        TestNullHandlingExpressionResult(field_0 = {"score": None}, field_1 = "value.score !== null ? 'has score' : 'no score'", field_2 = "no score"),  # Ternary with null
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
        TestNullSentinelBehaviorResult(field_0 = None, field_1 = 'value ? "truthy" : "falsy"', field_2 = "falsy", field_3 = "null is falsy in JS"),
        TestNullSentinelBehaviorResult(field_0 = None, field_1 = "typeof value", field_2 = "object", field_3 = "None type is object (null) in JS"),
        TestNullSentinelBehaviorResult(field_0 = [None, None], field_1 = "value[0] === value[1]", field_2 = True, field_3 = "null equality works"),
        TestNullSentinelBehaviorResult(field_0 = [1, None, 3], field_1 = "value.length", field_2 = 3, field_3 = "arrays with null preserve length"),
        TestNullSentinelBehaviorResult(field_0 = [1, None, 3], field_1 = "value.length", field_2 = 3, field_3 = "array length works with null"),
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
        TestMultilineExpressionResult(field_0 = {"score": 85}, field_1 = "let newScore = value.score + 5; return newScore;", field_2 = 90),
        TestMultilineExpressionResult(field_0 = {"name": "Alice", "age": 30}, field_1 = (
                "if (value.age > 25) { return value.name + ' is a senior'; } "
                "else { return value.name + ' is a junior'; }"
            ), field_2 = "Alice is a senior"),
        TestMultilineExpressionResult(field_0 = {"data": [10, 20, 30]}, field_1 = (
                "let total = 0; for (let item of value.data) { total += item; } "
                "return total;"
            ), field_2 = 60),
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


# --- Complex Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, operation, expression, expected_result",
    [
        # Complex conditional expressions
        TestComplexExpressionsResult(field_0 = [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
                {"name": "Charlie", "age": 35, "score": 78},
            ], field_1 = "find_by", field_2 = "item.age > 30", field_3 = "Charlie"),
        TestComplexExpressionsResult(field_0 = [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
                {"name": "Charlie", "age": 35, "score": 78},
            ], field_1 = "find_by", field_2 = "item.score > 90", field_3 = "Bob"),
        TestComplexExpressionsResult(field_0 = [
                {"name": "Alice", "age": 30, "score": 85},
                {"name": "Bob", "age": 25, "score": 92},
                {"name": "Charlie", "age": 35, "score": 78},
            ], field_1 = "find_by", field_2 = "item.age > 25 && item.score > 80", field_3 = "Alice"),
        # Engineering department filtering
        TestComplexExpressionsResult(field_0 = [
                {"name": "Alice", "department": "engineering"},
                {"name": "Bob", "department": "marketing"},
            ], field_1 = "find_by", field_2 = "item.department === 'engineering'", field_3 = "Alice"),
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


# --- New String Operations Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, operation, param, data, expected_result",
    [
        # strings.split operation
        TestNewStringOperationsExpressionsResult(field_0 = "a,b,c", field_1 = "split", field_2 = ",", field_3 = None, field_4 = ["a", "b", "c"]),
        TestNewStringOperationsExpressionsResult(field_0 = "hello world test", field_1 = "split", field_2 = " ", field_3 = None, field_4 = ["hello", "world", "test"]),
        TestNewStringOperationsExpressionsResult(field_0 = "one|two|three", field_1 = "split", field_2 = "|", field_3 = None, field_4 = ["one", "two", "three"]),
        TestNewStringOperationsExpressionsResult(field_0 = "no_delimiter", field_1 = "split", field_2 = ",", field_3 = None, field_4 = ["no_delimiter"]),
        TestNewStringOperationsExpressionsResult(field_0 = "", field_1 = "split", field_2 = ",", field_3 = None, field_4 = [""]),
        # strings.slice operation
        TestNewStringOperationsExpressionsResult(field_0 = "hello world", field_1 = "slice", field_2 = None, field_3 = {"from": 0, "to": 5}, field_4 = "hello"),
        TestNewStringOperationsExpressionsResult(field_0 = "testing", field_1 = "slice", field_2 = None, field_3 = {"from": 1, "to": 4}, field_4 = "est"),
        TestNewStringOperationsExpressionsResult(field_0 = "python", field_1 = "slice", field_2 = None, field_3 = {"from": 2}, field_4 = "thon"),  # from to end
        TestNewStringOperationsExpressionsResult(field_0 = "slice", field_1 = "slice", field_2 = None, field_3 = {"from": 0, "to": 3}, field_4 = "sli"),  # from start to index 3
    ],
)
async def test_new_string_operations_expressions(
    client, text, operation, param, data, expected_result
):
    call_params = {"text": text, "operation": operation}
    if param is not None:
        call_params["param"] = param
    if data is not None:
        call_params["data"] = data

    result, error = await make_tool_call(client, "strings", call_params)
    assert error is None
    assert result == expected_result


# --- New List Operations Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, operation, param, expected_result",
    [
        # lists.min operation
        TestNewListOperationsExpressionsResult(field_0 = [1, 3, 2, 5, 4], field_1 = "min", field_2 = None, field_3 = 1),
        TestNewListOperationsExpressionsResult(field_0 = [10, 5, 15, 3], field_1 = "min", field_2 = None, field_3 = 3),
        TestNewListOperationsExpressionsResult(field_0 = ["apple", "banana", "cherry"], field_1 = "min", field_2 = None, field_3 = "apple"),  # alphabetical
        # lists.max operation
        TestNewListOperationsExpressionsResult(field_0 = [1, 3, 2, 5, 4], field_1 = "max", field_2 = None, field_3 = 5),
        TestNewListOperationsExpressionsResult(field_0 = [10, 5, 15, 3], field_1 = "max", field_2 = None, field_3 = 15),
        TestNewListOperationsExpressionsResult(field_0 = ["apple", "banana", "cherry"], field_1 = "max", field_2 = None, field_3 = "cherry"),  # alphabetical
        # lists.join operation
        TestNewListOperationsExpressionsResult(field_0 = ["a", "b", "c"], field_1 = "join", field_2 = ",", field_3 = "a,b,c"),
        TestNewListOperationsExpressionsResult(field_0 = ["hello", "world"], field_1 = "join", field_2 = " ", field_3 = "hello world"),
        TestNewListOperationsExpressionsResult(field_0 = ["one", "two", "three"], field_1 = "join", field_2 = "|", field_3 = "one|two|three"),
        TestNewListOperationsExpressionsResult(field_0 = ["single"], field_1 = "join", field_2 = ",", field_3 = "single"),
        TestNewListOperationsExpressionsResult(field_0 = [], field_1 = "join", field_2 = ",", field_3 = ""),
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
        TestNewListByOperationsExpressionsResult(field_0 = [{"score": 85}, {"score": 92}, {"score": 78}], field_1 = "min_by", field_2 = "item.score", field_3 = {"score": 78}),
        TestNewListByOperationsExpressionsResult(field_0 = [
                {"age": 25, "name": "Alice"},
                {"age": 30, "name": "Bob"},
                {"age": 20, "name": "Charlie"},
            ], field_1 = "min_by", field_2 = "item.age", field_3 = {"age": 20, "name": "Charlie"}),
        # lists.max_by operation
        TestNewListByOperationsExpressionsResult(field_0 = [{"score": 85}, {"score": 92}, {"score": 78}], field_1 = "max_by", field_2 = "item.score", field_3 = {"score": 92}),
        TestNewListByOperationsExpressionsResult(field_0 = [
                {"age": 25, "name": "Alice"},
                {"age": 30, "name": "Bob"},
                {"age": 20, "name": "Charlie"},
            ], field_1 = "max_by", field_2 = "item.age", field_3 = {"age": 30, "name": "Bob"}),
        # Complex expressions for min_by/max_by
        TestNewListByOperationsExpressionsResult(field_0 = [{"x": 1, "y": 2}, {"x": 3, "y": 4}, {"x": 0, "y": 1}], field_1 = "min_by", field_2 = "item.x*item.x + item.y*item.y", field_3 = {"x": 0, "y": 1}),
        TestNewListByOperationsExpressionsResult(field_0 = [
                {"score": 90, "age": 25},
                {"score": 85, "age": 30},
                {"score": 95, "age": 28},
            ], field_1 = "max_by", field_2 = "item.score / item.age", field_3 = {"score": 90, "age": 25}),
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


# --- New Dict Operations Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, operation, expected_result",
    [
        # dicts.keys operation
        TestNewDictOperationsExpressionsResult(field_0 = {"a": 1, "b": 2, "c": 3}, field_1 = "keys", field_2 = ["a", "b", "c"]),
        TestNewDictOperationsExpressionsResult(field_0 = {"name": "Alice", "age": 30}, field_1 = "keys", field_2 = ["name", "age"]),
        TestNewDictOperationsExpressionsResult(field_0 = {}, field_1 = "keys", field_2 = []),
        # dicts.values operation
        TestNewDictOperationsExpressionsResult(field_0 = {"a": 1, "b": 2, "c": 3}, field_1 = "values", field_2 = [1, 2, 3]),
        TestNewDictOperationsExpressionsResult(field_0 = {"name": "Alice", "age": 30}, field_1 = "values", field_2 = [30, "Alice"]),
        TestNewDictOperationsExpressionsResult(field_0 = {}, field_1 = "values", field_2 = []),
        # dicts.items operation
        TestNewDictOperationsExpressionsResult(field_0 = {"a": 1, "b": 2}, field_1 = "items", field_2 = [["a", 1], ["b", 2]]),
        TestNewDictOperationsExpressionsResult(field_0 = {"name": "Alice", "age": 30}, field_1 = "items", field_2 = [["name", "Alice"], ["age", 30]]),
        TestNewDictOperationsExpressionsResult(field_0 = {}, field_1 = "items", field_2 = []),
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
        TestNewDictTransformationExpressionsResult(field_0 = {"name": "Alice", "age": 30}, field_1 = "map_keys", field_2 = "key.toUpperCase()", field_3 = {"NAME": "Alice", "AGE": 30}),
        TestNewDictTransformationExpressionsResult(field_0 = {"first": "John", "last": "Doe"}, field_1 = "map_keys", field_2 = "key + '_field'", field_3 = {"first_field": "John", "last_field": "Doe"}),
        # dicts.map_values operation
        TestNewDictTransformationExpressionsResult(field_0 = {"a": 1, "b": 2, "c": 3}, field_1 = "map_values", field_2 = "value * 2", field_3 = {"a": 2, "b": 4, "c": 6}),
        TestNewDictTransformationExpressionsResult(field_0 = {"greeting": "hello", "name": "world"}, field_1 = "map_values", field_2 = "value.toUpperCase()", field_3 = {"greeting": "HELLO", "name": "WORLD"}),
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
        TestNewDictStructureExpressionsResult(field_0 = {"a": {"b": {"c": 1}}, "d": 2}, field_1 = "flatten_keys", field_2 = {"a.b.c": 1, "d": 2}),
        TestNewDictStructureExpressionsResult(field_0 = {"user": {"name": "Alice", "profile": {"age": 30}}}, field_1 = "flatten_keys", field_2 = {"user.name": "Alice", "user.profile.age": 30}),
        # dicts.unflatten_keys operation
        TestNewDictStructureExpressionsResult(field_0 = {"a.b.c": 1, "a.b.d": 2, "e": 3}, field_1 = "unflatten_keys", field_2 = {"a": {"b": {"c": 1, "d": 2}}, "e": 3}),
        TestNewDictStructureExpressionsResult(field_0 = {"user.name": "Alice", "user.age": 30, "status": "active"}, field_1 = "unflatten_keys", field_2 = {"user": {"name": "Alice", "age": 30}, "status": "active"}),
    ],
)
async def test_new_dict_structure_expressions(client, obj, operation, expected_result):
    result, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": operation}
    )
    assert error is None
    assert result == expected_result


# --- New Any Operation Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected_result",
    [
        # any.size operation
        ("hello", 5),
        ([1, 2, 3, 4], 4),
        ({"a": 1, "b": 2}, 2),
        ("", 0),
        ([], 0),
        ({}, 0),
        (42, 1),  # scalar values have size 1
        (None, 0),  # null has size 0
        (True, 1),  # boolean has size 1
    ],
)
async def test_new_any_size_expressions(client, value, expected_result):
    result, error = await make_tool_call(
        client, "any", {"value": value, "operation": "size"}
    )
    assert error is None
    assert result == expected_result


# --- Complex Expression Tests Using New Operations ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, operation, expression, expected_count",
    [
        # Test lists.min_by with new items
        TestComplexExpressionsWithNewOperationsResult(field_0 = [{"score": 85}, {"score": 92}, {"score": 78}], field_1 = "min_by", field_2 = "item.score", field_3 = 1),
        # Test lists.max_by with new items
        TestComplexExpressionsWithNewOperationsResult(field_0 = [{"age": 25}, {"age": 30}, {"age": 20}], field_1 = "max_by", field_2 = "item.age", field_3 = 1),
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


# --- Complex Null Handling Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result, description",
    [
        # Complex null filtering (since Python None becomes JS null)
        TestComplexNullHandlingResult(field_0 = [
                {"name": "Alice", "score": 85, "metadata": None},
                {"name": "Bob", "score": None, "metadata": {"priority": "high"}},
            ], field_1 = "value[1].score === null", field_2 = True, field_3 = "Complex null filtering in nested structures"),
        # Return null values from expressions - these should be converted to Python None
        TestComplexNullHandlingResult(field_0 = {"test": "data"}, field_1 = "null", field_2 = None, field_3 = "Return direct null from expression"),
        TestComplexNullHandlingResult(field_0 = {"test": "data"}, field_1 = "[1, null, 3]", field_2 = [1, None, 3], field_3 = "Return list with null"),
        TestComplexNullHandlingResult(field_0 = {"test": "data"}, field_1 = "({a: 1, b: null, c: 3})", field_2 = {"a": 1, "b": None, "c": 3}, field_3 = "Return dict with null"),
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
