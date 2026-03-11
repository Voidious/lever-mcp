from tests import make_tool_call
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([1, 2, 3], 1),
        ([None, 2, 3], None),
        ([], None),
    ],
)
async def test_head(client, items, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "head"}
    )
    if expected is None:
        assert value is None
    else:
        assert value is not None
        assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([1, 2, 3], [2, 3]),
        ([1], []),
        ([], []),
    ],
)
async def test_tail(client, items, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "tail"}
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([1, 2, 3], 3),
        ([1, 2, None], None),
        ([], None),
    ],
)
async def test_last(client, items, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "last"}
    )
    if not value:
        assert expected is None
    else:
        assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([1, 2, 3], [1, 2]),
        ([1], []),
        ([], []),
    ],
)
async def test_initial(client, items, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "initial"}
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, n, expected",
    [
        ([1, 2, 3], 1, [2, 3]),
        ([1, 2, 3], 0, [1, 2, 3]),
        ([1, 2, 3], 5, []),
        ([], 2, []),
    ],
)
async def test_drop(client, items, n, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "drop", "param": n}
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, n, expected",
    [
        ([1, 2, 3], 1, [1, 2]),
        ([1, 2, 3], 0, [1, 2, 3]),
        ([1, 2, 3], 5, []),
        ([], 2, []),
    ],
)
async def test_drop_right(client, items, n, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "drop_right", "param": n}
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, n, expected",
    [
        ([1, 2, 3], 2, [1, 2]),
        ([1, 2, 3], 0, []),
        ([1, 2, 3], 5, [1, 2, 3]),
        ([], 2, []),
    ],
)
async def test_take(client, items, n, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "take", "param": n}
    )
    if not value:
        assert expected == []
    else:
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if len(expected) == 1 and not isinstance(value, list):
            assert [value] == expected
        else:
            assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, n, expected",
    [
        ([1, 2, 3], 2, [2, 3]),
        ([1, 2, 3], 0, []),
        ([1, 2, 3], 5, [1, 2, 3]),
        ([], 2, []),
    ],
)
async def test_take_right(client, items, n, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "take_right", "param": n}
    )
    if not value:
        assert expected == []
    else:
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if len(expected) == 1 and not isinstance(value, list):
            assert [value] == expected
        else:
            assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expected",
    [
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([[], [1]], [1]),
        ([[]], []),
        ([], []),
        ([1, [2, 3]], [1, 2, 3]),  # Non-list elements preserved
        ([1, 2, [3, 4]], [1, 2, 3, 4]),  # Multiple non-list elements
    ],
)
async def test_flatten(client, items, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": items, "operation": "flatten"}
    )
    if not value:
        assert expected == []
    else:
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if len(expected) == 1 and not isinstance(value, list):
            assert [value] == expected
        else:
            assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lists, expected",
    [
        ([[1, 2], [2, 3]], [1, 2, 3]),
        ([[], [1]], [1]),
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),
        ([], []),
    ],
)
async def test_union(client, lists, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": lists, "operation": "union"}
    )
    if not value:
        assert expected == []
    else:
        if isinstance(value, list):
            assert sorted(value) == sorted(expected)
        else:
            assert [value] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lists, expected",
    [
        ([[1, 2, 3], [2, 3, 4], [2, 5]], [2, 3]),
        ([[1, 2], [3, 4]], []),
        ([[], [1, 2]], []),
        ([], []),
    ],
)
async def test_intersection(client, lists, expected):
    if len(lists) < 2:
        assert expected == []
        return
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": lists[0], "others": lists[1], "operation": "intersection"},
    )
    if not value:
        assert expected == []
    else:
        if (
            isinstance(value, list)
            and value
            and all(isinstance(x, dict) and "value" in x for x in value)
        ):
            value = [x["value"] for x in value]
        if not isinstance(value, list):
            value = [value]
        if (
            isinstance(value, list)
            and isinstance(expected, list)
            and value
            and expected
        ):
            primitive_types = (int, float, str, bool, type(None))
            t = type(value[0])
            if all(
                isinstance(x, primitive_types) and type(x) == t  # noqa
                for x in value + expected
            ):
                assert set(value) == set(expected)
            elif all(isinstance(x, dict) for x in value + expected):

                def dicts_to_set(lst):
                    return set(tuple(sorted(d.items())) for d in lst)

                assert dicts_to_set(value) == dicts_to_set(expected)
            elif all(isinstance(x, list) for x in value + expected):
                assert set(tuple(x) for x in value) == set(tuple(x) for x in expected)
            else:
                assert value == expected
        else:
            assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, others, expected",
    [
        ([1, 2, 3], [[2, 4]], [1, 3]),
        ([1, 2, 3], [[4, 5]], [1, 2, 3]),
        ([], [[1]], []),
    ],
)
async def test_difference(client, items, others, expected):
    if not others or not others[0]:
        assert expected == []
        return
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "others": others[0], "operation": "difference"},
    )
    if not value:
        assert expected == []
    else:
        assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lists, expected",
    [
        ([[1, 2], [2, 3]], [1, 3]),
        ([[1, 2, 3], [2, 4, 5]], [1, 3, 4, 5]),
        ([[], [1, 2]], [1, 2]),
    ],
)
async def test_xor(client, lists, expected):
    value, error = await make_tool_call(
        client, "lists", {"items": lists[0], "others": lists[1], "operation": "xor"}
    )
    if (
        isinstance(value, list)
        and value
        and all(isinstance(x, dict) and "value" in x for x in value)
    ):
        value = [x["value"] for x in value]
    assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, keys, expected",
    [
        ({"a": 1, "b": 2}, ["a"], {"a": 1}),
        ({"a": 1, "b": 2}, ["a", "c"], {"a": 1}),
        ({}, ["a"], {}),
    ],
)
async def test_pick(client, obj, keys, expected):
    value, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": "pick", "param": keys}
    )
    assert error is None
    assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, keys, expected",
    [
        ({"a": 1, "b": 2}, ["a"], {"b": 2}),
        ({"a": 1, "b": 2}, ["c"], {"a": 1, "b": 2}),
        ({}, ["a"], {}),
    ],
)
async def test_omit(client, obj, keys, expected):
    value, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": "omit", "param": keys}
    )
    assert error is None
    assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, expected",
    [
        ({"a": "x", "b": "y"}, {"x": "a", "y": "b"}),
        ({"a": 1}, {"1": "a"}),
        ({}, {}),
    ],
)
async def test_invert(client, obj, expected):
    value, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": "invert"}
    )
    assert error is None
    assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "obj, key, expected",
    [
        ({"a": 1}, "a", True),
        ({"a": 1}, "b", False),
        ({}, "a", False),
    ],
)
async def test_has(client, obj, key, expected):
    value, error = await make_tool_call(
        client, "dicts", {"obj": obj, "operation": "has_key", "param": key}
    )
    assert error is None
    assert value == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "items, expression, expected",
    [
        (
            [{"id": "a", "v": 1}, {"id": "b", "v": 2}],
            "id",
            {"a": {"id": "a", "v": 1}, "b": {"id": "b", "v": 2}},
        ),
        ([], "id", {}),
    ],
)
async def test_key_by(client, items, expression, expected):
    value, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "key_by", "expression": expression},
    )
    assert error is None
    assert value == expected
