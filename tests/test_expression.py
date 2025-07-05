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
        ("hello", "string.upper(value)", "HELLO"),
        ([1, 2, 3, 4, 5], "#value", 5),
        (42, "value * 2 + 1", 85),
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


# --- Null Sentinel Behavior Tests ---


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
            "string.upper(key)",
            {"NAME": "Alice", "AGE": 30},
        ),
        (
            {"first": "John", "last": "Doe"},
            "map_keys",
            "key .. '_field'",
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
            "string.upper(value)",
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
