import pytest
import importlib
import main
from main import LeverMCP
from fastmcp import Client
from tests import make_tool_call


@pytest.fixture(params=["lua", "javascript"])
async def client(request):
    """
    Provides an isolated FastMCP client for each test by reloading the main
    module and configuring it for the specified engine (Lua or JavaScript).
    """
    engine = request.param

    # Reload main module to get fresh instance
    importlib.reload(main)

    # Set the global configuration before importing tools
    main.USE_JAVASCRIPT = engine == "javascript"

    # Create fresh MCP instance
    mcp_instance = LeverMCP("Lever MCP")

    # Register appropriate tools based on engine
    if engine == "javascript":
        from tools.js import register_js_tools

        register_js_tools(mcp_instance)
    else:
        from tools.lua import register_lua_tools

        register_lua_tools(mcp_instance)

    async with Client(mcp_instance) as c:
        yield c


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "first_tool,first_params,second_tool,second_params,input_value,expected_type,"
    "expected_value",
    [
        # strings (str -> str) -> strings (str -> str)
        (
            "strings",
            {"operation": "upper_case"},
            "strings",
            {"operation": "reverse"},
            "abc",
            str,
            "CBA",
        ),
        # strings (str -> str) -> strings (str -> bool)
        (
            "strings",
            {"operation": "upper_case"},
            "strings",
            {"operation": "is_upper"},
            "abc",
            bool,
            True,
        ),
        # strings (str -> str) -> generate (str -> list) (repeat)
        (
            "strings",
            {"operation": "capitalize"},
            "generate",
            {"operation": "repeat", "count": 2},
            "foo",
            list,
            ["Foo", "Foo"],
        ),
        # lists (list -> list) -> lists (list -> list)
        (
            "lists",
            {"operation": "flatten_deep"},
            "lists",
            {"operation": "compact"},
            [1, [0, 2, None]],
            list,
            [1, 2],
        ),
        # lists (list -> list) -> lists (list -> Any)
        (
            "lists",
            {"operation": "compact"},
            "lists",
            {"operation": "head"},
            [None, "foo", "bar"],
            str,
            "foo",
        ),
        # lists (list -> list) -> lists (list -> bool) is_empty
        (
            "lists",
            {"operation": "compact"},
            "lists",
            {"operation": "is_empty"},
            [None, None],
            bool,
            True,
        ),
        # lists (list -> list) -> lists (list -> bool) is_equal
        (
            "lists",
            {"operation": "compact"},
            "lists",
            {"operation": "is_equal", "param": [1, 2]},
            [1, 2],
            bool,
            True,
        ),
        # lists (list -> list) -> lists (list -> bool) contains
        (
            "lists",
            {"operation": "compact"},
            "lists",
            {"operation": "contains", "param": 2},
            [1, 2, 3],
            bool,
            True,
        ),
        # lists (list -> list) -> generate (powerset)
        (
            "lists",
            {"operation": "compact"},
            "generate",
            {"operation": "powerset"},
            [1, 2],
            list,
            [[], [1], [2], [1, 2]],
        ),
        # lists (list -> list) -> generate (permutations)
        (
            "lists",
            {"operation": "compact"},
            "generate",
            {"operation": "permutations"},
            [1, 2],
            list,
            [[1, 2], [2, 1]],
        ),
        # dicts (dict -> dict) -> dicts (dict -> list)
        (
            "dicts",
            {"operation": "pick", "param": ["name"]},
            "dicts",
            {"operation": "keys"},
            {"name": "Alice", "age": 30},
            list,
            ["name"],
        ),
        # dicts (dict -> dict) -> dicts (dict -> Any)
        (
            "dicts",
            {"operation": "pick", "param": ["name"]},
            "dicts",
            {"operation": "get_value", "path": "name"},
            {"name": "Alice", "age": 30},
            str,
            "Alice",
        ),
        # any (Any -> bool) -> any (bool -> Any)
        (
            "any",
            {"operation": "is_empty"},
            "any",
            {"operation": "is_equal", "param": True},
            "",
            bool,
            True,
        ),
        # any (Any -> int) -> any (int -> bool)
        (
            "any",
            {"operation": "size"},
            "any",
            {"operation": "is_equal", "param": 5},
            "hello",
            bool,
            True,
        ),
        # dicts (dict -> Any) -> strings (str -> str)
        (
            "dicts",
            {"operation": "get_value", "path": "name"},
            "strings",
            {"operation": "upper_case"},
            {"name": "alice", "age": 30},
            str,
            "ALICE",
        ),
    ],
)
async def test_basic_chain_pairings(
    client,
    first_tool,
    first_params,
    second_tool,
    second_params,
    input_value,
    expected_type,
    expected_value,
):
    chain_payload = {
        "input": input_value,
        "tool_calls": [
            {"tool": first_tool, "params": first_params},
            {"tool": second_tool, "params": second_params},
        ],
    }
    value, error = await make_tool_call(client, "chain", chain_payload)
    if expected_value is None:
        assert error is not None, f"Expected error, got value={value}, error={error}"
    else:
        assert error is None, f"Expected no error, got error={error}"
        assert isinstance(
            value, expected_type
        ), f"Expected type {expected_type}, got {type(value)}"
        # Handle list comparisons that might have different order
        if expected_type == list and len(expected_value) > 1:
            try:
                # For simple lists, check if same elements regardless of order
                if len(value) == len(expected_value) and set(value) == set(
                    expected_value
                ):
                    pass  # Same elements, different order is ok
                else:
                    assert (
                        value == expected_value
                    ), f"Expected value={expected_value}, got value={value}"
            except TypeError:
                # Lists contain unhashable types (like lists), do exact comparison
                assert (
                    value == expected_value
                ), f"Expected value={expected_value}, got value={value}"
        else:
            assert (
                value == expected_value
            ), f"Expected value={expected_value}, got value={value}"
