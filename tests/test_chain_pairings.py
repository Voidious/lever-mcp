import pytest
import importlib
import main
from main import LeverMCP
from fastmcp import Client
from . import make_tool_call


@pytest.fixture
async def client():
    importlib.reload(main)
    mcp_instance: LeverMCP = main.mcp
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
            {"operation": "repeat", "param": 2},
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
        # lists (list -> list) -> lists (list -> dict) (error due to non-string keys)
        (
            "lists",
            {"operation": "compact"},
            "lists",
            {"operation": "count_by", "key": 0},
            [[0], [0], [1]],
            dict,
            None,
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
        # lists (list -> list) -> generate (windowed)
        (
            "lists",
            {"operation": "compact"},
            "generate",
            {"operation": "windowed", "param": 2},
            [1, 2, 3],
            list,
            [[1, 2], [2, 3]],
        ),
        # lists (list -> list) -> generate (cycle)
        (
            "lists",
            {"operation": "compact"},
            "generate",
            {"operation": "cycle", "param": 3},
            [1, 2],
            list,
            [1, 2, 1],
        ),
        # lists (list -> list) -> generate (accumulate)
        (
            "lists",
            {"operation": "compact"},
            "generate",
            {"operation": "accumulate"},
            [1, 2, 3],
            list,
            [1, 3, 6],
        ),
        # lists (list -> list) -> generate (zip_with_index)
        (
            "lists",
            {"operation": "compact"},
            "generate",
            {"operation": "zip_with_index"},
            ["a", "b"],
            list,
            [[0, "a"], [1, "b"]],
        ),
        # lists (list -> list) -> generate (unique_pairs)
        (
            "lists",
            {"operation": "compact"},
            "generate",
            {"operation": "unique_pairs"},
            [1, 2, 3],
            list,
            [[1, 2], [1, 3], [2, 3]],
        ),
        # lists (list -> list) -> generate (combinations)
        (
            "lists",
            {"operation": "compact"},
            "generate",
            {"operation": "combinations", "param": 2},
            [1, 2, 3],
            list,
            [[1, 2], [1, 3], [2, 3]],
        ),
        # lists (list -> list) -> generate (repeat)
        (
            "lists",
            {"operation": "compact"},
            "generate",
            {"operation": "repeat", "param": 2},
            [1],
            list,
            [[1], [1]],
        ),
        # lists (list -> list) -> lists (difference)
        (
            "lists",
            {"operation": "compact"},
            "lists",
            {"operation": "difference", "others": [2, 3]},
            [1, 2, None, 3],
            list,
            [1],
        ),
        # lists (list -> list) -> lists (intersection)
        (
            "lists",
            {"operation": "compact"},
            "lists",
            {"operation": "intersection", "others": [2, 3]},
            [1, 2, None, 3],
            list,
            [2, 3],
        ),
        # lists (list -> list) -> lists (difference_by)
        (
            "lists",
            {"operation": "compact"},
            "lists",
            {"operation": "difference_by", "others": [{"id": 2}], "key": "id"},
            [{"id": 1}, None, {"id": 2}],
            list,
            [{"id": 1}],
        ),
        # lists (list -> list) -> lists (intersection_by)
        (
            "lists",
            {"operation": "compact"},
            "lists",
            {"operation": "intersection_by", "others": [{"id": 2}], "key": "id"},
            [{"id": 1}, None, {"id": 2}],
            list,
            [{"id": 2}],
        ),
        # lists (list -> dict) -> dicts (dict -> dict) (error due to non-string keys)
        (
            "lists",
            {"operation": "count_by", "key": 0},
            "dicts",
            {"operation": "invert"},
            [[0], [0], [1]],
            dict,
            None,
        ),
        # lists (list -> dict) -> dicts (dict -> bool) is_empty (error case)
        (
            "lists",
            {"operation": "count_by", "key": 0},
            "any",
            {"operation": "is_empty"},
            [[0], [0], [1]],
            bool,
            None,
        ),
        # lists (list -> dict) -> dicts (dict -> bool) is_empty (working case)
        (
            "lists",
            {"operation": "count_by", "key": "x"},
            "dicts",
            {"operation": "is_empty"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            bool,
            False,
        ),
        # lists (list -> dict) -> dicts (dict -> bool) has_key (error case)
        (
            "lists",
            {"operation": "count_by", "key": 0},
            "dicts",
            {"operation": "has_key", "param": 0},
            [[0], [0], [1]],
            bool,
            None,
        ),
        # lists (list -> dict) -> dicts (dict -> bool) has_key (working case)
        (
            "lists",
            {"operation": "count_by", "key": "x"},
            "dicts",
            {"operation": "has_key", "param": "1"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            bool,
            True,
        ),
        # lists (list -> dict) -> any (any -> bool) is_nil (error case)
        (
            "lists",
            {"operation": "count_by", "key": 0},
            "any",
            {"operation": "is_nil"},
            [[0], [0], [1]],
            bool,
            None,
        ),
        # lists (list -> dict) -> any (any -> bool) is_nil (working case)
        (
            "lists",
            {"operation": "count_by", "key": "x"},
            "any",
            {"operation": "is_nil"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            bool,
            False,
        ),
        # lists (list -> dict) -> any (any -> bool) contains (error case)
        (
            "lists",
            {"operation": "count_by", "key": 0},
            "any",
            {"operation": "contains", "param": 2},
            [[0], [0], [1]],
            bool,
            None,
        ),
        # lists (list -> dict) -> any (any -> bool) contains (working case)
        (
            "lists",
            {"operation": "count_by", "key": "x"},
            "any",
            {"operation": "contains", "param": "2"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            bool,
            False,
        ),
        # lists (list -> dict) -> dicts (dict -> Any) (error case)
        (
            "lists",
            {"operation": "count_by", "key": 0},
            "dicts",
            {"operation": "get_value", "path": 0},
            [[0], [0], [1]],
            int,
            None,
        ),
        # lists (list -> dict) -> dicts (dict -> Any) (working case)
        (
            "lists",
            {"operation": "count_by", "key": "x"},
            "dicts",
            {"operation": "get_value", "path": "1"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            int,
            2,
        ),
        # generate (Any -> Any, repeat str) -> lists (list -> list)
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "lists",
            {"operation": "compact"},
            "foo",
            list,
            ["foo", "foo"],
        ),
        # generate (Any -> Any, range) -> lists (list -> list) (compact removes 0)
        (
            "generate",
            {"operation": "range", "param": [0, 3]},
            "lists",
            {"operation": "compact"},
            None,
            list,
            [1, 2],
        ),
        # generate (Any -> Any, repeat str) -> lists (list -> Any)
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "lists",
            {"operation": "head"},
            "foo",
            str,
            "foo",
        ),
        # lists (list -> Any, head str) -> strings (str -> str) (working case)
        (
            "lists",
            {"operation": "head"},
            "strings",
            {"operation": "upper_case"},
            ["foo", "bar", "baz"],
            str,
            "FOO",
        ),
        # dicts (dict -> Any, str) -> strings (str -> str)
        (
            "dicts",
            {"operation": "get_value", "path": "a"},
            "strings",
            {"operation": "capitalize"},
            {"a": "hello"},
            str,
            "Hello",
        ),
        # dicts (dict -> Any, list) -> lists (list -> list)
        (
            "dicts",
            {"operation": "get_value", "path": "a"},
            "lists",
            {"operation": "compact"},
            {"a": [None, 1, 2]},
            list,
            [1, 2],
        ),
        # dicts (dict -> dict) -> dicts (dict -> dict)
        #   (tool response converts keys to JSON)
        (
            "dicts",
            {"operation": "invert"},
            "dicts",
            {"operation": "invert"},
            {"a": 1, "b": 2},
            dict,
            {"a": "1", "b": "2"},
        ),
        # dicts (list of dicts -> dict) -> dicts (dict -> dict)
        #   (int keys, converted to string)
        (
            "dicts",
            {"operation": "merge"},
            "dicts",
            {"operation": "invert"},
            [{"a": 1}, {"b": 2}],
            dict,
            {"1": "a", "2": "b"},
        ),
        # dicts (list of dicts -> dict) -> dicts (dict -> dict) (string keys)
        (
            "dicts",
            {"operation": "merge"},
            "dicts",
            {"operation": "invert"},
            [{"a": "x"}, {"b": "y"}],
            dict,
            {"x": "a", "y": "b"},
        ),
        # dicts (dict -> dict) -> dicts (dict -> dict)
        (
            "dicts",
            {"operation": "set_value", "path": "a.b", "value": 42},
            "dicts",
            {"operation": "get_value", "path": "a.b"},
            {"a": {}},
            int,
            42,
        ),
        # dicts (dict -> Any, int) -> generate (Any -> Any, repeat)
        (
            "dicts",
            {"operation": "get_value", "path": "a"},
            "generate",
            {"operation": "repeat", "param": 2},
            {"a": 7},
            list,
            [7, 7],
        ),
        # lists -> dicts (list of dicts)
        (
            "lists",
            {"operation": "compact"},
            "dicts",
            {"operation": "merge"},
            [{"a": 1}, None, {"b": 2}],
            dict,
            {"a": 1, "b": 2},
        ),
        # any -> lists (repeat bool)
        (
            "any",
            {"operation": "is_nil"},
            "generate",
            {"operation": "repeat", "param": 2},
            0,
            list,
            [False, False],
        ),
        # lists -> dicts (output: dict)
        (
            "lists",
            {"operation": "head"},
            "dicts",
            {"operation": "invert"},
            [{"a": "x", "b": "y"}],
            dict,
            {"x": "a", "y": "b"},
        ),
        # lists -> dicts (output: dict)
        (
            "lists",
            {"operation": "head"},
            "dicts",
            {"operation": "set_value", "path": "c", "value": 42},
            [{"a": 1, "b": 2}],
            dict,
            {"a": 1, "b": 2, "c": 42},
        ),
        # lists -> dicts (output: dict)
        (
            "lists",
            {"operation": "head"},
            "dicts",
            {"operation": "get_value", "path": "a"},
            [{"a": 7}, {"b": 8}],
            int,
            7,
        ),
        # lists -> dicts (output: list of dicts)
        (
            "lists",
            {"operation": "head"},
            "dicts",
            {"operation": "merge"},
            [[{"a": 1}, {"b": 2}], [{"c": 3}]],
            dict,
            {"a": 1, "b": 2},
        ),
        # lists -> lists
        (
            "lists",
            {"operation": "difference", "others": [2]},
            "lists",
            {"operation": "compact"},
            [1, 2, None],
            list,
            [1],
        ),
        # lists -> lists
        (
            "lists",
            {"operation": "difference", "others": [2]},
            "lists",
            {"operation": "is_empty"},
            [1, 2],
            bool,
            False,
        ),
        # lists -> lists
        (
            "lists",
            {"operation": "difference", "others": [2]},
            "lists",
            {"operation": "head"},
            [1, 2],
            int,
            1,
        ),
        # lists -> lists (list of dicts)
        (
            "lists",
            {"operation": "difference_by", "others": [{"id": 2}], "key": "id"},
            "lists",
            {"operation": "count_by", "key": "id"},
            [{"id": 1}, {"id": 2}, {"id": 1}],
            dict,
            {"1": 2},
        ),
        # lists -> generate (repeat the result of difference)
        (
            "lists",
            {"operation": "difference", "others": [2]},
            "generate",
            {"operation": "repeat", "param": 2},
            [1, 2],
            list,
            [[1], [1]],
        ),
        # lists -> dicts (difference_by, expect {"x": 1})
        (
            "lists",
            {"operation": "difference_by", "others": [{"x": 2}], "key": "x"},
            "dicts",
            {"operation": "merge"},
            [{"x": 1}, {"x": 2}],
            dict,
            {"x": 1},
        ),
        # lists -> dicts
        (
            "lists",
            {"operation": "key_by", "key": "id"},
            "dicts",
            {"operation": "set_value", "path": "x", "value": 99},
            [{"id": "a", "val": 1}],
            dict,
            {"a": {"id": "a", "val": 1}, "x": 99},
        ),
        # lists -> dicts
        (
            "lists",
            {"operation": "key_by", "key": "id"},
            "dicts",
            {"operation": "get_value", "path": "a"},
            [{"id": "a", "val": 1}],
            dict,
            {"id": "a", "val": 1},
        ),
        # dicts -> dicts
        (
            "dicts",
            {"operation": "invert"},
            "dicts",
            {"operation": "has_key", "param": "x"},
            {"a": "x", "b": "y"},
            bool,
            True,
        ),
        # dicts -> generate (repeat the output of invert)
        (
            "dicts",
            {"operation": "invert"},
            "generate",
            {"operation": "repeat", "param": 2},
            {"a": 1, "b": 2},
            list,
            [{"1": "a", "2": "b"}, {"1": "a", "2": "b"}],
        ),
        # dicts -> dicts (add a key to the output of invert)
        (
            "dicts",
            {"operation": "invert"},
            "dicts",
            {"operation": "set_value", "path": "c", "value": 42},
            {"a": 1, "b": 2},
            dict,
            {"1": "a", "2": "b", "c": 42},
        ),
        # dicts -> dicts (get a value from the output of invert)
        (
            "dicts",
            {"operation": "invert"},
            "dicts",
            {"operation": "get_value", "path": "1"},
            {"a": 1, "b": 2},
            str,
            "a",
        ),
        # generate -> lists
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "lists",
            {"operation": "is_empty"},
            [1, 2],
            bool,
            False,
        ),
        # generate -> lists (list of dicts)
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "lists",
            {"operation": "count_by", "key": "a"},
            {"a": 1},
            dict,
            {"1": 2},
        ),
        # generate -> dicts (list of dicts)
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "dicts",
            {"operation": "merge"},
            {"a": 1, "b": 2},
            dict,
            {"a": 1, "b": 2},
        ),
        # dicts -> dicts
        (
            "dicts",
            {"operation": "merge"},
            "dicts",
            {"operation": "has_key", "param": "a"},
            [{"a": 1}, {"b": 2}],
            bool,
            True,
        ),
        # dicts -> generate (repeat the output of merge)
        (
            "dicts",
            {"operation": "merge"},
            "generate",
            {"operation": "repeat", "param": 2},
            [{"a": 1, "b": 2}],
            list,
            [{"a": 1, "b": 2}, {"a": 1, "b": 2}],
        ),
        # dicts -> dicts (add a key to the output of merge)
        (
            "dicts",
            {"operation": "merge"},
            "dicts",
            {"operation": "set_value", "path": "c", "value": 42},
            [{"a": 1, "b": 2}],
            dict,
            {"a": 1, "b": 2, "c": 42},
        ),
        # dicts -> dicts (get a value from the output of merge)
        (
            "dicts",
            {"operation": "merge"},
            "dicts",
            {"operation": "get_value", "path": "a"},
            [{"a": 1, "b": 2}],
            int,
            1,
        ),
        # dicts -> dicts (invert the output of set_value)
        (
            "dicts",
            {"operation": "set_value", "path": "a", "value": 1},
            "dicts",
            {"operation": "invert"},
            {"b": 2},
            dict,
            {"2": "b", "1": "a"},
        ),
        # dicts -> generate (repeat the output dict)
        (
            "dicts",
            {"operation": "set_value", "path": "a", "value": 1},
            "generate",
            {"operation": "repeat", "param": 2},
            {"b": 2},
            list,
            [{"b": 2, "a": 1}, {"b": 2, "a": 1}],
        ),
        # dicts -> dicts (check for added key)
        (
            "dicts",
            {"operation": "set_value", "path": "a", "value": 1},
            "dicts",
            {"operation": "has_key", "param": "a"},
            {"b": 2},
            bool,
            True,
        ),
        # dicts -> dicts (add another key)
        (
            "dicts",
            {"operation": "set_value", "path": "a", "value": 1},
            "dicts",
            {"operation": "set_value", "path": "c", "value": 42},
            {"b": 2},
            dict,
            {"b": 2, "a": 1, "c": 42},
        ),
        # generate -> lists (is_equal)
        #   (list[str], list[int], list[dict], list[bool], list[list])
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "any",
            {"operation": "is_equal", "param": ["a", "a"]},
            "a",
            bool,
            True,
        ),
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "any",
            {"operation": "is_equal", "param": [1, 1]},
            1,
            bool,
            True,
        ),
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "any",
            {"operation": "is_equal", "param": [{"x": 1}, {"x": 1}]},
            {"x": 1},
            bool,
            True,
        ),
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "any",
            {"operation": "is_equal", "param": [True, True]},
            True,
            bool,
            True,
        ),
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "any",
            {"operation": "is_equal", "param": [[1], [1]]},
            [1],
            bool,
            True,
        ),
        # generate -> lists (contains) (list[str])
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "any",
            {"operation": "contains", "param": "a"},
            "a",
            bool,
            True,
        ),
        # lists -> lists (is_equal) (str, int, list, dict, bool)
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "is_equal", "param": "a"},
            ["a", "b"],
            bool,
            True,
        ),
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "is_equal", "param": 1},
            [1, 2],
            bool,
            True,
        ),
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "is_equal", "param": [1]},
            [[1], [2]],
            bool,
            True,
        ),
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "is_equal", "param": {"x": 1}},
            [{"x": 1}, {"x": 2}],
            bool,
            True,
        ),
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "is_equal", "param": True},
            [True, False],
            bool,
            True,
        ),
        # lists -> lists (contains) (list[str], list[int], str)
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "contains", "param": "a"},
            [["a", "b"], ["c"]],
            bool,
            True,
        ),
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "contains", "param": 1},
            [[1, 2], [3]],
            bool,
            True,
        ),
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "contains", "param": "b"},
            ["ab", "cd"],
            bool,
            True,
        ),
        # --- Restored: type-agnostic contains/is_equal using any ---
        (
            "dicts",
            {"operation": "invert"},
            "any",
            {"operation": "contains", "param": "a"},
            {"a": 1, "b": 2},
            bool,
            False,
        ),
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "contains", "param": 1},
            [[1]],
            bool,
            True,
        ),
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "is_equal", "param": 1},
            [1],
            bool,
            True,
        ),
        # lists -> lists (is_empty) (str)
        (
            "lists",
            {"operation": "head"},
            "any",
            {"operation": "is_empty"},
            [""],
            bool,
            True,
        ),
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
