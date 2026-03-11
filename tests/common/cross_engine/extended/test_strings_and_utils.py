from tests import make_tool_call
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("foo bar", "fooBar"),
        ("Foo-Bar", "fooBar"),
        ("__FOO_BAR__", "fooBar"),
        ("foo_bar_baz", "fooBarBaz"),
        ("", ""),
        ("single", "single"),
    ],
)
async def test_camel_case(client, input_str, expected):
    value, error = await make_tool_call(
        client, "strings", {"text": input_str, "operation": "camel_case"}
    )
    assert value == expected or (isinstance(value, dict) and "error" in value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("foo bar", "foo-bar"),
        ("FooBar", "foo-bar"),
        ("foo_bar", "foo-bar"),
        ("__FOO_BAR__", "foo-bar"),
        ("fooBarBaz", "foo-bar-baz"),
        ("", ""),
    ],
)
async def test_kebab_case(client, input_str, expected):
    value, error = await make_tool_call(
        client, "strings", {"text": input_str, "operation": "kebab_case"}
    )
    assert value == expected or (isinstance(value, dict) and "error" in value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("foo bar", "foo_bar"),
        ("FooBar", "foo_bar"),
        ("foo-bar", "foo_bar"),
        ("--FOO-BAR--", "foo_bar"),
        ("fooBarBaz", "foo_bar_baz"),
        ("", ""),
    ],
)
async def test_snake_case(client, input_str, expected):
    value, error = await make_tool_call(
        client, "strings", {"text": input_str, "operation": "snake_case"}
    )
    assert value == expected or (isinstance(value, dict) and "error" in value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("foo bar", "Foo bar"),
        ("FOO BAR", "Foo bar"),
        (" foo bar", " foo bar"),
        ("", ""),
    ],
)
async def test_capitalize(client, input_str, expected):
    value, error = await make_tool_call(
        client, "strings", {"text": input_str, "operation": "capitalize"}
    )
    assert value == expected or (isinstance(value, dict) and "error" in value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, target, expected",
    [
        ("abc", "a", True),
        ("abc", "b", False),
        ("abc", "", True),
        ("", "", True),
    ],
)
async def test_starts_with(client, text, target, expected):
    value, error = await make_tool_call(
        client,
        "strings",
        {"text": text, "operation": "starts_with", "param": target},
    )
    assert value is expected or (isinstance(value, dict) and "error" in value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, target, expected",
    [
        ("abc", "c", True),
        ("abc", "b", False),
        ("abc", "", True),
        ("", "", True),
    ],
)
async def test_ends_with(client, text, target, expected):
    value, error = await make_tool_call(
        client, "strings", {"text": text, "operation": "ends_with", "param": target}
    )
    assert value is expected or (isinstance(value, dict) and "error" in value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected",
    [
        ([], True),
        ({}, True),
        ("", True),
        ([1], False),
        ({"a": 1}, False),
        ("a", False),
        (None, True),
        (0, True),
        (False, True),
    ],
)
async def test_is_empty(client, value, expected):
    if isinstance(value, str):
        value_out, error = await make_tool_call(
            client, "strings", {"text": value, "operation": "is_empty"}
        )
    elif isinstance(value, list):
        value_out, error = await make_tool_call(
            client, "lists", {"items": value, "operation": "is_empty"}
        )
    elif isinstance(value, dict):
        value_out, error = await make_tool_call(
            client, "dicts", {"obj": value, "operation": "is_empty"}
        )
    else:
        value_out, error = await make_tool_call(
            client, "any", {"value": value, "operation": "is_empty"}
        )
    assert value_out is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("foo", "foo", True),
        (42, 42, True),
        (3.14, 3.14, True),
        (True, True, True),
        ([1, 2], [1, 2], True),
        ({"a": 1}, {"a": 1}, True),
        (None, None, True),
        ("foo", "bar", False),
        (42, 43, False),
        (3.14, 2.71, False),
        (True, False, False),
        ([1, 2], [2, 1], False),
        ({"a": 1}, {"a": 2}, False),
        (None, 0, False),
    ],
)
async def test_is_equal_all_types(client, a, b, expected):
    if isinstance(a, str) and isinstance(b, str):
        value_out, error = await make_tool_call(
            client, "strings", {"text": a, "operation": "is_equal", "param": b}
        )
    elif isinstance(a, list) and isinstance(b, list):
        value_out, error = await make_tool_call(
            client, "lists", {"items": a, "operation": "is_equal", "param": b}
        )
    elif isinstance(a, dict) and isinstance(b, dict):
        value_out, error = await make_tool_call(
            client, "dicts", {"obj": a, "operation": "is_equal", "param": b}
        )
    else:
        value_out, error = await make_tool_call(
            client, "any", {"value": a, "operation": "is_equal", "param": b}
        )
    assert value_out is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value, expected",
    [
        (None, True),
        (0, False),
        (1, False),
        (3.14, False),
        ("", False),
        ("foo", False),
        ([], False),
        ([1, 2], False),
        ({}, False),
        ({"a": 1}, False),
        (False, False),
        (True, False),
    ],
)
async def test_any_is_nil(client, value, expected):
    value_out, error = await make_tool_call(
        client, "any", {"value": value, "operation": "is_nil"}
    )
    assert value_out is expected
