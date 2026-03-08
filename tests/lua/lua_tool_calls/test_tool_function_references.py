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
