from typing import Any
from dataclasses import dataclass
import pytest
import importlib
import main
from main import LeverMCP
from fastmcp import Client
from tests import make_tool_call
@dataclass
class TestBasicChainPairingsResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
    field_4: Any
    field_5: Any
    field_6: Any


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
        TestBasicChainPairingsResult(field_0 = "strings", field_1 = {"operation": "upper_case"}, field_2 = "strings", field_3 = {"operation": "reverse"}, field_4 = "abc", field_5 = str, field_6 = "CBA"),
        # strings (str -> str) -> strings (str -> bool)
        TestBasicChainPairingsResult(field_0 = "strings", field_1 = {"operation": "upper_case"}, field_2 = "strings", field_3 = {"operation": "is_upper"}, field_4 = "abc", field_5 = bool, field_6 = True),
        # strings (str -> str) -> generate (str -> list) (repeat)
        TestBasicChainPairingsResult(field_0 = "strings", field_1 = {"operation": "capitalize"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = "foo", field_5 = list, field_6 = ["Foo", "Foo"]),
        # lists (list -> list) -> lists (list -> list)
        TestBasicChainPairingsResult(field_0 = "lists", field_1 = {"operation": "flatten_deep"}, field_2 = "lists", field_3 = {"operation": "compact"}, field_4 = [1, [0, 2, None]], field_5 = list, field_6 = [1, 2]),
        # lists (list -> list) -> lists (list -> Any)
        TestBasicChainPairingsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "head"}, field_4 = [None, "foo", "bar"], field_5 = str, field_6 = "foo"),
        # lists (list -> list) -> lists (list -> bool) is_empty
        TestBasicChainPairingsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "is_empty"}, field_4 = [None, None], field_5 = bool, field_6 = True),
        # lists (list -> list) -> lists (list -> bool) is_equal
        TestBasicChainPairingsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "is_equal", "param": [1, 2]}, field_4 = [1, 2], field_5 = bool, field_6 = True),
        # lists (list -> list) -> lists (list -> bool) contains
        TestBasicChainPairingsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "contains", "param": 2}, field_4 = [1, 2, 3], field_5 = bool, field_6 = True),
        # lists (list -> list) -> generate (powerset)
        TestBasicChainPairingsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "powerset"}, field_4 = [1, 2], field_5 = list, field_6 = [[], [1], [2], [1, 2]]),
        # lists (list -> list) -> generate (permutations)
        TestBasicChainPairingsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "permutations"}, field_4 = [1, 2], field_5 = list, field_6 = [[1, 2], [2, 1]]),
        # dicts (dict -> dict) -> dicts (dict -> list)
        TestBasicChainPairingsResult(field_0 = "dicts", field_1 = {"operation": "pick", "param": ["name"]}, field_2 = "dicts", field_3 = {"operation": "keys"}, field_4 = {"name": "Alice", "age": 30}, field_5 = list, field_6 = ["name"]),
        # dicts (dict -> dict) -> dicts (dict -> Any)
        TestBasicChainPairingsResult(field_0 = "dicts", field_1 = {"operation": "pick", "param": ["name"]}, field_2 = "dicts", field_3 = {"operation": "get_value", "path": "name"}, field_4 = {"name": "Alice", "age": 30}, field_5 = str, field_6 = "Alice"),
        # any (Any -> bool) -> any (bool -> Any)
        TestBasicChainPairingsResult(field_0 = "any", field_1 = {"operation": "is_empty"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": True}, field_4 = "", field_5 = bool, field_6 = True),
        # any (Any -> int) -> any (int -> bool)
        TestBasicChainPairingsResult(field_0 = "any", field_1 = {"operation": "size"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": 5}, field_4 = "hello", field_5 = bool, field_6 = True),
        # dicts (dict -> Any) -> strings (str -> str)
        TestBasicChainPairingsResult(field_0 = "dicts", field_1 = {"operation": "get_value", "path": "name"}, field_2 = "strings", field_3 = {"operation": "upper_case"}, field_4 = {"name": "alice", "age": 30}, field_5 = str, field_6 = "ALICE"),
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
