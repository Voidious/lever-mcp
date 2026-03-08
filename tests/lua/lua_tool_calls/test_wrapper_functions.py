from lib.lua import evaluate_expression


class TestLuaWrapperFunctions:
    """Test list(), dict(), and unwrap() wrapper functions."""

    def test_list_wrapper_basic(self):
        """Test basic list() wrapper functionality."""
        # Test wrapping a simple list
        result = evaluate_expression("list({1, 2, 3})", {})
        assert result == [1, 2, 3]

        # Test wrapping empty list
        result = evaluate_expression("list({})", {})
        assert result == []

    def test_dict_wrapper_basic(self):
        """Test basic dict() wrapper functionality."""
        # Test wrapping a simple dict
        result = evaluate_expression("dict({a=1, b=2})", {})
        assert result == {"a": 1, "b": 2}

        # Test wrapping empty dict
        result = evaluate_expression("dict({})", {})
        assert result == {}

    def test_unwrap_function(self):
        """Test unwrap() function."""
        # Test unwrapping works correctly in expressions
        result = evaluate_expression("unwrap(list({1, 2, 3}))", {})
        # unwrap() returns the data part, which should be processed normally
        assert result == [1, 2, 3]

        result = evaluate_expression("unwrap(dict({a=1, b=2}))", {})
        assert result == {"a": 1, "b": 2}

    def test_unwrap_with_lua_expressions(self):
        """Improved unwrap test coverage using Lua expressions with any.eval for
        validation."""
        # Test unwrap with type checking using any.eval
        result = evaluate_expression('any.eval(unwrap(list({1, 2, 3})), "#value")', {})
        assert result == 3  # Length of unwrapped list

        result = evaluate_expression(
            'any.eval(unwrap(dict({x=10, y=20})), "x + y")', {}
        )
        assert result == 30  # Sum of unwrapped dict values

        # Test unwrap with complex nested expressions
        result = evaluate_expression(
            'any.eval(unwrap(list({5, 10, 15})), "value[2] * 2")', {}
        )
        assert result == 20  # Second element (10) * 2

        # Test unwrap in conditional expressions
        result = evaluate_expression(
            'any.eval(unwrap(dict({status="active", count=5})), '
            '"status == \\"active\\" and count > 3")',
            {},
        )
        assert result is True

        # Test unwrap with list operations
        result = evaluate_expression(
            "lists.contains(unwrap(list({1, 2, 3})), nil, 2)", {}
        )
        assert result is True

        # Test unwrap with string operations on dict values
        result = evaluate_expression(
            'strings.upper_case(any.eval(unwrap(dict({name="alice"})), "name"))', {}
        )
        assert result == "ALICE"

        # Test unwrap with empty structures
        result = evaluate_expression('any.eval(unwrap(list({})), "#value")', {})
        assert result == 0  # Length of empty unwrapped list

        result = evaluate_expression("any.size(unwrap(dict({})))", {})
        assert result == 0  # Size of empty unwrapped dict

        # Test unwrap with null values
        result = evaluate_expression(
            'any.eval(unwrap(list({1, null, 3})), "value[2] == null")', {}
        )
        assert result is True  # Check if second element is null

        # Test unwrap with non-wrapped objects (should pass through unchanged)
        result = evaluate_expression('any.eval(unwrap({a=1, b=2}), "a + b")', {})
        assert result == 3  # Regular dict passed through unwrap unchanged

    def test_wrap_parameter_functionality(self):
        """Test wrap=True parameter in table-based Lua function calls."""
        # Test that wrap=True creates wrapped structures in the JSON-serializable result
        # Note: The wrapped result gets converted back to Python by evaluate_expression,
        # but in actual MCP usage, the wrapped result would be serialized to JSON

        # Test lists.map with wrap=True using table syntax
        result = evaluate_expression(
            'lists.map{items={1, 2}, expression="{}", wrap=true}', {}
        )
        # With wrap=true, results should be wrapped
        assert result == {
            "__type": "list",
            "data": [{"__type": "dict", "data": {}}, {"__type": "dict", "data": {}}],
        }

        # Test with nested structure
        result = evaluate_expression(
            'lists.map{items={1, 2}, expression="{item}", wrap=true}', {}
        )
        assert result == {
            "__type": "list",
            "data": [{"__type": "list", "data": [1]}, {"__type": "list", "data": [2]}],
        }

        # Test dicts.values with wrap=True
        result = evaluate_expression("dicts.values{obj={a=1, b=2}, wrap=true}", {})
        assert sorted(result["data"]) == [1, 2]
        assert result["__type"] == "list"

        # Test any.eval with wrap=True
        result = evaluate_expression(
            'any.eval{value={x=5}, expression="x * 2", wrap=true}', {}
        )
        assert result == 10

    def test_auto_wrap_for_returned_functions(self):
        """Test that MCP tool functions returned from expressions get auto-wrap=true."""
        # Test returning a simple function (non-MCP) - should work normally
        result = evaluate_expression("function(x) return x * 2 end", 5)
        assert result == 10

        # Test basic function return functionality
        result = evaluate_expression("function(item) return #item end", [1, 2, 3])
        assert result == 3

        # CRITICAL TEST: MCP tool function references get auto-wrap
        # When an expression returns an MCP tool function, it should be called
        # with wrap=true
        result = evaluate_expression("strings.upper_case", "hello")
        assert result == "HELLO"

        # Test MCP tool function auto-wrap with list-returning function
        result = evaluate_expression("lists.tail", [1, 2, 3])
        assert result == {"__type": "list", "data": [2, 3]}

        # CRITICAL TEST: Empty list preservation with auto-wrap
        result = evaluate_expression("lists.tail", [1])  # Single item -> empty tail
        assert result == {
            "__type": "list",
            "data": [],
        }  # Empty list properly preserved through auto-wrap

        # Test single-parameter MCP functions work with auto-wrap
        result = evaluate_expression("lists.head", [1, 2, 3])
        assert result == 1

        result = evaluate_expression("strings.reverse", "hello")
        assert result == "olleh"

    def test_list_wrapper_in_tool_operations(self):
        """Test using list() wrapper with tool operations."""
        # Test lists.map with wrapped lists - should return list of lists
        result = evaluate_expression('lists.map({1, 2, 3}, "list({item * 2})")', {})
        assert result == [[2], [4], [6]]

        # Test using wrapped list as input to operation
        result = evaluate_expression("lists.head(list({5, 6, 7}))", {})
        assert result == 5

    def test_dict_wrapper_in_tool_operations(self):
        """Test using dict() wrapper with tool operations."""
        # Test with dict operations
        result = evaluate_expression("dicts.keys(dict({x=1, y=2}))", {})
        assert sorted(result) == ["x", "y"]

        # Test creating dicts in expressions
        result = evaluate_expression('lists.map({1, 2}, "dict({value=item})")', {})
        assert result == [{"value": 1}, {"value": 2}]

    def test_empty_wrappers(self):
        """Test empty list and dict wrappers."""
        # Empty list should stay empty list
        result = evaluate_expression("lists.head(list({}))", {})
        assert result is None  # head of empty list

        # Empty dict should stay empty dict
        result = evaluate_expression("dicts.keys(dict({}))", {})
        assert result == {}  # Empty result (conversion ambiguity)

    def test_nested_wrapped_objects(self):
        """Test wrapped objects nested in other structures."""
        # List containing wrapped dicts
        result = evaluate_expression(
            'lists.map({1, 2}, "dict({id=item, data=list({item, item*2})})")', {}
        )
        expected = [{"id": 1, "data": [1, 2]}, {"id": 2, "data": [2, 4]}]
        assert result == expected

        # Dict containing wrapped lists
        result = evaluate_expression("dict({items=list({1, 2, 3}), count=3})", {})
        assert result == {"items": [1, 2, 3], "count": 3}

    def test_wrapper_type_preservation(self):
        """Test that wrappers preserve types correctly."""
        # Empty table wrapped as list should become empty list
        result = evaluate_expression("any.size(list({}))", {})
        assert result == 0

        # Empty table wrapped as dict should become empty dict
        result = evaluate_expression("any.size(dict({}))", {})
        assert result == 0

        # Compare unwrapped vs wrapped
        wrapped_result = evaluate_expression('lists.join(list({1, 2, 3}), ",")', {})
        unwrapped_result = evaluate_expression('lists.join({1, 2, 3}, ",")', {})
        assert wrapped_result == unwrapped_result == "1,2,3"

    def test_complex_wrapper_scenarios(self):
        """Test complex scenarios with multiple wrappers."""
        # Test any.eval with list creation (returns unwrapped result by default)
        result = evaluate_expression('any.eval({x=2}, "list({x, x*2, x*3})")', {})
        assert result == [2, 4, 6]

        # Test chaining operations with wrappers
        result = evaluate_expression(
            'lists.map(list({1, 2}), "dict({value=item, double=item*2})")', {}
        )
        assert result == [{"value": 1, "double": 2}, {"value": 2, "double": 4}]

        # Test unwrap in complex expression
        result = evaluate_expression(
            "lists.contains(unwrap(list({5, 10, 15})), nil, 10)", {}
        )
        assert result is True

    def test_wrapper_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test unwrap with non-wrapped object
        result = evaluate_expression("unwrap({a=1, b=2})", {})
        assert result == {"a": 1, "b": 2}  # Should pass through unchanged

        # Test wrapper with null values
        result = evaluate_expression("list({1, null, 3})", {})
        assert result == [1, None, 3]

        result = evaluate_expression("dict({a=1, b=null, c=3})", {})
        assert result == {"a": 1, "b": None, "c": 3}

    def test_empty_wrappers_in_nested_structures(self):
        """Test empty list/dict wrappers in nested structures."""
        # Note: Due to current conversion pipeline limitations, empty tables in
        # expressions are converted to dicts by default, even when wrapped as lists in
        # map operations. This is a known limitation where the expression evaluation
        # process applies ambiguous-empty-table-to-dict conversion after tool functions
        # return.

        # Empty wrapper in nested list structure (currently both become dicts
        # due to conversion pipeline)
        result = evaluate_expression('lists.map({1, 2}, "list({})")', {})
        assert result == [
            {},
            {},
        ]  # Currently becomes empty dicts due to conversion pipeline

        result = evaluate_expression('lists.map({1, 2}, "dict({})")', {})
        assert result == [{}, {}]  # Empty dict wrapper in nested list structure

        # Empty list wrapper in nested dict structure (works correctly for direct usage)
        result = evaluate_expression("dict({items=list({}), count=0})", {})
        assert result == {"items": [], "count": 0}

        # Empty dict wrapper in nested dict structure
        result = evaluate_expression('dict({data=dict({}), status="empty"})', {})
        assert result == {"data": {}, "status": "empty"}

        # Test with non-empty content to verify wrappers work correctly
        result = evaluate_expression('lists.map({1, 2}, "list({item})")', {})
        assert result == [[1], [2]]  # Non-empty wrapped lists work correctly

        result = evaluate_expression('lists.map({1, 2}, "dict({value=item})")', {})
        assert result == [
            {"value": 1},
            {"value": 2},
        ]  # Non-empty wrapped dicts work correctly
