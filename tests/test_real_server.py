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
async def test_mutate_string_real_server(shared_client):
    result = await shared_client.call_tool(
        "mutate_string", {"text": "hello", "mutation": "upper_case"}
    )
    assert json.loads(result[0].text)["value"] == "HELLO"


@pytest.mark.asyncio
async def test_mutate_list_real_server(shared_client):
    items = [1, None, 2]
    mutation = "compact"
    result = await shared_client.call_tool(
        "mutate_list", {"items": items, "mutation": mutation}
    )
    assert json.loads(result[0].text)["value"] == [1, 2]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj,property,param,expected",
    [
        ("abc", "is_upper", None, False),
        ("ABC", "is_upper", None, True),
        ([1, 2, 3], "contains", 2, True),
        ({"a": 1}, "has_key", "a", True),
        (None, "is_empty", None, True),
        (42, "is_equal", 42, True),
        (3.14, "is_equal", 3.14, True),
        (False, "is_equal", False, True),
    ],
)
async def test_has_property_types_real_server(
    shared_client, obj, property, param, expected
):
    args = {"obj": obj, "property": property}
    if param is not None:
        args["param"] = param
    result = await shared_client.call_tool("has_property", args)
    assert json.loads(result[0].text)["value"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items,operation,param,expected",
    [
        ([1, 2, 3], "last", None, 3),
        ([1, 2, 3.14], "last", None, 3.14),
        (["a", "b"], "head", None, "a"),
        ([True, False], "head", None, True),
        ([None, "a"], "head", None, None),
        ([["a"], ["b"]], "head", None, ["a"]),
        ([{"x": 1}, {"x": 2}], "find_by", {"key": "x", "value": 2}, {"x": 2}),
        ([{"x": "a"}, {"x": "b"}], "find_by", {"key": "x", "value": "b"}, {"x": "b"}),
        (
            [{"x": True}, {"x": False}],
            "find_by",
            {"key": "x", "value": False},
            {"x": False},
        ),
        ([{"x": None}, {"x": 1}], "find_by", {"key": "x", "value": None}, {"x": None}),
        ([{"x": [1]}, {"x": [2]}], "find_by", {"key": "x", "value": [2]}, {"x": [2]}),
        ([{"x": 1}, {"x": 2}], "nth", 1, {"x": 2}),
    ],
)
async def test_select_from_list_types_real_server(
    shared_client, items, operation, param, expected
):
    args = {"items": items, "operation": operation}
    if param is not None:
        args["param"] = param
    result = await shared_client.call_tool("select_from_list", args)
    assert json.loads(result[0].text)["value"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "a,b,operation,key,expected",
    [
        ([1, 2, 3], [2], "difference", None, [1, 3]),
        (["a", "b"], ["b"], "intersection", None, ["b"]),
        ([True, True, False], [False], "difference", None, [True, True]),
        ([None, {"id": 1}], [{"id": 1}], "difference", None, [None]),
        ([None, {"id": 1}], [None], "difference", None, [{"id": 1}]),
        ([{"id": 1}, {"id": 2}], [{"id": 2}], "difference_by", "id", [{"id": 1}]),
        ([[1], [2], [3]], [[2]], "intersection", None, [[2]]),
    ],
)
async def test_compare_lists_types_real_server(
    shared_client, a, b, operation, key, expected
):
    args = {"a": a, "b": b, "operation": operation}
    if key is not None:
        args["key"] = key
    result = await shared_client.call_tool("compare_lists", args)
    assert json.loads(result[0].text)["value"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input,operation,param,expected",
    [
        (3, "repeat", 2, [3, 3]),
        ([1, 2], "powerset", None, [[], [1], [2], [1, 2]]),
        (
            [[1, 2], ["a", "b"]],
            "cartesian_product",
            None,
            [[1, "a"], [1, "b"], [2, "a"], [2, "b"]],
        ),
    ],
)
async def test_generate_types_real_server(
    shared_client, input, operation, param, expected
):
    args = {"input": input, "operation": operation}
    if param is not None:
        args["param"] = param
    result = await shared_client.call_tool("generate", args)
    assert json.loads(result[0].text)["value"] == expected


@pytest.mark.asyncio
async def test_get_value_real_server(shared_client):
    obj = {"a": {"b": 1}}
    path = "a.b"
    result = await shared_client.call_tool("get_value", {"obj": obj, "path": path})
    assert json.loads(result[0].text)["value"] == 1


@pytest.mark.asyncio
async def test_set_value_real_server(shared_client):
    obj = {"a": {}}
    path = "a.b"
    value = 42
    result = await shared_client.call_tool(
        "set_value", {"obj": obj, "path": path, "value": value}
    )
    assert json.loads(result[0].text)["value"] == {"a": {"b": 42}}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items,mutation,param,expected",
    [
        ([1, None, 2], "compact", None, [1, 2]),
        ([[1, [2, 3]], 4], "flatten_deep", None, [1, 2, 3, 4]),
        ([{"id": 1}, {"id": 1}, {"id": 2}], "uniq_by", "id", [{"id": 1}, {"id": 2}]),
    ],
)
async def test_mutate_list_types_real_server(
    shared_client, items, mutation, param, expected
):
    args = {"items": items, "mutation": mutation}
    if param is not None:
        args["param"] = param
    result = await shared_client.call_tool("mutate_list", args)
    assert json.loads(result[0].text)["value"] == expected


@pytest.mark.asyncio
async def test_chain_real_server(shared_client):
    chain_payload = {
        "input": "abc",
        "tool_calls": [{"tool": "mutate_string", "params": {"mutation": "upper_case"}}],
    }
    result = await shared_client.call_tool("chain", chain_payload)
    assert json.loads(result[0].text)["value"] == "ABC"


@pytest.mark.asyncio
async def test_process_list_real_server(shared_client):
    items = [{"type": "a"}, {"type": "b"}, {"type": "a"}]
    result = await shared_client.call_tool(
        "process_list", {"items": items, "operation": "count_by", "key": "type"}
    )
    assert json.loads(result[0].text)["value"] == {"a": 2, "b": 1}


@pytest.mark.asyncio
async def test_process_dict_real_server(shared_client):
    obj = {"a": "x", "b": "y"}
    result = await shared_client.call_tool(
        "process_dict", {"obj": obj, "operation": "invert"}
    )
    assert json.loads(result[0].text)["value"] == {"x": "a", "y": "b"}


@pytest.mark.asyncio
async def test_merge_real_server(shared_client):
    dicts = [{"a": 1}, {"b": 2}]
    result = await shared_client.call_tool("merge", {"dicts": dicts})
    assert json.loads(result[0].text)["value"] == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_chain_single_step_real_server(shared_client):
    chain_payload = {
        "input": "abc",
        "tool_calls": [{"tool": "mutate_string", "params": {"mutation": "upper_case"}}],
    }
    result = await shared_client.call_tool("chain", chain_payload)
    assert json.loads(result[0].text)["value"] == "ABC"
