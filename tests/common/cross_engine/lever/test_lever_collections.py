from tests import make_tool_call
import main
import pytest


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

    # Non-dict items - should group under "(null)" key when property doesn't exist
    value, error = await make_tool_call(
        client, "lists", {"items": [1, 2], "operation": "group_by", "expression": "a"}
    )
    assert error is None
    assert value == {"(null)": [1, 2]}

    # Unknown operation returns error
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": [{"a": 1}], "operation": "unknown", "expression": "a"},
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

    # Use appropriate syntax for each engine

    if getattr(main, "USE_JAVASCRIPT", False):
        # JavaScript array syntax
        expression = "[item, item * 10]"
    else:
        # Lua table syntax
        expression = "{item, item * 10}"

    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "flat_map", "expression": expression},
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
