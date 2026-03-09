from lib.lua import evaluate_expression


class TestLuaToolFunctionReferences:
    """Test using tool functions directly as expressions."""

    def test_lists_partition_with_string_function_ref(self):
        """Test lists.partition using strings.is_digit as expression."""
        # Mix of digit and non-digit strings
        items = ["123", "abc", "456", "def", "789"]
        result = evaluate_expression(
            'lists.partition(items, "strings.is_digit")', {"items": items}
        )

        # partition returns a list [truthy_items, falsy_items]
        assert isinstance(result, list)
        assert len(result) == 2

        # Check that digit strings are correctly identified
        digit_strings = result[0]  # truthy items
        non_digit_strings = result[1]  # falsy items
        assert "123" in digit_strings
        assert "456" in digit_strings
        assert "789" in digit_strings
        assert "abc" in non_digit_strings
        assert "def" in non_digit_strings

    def test_lists_filter_by_with_string_function_ref(self):
        """Test lists.filter_by using strings.is_alpha as expression."""
        items = ["hello", "world123", "test", "abc456", "pure"]
        result = evaluate_expression(
            'lists.filter_by(items, "strings.is_alpha")', {"items": items}
        )

        # Should only keep alphabetic strings
        expected = ["hello", "test", "pure"]
        assert result == expected

    def test_lists_map_with_string_function_ref(self):
        """Test lists.map using strings.upper_case as expression."""
        items = ["hello", "world", "test"]
        result = evaluate_expression(
            'lists.map(items, "strings.upper_case")', {"items": items}
        )

        expected = ["HELLO", "WORLD", "TEST"]
        assert result == expected

    def test_lists_all_by_with_string_function_ref(self):
        """Test lists.all_by using strings.is_alpha as expression."""
        # All alphabetic
        items1 = ["hello", "world", "test"]
        result1 = evaluate_expression(
            'lists.all_by(items, "strings.is_alpha")', {"items": items1}
        )
        assert result1 is True

        # Mixed (not all alphabetic)
        items2 = ["hello", "world123", "test"]
        result2 = evaluate_expression(
            'lists.all_by(items, "strings.is_alpha")', {"items": items2}
        )
        assert result2 is False

    def test_lists_any_by_with_string_function_ref(self):
        """Test lists.any_by using strings.is_digit as expression."""
        # Contains at least one digit string
        items1 = ["hello", "123", "world"]
        result1 = evaluate_expression(
            'lists.any_by(items, "strings.is_digit")', {"items": items1}
        )
        assert result1 is True

        # No digit strings
        items2 = ["hello", "world", "test"]
        result2 = evaluate_expression(
            'lists.any_by(items, "strings.is_digit")', {"items": items2}
        )
        assert result2 is False

    def test_lists_count_by_with_function_ref(self):
        """Test lists.count_by using a function reference to group by result."""
        items = ["123", "abc", "456", "def", "789", "xyz"]
        result = evaluate_expression(
            'lists.count_by(items, "strings.is_digit")', {"items": items}
        )

        # Should count True/False as string keys
        expected = {"True": 3, "False": 3}  # 3 digit strings, 3 non-digit strings
        assert result == expected

    def test_lists_group_by_with_function_ref(self):
        """Test lists.group_by using a function reference."""
        items = ["123", "abc", "456", "def"]
        result = evaluate_expression(
            'lists.group_by(items, "strings.is_digit")', {"items": items}
        )

        # Should group by whether string is all digits
        # group_by converts boolean results to string keys
        assert "True" in result
        assert "False" in result
        assert "123" in result["True"]
        assert "456" in result["True"]
        assert "abc" in result["False"]
        assert "def" in result["False"]

    def test_lists_sort_by_with_function_ref(self):
        """Test lists.sort_by using a function reference."""
        # Sort by string length
        items = ["hello", "hi", "world", "a"]
        result = evaluate_expression(
            'lists.sort_by(items, "strings.trim")', {"items": items}
        )

        # strings.trim doesn't change order but returns the strings
        # This tests that function refs work, even if sorting by trim doesn't
        # change much
        assert len(result) == 4
        assert all(item in result for item in items)

    def test_chained_function_refs(self):
        """Test using function references in more complex expressions."""
        items = [{"name": "ALICE"}, {"name": "bob"}, {"name": "CHARLIE"}]
        result = evaluate_expression(
            'lists.map(items, "strings.lower_case(name)")', {"items": items}
        )

        expected = ["alice", "bob", "charlie"]
        assert result == expected

    def test_nested_function_calls_in_expressions(self):
        """Test nested function calls within expressions."""
        items = ["  hello  ", "  WORLD  ", "  test  "]
        # Trim and then uppercase
        result = evaluate_expression(
            'lists.map(items, "strings.upper_case(strings.trim(item))")',
            {"items": items},
        )

        expected = ["HELLO", "WORLD", "TEST"]
        assert result == expected

    def test_new_operations_in_expressions(self):
        """Test using new operations in complex expressions."""
        # Using strings.split in expression
        items = [{"data": "a,b,c"}, {"data": "x,y"}, {"data": "single"}]
        result = evaluate_expression(
            "lists.filter_by(items, \"any.size(strings.split(data, ',')) > 2\")",
            {"items": items},
        )
        # Should keep items with more than 2 parts after splitting
        assert len(result) == 1
        assert result[0]["data"] == "a,b,c"

        # Using lists.min and lists.max in expressions
        data = [{"scores": [85, 92, 78]}, {"scores": [90, 88, 95]}]
        result = evaluate_expression(
            'lists.map(data, "lists.max(scores)")', {"data": data}
        )
        assert result == [92, 95]  # Max score from each list

        # Using dicts.keys in expressions
        objects = [{"user": {"name": "Alice", "age": 30}}, {"user": {"name": "Bob"}}]
        result = evaluate_expression(
            'lists.filter_by(objects, "any.size(dicts.keys(user)) > 1")',
            {"objects": objects},
        )
        # Should keep objects where user has more than 1 key
        assert len(result) == 1
        assert result[0]["user"]["name"] == "Alice"

    def test_new_operations_with_function_references(self):
        """Test using new operations as function references."""
        # Test with string lists and any.size
        string_lists = [["a", "b"], ["x", "y", "z"], ["single"]]
        result = evaluate_expression(
            'lists.map(string_lists, "any.size(item)")', {"string_lists": string_lists}
        )
        assert result == [2, 3, 1]  # Sizes of each sublist

        # Test min/max with lists of numbers
        number_lists = [[3, 1, 4], [2, 8, 5], [9, 6]]
        result = evaluate_expression(
            'lists.map(number_lists, "lists.min(item)")', {"number_lists": number_lists}
        )
        assert result == [1, 2, 6]  # Min from each sublist

        result = evaluate_expression(
            'lists.map(number_lists, "lists.max(item)")', {"number_lists": number_lists}
        )
        assert result == [4, 8, 9]  # Max from each sublist

    def test_new_operations_complex_combinations(self):
        """Test complex combinations of new operations."""
        # Split text, then join with different delimiter
        items = [{"text": "a,b,c"}, {"text": "x,y,z"}]
        result = evaluate_expression(
            "lists.map(items, \"lists.join(strings.split(text, ','), '|')\")",
            {"items": items},
        )
        assert result == ["a|b|c", "x|y|z"]

        # Use slice and split together
        data = [{"line": "name=Alice,age=30"}, {"line": "name=Bob,age=25"}]
        result = evaluate_expression(
            'lists.map(data, "strings.slice(line, {from=5})")',  # Remove "name=" part
            {"data": data},
        )
        assert result == ["Alice,age=30", "Bob,age=25"]

    def test_any_eval_with_tool_function_ref(self):
        """Test that any.eval supports tool function references with auto-wrap."""
        # any.eval DOES support tool function references (unlike dict operations)
        result = evaluate_expression('any.eval("hello", "strings.upper_case")', {})
        assert result == "HELLO"

        # Test with validation function
        result = evaluate_expression('any.eval("test123", "strings.is_alpha")', {})
        assert result is False

        # Test with function that works without parameters
        result = evaluate_expression('any.eval("  hello  ", "strings.trim")', {})
        assert result == "hello"

    def test_dicts_map_values_with_tool_function_ref(self):
        """Test dicts.map_values using tool function references as expressions."""
        # Test with strings.upper_case as function reference (should work like lists)
        data = {"greeting": "hello", "name": "world", "status": "active"}
        result = evaluate_expression(
            'dicts.map_values(data, "strings.upper_case")', {"data": data}
        )

        expected = {"greeting": "HELLO", "name": "WORLD", "status": "ACTIVE"}
        assert result == expected

    def test_dicts_map_values_with_string_validation(self):
        """Test dicts.map_values using strings.is_alpha as expression."""
        # Test with validation function reference (should work like lists)
        data = {"name": "alice", "id": "123", "city": "paris", "code": "abc456"}
        result = evaluate_expression(
            'dicts.map_values(data, "strings.is_alpha")', {"data": data}
        )

        expected = {"name": True, "id": False, "city": True, "code": False}
        assert result == expected

    def test_dicts_map_keys_with_tool_function_ref(self):
        """Test dicts.map_keys using tool function references as expressions."""
        # Test with strings.upper_case as function reference (should work like lists)
        data = {"first": "john", "last": "doe", "city": "paris"}
        result = evaluate_expression(
            'dicts.map_keys(data, "strings.upper_case")', {"data": data}
        )

        expected = {"FIRST": "john", "LAST": "doe", "CITY": "paris"}
        assert result == expected

    def test_dicts_with_nested_tool_function_calls(self):
        """Test dict operations with nested tool function calls."""
        # Test map_values with nested tool calls
        data = {"message": "  HELLO WORLD  ", "title": "  test case  "}
        result = evaluate_expression(
            'dicts.map_values(data, "strings.lower_case(strings.trim(value))")',
            {"data": data},
        )

        expected = {"message": "hello world", "title": "test case"}
        assert result == expected

    def test_dicts_map_with_list_returning_functions(self):
        """Test dict operations with tool functions that return lists."""
        # Test map_values with strings.split
        data = {"tags": "red,blue,green", "categories": "food,drink"}
        result = evaluate_expression(
            "dicts.map_values(data, \"strings.split(value, ',')\")", {"data": data}
        )

        expected = {"tags": ["red", "blue", "green"], "categories": ["food", "drink"]}
        assert result == expected


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
