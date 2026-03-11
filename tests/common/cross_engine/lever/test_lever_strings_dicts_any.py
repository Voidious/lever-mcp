from tests import make_tool_call
import pytest


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
