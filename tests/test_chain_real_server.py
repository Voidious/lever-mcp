import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json
import pytest
import random
import socket
import subprocess
import time
from fastmcp import Client


def normalize_json(obj):
    if isinstance(obj, str):
        return json.dumps(json.loads(obj), sort_keys=True, separators=(",", ":"))
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


@pytest.fixture(scope="session")
def server_url():
    port = random.randint(12001, 12999)
    host = "127.0.0.1"
    url = f"http://{host}:{port}/mcp/"
    # Redirect stdout/stderr to avoid pipe blocking
    proc = subprocess.Popen(
        [sys.executable, "main.py", "--http", "--host", host, "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(30):
            try:
                with socket.create_connection((host, port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.2)
        else:
            proc.terminate()
            raise RuntimeError("HTTP server did not start in time")
        yield url
    finally:
        # Only terminate if not told to keep alive
        import os

        if not os.environ.get("KEEP_SERVER_UP"):
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()


@pytest.fixture
async def shared_client(server_url):
    async with Client(server_url) as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "first_tool,first_params,second_tool,second_params,input_value,expected_type,"
    "expected_value",
    [
        # mutate_string (str -> str) -> mutate_string (str -> str)
        (
            "mutate_string",
            {"mutation": "upper_case"},
            "mutate_string",
            {"mutation": "reverse"},
            "abc",
            str,
            "CBA",
        ),
        # mutate_string (str -> str) -> has_property (str -> bool)
        (
            "mutate_string",
            {"mutation": "upper_case"},
            "has_property",
            {"property": "is_upper"},
            "abc",
            bool,
            True,
        ),
        # mutate_string (str -> str) -> generate (str -> list) (repeat)
        (
            "mutate_string",
            {"mutation": "capitalize"},
            "generate",
            {"operation": "repeat", "param": 2},
            "foo",
            list,
            ["Foo", "Foo"],
        ),
        # mutate_list (list -> list) -> mutate_list (list -> list)
        (
            "mutate_list",
            {"mutation": "flatten_deep"},
            "mutate_list",
            {"mutation": "compact"},
            [1, [0, 2, None]],
            list,
            [1, 2],
        ),
        # mutate_list (list -> list) -> select_from_list (list -> Any)
        (
            "mutate_list",
            {"mutation": "compact"},
            "select_from_list",
            {"operation": "head"},
            [None, "foo", "bar"],
            str,
            "foo",
        ),
        # mutate_list (list -> list) -> process_list (list -> dict) (expect error due to
        # non-string keys)
        (
            "mutate_list",
            {"mutation": "compact"},
            "process_list",
            {"operation": "count_by", "key": 0},
            [[0], [0], [1]],
            dict,
            None,
        ),
        # mutate_list (list -> list) -> has_property (list -> bool) is_empty
        (
            "mutate_list",
            {"mutation": "compact"},
            "has_property",
            {"property": "is_empty"},
            [None, None],
            bool,
            True,
        ),
        # mutate_list (list -> list) -> has_property (list -> bool) is_equal
        (
            "mutate_list",
            {"mutation": "compact"},
            "has_property",
            {"property": "is_equal", "param": [1, 2]},
            [1, 2],
            bool,
            True,
        ),
        # mutate_list (list -> list) -> has_property (list -> bool) is_nil
        (
            "mutate_list",
            {"mutation": "compact"},
            "has_property",
            {"property": "is_nil"},
            [],
            bool,
            False,
        ),
        # mutate_list (list -> list) -> has_property (list -> bool) contains
        (
            "mutate_list",
            {"mutation": "compact"},
            "has_property",
            {"property": "contains", "param": 2},
            [1, 2, 3],
            bool,
            True,
        ),
        # mutate_list (list -> list) -> generate (powerset)
        (
            "mutate_list",
            {"mutation": "compact"},
            "generate",
            {"operation": "powerset"},
            [1, 2],
            list,
            [[], [1], [2], [1, 2]],
        ),
        # mutate_list (list -> list) -> generate (permutations)
        (
            "mutate_list",
            {"mutation": "compact"},
            "generate",
            {"operation": "permutations"},
            [1, 2],
            list,
            [[1, 2], [2, 1]],
        ),
        # mutate_list (list -> list) -> generate (windowed)
        (
            "mutate_list",
            {"mutation": "compact"},
            "generate",
            {"operation": "windowed", "param": 2},
            [1, 2, 3],
            list,
            [[1, 2], [2, 3]],
        ),
        # mutate_list (list -> list) -> generate (cycle)
        (
            "mutate_list",
            {"mutation": "compact"},
            "generate",
            {"operation": "cycle", "param": 3},
            [1, 2],
            list,
            [1, 2, 1],
        ),
        # mutate_list (list -> list) -> generate (accumulate)
        (
            "mutate_list",
            {"mutation": "compact"},
            "generate",
            {"operation": "accumulate"},
            [1, 2, 3],
            list,
            [1, 3, 6],
        ),
        # mutate_list (list -> list) -> generate (zip_with_index)
        (
            "mutate_list",
            {"mutation": "compact"},
            "generate",
            {"operation": "zip_with_index"},
            ["a", "b"],
            list,
            [[0, "a"], [1, "b"]],
        ),
        # mutate_list (list -> list) -> generate (unique_pairs)
        (
            "mutate_list",
            {"mutation": "compact"},
            "generate",
            {"operation": "unique_pairs"},
            [1, 2, 3],
            list,
            [[1, 2], [1, 3], [2, 3]],
        ),
        # mutate_list (list -> list) -> generate (combinations)
        (
            "mutate_list",
            {"mutation": "compact"},
            "generate",
            {"operation": "combinations", "param": 2},
            [1, 2, 3],
            list,
            [[1, 2], [1, 3], [2, 3]],
        ),
        # mutate_list (list -> list) -> generate (repeat)
        (
            "mutate_list",
            {"mutation": "compact"},
            "generate",
            {"operation": "repeat", "param": 2},
            [1],
            list,
            [[1], [1]],
        ),
        # mutate_list (list -> list) -> compare_lists (difference)
        (
            "mutate_list",
            {"mutation": "compact"},
            "compare_lists",
            {"b": [2, 3], "operation": "difference"},
            [1, 2, None, 3],
            list,
            [1],
        ),
        # mutate_list (list -> list) -> compare_lists (intersection)
        (
            "mutate_list",
            {"mutation": "compact"},
            "compare_lists",
            {"b": [2, 3], "operation": "intersection"},
            [1, 2, None, 3],
            list,
            [2, 3],
        ),
        # mutate_list (list -> list) -> compare_lists (difference_by)
        (
            "mutate_list",
            {"mutation": "compact"},
            "compare_lists",
            {"b": [{"id": 2}], "operation": "difference_by", "key": "id"},
            [{"id": 1}, None, {"id": 2}],
            list,
            [{"id": 1}],
        ),
        # mutate_list (list -> list) -> compare_lists (intersection_by)
        (
            "mutate_list",
            {"mutation": "compact"},
            "compare_lists",
            {"b": [{"id": 2}], "operation": "intersection_by", "key": "id"},
            [{"id": 1}, None, {"id": 2}],
            list,
            [{"id": 2}],
        ),
        # process_list (list -> dict) -> process_dict (dict -> dict) (expect error due
        # to non-string keys)
        (
            "process_list",
            {"operation": "count_by", "key": 0},
            "process_dict",
            {"operation": "invert"},
            [[0], [0], [1]],
            dict,
            None,
        ),
        # process_list (list -> dict) -> has_property (dict -> bool) is_empty (error
        # case)
        (
            "process_list",
            {"operation": "count_by", "key": 0},
            "has_property",
            {"property": "is_empty"},
            [[0], [0], [1]],
            bool,
            None,
        ),
        # process_list (list -> dict) -> has_property (dict -> bool) is_empty (working
        # case)
        (
            "process_list",
            {"operation": "count_by", "key": "x"},
            "has_property",
            {"property": "is_empty"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            bool,
            False,
        ),
        # process_list (list -> dict) -> has_property (dict -> bool) has_key (error
        # case)
        (
            "process_list",
            {"operation": "count_by", "key": 0},
            "has_property",
            {"property": "has_key", "param": 0},
            [[0], [0], [1]],
            bool,
            None,
        ),
        # process_list (list -> dict) -> has_property (dict -> bool) has_key (working
        # case)
        (
            "process_list",
            {"operation": "count_by", "key": "x"},
            "has_property",
            {"property": "has_key", "param": "1"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            bool,
            True,
        ),
        # process_list (list -> dict) -> has_property (dict -> bool) is_nil (error
        # case)
        (
            "process_list",
            {"operation": "count_by", "key": 0},
            "has_property",
            {"property": "is_nil"},
            [[0], [0], [1]],
            bool,
            None,
        ),
        # process_list (list -> dict) -> has_property (dict -> bool) is_nil (working
        # case)
        (
            "process_list",
            {"operation": "count_by", "key": "x"},
            "has_property",
            {"property": "is_nil"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            bool,
            False,
        ),
        # process_list (list -> dict) -> has_property (dict -> bool) contains (error
        # case)
        (
            "process_list",
            {"operation": "count_by", "key": 0},
            "has_property",
            {"property": "contains", "param": 2},
            [[0], [0], [1]],
            bool,
            None,
        ),
        # process_list (list -> dict) -> has_property (dict -> bool) contains (working
        # case)
        (
            "process_list",
            {"operation": "count_by", "key": "x"},
            "has_property",
            {"property": "contains", "param": "2"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            bool,
            False,
        ),
        # process_list (list -> dict) -> get_value (dict -> Any) (error case)
        (
            "process_list",
            {"operation": "count_by", "key": 0},
            "get_value",
            {"path": 0},
            [[0], [0], [1]],
            int,
            None,
        ),
        # process_list (list -> dict) -> get_value (dict -> Any) (working case)
        (
            "process_list",
            {"operation": "count_by", "key": "x"},
            "get_value",
            {"path": "1"},
            [{"x": 1}, {"x": 1}, {"x": 2}],
            int,
            2,
        ),
        # generate (Any -> Any, repeat str) -> mutate_list (list -> list)
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "mutate_list",
            {"mutation": "compact"},
            "foo",
            list,
            ["foo", "foo"],
        ),
        # generate (Any -> Any, range) -> mutate_list (list -> list) (compact removes 0)
        (
            "generate",
            {"operation": "range", "param": [0, 3]},
            "mutate_list",
            {"mutation": "compact"},
            None,
            list,
            [1, 2],
        ),
        # generate (Any -> Any, repeat str) -> select_from_list (list -> Any)
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "select_from_list",
            {"operation": "head"},
            "foo",
            str,
            "foo",
        ),
        # select_from_list (list -> Any, head str) -> mutate_string (str -> str)
        # (working case)
        (
            "select_from_list",
            {"operation": "head"},
            "mutate_string",
            {"mutation": "upper_case"},
            ["foo", "bar", "baz"],
            str,
            "FOO",
        ),
        # get_value (dict -> Any, str) -> mutate_string (str -> str)
        (
            "get_value",
            {"path": "a"},
            "mutate_string",
            {"mutation": "capitalize"},
            {"a": "hello"},
            str,
            "Hello",
        ),
        # get_value (dict -> Any, list) -> mutate_list (list -> list)
        (
            "get_value",
            {"path": "a"},
            "mutate_list",
            {"mutation": "compact"},
            {"a": [None, 1, 2]},
            list,
            [1, 2],
        ),
        # process_dict (dict -> dict) -> process_dict (dict -> dict) (invert twice
        # returns original dict with string values)
        (
            "process_dict",
            {"operation": "invert"},
            "process_dict",
            {"operation": "invert"},
            {"a": 1, "b": 2},
            dict,
            {"a": "1", "b": "2"},
        ),
        # merge (list of dicts -> dict) -> process_dict (dict -> dict) (int keys,
        # converted to string)
        (
            "merge",
            {},
            "process_dict",
            {"operation": "invert"},
            [{"a": 1}, {"b": 2}],
            dict,
            {"1": "a", "2": "b"},
        ),
        # merge (list of dicts -> dict) -> process_dict (dict -> dict) (string keys)
        (
            "merge",
            {},
            "process_dict",
            {"operation": "invert"},
            [{"a": "x"}, {"b": "y"}],
            dict,
            {"x": "a", "y": "b"},
        ),
        # set_value (dict -> dict) -> get_value (dict -> Any)
        (
            "set_value",
            {"path": "a.b", "value": 42},
            "get_value",
            {"path": "a.b"},
            {"a": {}},
            int,
            42,
        ),
        # get_value (dict -> Any, int) -> generate (Any -> Any, repeat)
        (
            "get_value",
            {"path": "a"},
            "generate",
            {"operation": "repeat", "param": 2},
            {"a": 7},
            list,
            [7, 7],
        ),
        # has_property (Any -> bool, is_upper) -> mutate_string (should error,
        # bool->str)
        (
            "has_property",
            {"property": "is_upper"},
            "mutate_string",
            {"mutation": "upper_case"},
            "abc",
            str,
            None,
        ),
        # select_from_list (list -> Any, head int) -> generate (Any -> Any, repeat)
        (
            "select_from_list",
            {"operation": "head"},
            "generate",
            {"operation": "repeat", "param": 2},
            [7, 8],
            list,
            [7, 7],
        ),
        # mutate_list -> merge (list of dicts)
        (
            "mutate_list",
            {"mutation": "compact"},
            "merge",
            {},
            [{"a": 1}, None, {"b": 2}],
            dict,
            {"a": 1, "b": 2},
        ),
        # has_property -> generate (repeat bool)
        (
            "has_property",
            {"property": "is_nil"},
            "generate",
            {"operation": "repeat", "param": 2},
            0,
            list,
            [False, False],
        ),
        # select_from_list -> has_property (output: str)
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "is_digit"},
            ["7", "8"],
            bool,
            True,
        ),
        # select_from_list -> process_dict (output: dict)
        (
            "select_from_list",
            {"operation": "head"},
            "process_dict",
            {"operation": "invert"},
            [{"a": "x", "b": "y"}],
            dict,
            {"x": "a", "y": "b"},
        ),
        # select_from_list -> set_value (output: dict)
        (
            "select_from_list",
            {"operation": "head"},
            "set_value",
            {"path": "c", "value": 42},
            [{"a": 1, "b": 2}],
            dict,
            {"a": 1, "b": 2, "c": 42},
        ),
        # select_from_list -> get_value (output: dict)
        (
            "select_from_list",
            {"operation": "head"},
            "get_value",
            {"path": "a"},
            [{"a": 7}, {"b": 8}],
            int,
            7,
        ),
        # select_from_list -> merge (output: list of dicts)
        (
            "select_from_list",
            {"operation": "head"},
            "merge",
            {},
            [[{"a": 1}, {"b": 2}], [{"c": 3}]],
            dict,
            {"a": 1, "b": 2},
        ),
        # compare_lists -> mutate_list
        (
            "compare_lists",
            {"b": [2], "operation": "difference"},
            "mutate_list",
            {"mutation": "compact"},
            [1, 2, None],
            list,
            [1],
        ),
        # compare_lists -> has_property
        (
            "compare_lists",
            {"b": [2], "operation": "difference"},
            "has_property",
            {"property": "is_empty"},
            [1, 2],
            bool,
            False,
        ),
        # compare_lists -> select_from_list
        (
            "compare_lists",
            {"b": [2], "operation": "difference"},
            "select_from_list",
            {"operation": "head"},
            [1, 2],
            int,
            1,
        ),
        # compare_lists -> process_list (list of dicts)
        (
            "compare_lists",
            {"b": [{"id": 2}], "operation": "difference_by", "key": "id"},
            "process_list",
            {"operation": "count_by", "key": "id"},
            [{"id": 1}, {"id": 2}, {"id": 1}],
            dict,
            {1: 2},
        ),
        # compare_lists -> generate (repeat the result of difference)
        (
            "compare_lists",
            {"b": [2], "operation": "difference"},
            "generate",
            {"operation": "repeat", "param": 2},
            [1, 2],
            list,
            [[1], [1]],
        ),
        # compare_lists -> merge (difference_by, expect {"x": 1})
        (
            "compare_lists",
            {"b": [{"x": 2}], "operation": "difference_by", "key": "x"},
            "merge",
            {},
            [{"x": 1}, {"x": 2}],
            dict,
            {"x": 1},
        ),
        # process_list -> set_value
        (
            "process_list",
            {"operation": "key_by", "key": "id"},
            "set_value",
            {"path": "x", "value": 99},
            [{"id": "a", "val": 1}],
            dict,
            {"a": {"id": "a", "val": 1}, "x": 99},
        ),
        # process_list -> get_value
        (
            "process_list",
            {"operation": "key_by", "key": "id"},
            "get_value",
            {"path": "a"},
            [{"id": "a", "val": 1}],
            dict,
            {"id": "a", "val": 1},
        ),
        # process_dict -> has_property
        (
            "process_dict",
            {"operation": "invert"},
            "has_property",
            {"property": "has_key", "param": "x"},
            {"a": "x", "b": "y"},
            bool,
            True,
        ),
        # process_dict -> generate (repeat the output of invert)
        (
            "process_dict",
            {"operation": "invert"},
            "generate",
            {"operation": "repeat", "param": 2},
            {"a": 1, "b": 2},
            list,
            [{"1": "a", "2": "b"}, {"1": "a", "2": "b"}],
        ),
        # process_dict -> set_value (add a key to the output of invert)
        (
            "process_dict",
            {"operation": "invert"},
            "set_value",
            {"path": "c", "value": 42},
            {"a": 1, "b": 2},
            dict,
            {"1": "a", "2": "b", "c": 42},
        ),
        # process_dict -> get_value (get a value from the output of invert)
        (
            "process_dict",
            {"operation": "invert"},
            "get_value",
            {"path": "1"},
            {"a": 1, "b": 2},
            str,
            "a",
        ),
        # generate -> has_property
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "has_property",
            {"property": "is_empty"},
            [1, 2],
            bool,
            False,
        ),
        # generate -> process_list (list of dicts)
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "process_list",
            {"operation": "count_by", "key": "a"},
            {"a": 1},
            dict,
            {1: 2},
        ),
        # generate -> merge (list of dicts)
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "merge",
            {},
            {"a": 1, "b": 2},
            dict,
            {"a": 1, "b": 2},
        ),
        # merge -> has_property
        (
            "merge",
            {},
            "has_property",
            {"property": "has_key", "param": "a"},
            [{"a": 1}, {"b": 2}],
            bool,
            True,
        ),
        # merge -> generate (repeat the output of merge)
        (
            "merge",
            {},
            "generate",
            {"operation": "repeat", "param": 2},
            [{"a": 1, "b": 2}],
            list,
            [{"a": 1, "b": 2}, {"a": 1, "b": 2}],
        ),
        # merge -> set_value (add a key to the output of merge)
        (
            "merge",
            {},
            "set_value",
            {"path": "c", "value": 42},
            [{"a": 1, "b": 2}],
            dict,
            {"a": 1, "b": 2, "c": 42},
        ),
        # merge -> get_value (get a value from the output of merge)
        ("merge", {}, "get_value", {"path": "a"}, [{"a": 1, "b": 2}], int, 1),
        # set_value -> process_dict (invert the output of set_value)
        (
            "set_value",
            {"path": "a", "value": 1},
            "process_dict",
            {"operation": "invert"},
            {"b": 2},
            dict,
            {"2": "b", "1": "a"},
        ),
        # set_value -> generate (repeat the output dict)
        (
            "set_value",
            {"path": "a", "value": 1},
            "generate",
            {"operation": "repeat", "param": 2},
            {"b": 2},
            list,
            [{"b": 2, "a": 1}, {"b": 2, "a": 1}],
        ),
        # set_value -> has_property (check for added key)
        (
            "set_value",
            {"path": "a", "value": 1},
            "has_property",
            {"property": "has_key", "param": "a"},
            {"b": 2},
            bool,
            True,
        ),
        # set_value -> set_value (add another key)
        (
            "set_value",
            {"path": "a", "value": 1},
            "set_value",
            {"path": "c", "value": 42},
            {"b": 2},
            dict,
            {"b": 2, "a": 1, "c": 42},
        ),
        # generate -> has_property(is_equal) (list[str], list[int], list[dict],
        # list[bool], list[list])
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "has_property",
            {"property": "is_equal", "param": ["a", "a"]},
            "a",
            bool,
            True,
        ),
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "has_property",
            {"property": "is_equal", "param": [1, 1]},
            1,
            bool,
            True,
        ),
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "has_property",
            {"property": "is_equal", "param": [{"x": 1}, {"x": 1}]},
            {"x": 1},
            bool,
            True,
        ),
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "has_property",
            {"property": "is_equal", "param": [True, True]},
            True,
            bool,
            True,
        ),
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "has_property",
            {"property": "is_equal", "param": [[1], [1]]},
            [1],
            bool,
            True,
        ),
        # generate -> has_property(contains) (list[str])
        (
            "generate",
            {"operation": "repeat", "param": 2},
            "has_property",
            {"property": "contains", "param": "a"},
            "a",
            bool,
            True,
        ),
        # select_from_list -> has_property(is_equal) (str, int, list, dict, bool)
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "is_equal", "param": "a"},
            ["a", "b"],
            bool,
            True,
        ),
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "is_equal", "param": 1},
            [1, 2],
            bool,
            True,
        ),
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "is_equal", "param": [1]},
            [[1], [2]],
            bool,
            True,
        ),
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "is_equal", "param": {"x": 1}},
            [{"x": 1}, {"x": 2}],
            bool,
            True,
        ),
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "is_equal", "param": True},
            [True, False],
            bool,
            True,
        ),
        # select_from_list -> has_property(contains) (list[str], list[int], str)
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "contains", "param": "a"},
            [["a", "b"], ["c"]],
            bool,
            True,
        ),
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "contains", "param": 1},
            [[1, 2], [3]],
            bool,
            True,
        ),
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "contains", "param": "b"},
            ["ab", "cd"],
            bool,
            True,
        ),
        # select_from_list -> has_property(is_empty) (str)
        (
            "select_from_list",
            {"operation": "head"},
            "has_property",
            {"property": "is_empty"},
            [""],
            bool,
            True,
        ),
    ],
)
async def test_chain_all_tool_pairs_real_server(
    shared_client,
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
    request_json = json.dumps(chain_payload, sort_keys=True, separators=(",", ":"))
    result = await shared_client.call_tool("chain", json.loads(request_json))
    response = result[0].text if result and hasattr(result[0], "text") else None
    assert response is not None
    response_norm = normalize_json(response)
    if expected_value is None:
        data = json.loads(response)
        assert "error" in data, f"Expected error, got {data}"
    else:
        # Build expected response JSON string
        expected_response = {"value": expected_value}
        expected_norm = normalize_json(expected_response)
        assert response_norm == expected_norm
