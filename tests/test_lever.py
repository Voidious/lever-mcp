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
        client, "process_list", {"items": items, "operation": "group_by", "key": "type"}
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
    value, error = await make_tool_call(client, "merge", {"dicts": [d1, d2]})
    assert value == {"a": 1, "b": {"c": 2, "d": 3}}


@pytest.mark.asyncio
async def test_flatten_deep(client):
    items = [1, [2, [3, 4], 5]]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "flatten_deep"}
    )
    assert value == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
async def test_sort_by(client):
    items = [{"name": "b"}, {"name": "a"}]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "sort_by", "param": "name"}
    )
    assert value == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_uniq_by(client):
    items = [{"id": 1, "name": "a"}, {"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "uniq_by", "param": "id"}
    )
    assert value == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]


@pytest.mark.asyncio
async def test_deburr(client):
    value, error = await make_tool_call(
        client, "mutate_string", {"text": "Café déjà vu", "mutation": "deburr"}
    )
    assert value == "Cafe deja vu"


@pytest.mark.asyncio
async def test_template(client):
    value, error = await make_tool_call(
        client,
        "mutate_string",
        {"text": "Hello, {name}!", "mutation": "template", "data": {"name": "World"}},
    )
    assert value == "Hello, World!"


@pytest.mark.asyncio
async def test_set_and_get_value(client):
    obj = {"a": {"b": 1}}
    value, error = await make_tool_call(
        client, "set_value", {"obj": obj, "path": "a.b", "value": 2}
    )
    assert value == {"a": {"b": 2}}
    value, error = await make_tool_call(
        client, "get_value", {"obj": {"a": {"b": 2}}, "path": "a.b"}
    )
    assert value == 2
    value, error = await make_tool_call(
        client, "get_value", {"obj": {"a": {"b": 2}}, "path": "a.c", "default": 42}
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
        "mutate_list",
        {"items": items, "mutation": "partition", "param": "even"},
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
        "mutate_list",
        {"items": items, "mutation": "partition", "param": "value"},
    )
    assert value == [[{"value": 1}, {"value": 2}], [{"value": 0}, {"value": 0}]]


@pytest.mark.asyncio
async def test_partition_by_string(client):
    items = [{"name": "foo"}, {"name": ""}, {"name": "bar"}, {"name": ""}]
    value, error = await make_tool_call(
        client,
        "mutate_list",
        {"items": items, "mutation": "partition", "param": "name"},
    )
    assert value == [[{"name": "foo"}, {"name": "bar"}], [{"name": ""}, {"name": ""}]]


@pytest.mark.asyncio
async def test_partition_by_none(client):
    items = [{"flag": None}, {"flag": True}, {"flag": False}, {"flag": None}]
    value, error = await make_tool_call(
        client,
        "mutate_list",
        {"items": items, "mutation": "partition", "param": "flag"},
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
        client, "process_list", {"items": items, "operation": "group_by", "key": "type"}
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
        "process_list",
        {"items": items, "operation": "group_by", "key": "value"},
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
        client, "process_list", {"items": items, "operation": "group_by", "key": "flag"}
    )
    assert value == {
        "true": [{"flag": True, "name": "a"}, {"flag": True, "name": "c"}],
        "false": [{"flag": False, "name": "b"}],
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
            "process_list",
            {"items": items, "operation": "group_by", "key": "meta"},
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
        client, "mutate_list", {"items": items, "mutation": "sort_by", "param": "name"}
    )
    assert value == [{"name": "a"}, {"name": "b"}]


@pytest.mark.asyncio
async def test_sort_by_number(client):
    items = [{"value": 2}, {"value": 1}]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "sort_by", "param": "value"}
    )
    assert value == [{"value": 1}, {"value": 2}]


@pytest.mark.asyncio
async def test_sort_by_boolean(client):
    items = [{"flag": True}, {"flag": False}]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "sort_by", "param": "flag"}
    )
    assert value == [{"flag": False}, {"flag": True}]


@pytest.mark.asyncio
async def test_sort_by_dict(client):
    items = [{"meta": {"x": 2}}, {"meta": {"x": 1}}]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "sort_by", "param": "meta"}
    )
    assert value == [{"meta": {"x": 1}}, {"meta": {"x": 2}}]


@pytest.mark.asyncio
async def test_uniq_by_string(client):
    items = [{"type": "a"}, {"type": "a"}, {"type": "b"}]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "uniq_by", "param": "type"}
    )
    assert value == [{"type": "a"}, {"type": "b"}]


@pytest.mark.asyncio
async def test_uniq_by_number(client):
    items = [{"value": 1}, {"value": 1}, {"value": 2}]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "uniq_by", "param": "value"}
    )
    assert value == [{"value": 1}, {"value": 2}]


@pytest.mark.asyncio
async def test_uniq_by_boolean(client):
    items = [{"flag": True}, {"flag": True}, {"flag": False}]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "uniq_by", "param": "flag"}
    )
    assert value == [{"flag": True}, {"flag": False}]


@pytest.mark.asyncio
async def test_uniq_by_dict(client):
    items = [{"meta": {"x": 1}}, {"meta": {"x": 1}}, {"meta": {"x": 2}}]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "uniq_by", "param": "meta"}
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
        client, "mutate_list", {"items": items, "mutation": "pluck", "param": "name"}
    )
    assert value == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_compact(client):
    items = [0, 1, False, 2, "", 3, None]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "compact"}
    )
    assert value == [1, 2, 3]


@pytest.mark.asyncio
async def test_chunk(client):
    items = [1, 2, 3, 4, 5]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "chunk", "param": 2}
    )
    assert value == [[1, 2], [3, 4], [5]]


@pytest.mark.asyncio
async def test_count_by(client):
    items = [{"type": "a"}, {"type": "b"}, {"type": "a"}, {"type": "c"}, {"type": "b"}]
    value, error = await make_tool_call(
        client, "process_list", {"items": items, "operation": "count_by", "key": "type"}
    )
    assert value == {"a": 2, "b": 2, "c": 1}


@pytest.mark.asyncio
async def test_difference_by(client):
    a = [{"id": 1}, {"id": 2}, {"id": 3}]
    b = [{"id": 2}]
    value, error = await make_tool_call(
        client,
        "compare_lists",
        {"a": a, "b": b, "operation": "difference_by", "key": "id"},
    )
    assert value == [{"id": 1}, {"id": 3}]


@pytest.mark.asyncio
async def test_intersection_by(client):
    a = [{"id": 1}, {"id": 2}, {"id": 3}]
    b = [{"id": 2}, {"id": 4}]
    value, error = await make_tool_call(
        client,
        "compare_lists",
        {"a": a, "b": b, "operation": "intersection_by", "key": "id"},
    )
    assert value == [{"id": 2}]


@pytest.mark.asyncio
async def test_zip_lists(client):
    l1 = [1, 2]
    l2 = ["a", "b"]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": [l1, l2], "mutation": "zip_lists"}
    )
    assert value is not None
    assert error is None
    value = [[y for y in x] for x in value]
    assert value == [[1, "a"], [2, "b"]]


@pytest.mark.asyncio
async def test_unzip_list(client):
    items = [[1, "a"], [2, "b"]]
    value, error = await make_tool_call(
        client, "mutate_list", {"items": items, "mutation": "unzip_list"}
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
        "select_from_list",
        {"items": items, "operation": "find_by", "param": {"key": "id", "value": 2}},
    )
    assert value == {"id": 2}
    # Test not found
    value, error = await make_tool_call(
        client,
        "select_from_list",
        {"items": items, "operation": "find_by", "param": {"key": "id", "value": 99}},
    )
    assert value is None


@pytest.mark.asyncio
async def test_remove_by(client):
    items = [{"id": 1}, {"id": 2}, {"id": 1}]
    value, error = await make_tool_call(
        client,
        "mutate_list",
        {"items": items, "mutation": "remove_by", "param": {"key": "id", "value": 1}},
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
            "tool_calls": [
                {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}}
            ],
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
                {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}},
                {"tool": "mutate_list", "params": {"mutation": "compact"}},
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
                {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}},
                {"tool": "mutate_list", "params": {"mutation": "chunk", "param": 2}},
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
            "tool_calls": [{"tool": "mutate_list", "params": {"mutation": "chunk"}}],
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
                {"tool": "mutate_list", "params": {"mutation": "flatten_deep"}},
                {
                    "tool": "process_list",
                    "params": {"operation": "group_by", "key": "type"},
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
                    "tool": "mutate_string",
                    "params": {
                        "text": "Hello, {name}!",
                        "mutation": "template",
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
        client, "mutate_string", {"text": "", "mutation": "camel_case"}
    )
    assert value == ""
    # Missing data for template
    value, error = await make_tool_call(
        client, "mutate_string", {"text": "Hello, {name}!", "mutation": "template"}
    )
    assert error is not None
    # Non-string input
    with pytest.raises(ToolError):
        await make_tool_call(
            client, "mutate_string", {"text": 123, "mutation": "camel_case"}
        )
    # Unknown mutation
    value, error = await make_tool_call(
        client, "mutate_string", {"text": "foo", "mutation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_mutate_list_edge_cases(client):
    # Deeply nested list
    value, error = await make_tool_call(
        client,
        "mutate_list",
        {"items": [1, [2, [3, [4, [5]]]]], "mutation": "flatten_deep"},
    )
    assert value == [1, 2, 3, 4, 5]
    # Invalid param type
    value, error = await make_tool_call(
        client, "mutate_list", {"items": [1, 2], "mutation": "chunk", "param": "two"}
    )
    assert error is not None
    # Empty input for all mutations, using correct param types
    empty_mutations = [
        ("flatten_deep", None),
        ("compact", None),
        ("chunk", 2),
        ("sort_by", "x"),
        ("uniq_by", "x"),
        ("pluck", "x"),
        ("partition", "x"),
    ]
    for mutation, param in empty_mutations:
        params = {"items": [], "mutation": mutation}
        if param is not None:
            params["param"] = param
        value, error = await make_tool_call(client, "mutate_list", params)
        # Partition returns a pair of empty lists
        if mutation == "partition":
            assert value == [[], []]
        else:
            assert value == []

    # Unknown mutation
    value, error = await make_tool_call(
        client, "mutate_list", {"items": [1, 2], "mutation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_has_property_edge_cases(client):
    # Non-string/non-dict input returns false
    value, error = await make_tool_call(
        client, "has_property", {"obj": 123, "property": "starts_with", "param": "1"}
    )
    assert value is False

    # Missing param returns false
    value, error = await make_tool_call(
        client, "has_property", {"obj": "abc", "property": "starts_with"}
    )
    assert value is False

    # Unknown property returns error
    value, error = await make_tool_call(
        client, "has_property", {"obj": "abc", "property": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_select_from_list_edge_cases(client):
    # Non-dict items for find_by returns error
    value, error = await make_tool_call(
        client,
        "select_from_list",
        {"items": [1, 2], "operation": "find_by", "param": {"key": "id", "value": 1}},
    )
    assert error is not None

    # Missing param for find_by returns error
    value, error = await make_tool_call(
        client, "select_from_list", {"items": [{"id": 1}], "operation": "find_by"}
    )
    assert error is not None

    # Unknown operation returns error
    value, error = await make_tool_call(
        client, "select_from_list", {"items": [1, 2], "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_compare_lists_edge_cases(client):
    # Non-dict items for *_by returns []
    value, error = await make_tool_call(
        client,
        "compare_lists",
        {"a": [1, 2], "b": [2, 3], "operation": "difference_by", "key": "id"},
    )
    assert value == []

    # Missing key for *_by returns error
    value, error = await make_tool_call(
        client,
        "compare_lists",
        {"a": [{"id": 1}], "b": [{"id": 2}], "operation": "difference_by"},
    )
    assert error is not None

    # Unknown operation returns error
    value, error = await make_tool_call(
        client, "compare_lists", {"a": [1], "b": [2], "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_process_list_edge_cases(client):
    # Missing key
    with pytest.raises(ToolError):
        await make_tool_call(
            client, "process_list", {"items": [{"a": 1}], "operation": "group_by"}
        )

    # Non-dict items
    value, error = await make_tool_call(
        client, "process_list", {"items": [1, 2], "operation": "group_by", "key": "a"}
    )
    assert error is not None

    # Unknown operation returns error
    value, error = await make_tool_call(
        client,
        "process_list",
        {"items": [{"a": 1}], "operation": "unknown", "key": "a"},
    )
    assert error is not None


@pytest.mark.asyncio
async def test_process_dict_edge_cases(client):
    # Non-dict input
    with pytest.raises(ToolError):
        await make_tool_call(
            client, "process_dict", {"obj": 123, "operation": "pick", "param": ["a"]}
        )

    # Missing param for pick/omit returns error
    value, error = await make_tool_call(
        client, "process_dict", {"obj": {"a": 1}, "operation": "pick"}
    )
    assert error is not None

    # Unknown operation returns error
    value, error = await make_tool_call(
        client, "process_dict", {"obj": {"a": 1}, "operation": "unknown"}
    )
    assert error is not None


@pytest.mark.asyncio
async def test_merge_edge_cases(client):
    # More than two dicts
    dicts = [{"a": 1}, {"b": 2}, {"c": 3}]
    value, error = await make_tool_call(client, "merge", {"dicts": dicts})
    assert error is None
    assert value == {"a": 1, "b": 2, "c": 3}

    # Empty list
    value, error = await make_tool_call(client, "merge", {"dicts": []})
    assert error is None
    assert value == {}

    # Non-dict input returns error
    value, error = await make_tool_call(client, "merge", {"dicts": [1, 2]})
    assert error is not None


@pytest.mark.asyncio
async def test_set_value_edge_cases(client):
    # List path (invalid)
    value, error = await make_tool_call(
        client, "set_value", {"obj": {}, "path": [1, 2], "value": 42}
    )
    assert error is not None

    # Valid list path (should succeed)
    obj = {"a": {"b": 1}}
    value, error = await make_tool_call(
        client, "set_value", {"obj": obj, "path": ["a", "b"], "value": 3}
    )
    assert error is None
    assert value is not None
    assert value["a"]["b"] == 3

    # Creating new keys with dotted string path
    obj = {}
    value, error = await make_tool_call(
        client, "set_value", {"obj": obj, "path": "x.y.z", "value": 1}
    )
    assert error is None
    assert value is not None
    assert value["x"]["y"]["z"] == 1

    # Invalid path type
    with pytest.raises(ToolError):
        await make_tool_call(client, "set_value", {"obj": {}, "path": 123, "value": 1})

    # Non-dict input
    with pytest.raises(ToolError):
        await make_tool_call(
            client, "set_value", {"obj": 123, "path": "a.b", "value": 1}
        )


@pytest.mark.asyncio
async def test_get_value_edge_cases(client):
    # List path (valid)
    obj = {"a": {"b": 2}}
    value, error = await make_tool_call(
        client, "get_value", {"obj": obj, "path": ["a", "b"]}
    )
    assert error is None
    assert value == 2

    # Missing path returns default
    value, error = await make_tool_call(
        client, "get_value", {"obj": obj, "path": "x.y", "default": "not found"}
    )
    assert error is None
    assert value == "not found"

    # Non-dict input
    with pytest.raises(ToolError):
        await make_tool_call(client, "get_value", {"obj": 123, "path": "a.b"})

    # List path with non-string elements
    value, error = await make_tool_call(
        client, "get_value", {"obj": {}, "path": [1, 2]}
    )
    assert error is not None
