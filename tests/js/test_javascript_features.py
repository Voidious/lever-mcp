from typing import Any
from dataclasses import dataclass
"""
JavaScript-specific language feature tests.

This test suite covers JavaScript language features that are unique to JavaScript
and not available in Lua, ensuring proper support for modern JavaScript syntax.
"""

import pytest
import importlib
import main
from main import LeverMCP
from fastmcp import Client
from tests import make_tool_call
@dataclass
class TestTemplateLiteralsResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestDestructuringResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestSpreadOperatorResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestTruthyFalsyBehaviorResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestTypeSystemResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestJsonOperationsResult:
    field_0: Any
    field_1: Any
    field_2: Any
@dataclass
class TestRegularExpressionsResult:
    field_0: Any
    field_1: Any
    field_2: Any


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


# --- Arrow Function Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression, expected_result",
    [
        # Single parameter arrow functions
        ("[1, 2, 3].map(x => x * 2)", [2, 4, 6]),
        ("[1, 2, 3].filter(x => x > 1)", [2, 3]),
        ("[1, 2, 3].find(x => x > 2)", 3),
        # Multiple parameter arrow functions
        ("[1, 2, 3].map((x, i) => x + i)", [1, 3, 5]),
        ("[1, 2, 3].reduce((acc, val) => acc + val, 0)", 6),
        # Parenthesized single parameter
        ("[1, 2, 3].map((x) => x * 3)", [3, 6, 9]),
        # Block body arrow functions
        ("[1, 2, 3].map(x => { return x * x; })", [1, 4, 9]),
        # Arrow functions with complex expressions
        ("[{a:1}, {a:2}].map(obj => obj.a * 2)", [2, 4]),
    ],
)
async def test_arrow_functions(client, expression, expected_result):
    """Test various arrow function syntaxes."""
    result, error = await make_tool_call(
        client, "any", {"value": {}, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result


# --- Template Literal Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression, context_value, expected_result",
    [
        # Basic template literals
        TestTemplateLiteralsResult(field_0 = "`Hello ${value.name}!`", field_1 = {"name": "World"}, field_2 = "Hello World!"),
        TestTemplateLiteralsResult(field_0 = "`Value: ${value.count}`", field_1 = {"count": 42}, field_2 = "Value: 42"),
        # Template literals with expressions
        TestTemplateLiteralsResult(field_0 = "`Sum: ${value.a + value.b}`", field_1 = {"a": 5, "b": 3}, field_2 = "Sum: 8"),
        TestTemplateLiteralsResult(field_0 = "`Name: ${value.name.toUpperCase()}`", field_1 = {"name": "alice"}, field_2 = "Name: ALICE"),
        # Multiple interpolations
        TestTemplateLiteralsResult(field_0 = "`${value.first} ${value.last}`", field_1 = {"first": "John", "last": "Doe"}, field_2 = "John Doe"),
        # Template literals with ternary
        TestTemplateLiteralsResult(field_0 = "`Result: ${value.score > 80 ? 'Pass' : 'Fail'}`", field_1 = {"score": 85}, field_2 = "Result: Pass"),
        TestTemplateLiteralsResult(field_0 = "`Result: ${value.score > 80 ? 'Pass' : 'Fail'}`", field_1 = {"score": 75}, field_2 = "Result: Fail"),
    ],
)
async def test_template_literals(client, expression, context_value, expected_result):
    """Test template literal syntax."""
    result, error = await make_tool_call(
        client,
        "any",
        {"value": context_value, "operation": "eval", "expression": expression},
    )
    assert error is None
    assert result == expected_result


# --- Destructuring Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression, context_value, expected_result",
    [
        # Object destructuring
        TestDestructuringResult(field_0 = "(function() { const {name, age} = value; return name + ' is ' + age; })()", field_1 = {"name": "Alice", "age": 30}, field_2 = "Alice is 30"),
        # Array destructuring
        TestDestructuringResult(field_0 = "(function() { const [first, second] = value; return first + second; })()", field_1 = [10, 20], field_2 = 30),
        # Destructuring with defaults
        TestDestructuringResult(field_0 = (
                "(function() { const {name = 'Unknown', age = 0} = value; "
                "return name + ' ' + age; })()"
            ), field_1 = {"name": "Bob"}, field_2 = "Bob 0"),
        # Nested destructuring
        TestDestructuringResult(field_0 = "(function() { const {user: {name}} = value; return name; })()", field_1 = {"user": {"name": "Charlie"}}, field_2 = "Charlie"),
    ],
)
async def test_destructuring(client, expression, context_value, expected_result):
    """Test destructuring assignment syntax."""
    result, error = await make_tool_call(
        client,
        "any",
        {"value": context_value, "operation": "eval", "expression": expression},
    )
    assert error is None
    assert result == expected_result


# --- Spread Operator Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression, context_value, expected_result",
    [
        # Array spread
        TestSpreadOperatorResult(field_0 = "[...value.arr1, ...value.arr2]", field_1 = {"arr1": [1, 2], "arr2": [3, 4]}, field_2 = [1, 2, 3, 4]),
        # Object spread
        TestSpreadOperatorResult(field_0 = "({...value.obj1, ...value.obj2})", field_1 = {"obj1": {"a": 1}, "obj2": {"b": 2}}, field_2 = {"a": 1, "b": 2}),
        # Function spread
        TestSpreadOperatorResult(field_0 = "Math.max(...value)", field_1 = [1, 5, 3, 2], field_2 = 5),
        # Array copying
        TestSpreadOperatorResult(field_0 = "[...value]", field_1 = [1, 2, 3], field_2 = [1, 2, 3]),
    ],
)
async def test_spread_operator(client, expression, context_value, expected_result):
    """Test spread operator syntax."""
    result, error = await make_tool_call(
        client,
        "any",
        {"value": context_value, "operation": "eval", "expression": expression},
    )
    assert error is None
    assert result == expected_result


# --- Modern Array Methods Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression, expected_result",
    [
        # Array.from
        ("Array.from({length: 3}, (_, i) => i * 2)", [0, 2, 4]),
        ("Array.from('hello')", ["h", "e", "l", "l", "o"]),
        # includes method
        ("[1, 2, 3].includes(2)", True),
        ("[1, 2, 3].includes(4)", False),
        # find and findIndex
        ("[1, 2, 3, 4].find(x => x > 2)", 3),
        ("[1, 2, 3, 4].findIndex(x => x > 2)", 2),
        # some and every
        ("[1, 2, 3].some(x => x > 2)", True),
        ("[1, 2, 3].every(x => x > 0)", True),
        ("[1, 2, 3].every(x => x > 2)", False),
        # Array method chaining
        ("[1, 2, 3, 4, 5].filter(x => x > 2).map(x => x * 2)", [6, 8, 10]),
    ],
)
async def test_modern_array_methods(client, expression, expected_result):
    """Test modern JavaScript array methods."""
    result, error = await make_tool_call(
        client, "any", {"value": {}, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result


# --- Let/Const Scoping Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression, expected_result",
    [
        # Block scoping with let
        (
            """(function() {
            let x = 1;
            if (true) {
                let x = 2;
                return x;
            }
        })()""",
            2,
        ),
        # Const declarations
        (
            """(function() {
            const PI = 3.14159;
            return PI * 2;
        })()""",
            6.28318,
        ),
        # Loop with let
        (
            """(function() {
            let results = [];
            for (let i = 0; i < 3; i++) {
                results.push(i * 2);
            }
            return results;
        })()""",
            [0, 2, 4],
        ),
    ],
)
async def test_let_const_scoping(client, expression, expected_result):
    """Test let/const scoping behavior."""
    result, error = await make_tool_call(
        client, "any", {"value": {}, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result


# --- Truthy/Falsy Behavior Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result",
    [
        # Falsy values
        TestTruthyFalsyBehaviorResult(field_0 = False, field_1 = "!!value", field_2 = False),
        TestTruthyFalsyBehaviorResult(field_0 = 0, field_1 = "!!value", field_2 = False),
        TestTruthyFalsyBehaviorResult(field_0 = "", field_1 = "!!value", field_2 = False),
        TestTruthyFalsyBehaviorResult(field_0 = None, field_1 = "!!value", field_2 = False),  # Python None becomes JS null
        # Truthy values
        TestTruthyFalsyBehaviorResult(field_0 = True, field_1 = "!!value", field_2 = True),
        TestTruthyFalsyBehaviorResult(field_0 = 1, field_1 = "!!value", field_2 = True),
        TestTruthyFalsyBehaviorResult(field_0 = "hello", field_1 = "!!value", field_2 = True),
        TestTruthyFalsyBehaviorResult(field_0 = [], field_1 = "!!value", field_2 = True),  # Empty array is truthy in JS
        TestTruthyFalsyBehaviorResult(field_0 = {}, field_1 = "!!value", field_2 = True),  # Empty object is truthy in JS
        # Ternary with truthy/falsy
        TestTruthyFalsyBehaviorResult(field_0 = 0, field_1 = "value ? 'truthy' : 'falsy'", field_2 = "falsy"),
        TestTruthyFalsyBehaviorResult(field_0 = 1, field_1 = "value ? 'truthy' : 'falsy'", field_2 = "truthy"),
        TestTruthyFalsyBehaviorResult(field_0 = "", field_1 = "value ? 'truthy' : 'falsy'", field_2 = "falsy"),
        TestTruthyFalsyBehaviorResult(field_0 = "hello", field_1 = "value ? 'truthy' : 'falsy'", field_2 = "truthy"),
        # Logical operators
        TestTruthyFalsyBehaviorResult(field_0 = 0, field_1 = "value || 'default'", field_2 = "default"),
        TestTruthyFalsyBehaviorResult(field_0 = 42, field_1 = "value || 'default'", field_2 = 42),
        TestTruthyFalsyBehaviorResult(field_0 = None, field_1 = "value && 'has value'", field_2 = None),
        TestTruthyFalsyBehaviorResult(field_0 = 42, field_1 = "value && 'has value'", field_2 = "has value"),
    ],
)
async def test_truthy_falsy_behavior(client, value, expression, expected_result):
    """Test JavaScript truthy/falsy behavior."""
    result, error = await make_tool_call(
        client, "any", {"value": value, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result


# --- Type System Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expression, expected_result",
    [
        # typeof operator
        TestTypeSystemResult(field_0 = "hello", field_1 = "typeof value", field_2 = "string"),
        TestTypeSystemResult(field_0 = 42, field_1 = "typeof value", field_2 = "number"),
        TestTypeSystemResult(field_0 = True, field_1 = "typeof value", field_2 = "boolean"),
        TestTypeSystemResult(field_0 = None, field_1 = "typeof value", field_2 = "object"),  # null is object in JS
        TestTypeSystemResult(field_0 = [], field_1 = "typeof value", field_2 = "object"),
        TestTypeSystemResult(field_0 = {}, field_1 = "typeof value", field_2 = "object"),
        # instanceof checks
        TestTypeSystemResult(field_0 = [], field_1 = "value instanceof Array", field_2 = True),
        TestTypeSystemResult(field_0 = {}, field_1 = "value instanceof Array", field_2 = False),
        TestTypeSystemResult(field_0 = {}, field_1 = "value instanceof Object", field_2 = True),
        # Array.isArray
        TestTypeSystemResult(field_0 = [], field_1 = "Array.isArray(value)", field_2 = True),
        TestTypeSystemResult(field_0 = {}, field_1 = "Array.isArray(value)", field_2 = False),
        # Number checks
        TestTypeSystemResult(field_0 = 42, field_1 = "Number.isInteger(value)", field_2 = True),
        TestTypeSystemResult(field_0 = 42.5, field_1 = "Number.isInteger(value)", field_2 = False),
        TestTypeSystemResult(field_0 = 42, field_1 = "Number.isFinite(value)", field_2 = True),
        # String methods
        TestTypeSystemResult(field_0 = "hello", field_1 = "value.charAt(1)", field_2 = "e"),
        TestTypeSystemResult(field_0 = "hello", field_1 = "value.slice(1, 3)", field_2 = "el"),
        TestTypeSystemResult(field_0 = "hello", field_1 = "value.indexOf('l')", field_2 = 2),
    ],
)
async def test_type_system(client, value, expression, expected_result):
    """Test JavaScript type system features."""
    result, error = await make_tool_call(
        client, "any", {"value": value, "operation": "eval", "expression": expression}
    )
    assert error is None
    assert result == expected_result


# --- Error Handling Tests ---


@pytest.mark.asyncio
async def test_try_catch_expressions(client):
    """Test try/catch error handling in expressions."""
    # Test successful try block
    result, error = await make_tool_call(
        client,
        "any",
        {
            "value": {"prop": "value"},
            "operation": "eval",
            "expression": """
                try {
                    return value.prop.toUpperCase();
                } catch (e) {
                    return 'error caught';
                }
            """,
        },
    )
    assert error is None
    assert result == "VALUE"

    # Test catch block execution
    result, error = await make_tool_call(
        client,
        "any",
        {
            "value": None,
            "operation": "eval",
            "expression": """
                try {
                    return value.nonexistent.property;
                } catch (e) {
                    return 'error caught';
                }
            """,
        },
    )
    assert error is None
    assert result == "error caught"


# --- JSON Operations Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression, context_value, expected_result",
    [
        # JSON.stringify
        TestJsonOperationsResult(field_0 = "JSON.stringify(value)", field_1 = {"name": "Alice", "age": 30}, field_2 = '{"name":"Alice","age":30}'),
        TestJsonOperationsResult(field_0 = "JSON.stringify(value)", field_1 = [1, 2, 3], field_2 = "[1,2,3]"),
        # JSON.parse
        TestJsonOperationsResult(field_0 = "JSON.parse(value)", field_1 = '{"a":1,"b":2}', field_2 = {"a": 1, "b": 2}),
        TestJsonOperationsResult(field_0 = "JSON.parse(value)", field_1 = "[1,2,3]", field_2 = [1, 2, 3]),
        # Pretty print JSON
        TestJsonOperationsResult(field_0 = "JSON.stringify(value, null, 2)", field_1 = {"a": 1}, field_2 = '{\n  "a": 1\n}'),
    ],
)
async def test_json_operations(client, expression, context_value, expected_result):
    """Test JSON.stringify and JSON.parse operations."""
    result, error = await make_tool_call(
        client,
        "any",
        {"value": context_value, "operation": "eval", "expression": expression},
    )
    assert error is None
    assert result == expected_result


# --- Regular Expression Tests ---


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression, context_value, expected_result",
    [
        # RegExp test
        TestRegularExpressionsResult(field_0 = "/hello/.test(value)", field_1 = "hello world", field_2 = True),
        TestRegularExpressionsResult(field_0 = "/hello/.test(value)", field_1 = "hi world", field_2 = False),
        # String match
        TestRegularExpressionsResult(field_0 = "value.match(/[0-9]+/)", field_1 = "abc123def", field_2 = ["123"]),
        TestRegularExpressionsResult(field_0 = "value.match(/[0-9]+/g)", field_1 = "12 34 56", field_2 = ["12", "34", "56"]),
        # String replace with regex
        TestRegularExpressionsResult(field_0 = "value.replace(/[0-9]/g, 'X')", field_1 = "a1b2c3", field_2 = "aXbXcX"),
        # String split with regex
        TestRegularExpressionsResult(field_0 = "value.split(/[,;]/)", field_1 = "a,b;c", field_2 = ["a", "b", "c"]),
    ],
)
async def test_regular_expressions(client, expression, context_value, expected_result):
    """Test regular expression support."""
    result, error = await make_tool_call(
        client,
        "any",
        {"value": context_value, "operation": "eval", "expression": expression},
    )
    assert error is None
    assert result == expected_result
