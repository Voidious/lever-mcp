from typing import Any
from dataclasses import dataclass
import pytest
import importlib
import main
from main import LeverMCP
from fastmcp import Client
from tests import make_tool_call
@dataclass
class TestChainAllToolPairsResult:
    field_0: Any
    field_1: Any
    field_2: Any
    field_3: Any
    field_4: Any
    field_5: Any
    field_6: Any


def get_engine_expression(lua_expr, js_expr):
    """Return appropriate expression based on current engine configuration."""
    if getattr(main, "USE_JAVASCRIPT", False):
        return js_expr
    else:
        return lua_expr


@pytest.fixture
async def client():
    """
    Provides an isolated FastMCP client for each test by reloading the main
    module and explicitly resetting the application state for the session.
    """
    importlib.reload(main)
    main.USE_JAVASCRIPT = True

    # Create fresh MCP instance with JavaScript tools
    mcp_instance = LeverMCP("Lever MCP")
    from tools.js import register_js_tools

    register_js_tools(mcp_instance)

    async with Client(mcp_instance) as c:
        yield c


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "first_tool,first_params,second_tool,second_params,input_value,expected_type,"
    "expected_value",
    [
        # strings (str -> str) -> strings (str -> str)
        TestChainAllToolPairsResult(field_0 = "strings", field_1 = {"operation": "upper_case"}, field_2 = "strings", field_3 = {"operation": "reverse"}, field_4 = "abc", field_5 = str, field_6 = "CBA"),
        # strings (str -> str) -> strings (str -> bool)
        TestChainAllToolPairsResult(field_0 = "strings", field_1 = {"operation": "upper_case"}, field_2 = "strings", field_3 = {"operation": "is_upper"}, field_4 = "abc", field_5 = bool, field_6 = True),
        # strings (str -> str) -> generate (str -> list) (repeat)
        TestChainAllToolPairsResult(field_0 = "strings", field_1 = {"operation": "capitalize"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = "foo", field_5 = list, field_6 = ["Foo", "Foo"]),
        # lists (list -> list) -> lists (list -> list)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "flatten_deep"}, field_2 = "lists", field_3 = {"operation": "compact"}, field_4 = [1, [0, 2, None]], field_5 = list, field_6 = [1, 2]),
        # lists (list -> list) -> lists (list -> Any)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "head"}, field_4 = [None, "foo", "bar"], field_5 = str, field_6 = "foo"),
        # lists (list -> list) -> lists (list -> dict) (error due to non-string keys)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "count_by", "expression": 0}, field_4 = [[0], [0], [1]], field_5 = dict, field_6 = None),
        # lists (list -> list) -> lists (list -> bool) is_empty
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "is_empty"}, field_4 = [None, None], field_5 = bool, field_6 = True),
        # lists (list -> list) -> lists (list -> bool) is_equal
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "is_equal", "param": [1, 2]}, field_4 = [1, 2], field_5 = bool, field_6 = True),
        # lists (list -> list) -> lists (list -> bool) contains
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "contains", "param": 2}, field_4 = [1, 2, 3], field_5 = bool, field_6 = True),
        # lists (list -> list) -> generate (powerset)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "powerset"}, field_4 = [1, 2], field_5 = list, field_6 = [[], [1], [2], [1, 2]]),
        # lists (list -> list) -> generate (permutations)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "permutations"}, field_4 = [1, 2], field_5 = list, field_6 = [[1, 2], [2, 1]]),
        # lists (list -> list) -> generate (windowed)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "windowed", "size": 2}, field_4 = [1, 2, 3], field_5 = list, field_6 = [[1, 2], [2, 3]]),
        # lists (list -> list) -> generate (cycle)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "cycle", "count": 3}, field_4 = [1, 2], field_5 = list, field_6 = [1, 2, 1]),
        # lists (list -> list) -> generate (accumulate)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "accumulate"}, field_4 = [1, 2, 3], field_5 = list, field_6 = [1, 3, 6]),
        # lists (list -> list) -> generate (zip_with_index)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "zip_with_index"}, field_4 = ["a", "b"], field_5 = list, field_6 = [[0, "a"], [1, "b"]]),
        # lists (list -> list) -> generate (unique_pairs)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "unique_pairs"}, field_4 = [1, 2, 3], field_5 = list, field_6 = [[1, 2], [1, 3], [2, 3]]),
        # lists (list -> list) -> generate (combinations)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "combinations", "length": 2}, field_4 = [1, 2, 3], field_5 = list, field_6 = [[1, 2], [1, 3], [2, 3]]),
        # lists (list -> list) -> generate (repeat)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = [1], field_5 = list, field_6 = [[1], [1]]),
        # lists (list -> list) -> lists (difference)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "difference", "others": [2, 3]}, field_4 = [1, 2, None, 3], field_5 = list, field_6 = [1]),
        # lists (list -> list) -> lists (intersection)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "intersection", "others": [2, 3]}, field_4 = [1, 2, None, 3], field_5 = list, field_6 = [2, 3]),
        # lists (list -> list) -> lists (difference_by)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {
                "operation": "difference_by",
                "others": [{"id": 2}],
                "expression": "item.id",
            }, field_4 = [{"id": 1}, None, {"id": 2}], field_5 = list, field_6 = [{"id": 1}]),
        # lists (list -> list) -> lists (intersection_by)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {
                "operation": "intersection_by",
                "others": [{"id": 2}],
                "expression": "item.id",
            }, field_4 = [{"id": 1}, None, {"id": 2}], field_5 = list, field_6 = [{"id": 2}]),
        # lists (list -> dict) -> dicts (dict -> dict) (error due to non-string keys)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": 0}, field_2 = "dicts", field_3 = {"operation": "invert"}, field_4 = [[0], [0], [1]], field_5 = dict, field_6 = None),
        # lists (list -> dict) -> dicts (dict -> bool) is_empty (error case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": 0}, field_2 = "any", field_3 = {"operation": "is_empty"}, field_4 = [[0], [0], [1]], field_5 = bool, field_6 = None),
        # lists (list -> dict) -> dicts (dict -> bool) is_empty (working case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": "item.x"}, field_2 = "dicts", field_3 = {"operation": "is_empty"}, field_4 = [{"x": 1}, {"x": 1}, {"x": 2}], field_5 = bool, field_6 = False),
        # lists (list -> dict) -> dicts (dict -> bool) has_key (error case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": 0}, field_2 = "dicts", field_3 = {"operation": "has_key", "param": 0}, field_4 = [[0], [0], [1]], field_5 = bool, field_6 = None),
        # lists (list -> dict) -> dicts (dict -> bool) has_key (working case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": "item.x"}, field_2 = "dicts", field_3 = {"operation": "has_key", "param": "1"}, field_4 = [{"x": 1}, {"x": 1}, {"x": 2}], field_5 = bool, field_6 = True),
        # lists (list -> dict) -> any (any -> bool) is_nil (error case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": 0}, field_2 = "any", field_3 = {"operation": "is_nil"}, field_4 = [[0], [0], [1]], field_5 = bool, field_6 = None),
        # lists (list -> dict) -> any (any -> bool) is_nil (working case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": "item.x"}, field_2 = "any", field_3 = {"operation": "is_nil"}, field_4 = [{"x": 1}, {"x": 1}, {"x": 2}], field_5 = bool, field_6 = False),
        # lists (list -> dict) -> any (any -> bool) contains (error case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": 0}, field_2 = "any", field_3 = {"operation": "contains", "param": 2}, field_4 = [[0], [0], [1]], field_5 = bool, field_6 = None),
        # lists (list -> dict) -> any (any -> bool) contains (working case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": "item.x"}, field_2 = "any", field_3 = {"operation": "contains", "param": "2"}, field_4 = [{"x": 1}, {"x": 1}, {"x": 2}], field_5 = bool, field_6 = False),
        # lists (list -> dict) -> dicts (dict -> Any) (error case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": 0}, field_2 = "dicts", field_3 = {"operation": "get_value", "path": 0}, field_4 = [[0], [0], [1]], field_5 = int, field_6 = None),
        # lists (list -> dict) -> dicts (dict -> Any) (working case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": "item.x"}, field_2 = "dicts", field_3 = {"operation": "get_value", "path": "1"}, field_4 = [{"x": 1}, {"x": 1}, {"x": 2}], field_5 = int, field_6 = 2),
        # generate (Any -> Any, repeat str) -> lists (list -> list)
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "lists", field_3 = {"operation": "compact"}, field_4 = "foo", field_5 = list, field_6 = ["foo", "foo"]),
        # generate (Any -> Any, range) -> lists (list -> list) (compact removes 0)
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "range", "from": 0, "to": 3}, field_2 = "lists", field_3 = {"operation": "compact"}, field_4 = None, field_5 = list, field_6 = [1, 2]),
        # generate (Any -> Any, repeat str) -> lists (list -> Any)
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "lists", field_3 = {"operation": "head"}, field_4 = "foo", field_5 = str, field_6 = "foo"),
        # lists (list -> Any, head str) -> strings (str -> str) (working case)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "strings", field_3 = {"operation": "upper_case"}, field_4 = ["foo", "bar", "baz"], field_5 = str, field_6 = "FOO"),
        # dicts (dict -> Any, str) -> strings (str -> str)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "get_value", "path": "a"}, field_2 = "strings", field_3 = {"operation": "capitalize"}, field_4 = {"a": "hello"}, field_5 = str, field_6 = "Hello"),
        # dicts (dict -> Any, list) -> lists (list -> list)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "get_value", "path": "a"}, field_2 = "lists", field_3 = {"operation": "compact"}, field_4 = {"a": [None, 1, 2]}, field_5 = list, field_6 = [1, 2]),
        # dicts (dict -> dict) -> dicts (dict -> dict)
        #   (tool response converts keys to JSON)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "invert"}, field_2 = "dicts", field_3 = {"operation": "invert"}, field_4 = {"a": 1, "b": 2}, field_5 = dict, field_6 = {"a": "1", "b": "2"}),
        # dicts (list of dicts -> dict) -> dicts (dict -> dict)
        #   (int keys, converted to string)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "merge"}, field_2 = "dicts", field_3 = {"operation": "invert"}, field_4 = [{"a": 1}, {"b": 2}], field_5 = dict, field_6 = {"1": "a", "2": "b"}),
        # dicts (list of dicts -> dict) -> dicts (dict -> dict) (string keys)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "merge"}, field_2 = "dicts", field_3 = {"operation": "invert"}, field_4 = [{"a": "x"}, {"b": "y"}], field_5 = dict, field_6 = {"x": "a", "y": "b"}),
        # dicts (dict -> dict) -> dicts (dict -> dict)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "set_value", "path": "a.b", "value": 42}, field_2 = "dicts", field_3 = {"operation": "get_value", "path": "a.b"}, field_4 = {"a": {}}, field_5 = int, field_6 = 42),
        # dicts (dict -> Any, int) -> generate (Any -> Any, repeat)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "get_value", "path": "a"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = {"a": 7}, field_5 = list, field_6 = [7, 7]),
        # lists -> dicts (list of dicts)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "dicts", field_3 = {"operation": "merge"}, field_4 = [{"a": 1}, None, {"b": 2}], field_5 = dict, field_6 = {"a": 1, "b": 2}),
        # any -> lists (repeat bool)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "is_nil"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = 0, field_5 = list, field_6 = [False, False]),
        # lists -> dicts (output: dict)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "dicts", field_3 = {"operation": "invert"}, field_4 = [{"a": "x", "b": "y"}], field_5 = dict, field_6 = {"x": "a", "y": "b"}),
        # lists -> dicts (output: dict)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "dicts", field_3 = {"operation": "set_value", "path": "c", "value": 42}, field_4 = [{"a": 1, "b": 2}], field_5 = dict, field_6 = {"a": 1, "b": 2, "c": 42}),
        # lists -> dicts (output: dict)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "dicts", field_3 = {"operation": "get_value", "path": "a"}, field_4 = [{"a": 7}, {"b": 8}], field_5 = int, field_6 = 7),
        # lists -> dicts (output: list of dicts)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "dicts", field_3 = {"operation": "merge"}, field_4 = [[{"a": 1}, {"b": 2}], [{"c": 3}]], field_5 = dict, field_6 = {"a": 1, "b": 2}),
        # lists -> lists
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "difference", "others": [2]}, field_2 = "lists", field_3 = {"operation": "compact"}, field_4 = [1, 2, None], field_5 = list, field_6 = [1]),
        # lists -> lists
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "difference", "others": [2]}, field_2 = "lists", field_3 = {"operation": "is_empty"}, field_4 = [1, 2], field_5 = bool, field_6 = False),
        # lists -> lists
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "difference", "others": [2]}, field_2 = "lists", field_3 = {"operation": "head"}, field_4 = [1, 2], field_5 = int, field_6 = 1),
        # lists -> lists (list of dicts)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {
                "operation": "difference_by",
                "others": [{"id": 2}],
                "expression": "item.id",
            }, field_2 = "lists", field_3 = {"operation": "count_by", "expression": "item.id"}, field_4 = [{"id": 1}, {"id": 2}, {"id": 1}], field_5 = dict, field_6 = {"1": 2}),
        # lists -> generate (repeat the result of difference)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "difference", "others": [2]}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = [1, 2], field_5 = list, field_6 = [[1], [1]]),
        # lists -> dicts (difference_by, expect {"x": 1})
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {
                "operation": "difference_by",
                "others": [{"x": 2}],
                "expression": "item.x",
            }, field_2 = "dicts", field_3 = {"operation": "merge"}, field_4 = [{"x": 1}, {"x": 2}], field_5 = dict, field_6 = {"x": 1}),
        # lists -> dicts
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "key_by", "expression": "item.id"}, field_2 = "dicts", field_3 = {"operation": "set_value", "path": "x", "value": 99}, field_4 = [{"id": "a", "val": 1}], field_5 = dict, field_6 = {"a": {"id": "a", "val": 1}, "x": 99}),
        # lists -> dicts
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "key_by", "expression": "item.id"}, field_2 = "dicts", field_3 = {"operation": "get_value", "path": "a"}, field_4 = [{"id": "a", "val": 1}], field_5 = dict, field_6 = {"id": "a", "val": 1}),
        # dicts -> dicts
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "invert"}, field_2 = "dicts", field_3 = {"operation": "has_key", "param": "x"}, field_4 = {"a": "x", "b": "y"}, field_5 = bool, field_6 = True),
        # dicts -> generate (repeat the output of invert)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "invert"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = {"a": 1, "b": 2}, field_5 = list, field_6 = [{"1": "a", "2": "b"}, {"1": "a", "2": "b"}]),
        # dicts -> dicts (add a key to the output of invert)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "invert"}, field_2 = "dicts", field_3 = {"operation": "set_value", "path": "c", "value": 42}, field_4 = {"a": 1, "b": 2}, field_5 = dict, field_6 = {"1": "a", "2": "b", "c": 42}),
        # dicts -> dicts (get a value from the output of invert)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "invert"}, field_2 = "dicts", field_3 = {"operation": "get_value", "path": "1"}, field_4 = {"a": 1, "b": 2}, field_5 = str, field_6 = "a"),
        # generate -> lists
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "lists", field_3 = {"operation": "is_empty"}, field_4 = [1, 2], field_5 = bool, field_6 = False),
        # generate -> lists (list of dicts)
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "lists", field_3 = {"operation": "count_by", "expression": "item.a"}, field_4 = {"a": 1}, field_5 = dict, field_6 = {"1": 2}),
        # generate -> dicts (list of dicts)
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "dicts", field_3 = {"operation": "merge"}, field_4 = {"a": 1, "b": 2}, field_5 = dict, field_6 = {"a": 1, "b": 2}),
        # dicts -> dicts
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "merge"}, field_2 = "dicts", field_3 = {"operation": "has_key", "param": "a"}, field_4 = [{"a": 1}, {"b": 2}], field_5 = bool, field_6 = True),
        # dicts -> generate (repeat the output of merge)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "merge"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = [{"a": 1, "b": 2}], field_5 = list, field_6 = [{"a": 1, "b": 2}, {"a": 1, "b": 2}]),
        # dicts -> dicts (add a key to the output of merge)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "merge"}, field_2 = "dicts", field_3 = {"operation": "set_value", "path": "c", "value": 42}, field_4 = [{"a": 1, "b": 2}], field_5 = dict, field_6 = {"a": 1, "b": 2, "c": 42}),
        # dicts -> dicts (get a value from the output of merge)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "merge"}, field_2 = "dicts", field_3 = {"operation": "get_value", "path": "a"}, field_4 = [{"a": 1, "b": 2}], field_5 = int, field_6 = 1),
        # dicts -> dicts (invert the output of set_value)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "set_value", "path": "a", "value": 1}, field_2 = "dicts", field_3 = {"operation": "invert"}, field_4 = {"b": 2}, field_5 = dict, field_6 = {"2": "b", "1": "a"}),
        # dicts -> generate (repeat the output dict)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "set_value", "path": "a", "value": 1}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = {"b": 2}, field_5 = list, field_6 = [{"b": 2, "a": 1}, {"b": 2, "a": 1}]),
        # dicts -> dicts (check for added key)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "set_value", "path": "a", "value": 1}, field_2 = "dicts", field_3 = {"operation": "has_key", "param": "a"}, field_4 = {"b": 2}, field_5 = bool, field_6 = True),
        # dicts -> dicts (add another key)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "set_value", "path": "a", "value": 1}, field_2 = "dicts", field_3 = {"operation": "set_value", "path": "c", "value": 42}, field_4 = {"b": 2}, field_5 = dict, field_6 = {"b": 2, "a": 1, "c": 42}),
        # generate -> lists (is_equal)
        #   (list[str], list[int], list[dict], list[bool], list[list])
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "any", field_3 = {"operation": "is_equal", "param": ["a", "a"]}, field_4 = "a", field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "any", field_3 = {"operation": "is_equal", "param": [1, 1]}, field_4 = 1, field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "any", field_3 = {"operation": "is_equal", "param": [{"x": 1}, {"x": 1}]}, field_4 = {"x": 1}, field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "any", field_3 = {"operation": "is_equal", "param": [True, True]}, field_4 = True, field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "any", field_3 = {"operation": "is_equal", "param": [[1], [1]]}, field_4 = [1], field_5 = bool, field_6 = True),
        # generate -> lists (contains) (list[str])
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "any", field_3 = {"operation": "contains", "param": "a"}, field_4 = "a", field_5 = bool, field_6 = True),
        # lists -> lists (is_equal) (str, int, list, dict, bool)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": "a"}, field_4 = ["a", "b"], field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": 1}, field_4 = [1, 2], field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": [1]}, field_4 = [[1], [2]], field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": {"x": 1}}, field_4 = [{"x": 1}, {"x": 2}], field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": True}, field_4 = [True, False], field_5 = bool, field_6 = True),
        # lists -> lists (contains) (list[str], list[int], str)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "contains", "param": "a"}, field_4 = [["a", "b"], ["c"]], field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "contains", "param": 1}, field_4 = [[1, 2], [3]], field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "contains", "param": "b"}, field_4 = ["ab", "cd"], field_5 = bool, field_6 = True),
        # --- Restored: type-agnostic contains/is_equal using any ---
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "invert"}, field_2 = "any", field_3 = {"operation": "contains", "param": "a"}, field_4 = {"a": 1, "b": 2}, field_5 = bool, field_6 = False),
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "contains", "param": 1}, field_4 = [[1]], field_5 = bool, field_6 = True),
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": 1}, field_4 = [1], field_5 = bool, field_6 = True),
        # lists -> lists (is_empty) (str)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {"operation": "is_empty"}, field_4 = [""], field_5 = bool, field_6 = True),
        # === any.eval as FIRST tool (outputting different types) ===
        # any.eval (Any -> str) -> strings (str -> str)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value"}, field_2 = "strings", field_3 = {"operation": "upper_case"}, field_4 = "hello", field_5 = str, field_6 = "HELLO"),
        # any.eval (Any -> str) -> strings (str -> bool)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value"}, field_2 = "strings", field_3 = {"operation": "contains", "param": "ell"}, field_4 = "hello", field_5 = bool, field_6 = True),
        # any.eval (Any -> int) -> generate (int -> list)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value * 2"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 3}, field_4 = 5, field_5 = list, field_6 = [10, 10, 10]),
        # any.eval (Any -> int) -> generate (int -> list)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value * 2"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = 8, field_5 = list, field_6 = [16, 16]),
        # any.eval (Any -> bool) -> generate (bool -> list)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value > 5"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = 10, field_5 = list, field_6 = [True, True]),
        # any.eval (Any -> list) -> lists (list -> list)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value"}, field_2 = "lists", field_3 = {"operation": "compact"}, field_4 = [1, None, 2], field_5 = list, field_6 = [1, 2]),
        # any.eval (Any -> int) -> generate (int -> list)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value * 3"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = 5, field_5 = list, field_6 = [15, 15]),
        # any.eval (Any -> str) -> strings (str -> str)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value.toString().toUpperCase()"}, field_2 = "strings", field_3 = {"operation": "reverse"}, field_4 = 3, field_5 = str, field_6 = "3"),
        # any.eval (Any -> bool) -> any (bool -> bool)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value > 20"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": True}, field_4 = 25, field_5 = bool, field_6 = True),
        # any.eval (Any -> float) -> any (float -> bool)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value / 2.0"}, field_2 = "any", field_3 = {"operation": "is_equal", "param": 2.5}, field_4 = 5, field_5 = bool, field_6 = True),
        # === any.eval as SECOND tool (accepting different input types) ===
        # strings (str -> str) -> any.eval (str -> str)
        TestChainAllToolPairsResult(field_0 = "strings", field_1 = {"operation": "upper_case"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value.split('').reverse().join('')"}, field_4 = "hello", field_5 = str, field_6 = "OLLEH"),
        # strings (str -> str) -> any.eval (str -> int)
        TestChainAllToolPairsResult(field_0 = "strings", field_1 = {"operation": "upper_case"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value.length"}, field_4 = "hello", field_5 = int, field_6 = 5),
        # strings (str -> str) -> any.eval (str -> bool)
        TestChainAllToolPairsResult(field_0 = "strings", field_1 = {"operation": "upper_case"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value.includes('H')"}, field_4 = "hello", field_5 = bool, field_6 = True),
        # strings (str -> str) -> any.eval (str -> float)
        TestChainAllToolPairsResult(field_0 = "strings", field_1 = {"operation": "template", "data": {"num": "3.14"}}, field_2 = "any", field_3 = {
                "operation": "eval",
                "expression": "parseFloat(value.match(/\\d+\\.\\d+/)[0])",
            }, field_4 = "The number is {num}", field_5 = float, field_6 = 3.14),
        # lists (list -> list) -> any.eval (list -> int)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value[0] ? 1 : 0"}, field_4 = [1, None, 2, 3], field_5 = int, field_6 = 1),
        # lists (list -> list) -> any.eval (list -> str)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value[0].toString()"}, field_4 = ["a", None, "b", "c"], field_5 = str, field_6 = "a"),
        # lists (list -> list) -> any.eval (list -> bool)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value[1] !== undefined"}, field_4 = [1, None, 2, 3], field_5 = bool, field_6 = True),
        # lists (list -> list) -> any.eval (list -> float)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "(value[0] + value[1]) / 2.0"}, field_4 = [10, None, 20], field_5 = float, field_6 = 15.0),
        # lists (list -> dict) -> any.eval (dict -> str)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": "item.type"}, field_2 = "any", field_3 = {
                "operation": "eval",
                "expression": "value.fruit ? 'has fruit' : 'no fruit'",
            }, field_4 = [{"type": "fruit"}, {"type": "fruit"}, {"type": "vegetable"}], field_5 = str, field_6 = "has fruit"),
        # lists (list -> dict) -> any.eval (dict -> int)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": "item.category"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value.A || 0"}, field_4 = [{"category": "A"}, {"category": "A"}, {"category": "B"}], field_5 = int, field_6 = 2),
        # lists (list -> dict) -> any.eval (dict -> bool)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "count_by", "expression": "item.status"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value.active && value.active > 1"}, field_4 = [{"status": "active"}, {"status": "active"}, {"status": "inactive"}], field_5 = bool, field_6 = True),
        # lists (list -> Any) -> any.eval (Any -> str)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {
                "operation": "eval",
                "expression": (
                    "typeof value === 'string' ? value.toUpperCase() : value.toString()"
                ),
            }, field_4 = ["hello", "world"], field_5 = str, field_6 = "HELLO"),
        # lists (list -> Any) -> any.eval (Any -> int)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "head"}, field_2 = "any", field_3 = {
                "operation": "eval",
                "expression": (
                    "typeof value === 'number' ? value * 2 : " "value.toString().length"
                ),
            }, field_4 = [42, "test"], field_5 = int, field_6 = 84),
        # dicts (dict -> dict) -> any.eval (dict -> str)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "invert"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value['2'] || 'not found'"}, field_4 = {"a": 1, "b": 2}, field_5 = str, field_6 = "b"),
        # dicts (dict -> dict) -> any.eval (dict -> int)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "invert"}, field_2 = "any", field_3 = {
                "operation": "eval",
                "expression": "value['1'] ? value['1'].length : 0",
            }, field_4 = {"a": 1, "b": 2}, field_5 = int, field_6 = 1),
        # dicts (dict -> dict) -> any.eval (dict -> bool)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "invert"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value['1'] !== undefined"}, field_4 = {"a": 1, "b": 2}, field_5 = bool, field_6 = True),
        # dicts (dict -> Any) -> any.eval (Any -> str)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "get_value", "path": "name"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value.toUpperCase()"}, field_4 = {"name": "alice", "age": 30}, field_5 = str, field_6 = "ALICE"),
        # dicts (dict -> Any) -> any.eval (Any -> int)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "get_value", "path": "age"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value + 10"}, field_4 = {"name": "alice", "age": 30}, field_5 = int, field_6 = 40),
        # dicts (dict -> Any) -> any.eval (Any -> bool)
        TestChainAllToolPairsResult(field_0 = "dicts", field_1 = {"operation": "get_value", "path": "score"}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value >= 80"}, field_4 = {"name": "alice", "score": 95}, field_5 = bool, field_6 = True),
        # generate (Any -> list) -> any.eval (list -> int)
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 3}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value[1] ? 3 : 0"}, field_4 = "x", field_5 = int, field_6 = 3),
        # generate (Any -> list) -> any.eval (list -> str)
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "range", "from": 1, "to": 4}, field_2 = "any", field_3 = {
                "operation": "eval",
                "expression": (
                    "value[0].toString() + '-' + value[1].toString() + '-' + "
                    "value[2].toString()"
                ),
            }, field_4 = None, field_5 = str, field_6 = "1-2-3"),
        # generate (Any -> list) -> any.eval (list -> bool)
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "repeat", "count": 2}, field_2 = "any", field_3 = {"operation": "eval", "expression": "value[0] === value[1]"}, field_4 = 42, field_5 = bool, field_6 = True),
        # generate (Any -> list) -> any.eval (list -> float)
        TestChainAllToolPairsResult(field_0 = "generate", field_1 = {"operation": "range", "from": 1, "to": 6}, field_2 = "any", field_3 = {"operation": "eval", "expression": "(value[0] + value[4]) / 2.0"}, field_4 = None, field_5 = float, field_6 = 3.0),
        # === Complex type conversion chains with any.eval ===
        # any.eval (nested dict -> extracted value) -> strings
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value.user.name"}, field_2 = "strings", field_3 = {"operation": "capitalize"}, field_4 = {"user": {"name": "alice", "age": 30}}, field_5 = str, field_6 = "Alice"),
        # any.eval (arithmetic calculation) -> generate
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value - 2"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 2}, field_4 = 7, field_5 = list, field_6 = [5, 5]),
        # any.eval (math calculation) -> lists (single item list)
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value * 3"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 1}, field_4 = 10, field_5 = list, field_6 = [30]),
        # any.eval (simple calculation) -> generate
        TestChainAllToolPairsResult(field_0 = "any", field_1 = {"operation": "eval", "expression": "value * 2"}, field_2 = "generate", field_3 = {"operation": "repeat", "count": 1}, field_4 = 5, field_5 = list, field_6 = [10]),
        # --- New: map, reduce, flat_map, filter_by, zip_with, all_by, any_by ---
        # map -> reduce
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "map", "expression": "item * 2"}, field_2 = "lists", field_3 = {"operation": "reduce", "expression": "acc + item", "param": 0}, field_4 = [1, 2, 3], field_5 = int, field_6 = 12),
        # filter_by -> map
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "filter_by", "expression": "item % 2 === 0"}, field_2 = "lists", field_3 = {"operation": "map", "expression": "item * 10"}, field_4 = [1, 2, 3, 4], field_5 = list, field_6 = [20, 40]),
        # map -> filter_by
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "map", "expression": "item * 2"}, field_2 = "lists", field_3 = {"operation": "filter_by", "expression": "item > 2"}, field_4 = [1, 2, 3], field_5 = list, field_6 = [4, 6]),
        # flat_map -> reduce
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "flat_map", "expression": "[item, item * 10]"}, field_2 = "lists", field_3 = {"operation": "reduce", "expression": "acc + item", "param": 0}, field_4 = [1, 2], field_5 = int, field_6 = 33),
        # map -> all_by
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "map", "expression": "item * 2"}, field_2 = "lists", field_3 = {"operation": "all_by", "expression": "item % 2 === 0"}, field_4 = [1, 2, 3], field_5 = bool, field_6 = True),
        # map -> any_by
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "map", "expression": "item * 2"}, field_2 = "lists", field_3 = {"operation": "any_by", "expression": "item === 4"}, field_4 = [1, 2, 3], field_5 = bool, field_6 = True),
        # zip_with -> map
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {
                "operation": "zip_with",
                "others": [10, 20, 30],
                "expression": "item + other",
            }, field_2 = "lists", field_3 = {"operation": "map", "expression": "item * 2"}, field_4 = [1, 2, 3], field_5 = list, field_6 = [22, 44, 66]),
        # map -> compact
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "map", "expression": "item > 1 ? item : null"}, field_2 = "lists", field_3 = {"operation": "compact"}, field_4 = [0, 1, 2, 3], field_5 = list, field_6 = [2, 3]),
        # compact -> map
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "compact"}, field_2 = "lists", field_3 = {"operation": "map", "expression": "item * 3"}, field_4 = [None, 1, 2], field_5 = list, field_6 = [3, 6]),
        # filter_by -> reduce
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "filter_by", "expression": "item > 1"}, field_2 = "lists", field_3 = {"operation": "reduce", "expression": "acc + item", "param": 0}, field_4 = [0, 1, 2, 3], field_5 = int, field_6 = 5),
        # map -> flat_map
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "map", "expression": "item + 1"}, field_2 = "lists", field_3 = {"operation": "flat_map", "expression": "[item, item * 2]"}, field_4 = [1, 2], field_5 = list, field_6 = [2, 4, 3, 6]),
        # flat_map -> filter_by
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "flat_map", "expression": "[item, item * 2]"}, field_2 = "lists", field_3 = {"operation": "filter_by", "expression": "item > 2"}, field_4 = [1, 2], field_5 = list, field_6 = [4]),
        # map -> head
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "map", "expression": "item * 2"}, field_2 = "lists", field_3 = {"operation": "head"}, field_4 = [1, 2, 3], field_5 = int, field_6 = 2),
        # filter_by -> head
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "filter_by", "expression": "item > 1"}, field_2 = "lists", field_3 = {"operation": "head"}, field_4 = [0, 1, 2, 3], field_5 = int, field_6 = 2),
        # map -> reduce (no param)
        TestChainAllToolPairsResult(field_0 = "lists", field_1 = {"operation": "map", "expression": "item * 2"}, field_2 = "lists", field_3 = {"operation": "reduce", "expression": "acc + item"}, field_4 = [1, 2, 3], field_5 = int, field_6 = 12),
        # --- End new chain pairings ---
    ],
)
async def test_chain_all_tool_pairs(
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
        assert (
            value == expected_value
        ), f"Expected value={expected_value}, got value={value}"
