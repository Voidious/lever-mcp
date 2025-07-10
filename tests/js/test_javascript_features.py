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
        ("`Hello ${value.name}!`", {"name": "World"}, "Hello World!"),
        ("`Value: ${value.count}`", {"count": 42}, "Value: 42"),
        # Template literals with expressions
        ("`Sum: ${value.a + value.b}`", {"a": 5, "b": 3}, "Sum: 8"),
        ("`Name: ${value.name.toUpperCase()}`", {"name": "alice"}, "Name: ALICE"),
        # Multiple interpolations
        (
            "`${value.first} ${value.last}`",
            {"first": "John", "last": "Doe"},
            "John Doe",
        ),
        # Template literals with ternary
        (
            "`Result: ${value.score > 80 ? 'Pass' : 'Fail'}`",
            {"score": 85},
            "Result: Pass",
        ),
        (
            "`Result: ${value.score > 80 ? 'Pass' : 'Fail'}`",
            {"score": 75},
            "Result: Fail",
        ),
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
        (
            "(function() { const {name, age} = value; return name + ' is ' + age; })()",
            {"name": "Alice", "age": 30},
            "Alice is 30",
        ),
        # Array destructuring
        (
            "(function() { const [first, second] = value; return first + second; })()",
            [10, 20],
            30,
        ),
        # Destructuring with defaults
        (
            (
                "(function() { const {name = 'Unknown', age = 0} = value; "
                "return name + ' ' + age; })()"
            ),
            {"name": "Bob"},
            "Bob 0",
        ),
        # Nested destructuring
        (
            "(function() { const {user: {name}} = value; return name; })()",
            {"user": {"name": "Charlie"}},
            "Charlie",
        ),
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
        (
            "[...value.arr1, ...value.arr2]",
            {"arr1": [1, 2], "arr2": [3, 4]},
            [1, 2, 3, 4],
        ),
        # Object spread
        (
            "({...value.obj1, ...value.obj2})",
            {"obj1": {"a": 1}, "obj2": {"b": 2}},
            {"a": 1, "b": 2},
        ),
        # Function spread
        ("Math.max(...value)", [1, 5, 3, 2], 5),
        # Array copying
        ("[...value]", [1, 2, 3], [1, 2, 3]),
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
        (False, "!!value", False),
        (0, "!!value", False),
        ("", "!!value", False),
        (None, "!!value", False),  # Python None becomes JS null
        # Truthy values
        (True, "!!value", True),
        (1, "!!value", True),
        ("hello", "!!value", True),
        ([], "!!value", True),  # Empty array is truthy in JS
        ({}, "!!value", True),  # Empty object is truthy in JS
        # Ternary with truthy/falsy
        (0, "value ? 'truthy' : 'falsy'", "falsy"),
        (1, "value ? 'truthy' : 'falsy'", "truthy"),
        ("", "value ? 'truthy' : 'falsy'", "falsy"),
        ("hello", "value ? 'truthy' : 'falsy'", "truthy"),
        # Logical operators
        (0, "value || 'default'", "default"),
        (42, "value || 'default'", 42),
        (None, "value && 'has value'", None),
        (42, "value && 'has value'", "has value"),
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
        ("hello", "typeof value", "string"),
        (42, "typeof value", "number"),
        (True, "typeof value", "boolean"),
        (None, "typeof value", "object"),  # null is object in JS
        ([], "typeof value", "object"),
        ({}, "typeof value", "object"),
        # instanceof checks
        ([], "value instanceof Array", True),
        ({}, "value instanceof Array", False),
        ({}, "value instanceof Object", True),
        # Array.isArray
        ([], "Array.isArray(value)", True),
        ({}, "Array.isArray(value)", False),
        # Number checks
        (42, "Number.isInteger(value)", True),
        (42.5, "Number.isInteger(value)", False),
        (42, "Number.isFinite(value)", True),
        # String methods
        ("hello", "value.charAt(1)", "e"),
        ("hello", "value.slice(1, 3)", "el"),
        ("hello", "value.indexOf('l')", 2),
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
        (
            "JSON.stringify(value)",
            {"name": "Alice", "age": 30},
            '{"name":"Alice","age":30}',
        ),
        ("JSON.stringify(value)", [1, 2, 3], "[1,2,3]"),
        # JSON.parse
        ("JSON.parse(value)", '{"a":1,"b":2}', {"a": 1, "b": 2}),
        ("JSON.parse(value)", "[1,2,3]", [1, 2, 3]),
        # Pretty print JSON
        ("JSON.stringify(value, null, 2)", {"a": 1}, '{\n  "a": 1\n}'),
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
        ("/hello/.test(value)", "hello world", True),
        ("/hello/.test(value)", "hi world", False),
        # String match
        ("value.match(/[0-9]+/)", "abc123def", ["123"]),
        ("value.match(/[0-9]+/g)", "12 34 56", ["12", "34", "56"]),
        # String replace with regex
        ("value.replace(/[0-9]/g, 'X')", "a1b2c3", "aXbXcX"),
        # String split with regex
        ("value.split(/[,;]/)", "a,b;c", ["a", "b", "c"]),
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
