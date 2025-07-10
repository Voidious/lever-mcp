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


# --- Filter By Expression Tests ---


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


# --- Map Expression Tests ---


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


# --- Group By Expression Tests ---


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


# --- Sort By Expression Tests ---


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


# --- Min/Max By Expression Tests ---


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


# --- Difference/Intersection By Expression Tests ---


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


# --- Remove By Expression Tests ---


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


# --- Null Handling Expression Tests ---


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


# --- Null Sentinel Behavior Tests ---


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


# --- Multi-line Expression Tests ---


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


# --- New String Operations Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, operation, param, data, expected_result",
    [
        # strings.split operation
        ("a,b,c", "split", ",", None, ["a", "b", "c"]),
        ("hello world test", "split", " ", None, ["hello", "world", "test"]),
        ("one|two|three", "split", "|", None, ["one", "two", "three"]),
        ("no_delimiter", "split", ",", None, ["no_delimiter"]),
        ("", "split", ",", None, [""]),
        # strings.slice operation
        ("hello world", "slice", None, {"from": 0, "to": 5}, "hello"),
        ("testing", "slice", None, {"from": 1, "to": 4}, "est"),
        ("python", "slice", None, {"from": 2}, "thon"),  # from to end
        ("slice", "slice", None, {"from": 0, "to": 3}, "sli"),  # from start to index 3
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


# --- New Dict Operations Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, operation, expected_result",
    [
        # dicts.keys operation
        ({"a": 1, "b": 2, "c": 3}, "keys", ["a", "b", "c"]),
        ({"name": "Alice", "age": 30}, "keys", ["name", "age"]),
        ({}, "keys", []),
        # dicts.values operation
        ({"a": 1, "b": 2, "c": 3}, "values", [1, 2, 3]),
        ({"name": "Alice", "age": 30}, "values", [30, "Alice"]),
        ({}, "values", []),
        # dicts.items operation
        ({"a": 1, "b": 2}, "items", [["a", 1], ["b", 2]]),
        ({"name": "Alice", "age": 30}, "items", [["name", "Alice"], ["age", 30]]),
        ({}, "items", []),
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
        (
            {"name": "Alice", "age": 30},
            "map_keys",
            "key.toUpperCase()",
            {"NAME": "Alice", "AGE": 30},
        ),
        (
            {"first": "John", "last": "Doe"},
            "map_keys",
            "key + '_field'",
            {"first_field": "John", "last_field": "Doe"},
        ),
        # dicts.map_values operation
        (
            {"a": 1, "b": 2, "c": 3},
            "map_values",
            "value * 2",
            {"a": 2, "b": 4, "c": 6},
        ),
        (
            {"greeting": "hello", "name": "world"},
            "map_values",
            "value.toUpperCase()",
            {"greeting": "HELLO", "name": "WORLD"},
        ),
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
        (
            {"a": {"b": {"c": 1}}, "d": 2},
            "flatten_keys",
            {"a.b.c": 1, "d": 2},
        ),
        (
            {"user": {"name": "Alice", "profile": {"age": 30}}},
            "flatten_keys",
            {"user.name": "Alice", "user.profile.age": 30},
        ),
        # dicts.unflatten_keys operation
        (
            {"a.b.c": 1, "a.b.d": 2, "e": 3},
            "unflatten_keys",
            {"a": {"b": {"c": 1, "d": 2}}, "e": 3},
        ),
        (
            {"user.name": "Alice", "user.age": 30, "status": "active"},
            "unflatten_keys",
            {"user": {"name": "Alice", "age": 30}, "status": "active"},
        ),
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
        (
            [{"score": 85}, {"score": 92}, {"score": 78}],
            "min_by",
            "item.score",
            1,  # One result: the minimum item
        ),
        # Test lists.max_by with new items
        (
            [{"age": 25}, {"age": 30}, {"age": 20}],
            "max_by",
            "item.age",
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


# --- Complex Null Handling Tests ---


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
