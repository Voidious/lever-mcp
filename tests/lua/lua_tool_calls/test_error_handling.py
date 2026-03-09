from lib.lua import evaluate_expression


class TestLuaEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_arguments(self):
        # Some operations should handle empty/missing arguments gracefully
        result = evaluate_expression('strings.is_empty("")', {})
        assert result is True

        result = evaluate_expression("lists.is_empty({})", {})
        assert result is True

    def test_null_handling(self):
        # Test null value handling
        result = evaluate_expression("any.is_nil(null)", {})
        assert result is True

        result = evaluate_expression("strings.upper_case(null)", {})
        # Should handle null gracefully
        assert result is None or result == ""

    def test_mixed_syntax_in_expression(self):
        # Test using both positional and table syntax in same expression
        result = evaluate_expression(
            'strings.upper_case(lists.head({"hello", "world"}))', {}
        )
        assert result == "HELLO"

        result = evaluate_expression(
            'lists.map({items={"a", "b"}}, "strings.upper_case(item)")', {}
        )
        assert result == ["A", "B"]

    def test_nested_function_calls(self):
        # Test complex nested calls
        result = evaluate_expression(
            'lists.filter_by({items={{name="Alice", age=25}, {name="Bob", age=17}}}, '
            '"age >= 18")',
            {},
        )
        assert result == [{"name": "Alice", "age": 25}]

        # Nested with map
        result = evaluate_expression(
            'lists.map({items={{name="alice"}, {name="bob"}}}, '
            '"strings.upper_case(name)")',
            {},
        )
        assert result == ["ALICE", "BOB"]


class TestLuaErrorHandling:
    """Test error handling and boundary conditions for Lua tool calls."""

    def test_invalid_operation_names(self):
        # Test calling non-existent operations - should return None gracefully
        result = evaluate_expression('strings.nonexistent("test")', {})
        assert result is None

        result = evaluate_expression("lists.invalid_op({1, 2, 3})", {})
        assert result is None

    def test_malformed_expressions(self):
        # Test invalid Lua expressions - filter_by should return empty result
        # when expressions fail
        result = evaluate_expression(
            'lists.filter_by({1, 2, 3}, "invalid lua ++ syntax")', {}
        )
        assert result == {}  # Empty result due to failed filter expression

        result = evaluate_expression("strings.upper_case(unclosed_paren(", {})
        assert result is None

    def test_boundary_conditions_numeric_params(self):
        # Test edge cases for numeric parameters

        # Negative sample_size should handle gracefully
        result = evaluate_expression('strings.sample_size("hello", -1)', {})
        assert result is None

        # Zero sample_size
        result = evaluate_expression('strings.sample_size("hello", 0)', {})
        assert result == ""

        # Sample size larger than string
        result = evaluate_expression('strings.sample_size("hi", 10)', {})
        assert isinstance(result, str) and len(result) == 2

        # Negative nth index
        result = evaluate_expression("lists.nth({1, 2, 3}, nil, -1)", {})
        assert result == 3  # Should work (negative indexing)

        # Out of bounds nth
        result = evaluate_expression("lists.nth({1, 2, 3}, nil, 10)", {})
        assert result is None

    def test_type_validation_errors(self):
        # Test operations with wrong input types - should return None with error

        # String operations on non-strings
        result = evaluate_expression("strings.upper_case(123)", {})
        assert result is None

        # List operations on non-lists
        result = evaluate_expression('lists.head("not a list")', {})
        assert result is None

        # Dict operations on non-dicts
        result = evaluate_expression('dicts.has_key("not a dict", "key")', {})
        assert result is None

    def test_missing_required_parameters(self):
        # Test operations missing required parameters - should return None

        # strings.contains without param
        result = evaluate_expression('strings.contains("hello")', {})
        assert result is None

        # lists.nth without param (index)
        result = evaluate_expression("lists.nth({1, 2, 3})", {})
        assert result is None

        # strings.template without data
        result = evaluate_expression('strings.template("Hello {name}!")', {})
        assert result is None

        # strings.starts_with without param
        result = evaluate_expression('strings.starts_with("hello")', {})
        assert result is None

    def test_empty_data_structures(self):
        # Test operations on empty inputs

        # Operations on empty lists
        result = evaluate_expression("lists.head({})", {})
        assert result is None

        result = evaluate_expression('lists.max_by({}, "value")', {})
        assert result is None

        # Operations on empty strings
        result = evaluate_expression('strings.sample_size("", 1)', {})
        assert result == ""

        result = evaluate_expression('strings.reverse("")', {})
        assert result == ""

    def test_complex_nested_data_edge_cases(self):
        # Test edge cases with complex nested structures

        # Deeply nested null values
        result = evaluate_expression(
            'any.eval({deep={nested=null}}, "deep.nested == null")', {}
        )
        assert result is True

        # Mixed type operations
        result = evaluate_expression(
            'lists.filter_by({{id=1}, "string", {id=2}}, "type(item) == \'table\'")', {}
        )
        # Should filter to only the dict items
        assert len(result) == 2
        assert all(isinstance(item, dict) for item in result)

    def test_resource_intensive_operations(self):
        # Test operations with larger inputs (not exhaustive, just basic checks)

        # Large list operations - pass the list as context item
        large_list = list(range(100))  # Reduce size for testing
        result = evaluate_expression(
            "lists.shuffle(item)", large_list, context={"item": large_list}
        )
        assert result is not None and len(result) == 100

        # Large string operations
        large_string = "a" * 100  # Reduce size for testing
        result = evaluate_expression(
            "strings.upper_case(text)", large_string, context={"text": large_string}
        )
        assert result is not None and len(result) == 100 and result.isupper()
