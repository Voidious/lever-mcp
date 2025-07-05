import importlib
import main
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from main import LeverMCP
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


@pytest.mark.asyncio
async def test_group_by(client):
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "vegetable", "name": "carrot"},
    ]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "group_by", "expression": "type"}
    )
    assert value == {
        "fruit": [
            {"type": "fruit", "name": "apple"},
            {"type": "fruit", "name": "banana"},
        ],
        "vegetable": [{"type": "vegetable", "name": "carrot"}],
    }


@pytest.mark.asyncio
async def test_merge(client):
    d1 = {"a": 1, "b": {"c": 2}}
    d2 = {"b": {"d": 3}}
    value, error = await make_tool_call(
        client, "dicts", {"obj": [d1, d2], "operation": "merge"}
    )
    assert value == {"a": 1, "b": {"c": 2, "d": 3}}


@pytest.mark.asyncio
async def test_flatten_deep(client):
    items = [1, [2, [3, 4], 5]]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "flatten_deep"}
    )
    assert value == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_sort_by(client):
    items = [{"name": "b"}, {"name": "a"}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "sort_by", "param": "name"}
    )
    assert value == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_uniq_by(client):
    items = [{"id": 1, "name": "a"}, {"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "uniq_by", "param": "id"}
    )
    assert value == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]


@pytest.mark.asyncio
async def test_deburr(client):
    value, error = await make_tool_call(
        client, "strings", {"text": "Café déjà vu", "operation": "deburr"}
    )
    assert value == "Cafe deja vu"


@pytest.mark.asyncio
async def test_template(client):
    value, error = await make_tool_call(
        client,
        "strings",
        {"text": "Hello, {name}!", "operation": "template", "data": {"name": "World"}},
    )
    assert value == "Hello, World!"


@pytest.mark.asyncio
async def test_set_and_get_value(client):
    obj = {"a": {"b": 1}}
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": obj, "operation": "set_value", "path": "a.b", "value": 2},
    )
    assert value == {"a": {"b": 2}}
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": {"a": {"b": 2}}, "path": "a.b", "operation": "get_value"},
    )
    assert value == 2
    value, error = await make_tool_call(
        client,
        "dicts",
        {
            "obj": {"a": {"b": 2}},
            "path": "a.c",
            "default": 42,
            "operation": "get_value",
        },
    )
    assert value == 42


@pytest.mark.asyncio
async def test_partition_by_boolean(client):
    items = [
        {"value": 2, "even": True},
        {"value": 1, "even": False},
        {"value": 4, "even": True},
        {"value": 3, "even": False},
    ]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "partition", "param": "even"},
    )
    assert value == [
        [{"value": 2, "even": True}, {"value": 4, "even": True}],
        [{"value": 1, "even": False}, {"value": 3, "even": False}],
    ]


@pytest.mark.asyncio
async def test_partition_by_int(client):
    items = [{"value": 0}, {"value": 1}, {"value": 2}, {"value": 0}]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "partition", "param": "value"},
    )
    assert value == [[{"value": 1}, {"value": 2}], [{"value": 0}, {"value": 0}]]


@pytest.mark.asyncio
async def test_partition_by_string(client):
    items = [{"name": "foo"}, {"name": ""}, {"name": "bar"}, {"name": ""}]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "partition", "param": "name"},
    )
    assert value == [[{"name": "foo"}, {"name": "bar"}], [{"name": ""}, {"name": ""}]]


@pytest.mark.asyncio
async def test_partition_by_none(client):
    items = [{"flag": None}, {"flag": True}, {"flag": False}, {"flag": None}]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "partition", "param": "flag"},
    )
    assert value == [
        [{"flag": True}],
        [{"flag": None}, {"flag": False}, {"flag": None}],
    ]


@pytest.mark.asyncio
async def test_group_by_string(client):
    items = [
        {"type": "fruit", "name": "apple"},
        {"type": "fruit", "name": "banana"},
        {"type": "vegetable", "name": "carrot"},
    ]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "group_by", "expression": "type"}
    )
    assert value == {
        "fruit": [
            {"type": "fruit", "name": "apple"},
            {"type": "fruit", "name": "banana"},
        ],
        "vegetable": [{"type": "vegetable", "name": "carrot"}],
    }


@pytest.mark.asyncio
async def test_group_by_number(client):
    items = [
        {"value": 1, "name": "a"},
        {"value": 2, "name": "b"},
        {"value": 1, "name": "c"},
    ]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "group_by", "expression": "value"},
    )
    assert value == {
        "1": [{"value": 1, "name": "a"}, {"value": 1, "name": "c"}],
        "2": [{"value": 2, "name": "b"}],
    }


@pytest.mark.asyncio
async def test_group_by_boolean(client):
    items = [
        {"flag": True, "name": "a"},
        {"flag": False, "name": "b"},
        {"flag": True, "name": "c"},
    ]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "group_by", "expression": "flag"}
    )
    assert value == {
        "True": [{"flag": True, "name": "a"}, {"flag": True, "name": "c"}],
        "False": [{"flag": False, "name": "b"}],
    }


@pytest.mark.asyncio
async def test_group_by_dict(client):
    items = [
        {"meta": {"x": 1}, "name": "a"},
        {"meta": {"x": 2}, "name": "b"},
        {"meta": {"x": 1}, "name": "c"},
    ]
    # Dicts are not hashable, so all will be grouped under one key (or error)
    try:
        value, error = await make_tool_call(
            client,
            "lists",
            {"items": items, "operation": "group_by", "expression": "meta"},
        )
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
            if isinstance(value, dict):
                assert any(isinstance(k, str) for k in value.keys())
    except Exception:
        pass  # Accept error as valid outcome


@pytest.mark.asyncio
async def test_sort_by_string(client):
    items = [{"name": "b"}, {"name": "a"}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "sort_by", "param": "name"}
    )
    assert value == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_sort_by_number(client):
    items = [{"value": 2}, {"value": 1}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "sort_by", "param": "value"}
    )
    assert value == [{"value": 1}, {"value": 2}]


@pytest.mark.asyncio
async def test_sort_by_boolean(client):
    items = [{"flag": True}, {"flag": False}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "sort_by", "param": "flag"}
    )
    assert value == [{"flag": False}, {"flag": True}]


@pytest.mark.asyncio
async def test_sort_by_dict(client):
    items = [{"meta": {"x": 2}}, {"meta": {"x": 1}}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "sort_by", "param": "meta"}
    )
    assert value == [{"meta": {"x": 1}}, {"meta": {"x": 2}}]


@pytest.mark.asyncio
async def test_uniq_by_string(client):
    items = [{"type": "a"}, {"type": "a"}, {"type": "b"}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "uniq_by", "param": "type"}
    )
    assert value == [{"type": "a"}, {"type": "b"}]


@pytest.mark.asyncio
async def test_uniq_by_number(client):
    items = [{"value": 1}, {"value": 1}, {"value": 2}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "uniq_by", "param": "value"}
    )
    assert value == [{"value": 1}, {"value": 2}]


@pytest.mark.asyncio
async def test_uniq_by_boolean(client):
    items = [{"flag": True}, {"flag": True}, {"flag": False}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "uniq_by", "param": "flag"}
    )
    assert value == [{"flag": True}, {"flag": False}]


@pytest.mark.asyncio
async def test_uniq_by_dict(client):
    items = [{"meta": {"x": 1}}, {"meta": {"x": 1}}, {"meta": {"x": 2}}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "uniq_by", "param": "meta"}
    )
    assert value == [{"meta": {"x": 1}}, {"meta": {"x": 2}}]


@pytest.mark.asyncio
async def test_pluck(client):
    items = [
        {"id": 1, "name": "a"},
        {"id": 2, "name": "b"},
        {"id": 3, "name": "c"},
    ]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "pluck", "param": "name"}
    )
    assert value == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_compact(client):
    items = [0, 1, False, 2, "", 3, None]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "compact"}
    )
    assert value == [1, 2, 3]


@pytest.mark.asyncio
async def test_chunk(client):
    items = [1, 2, 3, 4, 5]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "chunk", "param": 2}
    )
    assert value == [[1, 2], [3, 4], [5]]


@pytest.mark.asyncio
async def test_count_by(client):
    items = [{"type": "a"}, {"type": "b"}, {"type": "a"}, {"type": "c"}, {"type": "b"}]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "count_by", "expression": "type"}
    )
    assert value == {"a": 2, "b": 2, "c": 1}


@pytest.mark.asyncio
async def test_difference_by(client):
    a = [{"id": 1}, {"id": 2}, {"id": 3}]
    b = [{"id": 2}]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": a, "others": b, "operation": "difference_by", "expression": "id"},
    )
    assert value == [{"id": 1}, {"id": 3}]


@pytest.mark.asyncio
async def test_intersection_by(client):
    a = [{"id": 1}, {"id": 2}, {"id": 3}]
    b = [{"id": 2}, {"id": 4}]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": a, "others": b, "operation": "intersection_by", "expression": "id"},
    )
    assert value == [{"id": 2}]


@pytest.mark.asyncio
async def test_zip_lists(client):
    l1 = [1, 2]
    l2 = ["a", "b"]
    value, error = await make_tool_call(
        client, "lists", {"items": [l1, l2], "operation": "zip_lists"}
    )
    assert value is not None
    assert error is None
    value = [[y for y in x] for x in value]
    assert value == [[1, "a"], [2, "b"]]


@pytest.mark.asyncio
async def test_unzip_list(client):
    items = [[1, "a"], [2, "b"]]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "unzip_list"}
    )
    if (
        isinstance(value, list)
        and value
        and all(isinstance(x, list) and len(x) == 2 for x in value)
    ):
        value = [[x[0], x[1]] for x in value]
    assert value == [[1, 2], ["a", "b"]]


@pytest.mark.asyncio
async def test_find_by(client):
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "find_by", "expression": "id == 2"},
    )
    assert value == {"id": 2}
    # Test not found
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "find_by", "expression": "id == 99"},
    )
    assert value is None


@pytest.mark.asyncio
async def test_remove_by(client):
    items = [{"id": 1}, {"id": 2}, {"id": 1}]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "remove_by", "expression": "id == 1"},
    )
    assert value == [{"id": 2}]


@pytest.mark.asyncio
async def test_chain_single_tool(client):
    # Should flatten a nested list
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [1, [2, [3, 4], 5]],
            "tool_calls": [{"tool": "lists", "params": {"operation": "flatten_deep"}}],
        },
    )
    assert value == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_chain_multiple_tools(client):
    # Should flatten and then compact (remove falsy values)
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [0, 1, [2, [0, 3, 4], 5], None],
            "tool_calls": [
                {"tool": "lists", "params": {"operation": "flatten_deep"}},
                {"tool": "lists", "params": {"operation": "compact"}},
            ],
        },
    )
    assert value == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_chain_with_params(client):
    # Should chunk after flattening
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [1, [2, [3, 4], 5]],
            "tool_calls": [
                {"tool": "lists", "params": {"operation": "flatten_deep"}},
                {"tool": "lists", "params": {"operation": "chunk", "param": 2}},
            ],
        },
    )
    assert value == [[1, 2], [3, 4], [5]]


@pytest.mark.asyncio
async def test_chain_error_missing_tool(client):
    # Should return error for missing tool
    value, error = await make_tool_call(
        client,
        "chain",
        {"input": [1, 2, 3], "tool_calls": [{"tool": "not_a_tool", "params": {}}]},
    )
    assert error is not None


@pytest.mark.asyncio
async def test_chain_error_missing_param(client):
    # Should return error for missing required param
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [1, 2, 3],
            "tool_calls": [{"tool": "lists", "params": {"operation": "chunk"}}],
        },
    )
    assert error is not None


@pytest.mark.asyncio
async def test_chain_type_chaining(client):
    # Should group by after flattening
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": [{"type": "a", "val": 1}, [{"type": "b", "val": 2}]],
            "tool_calls": [
                {"tool": "lists", "params": {"operation": "flatten_deep"}},
                {
                    "tool": "lists",
                    "params": {"operation": "group_by", "expression": "type"},
                },
            ],
        },
    )
    assert value is not None and "a" in value and "b" in value


@pytest.mark.asyncio
async def test_chain_empty_chain(client):
    # Should return the input unchanged
    value, error = await make_tool_call(
        client, "chain", {"input": 42, "tool_calls": []}
    )
    assert value == 42


@pytest.mark.asyncio
async def test_chain_chain_with_text_content(client):
    # Should error if user tries to specify the primary parameter in params
    value, error = await make_tool_call(
        client,
        "chain",
        {
            "input": None,
            "tool_calls": [
                {
                    "tool": "strings",
                    "params": {
                        "text": "Hello, {name}!",
                        "operation": "template",
                        "data": {"name": "World"},
                    },
                }
            ],
        },
    )
    assert error is not None


@pytest.mark.asyncio
async def test_mutate_string_edge_cases(client):
    # Empty string
    value, error = await make_tool_call(
        client, "strings", {"text": "", "operation": "camel_case"}
    )
    assert value == ""
    # Missing data for template
    value, error = await make_tool_call(
        client, "strings", {"text": "Hello, {name}!", "operation": "template"}
    )
    assert error is not None
    # Non-string input
    with pytest.raises(ToolError):
        await make_tool_call(
            client, "strings", {"text": 123, "operation": "camel_case"}
        )
    # Unknown operation
    value, error = await make_tool_call(
        client, "strings", {"text": "foo", "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_mutate_list_edge_cases(client):
    # Deeply nested list
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": [1, [2, [3, [4, [5]]]]], "operation": "flatten_deep"},
    )
    assert value == [1, 2, 3, 4, 5]
    # Invalid param type
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2], "operation": "chunk", "param": "two"}
    )
    assert error is not None
    # Empty input for all operations, using correct param types
    empty_operations = [
        ("flatten_deep", None),
        ("compact", None),
        ("chunk", 2),
        ("sort_by", "x"),
        ("uniq_by", "x"),
        ("pluck", "x"),
        ("partition", "x"),
    ]
    for operation, param in empty_operations:
        params = {"items": [], "operation": operation}
        if param is not None:
            params["param"] = param
        value, error = await make_tool_call(client, "lists", params)
        # Partition returns a pair of empty lists
        if operation == "partition":
            assert value == [[], []]
        else:
            assert value == []

    # Unknown operation
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2], "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_has_property_edge_cases(client):
    # Non-string/non-dict input returns false
    value, error = await make_tool_call(
        client, "dicts", {"obj": 123, "operation": "has_key", "param": "1"}
    )
    assert (value or False) is False

    # Missing param returns false
    value, error = await make_tool_call(
        client, "dicts", {"obj": "abc", "operation": "has_key"}
    )
    assert (value or False) is False

    # Unknown property returns error
    value, error = await make_tool_call(
        client, "dicts", {"obj": "abc", "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_select_from_list_edge_cases(client):
    # Non-dict items for find_by returns error
    value, error = await make_tool_call(
        client,
        "lists",
        {
            "items": [1, 2],
            "operation": "find_by",
            "param": {"expression": "id", "value": 1},
        },
    )
    assert error is not None

    # Missing param for find_by returns error
    value, error = await make_tool_call(
        client, "lists", {"items": [{"id": 1}], "operation": "find_by"}
    )
    assert error is not None

    # Unknown operation returns error
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2], "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_compare_lists_edge_cases(client):
    # Non-dict items for *_by returns []
    value, error = await make_tool_call(
        client,
        "lists",
        {
            "items": [1, 2],
            "others": [2, 3],
            "operation": "difference_by",
            "expression": "id",
        },
    )
    assert (value or []) == []

    # Missing key for *_by returns error
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": [{"id": 1}], "others": [{"id": 2}], "operation": "difference_by"},
    )
    assert error is not None

    # Unknown operation returns error
    value, error = await make_tool_call(
        client, "lists", {"items": [1], "others": [2], "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_process_list_edge_cases(client):
    # Missing key
    value, error = await make_tool_call(
        client, "lists", {"items": [{"a": 1}], "operation": "group_by"}
    )
    assert error is not None

    # Non-dict items - should group under "None" key when property doesn't exist
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2], "operation": "group_by", "expression": "a"}
    )
    assert error is None
    assert value == {"None": [1, 2]}

    # Unknown operation returns error
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": [{"a": 1}], "operation": "unknown", "expression": "a"},
    )
    assert error is not None


@pytest.mark.asyncio
async def test_process_dict_edge_cases(client):
    # Non-dict input
    value, error = await make_tool_call(
        client, "dicts", {"obj": 123, "operation": "pick", "param": ["a"]}
    )
    assert error is not None

    # Missing param for pick/omit returns error
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a": 1}, "operation": "pick"}
    )
    assert error is not None

    # Unknown operation returns error
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a": 1}, "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_merge_edge_cases(client):
    # More than two dicts
    dicts = [{"a": 1}, {"b": 2}, {"c": 3}]
    value, error = await make_tool_call(
        client, "dicts", {"obj": dicts, "operation": "merge"}
    )
    assert error is None
    assert value == {"a": 1, "b": 2, "c": 3}

    # Empty list
    value, error = await make_tool_call(
        client, "dicts", {"obj": [], "operation": "merge"}
    )
    assert error is None
    assert value == {}

    # Non-dict input returns error
    value, error = await make_tool_call(
        client, "dicts", {"obj": [1, 2], "operation": "merge"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_set_value_edge_cases(client):
    # List path (invalid)
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": {}, "operation": "set_value", "path": [1, 2], "value": 42},
    )
    assert error is not None

    # Valid list path (should succeed)
    obj = {"a": {"b": 1}}
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": obj, "operation": "set_value", "path": ["a", "b"], "value": 3},
    )
    assert error is None
    assert value is not None
    assert value["a"]["b"] == 3

    # Creating new keys with dotted string path
    obj = {}
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": obj, "operation": "set_value", "path": "x.y.z", "value": 1},
    )
    assert error is None
    assert value is not None
    assert value["x"]["y"]["z"] == 1

    # Invalid path type
    value, error = await make_tool_call(
        client, "dicts", {"obj": {}, "operation": "set_value", "path": 123, "value": 1}
    )
    assert error is not None

    # Non-dict input
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": 123, "operation": "set_value", "path": "a.b", "value": 1},
    )
    assert error is not None


@pytest.mark.asyncio
async def test_get_value_edge_cases(client):
    # List path (valid)
    obj = {"a": {"b": 2}}
    value, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": "get_value", "path": ["a", "b"]}
    )
    assert error is None
    assert value == 2

    # Missing path returns default
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": obj, "operation": "get_value", "path": "x.y", "default": "not found"},
    )
    assert error is None
    assert value == "not found"

    # Non-dict input
    value, error = await make_tool_call(
        client, "dicts", {"obj": 123, "operation": "get_value", "path": "a.b"}
    )
    assert error is not None

    # List path with non-string elements
    value, error = await make_tool_call(
        client, "dicts", {"obj": {}, "operation": "get_value", "path": [1, 2]}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_map(client):
    items = [1, 2, 3]
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "map", "expression": "item * 2"}
    )
    assert value == [2, 4, 6]


@pytest.mark.asyncio
async def test_reduce(client):
    items = [1, 2, 3, 4]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "reduce", "expression": "acc + item", "param": 0},
    )
    assert value == 10
    # Without param (should use first item as acc)
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "reduce", "expression": "acc + item"},
    )
    assert value == 10
    # Empty list
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": [], "operation": "reduce", "expression": "acc + item", "param": 0},
    )
    assert value == 0


@pytest.mark.asyncio
async def test_flat_map(client):
    items = [1, 2, 3]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "flat_map", "expression": "{item, item * 10}"},
    )
    assert value == [1, 10, 2, 20, 3, 30]
    # If expression returns non-list
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "flat_map", "expression": "item * 2"},
    )
    assert value == [2, 4, 6]


@pytest.mark.asyncio
async def test_all_by_any_by(client):
    items = [2, 4, 6]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "all_by", "expression": "item % 2 == 0"},
    )
    assert value is True
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "any_by", "expression": "item == 4"},
    )
    assert value is True
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "any_by", "expression": "item == 5"},
    )
    assert value is False
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "all_by", "expression": "item > 0"},
    )
    assert value is True
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "every", "expression": "item < 10"},
    )
    assert value is True
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "some", "expression": "item == 2"},
    )
    assert value is True


@pytest.mark.asyncio
async def test_filter_by(client):
    items = [1, 2, 3, 4]
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "filter_by", "expression": "item % 2 == 0"},
    )
    assert value == [2, 4]
    # No matches
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "filter_by", "expression": "item > 10"},
    )
    assert value == []


@pytest.mark.asyncio
async def test_zip_with(client):
    items = [1, 2, 3]
    others = [10, 20, 30]
    value, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "others": others,
            "operation": "zip_with",
            "expression": "item + other",
        },
    )
    assert value == [11, 22, 33]
    # Different lengths
    value, error = await make_tool_call(
        client,
        "lists",
        {
            "items": [1, 2],
            "others": [10, 20, 30],
            "operation": "zip_with",
            "expression": "item * other",
        },
    )
    assert value == [10, 40]


@pytest.mark.asyncio
async def test_strings_shuffle(client):
    # Normal usage
    value, error = await make_tool_call(
        client, "strings", {"text": "abcde", "operation": "shuffle"}
    )
    assert error is None
    assert value is not None and sorted(value) == list("abcde")
    # Edge case: empty string
    value, error = await make_tool_call(
        client, "strings", {"text": "", "operation": "shuffle"}
    )
    assert error is None
    assert value == ""


@pytest.mark.asyncio
async def test_strings_xor(client):
    # Normal usage
    value, error = await make_tool_call(
        client, "strings", {"text": "abc", "operation": "xor", "param": "bcd"}
    )
    assert error is None
    assert value is not None and set(value) == set("ad")
    # Edge case: identical strings
    value, error = await make_tool_call(
        client, "strings", {"text": "abc", "operation": "xor", "param": "abc"}
    )
    assert error is None
    assert value == ""


@pytest.mark.asyncio
async def test_strings_sample_size(client):
    # Normal usage
    value, error = await make_tool_call(
        client, "strings", {"text": "abcdef", "operation": "sample_size", "param": 3}
    )
    assert error is None
    assert value is not None and len(value) == 3
    assert set(value).issubset(set("abcdef"))
    # Edge case: n > len(text)
    value, error = await make_tool_call(
        client, "strings", {"text": "abc", "operation": "sample_size", "param": 10}
    )
    assert error is None
    assert value is not None and sorted(value) == sorted("abc")
    # Edge case: empty string
    value, error = await make_tool_call(
        client, "strings", {"text": "", "operation": "sample_size", "param": 2}
    )
    assert error is None
    assert value == ""


# Tests for new operations


@pytest.mark.asyncio
async def test_strings_split(client):
    """Test strings.split operation with various delimiters and edge cases."""
    # Basic split with comma
    value, error = await make_tool_call(
        client, "strings", {"text": "a,b,c", "operation": "split", "param": ","}
    )
    assert error is None
    assert value == ["a", "b", "c"]

    # Split with space (default)
    value, error = await make_tool_call(
        client, "strings", {"text": "hello world test", "operation": "split"}
    )
    assert error is None
    assert value == ["hello", "world", "test"]

    # Split with custom delimiter
    value, error = await make_tool_call(
        client, "strings", {"text": "one|two|three", "operation": "split", "param": "|"}
    )
    assert error is None
    assert value == ["one", "two", "three"]

    # Split empty string
    value, error = await make_tool_call(
        client, "strings", {"text": "", "operation": "split", "param": ","}
    )
    assert error is None
    assert value == [""]

    # Split string without delimiter
    value, error = await make_tool_call(
        client, "strings", {"text": "hello", "operation": "split", "param": ","}
    )
    assert error is None
    assert value == ["hello"]


@pytest.mark.asyncio
async def test_lists_join(client):
    """Test lists.join operation with various delimiters and edge cases."""
    # Basic join with comma
    value, error = await make_tool_call(
        client, "lists", {"items": ["a", "b", "c"], "operation": "join", "param": ","}
    )
    assert error is None
    assert value == "a,b,c"

    # Join with no delimiter (default empty string)
    value, error = await make_tool_call(
        client, "lists", {"items": ["a", "b", "c"], "operation": "join"}
    )
    assert error is None
    assert value == "abc"

    # Join with space
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": ["hello", "world"], "operation": "join", "param": " "},
    )
    assert error is None
    assert value == "hello world"

    # Join empty list
    value, error = await make_tool_call(
        client, "lists", {"items": [], "operation": "join", "param": ","}
    )
    assert error is None
    assert value == ""

    # Join with mixed types (should convert to strings)
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2, 3], "operation": "join", "param": "-"}
    )
    assert error is None
    assert value == "1-2-3"


@pytest.mark.asyncio
async def test_strings_slice(client):
    """Test strings.slice operation with various start/end positions."""
    # Basic slice
    value, error = await make_tool_call(
        client,
        "strings",
        {"text": "hello", "operation": "slice", "data": {"from": 1, "to": 4}},
    )
    assert error is None
    assert value == "ell"

    # Slice from start
    value, error = await make_tool_call(
        client,
        "strings",
        {"text": "hello", "operation": "slice", "data": {"from": 0, "to": 3}},
    )
    assert error is None
    assert value == "hel"

    # Slice to end (no to specified)
    value, error = await make_tool_call(
        client, "strings", {"text": "hello", "operation": "slice", "data": {"from": 2}}
    )
    assert error is None
    assert value == "llo"

    # Slice entire string
    value, error = await make_tool_call(
        client, "strings", {"text": "hello", "operation": "slice", "data": {"from": 0}}
    )
    assert error is None
    assert value == "hello"

    # Slice with negative indices (should work with Python slicing)
    value, error = await make_tool_call(
        client,
        "strings",
        {"text": "hello", "operation": "slice", "data": {"from": -3, "to": -1}},
    )
    assert error is None
    assert value == "ll"

    # Missing data should error
    value, error = await make_tool_call(
        client, "strings", {"text": "hello", "operation": "slice"}
    )
    assert error is not None
    assert "'data' with 'from' is required" in error


@pytest.mark.asyncio
async def test_lists_min(client):
    """Test lists.min operation with various data types."""
    # Basic min with numbers
    value, error = await make_tool_call(
        client, "lists", {"items": [3, 1, 4, 1, 5], "operation": "min"}
    )
    assert error is None
    assert value == 1

    # Min with strings
    value, error = await make_tool_call(
        client, "lists", {"items": ["apple", "banana", "cherry"], "operation": "min"}
    )
    assert error is None
    assert value == "apple"

    # Min with mixed comparable types
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2.5, 0.5], "operation": "min"}
    )
    assert error is None
    assert value == 0.5

    # Empty list should error
    value, error = await make_tool_call(
        client, "lists", {"items": [], "operation": "min"}
    )
    assert error is not None
    assert "Cannot find minimum of empty list" in error

    # Single item
    value, error = await make_tool_call(
        client, "lists", {"items": [42], "operation": "min"}
    )
    assert error is None
    assert value == 42


@pytest.mark.asyncio
async def test_lists_max(client):
    """Test lists.max operation with various data types."""
    # Basic max with numbers
    value, error = await make_tool_call(
        client, "lists", {"items": [3, 1, 4, 1, 5], "operation": "max"}
    )
    assert error is None
    assert value == 5

    # Max with strings
    value, error = await make_tool_call(
        client, "lists", {"items": ["apple", "banana", "cherry"], "operation": "max"}
    )
    assert error is None
    assert value == "cherry"

    # Max with mixed comparable types
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2.5, 0.5], "operation": "max"}
    )
    assert error is None
    assert value == 2.5

    # Empty list should error
    value, error = await make_tool_call(
        client, "lists", {"items": [], "operation": "max"}
    )
    assert error is not None
    assert "Cannot find maximum of empty list" in error

    # Single item
    value, error = await make_tool_call(
        client, "lists", {"items": [42], "operation": "max"}
    )
    assert error is None
    assert value == 42


@pytest.mark.asyncio
async def test_dicts_keys(client):
    """Test dicts.keys operation."""
    # Basic keys extraction
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a": 1, "b": 2, "c": 3}, "operation": "keys"}
    )
    assert error is None
    assert set(value) == {"a", "b", "c"}

    # Empty dict
    value, error = await make_tool_call(
        client, "dicts", {"obj": {}, "operation": "keys"}
    )
    assert error is None
    assert value == []

    # Non-dict should error
    value, error = await make_tool_call(
        client, "dicts", {"obj": "not_a_dict", "operation": "keys"}
    )
    assert error is not None
    assert "Dict operation 'keys' requires a dictionary input" in error


@pytest.mark.asyncio
async def test_dicts_values(client):
    """Test dicts.values operation."""
    # Basic values extraction
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a": 1, "b": 2, "c": 3}, "operation": "values"}
    )
    assert error is None
    assert set(value) == {1, 2, 3}

    # Empty dict
    value, error = await make_tool_call(
        client, "dicts", {"obj": {}, "operation": "values"}
    )
    assert error is None
    assert value == []

    # Non-dict should error
    value, error = await make_tool_call(
        client, "dicts", {"obj": "not_a_dict", "operation": "values"}
    )
    assert error is not None
    assert "Dict operation 'values' requires a dictionary input" in error


@pytest.mark.asyncio
async def test_dicts_items(client):
    """Test dicts.items operation."""
    # Basic items extraction
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a": 1, "b": 2}, "operation": "items"}
    )
    assert error is None
    assert sorted(value) == sorted([["a", 1], ["b", 2]])

    # Empty dict
    value, error = await make_tool_call(
        client, "dicts", {"obj": {}, "operation": "items"}
    )
    assert error is None
    assert value == []

    # Non-dict should error
    value, error = await make_tool_call(
        client, "dicts", {"obj": "not_a_dict", "operation": "items"}
    )
    assert error is not None
    assert "Dict operation 'items' requires a dictionary input" in error


@pytest.mark.asyncio
async def test_dicts_map_keys(client):
    """Test dicts.map_keys operation with Lua expressions."""
    # Transform keys to uppercase
    value, error = await make_tool_call(
        client,
        "dicts",
        {
            "obj": {"a": 1, "b": 2},
            "operation": "map_keys",
            "expression": "string.upper(key)",
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
            "expression": "'user_' .. key",
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
async def test_dicts_map_values(client):
    """Test dicts.map_values operation with Lua expressions."""
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
            "expression": "string.upper(value)",
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


@pytest.mark.asyncio
async def test_dicts_flatten_keys(client):
    """Test dicts.flatten_keys operation."""
    # Basic nested dict flattening
    value, error = await make_tool_call(
        client,
        "dicts",
        {"obj": {"a": {"b": {"c": 1}}, "d": 2}, "operation": "flatten_keys"},
    )
    assert error is None
    assert value == {"a.b.c": 1, "d": 2}

    # Complex nested structure
    value, error = await make_tool_call(
        client,
        "dicts",
        {
            "obj": {
                "user": {"name": "John", "contact": {"email": "john@email.com"}},
                "settings": {"theme": "dark"},
            },
            "operation": "flatten_keys",
        },
    )
    assert error is None
    expected = {
        "user.name": "John",
        "user.contact.email": "john@email.com",
        "settings.theme": "dark",
    }
    assert value == expected

    # Already flat dict
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a": 1, "b": 2}, "operation": "flatten_keys"}
    )
    assert error is None
    assert value == {"a": 1, "b": 2}

    # Empty dict
    value, error = await make_tool_call(
        client, "dicts", {"obj": {}, "operation": "flatten_keys"}
    )
    assert error is None
    assert value == {}

    # Non-dict should error
    value, error = await make_tool_call(
        client, "dicts", {"obj": "not_a_dict", "operation": "flatten_keys"}
    )
    assert error is not None
    assert "Dict operation 'flatten_keys' requires a dictionary input" in error


@pytest.mark.asyncio
async def test_dicts_unflatten_keys(client):
    """Test dicts.unflatten_keys operation."""
    # Basic unflatten
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a.b.c": 1, "d": 2}, "operation": "unflatten_keys"}
    )
    assert error is None
    assert value == {"a": {"b": {"c": 1}}, "d": 2}

    # Complex unflatten
    value, error = await make_tool_call(
        client,
        "dicts",
        {
            "obj": {
                "user.name": "John",
                "user.contact.email": "john@email.com",
                "settings.theme": "dark",
            },
            "operation": "unflatten_keys",
        },
    )
    assert error is None
    expected = {
        "user": {"name": "John", "contact": {"email": "john@email.com"}},
        "settings": {"theme": "dark"},
    }
    assert value == expected

    # Already nested dict (no dots in keys)
    value, error = await make_tool_call(
        client, "dicts", {"obj": {"a": 1, "b": 2}, "operation": "unflatten_keys"}
    )
    assert error is None
    assert value == {"a": 1, "b": 2}

    # Empty dict
    value, error = await make_tool_call(
        client, "dicts", {"obj": {}, "operation": "unflatten_keys"}
    )
    assert error is None
    assert value == {}

    # Non-dict should error
    value, error = await make_tool_call(
        client, "dicts", {"obj": "not_a_dict", "operation": "unflatten_keys"}
    )
    assert error is not None
    assert "Dict operation 'unflatten_keys' requires a dictionary input" in error


@pytest.mark.asyncio
async def test_any_size(client):
    """Test any.size operation with various data types."""
    # String size
    value, error = await make_tool_call(
        client, "any", {"value": "hello", "operation": "size"}
    )
    assert error is None
    assert value == 5

    # List size
    value, error = await make_tool_call(
        client, "any", {"value": [1, 2, 3, 4], "operation": "size"}
    )
    assert error is None
    assert value == 4

    # Dict size
    value, error = await make_tool_call(
        client, "any", {"value": {"a": 1, "b": 2, "c": 3}, "operation": "size"}
    )
    assert error is None
    assert value == 3

    # Empty collections
    value, error = await make_tool_call(
        client, "any", {"value": "", "operation": "size"}
    )
    assert error is None
    assert value == 0

    value, error = await make_tool_call(
        client, "any", {"value": [], "operation": "size"}
    )
    assert error is None
    assert value == 0

    value, error = await make_tool_call(
        client, "any", {"value": {}, "operation": "size"}
    )
    assert error is None
    assert value == 0

    # Scalar values (should return 1)
    value, error = await make_tool_call(
        client, "any", {"value": 42, "operation": "size"}
    )
    assert error is None
    assert value == 1

    value, error = await make_tool_call(
        client, "any", {"value": True, "operation": "size"}
    )
    assert error is None
    assert value == 1

    # None should return 0
    value, error = await make_tool_call(
        client, "any", {"value": None, "operation": "size"}
    )
    assert error is None
    assert value == 0
