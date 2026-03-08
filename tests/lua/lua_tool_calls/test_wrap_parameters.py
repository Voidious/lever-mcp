from lib.lua import evaluate_expression


class TestPositionalVsTableWrapParameter:
    """Test wrap parameter support for both positional and table-based syntax."""

    def test_lists_wrap_positional_syntax(self):
        """Test lists operations with wrap parameter using positional syntax."""
        # lists.map with positional args and wrap=true
        # Syntax: lists.map(items, expression, param, others, wrap)
        result = evaluate_expression('lists.map({1, 2}, "{}", nil, nil, true)', {})
        assert result == {
            "__type": "list",
            "data": [{"__type": "dict", "data": {}}, {"__type": "dict", "data": {}}],
        }

        # lists.head with wrap=true (should work but not really meaningful for
        # single values)
        result = evaluate_expression("lists.head({5, 6, 7}, nil, nil, nil, true)", {})
        assert result == 5

        # lists.filter_by with positional wrap
        result = evaluate_expression(
            'lists.filter_by({1, 2, 3, 4}, "item > 2", nil, nil, true)', {}
        )
        assert result == {"__type": "list", "data": [3, 4]}

    def test_lists_wrap_table_syntax(self):
        """Test lists operations with wrap parameter using table syntax."""
        # Test same operations as positional but with table syntax
        result = evaluate_expression(
            'lists.map{items={1, 2}, expression="{}", wrap=true}', {}
        )
        assert result == {
            "__type": "list",
            "data": [{"__type": "dict", "data": {}}, {"__type": "dict", "data": {}}],
        }

        result = evaluate_expression("lists.head{items={5, 6, 7}, wrap=true}", {})
        assert result == 5

        result = evaluate_expression(
            'lists.filter_by{items={1, 2, 3, 4}, expression="item > 2", wrap=true}', {}
        )
        assert result == {"__type": "list", "data": [3, 4]}

    def test_strings_wrap_positional_syntax(self):
        """Test strings operations with wrap parameter using positional syntax."""
        # strings.upper_case with positional wrap
        # Syntax: strings.upper_case(text, param, data, wrap)
        result = evaluate_expression('strings.upper_case("hello", nil, nil, true)', {})
        assert result == "HELLO"

        # strings.split with positional wrap (returns wrapped format)
        result = evaluate_expression('strings.split("a,b,c", ",", nil, true)', {})
        assert result == {"__type": "list", "data": ["a", "b", "c"]}

        # CRITICAL TEST: Empty string split with nil delimiter produces empty
        # list with wrap=true
        # This is the key test - empty list preservation via wrapping
        result = evaluate_expression('strings.split("", nil, nil, true)', {})
        assert result == {"__type": "list", "data": []}

    def test_strings_wrap_table_syntax(self):
        """Test strings operations with wrap parameter using table syntax."""
        result = evaluate_expression('strings.upper_case{text="hello", wrap=true}', {})
        assert result == "HELLO"

        result = evaluate_expression(
            'strings.split{text="a,b,c", param=",", wrap=true}', {}
        )
        assert result == {"__type": "list", "data": ["a", "b", "c"]}

        # CRITICAL TEST: Empty string split with table syntax and wrap=true
        result = evaluate_expression('strings.split{text="", wrap=true}', {})
        assert result == {"__type": "list", "data": []}

    def test_dicts_wrap_positional_syntax(self):
        """Test dicts operations with wrap parameter using positional syntax."""
        # dicts.keys with positional wrap
        # Syntax: dicts.keys(obj, param, path, value, default, expression, wrap)
        result = evaluate_expression(
            "dicts.keys({a=1, b=2}, nil, nil, nil, nil, nil, true)", {}
        )
        # dicts.keys returns wrapped list when wrap=true
        assert result == {"__type": "list", "data": ["a", "b"]} or result == {
            "__type": "list",
            "data": ["b", "a"],
        }

        # dicts.map_values with expression and wrap (expression is 2nd arg for
        # map_values)
        result = evaluate_expression(
            'dicts.map_values({a=1, b=2}, "value * 2", nil, nil, nil, nil, true)', {}
        )
        assert result == {"__type": "dict", "data": {"a": 2, "b": 4}}

    def test_dicts_wrap_table_syntax(self):
        """Test dicts operations with wrap parameter using table syntax."""
        result = evaluate_expression("dicts.keys{obj={a=1, b=2}, wrap=true}", {})
        assert result == {"__type": "list", "data": ["a", "b"]} or result == {
            "__type": "list",
            "data": ["b", "a"],
        }

        result = evaluate_expression(
            'dicts.map_values{obj={a=1, b=2}, expression="value * 2", wrap=true}', {}
        )
        assert result == {"__type": "dict", "data": {"a": 2, "b": 4}}

    def test_any_wrap_positional_syntax(self):
        """Test any operations with wrap parameter using positional syntax."""
        # any.eval with positional wrap
        # Syntax: any.eval(value, expression, param, wrap)
        result = evaluate_expression('any.eval({x=5}, "x * 2", nil, true)', {})
        assert result == 10

        # any.contains with positional wrap
        result = evaluate_expression('any.contains("hello", "ell", nil, true)', {})
        assert result is True

    def test_any_wrap_table_syntax(self):
        """Test any operations with wrap parameter using table syntax."""
        result = evaluate_expression(
            'any.eval{value={x=5}, expression="x * 2", wrap=true}', {}
        )
        assert result == 10

        result = evaluate_expression(
            'any.contains{value="hello", param="ell", wrap=true}', {}
        )
        assert result is True

    def test_wrap_with_empty_collections(self):
        """Test wrap parameter with empty collections - the critical test case."""
        # Empty list with positional wrap syntax
        result = evaluate_expression(
            'lists.map({1, 2}, "list({})", nil, nil, true)', {}
        )
        assert result == {
            "__type": "list",
            "data": [{"__type": "list", "data": []}, {"__type": "list", "data": []}],
        }  # Should be wrapped list of wrapped empty lists

        # Empty list with table wrap syntax
        result = evaluate_expression(
            'lists.map{items={1, 2}, expression="list({})", wrap=true}', {}
        )
        assert result == {
            "__type": "list",
            "data": [{"__type": "list", "data": []}, {"__type": "list", "data": []}],
        }  # Should be wrapped list of wrapped empty lists

        # Empty dict with wrap
        result = evaluate_expression(
            'lists.map{items={1, 2}, expression="dict({})", wrap=true}', {}
        )
        assert result == {
            "__type": "list",
            "data": [{"__type": "dict", "data": {}}, {"__type": "dict", "data": {}}],
        }  # Should be wrapped list of wrapped empty dicts

    def test_mixed_parameter_styles_compatibility(self):
        """Test that both positional and table syntax produce same results."""
        # Test that both syntax styles produce identical results
        positional_result = evaluate_expression(
            'lists.map({1, 2, 3}, "item * 2", nil, nil, false)', {}
        )
        table_result = evaluate_expression(
            'lists.map{items={1, 2, 3}, expression="item * 2", wrap=false}', {}
        )
        assert positional_result == table_result == [2, 4, 6]

        # Test with wrap=true
        positional_result = evaluate_expression(
            'strings.upper_case("test", nil, nil, true)', {}
        )
        table_result = evaluate_expression(
            'strings.upper_case{text="test", wrap=true}', {}
        )
        assert positional_result == table_result == "TEST"

    def test_wrap_parameter_type_validation(self):
        """Test that wrap parameter works correctly with boolean values."""
        # Test with explicit true
        result = evaluate_expression("lists.head{items={1, 2, 3}, wrap=true}", {})
        assert result == 1

        # Test with explicit false
        result = evaluate_expression("lists.head{items={1, 2, 3}, wrap=false}", {})
        assert result == 1

        # Test positional with boolean values
        result = evaluate_expression("lists.head({1, 2, 3}, nil, nil, nil, false)", {})
        assert result == 1
