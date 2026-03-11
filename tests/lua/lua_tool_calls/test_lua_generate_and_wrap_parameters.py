from lib.lua import evaluate_expression


class TestLuaGenerateOperations:
    """Test generate tool operations via Lua function calls."""

    def test_generate_range(self):
        # Table syntax with from/to parameters
        result = evaluate_expression("generate.range({from=0, to=5})", {})
        assert result == [0, 1, 2, 3, 4]

        result = evaluate_expression("generate.range({from=1, to=10, step=2})", {})
        assert result == [1, 3, 5, 7, 9]

        result = evaluate_expression("generate.range({from=0, to=3})", {})
        assert result == [0, 1, 2]

    def test_generate_repeat(self):
        # Use bracket syntax because 'repeat' is a Lua reserved keyword
        result = evaluate_expression('generate["repeat"]({value="x", count=3})', {})
        assert result == ["x", "x", "x"]

        result = evaluate_expression('generate["repeat"]({value="hello", count=2})', {})
        assert result == ["hello", "hello"]

    def test_generate_cycle(self):
        result = evaluate_expression("generate.cycle({items={1, 2}, count=5})", {})
        assert result == [1, 2, 1, 2, 1]

        result = evaluate_expression(
            'generate.cycle({items={"a", "b", "c"}, count=7})', {}
        )
        assert result == ["a", "b", "c", "a", "b", "c", "a"]

    def test_generate_accumulate(self):
        # Running totals (default addition)
        result = evaluate_expression("generate.accumulate({items={1, 2, 3, 4}})", {})
        assert result == [1, 3, 6, 10]  # [1, 1+2, 1+2+3, 1+2+3+4]

        result = evaluate_expression("generate.accumulate({items={5, 10, 15}})", {})
        assert result == [5, 15, 30]

        # Test explicit add function
        result = evaluate_expression(
            'generate.accumulate({items={1, 2, 3}, func="add"})', {}
        )
        assert result == [1, 3, 6]

    def test_generate_accumulate_functions(self):
        """Test accumulate with different functions."""
        # Test multiplication
        result = evaluate_expression(
            'generate.accumulate({items={1, 2, 3, 4}, func="mul"})', {}
        )
        assert result == [1, 2, 6, 24]  # [1, 1*2, 1*2*3, 1*2*3*4]

        # Test max
        result = evaluate_expression(
            'generate.accumulate({items={5, 2, 8, 1}, func="max"})', {}
        )
        assert result == [5, 5, 8, 8]  # Running maximum

        # Test min
        result = evaluate_expression(
            'generate.accumulate({items={5, 2, 8, 1}, func="min"})', {}
        )
        assert result == [5, 2, 2, 1]  # Running minimum

        # Test subtraction
        result = evaluate_expression(
            'generate.accumulate({items={10, 3, 2}, func="sub"})', {}
        )
        assert result == [10, 7, 5]  # [10, 10-3, 7-2]

        # Test division
        result = evaluate_expression(
            'generate.accumulate({items={100, 2, 5}, func="div"})', {}
        )
        assert result == [100, 50.0, 10.0]  # [100, 100/2, 50/5]

    def test_generate_cartesian_product(self):
        # Cartesian product of multiple lists
        result = evaluate_expression(
            'generate.cartesian_product({lists={{1, 2}, {"a", "b"}}})', {}
        )
        # Result comes as tuples, not lists
        expected = [(1, "a"), (1, "b"), (2, "a"), (2, "b")]
        assert sorted(result) == sorted(expected)

    def test_generate_combinations(self):
        # All combinations of given length
        result = evaluate_expression(
            'generate.combinations({items={"a", "b", "c"}, length=2})', {}
        )
        assert len(result) == 3  # C(3,2) = 3
        assert ["a", "b"] in result or ("a", "b") in result

    def test_generate_permutations(self):
        # All permutations of given length
        result = evaluate_expression(
            'generate.permutations({items={"a", "b"}, length=2})', {}
        )
        assert len(result) == 2  # P(2,2) = 2

        # Default length (all permutations)
        result = evaluate_expression('generate.permutations({items={"x", "y"}})', {})
        assert len(result) == 2

    def test_generate_powerset(self):
        # All possible subsets
        result = evaluate_expression("generate.powerset({items={1, 2}})", {})
        assert len(result) == 4  # 2^2 = 4 subsets
        assert (
            [] in result or {} in result
        )  # Empty subset (could be [] or {} depending on conversion)

        # Table syntax
        result = evaluate_expression('generate.powerset({items={"a"}})', {})
        assert len(result) == 2  # Empty subset and ["a"]

    def test_generate_unique_pairs(self):
        # All unique pairs from a list
        result = evaluate_expression("generate.unique_pairs({items={1, 2, 3}})", {})
        assert len(result) == 3  # (1,2), (1,3), (2,3)

        # Table syntax
        result = evaluate_expression(
            'generate.unique_pairs({items={"a", "b", "c", "d"}})', {}
        )
        assert len(result) == 6  # C(4,2) = 6

    def test_generate_windowed(self):
        # Sliding windows of given size
        result = evaluate_expression(
            "generate.windowed({items={1, 2, 3, 4}, size=3})", {}
        )
        assert result == [[1, 2, 3], [2, 3, 4]]

        # Table syntax
        result = evaluate_expression(
            'generate.windowed({items={"a", "b", "c"}, size=2})', {}
        )
        assert result == [["a", "b"], ["b", "c"]]

    def test_generate_zip_with_index(self):
        # Tuples of (index, value)
        result = evaluate_expression(
            'generate.zip_with_index({items={"a", "b", "c"}})', {}
        )
        assert result == [[0, "a"], [1, "b"], [2, "c"]]

        # Table syntax
        result = evaluate_expression("generate.zip_with_index({items={10, 20}})", {})
        assert result == [[0, 10], [1, 20]]


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


class TestGenerateWrapParameter:
    """Comprehensive test coverage for generate function wrap parameter."""

    def test_generate_range_wrap(self):
        """Test range operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression("generate.range({from=0, to=3})", {})
        assert result == [0, 1, 2]

        # With wrap=true
        result = evaluate_expression("generate.range({from=0, to=3, wrap=true})", {})
        expected = {"__type": "list", "data": [0, 1, 2]}
        assert result == expected

        # With wrap=false (explicit)
        result = evaluate_expression("generate.range({from=0, to=3, wrap=false})", {})
        assert result == [0, 1, 2]

        # Empty range with wrap
        result = evaluate_expression("generate.range({from=5, to=5, wrap=true})", {})
        expected = {"__type": "list", "data": []}
        assert result == expected

    def test_generate_repeat_wrap(self):
        """Test repeat operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression('generate["repeat"]({value="x", count=3})', {})
        assert result == ["x", "x", "x"]

        # With wrap=true
        result = evaluate_expression(
            'generate["repeat"]({value="x", count=3, wrap=true})', {}
        )
        expected = {"__type": "list", "data": ["x", "x", "x"]}
        assert result == expected

        # Empty repeat with wrap
        result = evaluate_expression(
            'generate["repeat"]({value="test", count=0, wrap=true})', {}
        )
        expected = {"__type": "list", "data": []}
        assert result == expected

    def test_generate_cycle_wrap(self):
        """Test cycle operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression("generate.cycle({items={1, 2}, count=5})", {})
        assert result == [1, 2, 1, 2, 1]

        # With wrap=true
        result = evaluate_expression(
            "generate.cycle({items={1, 2}, count=5, wrap=true})", {}
        )
        expected = {"__type": "list", "data": [1, 2, 1, 2, 1]}
        assert result == expected

        # Empty cycle with wrap
        result = evaluate_expression(
            "generate.cycle({items={1, 2}, count=0, wrap=true})", {}
        )
        expected = {"__type": "list", "data": []}
        assert result == expected

    def test_generate_accumulate_wrap(self):
        """Test accumulate operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression("generate.accumulate({items={1, 2, 3}})", {})
        assert result == [1, 3, 6]

        # With wrap=true
        result = evaluate_expression(
            "generate.accumulate({items={1, 2, 3}, wrap=true})", {}
        )
        expected = {"__type": "list", "data": [1, 3, 6]}
        assert result == expected

        # Empty accumulate with wrap
        result = evaluate_expression("generate.accumulate({items={}, wrap=true})", {})
        expected = {"__type": "list", "data": []}
        assert result == expected

    def test_generate_cartesian_product_wrap(self):
        """Test cartesian_product operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression(
            'generate.cartesian_product({lists={{1, 2}, {"a", "b"}}})', {}
        )
        expected = [(1, "a"), (1, "b"), (2, "a"), (2, "b")]
        assert sorted(result) == sorted(expected)

        # With wrap=true
        result = evaluate_expression(
            'generate.cartesian_product({lists={{1, 2}, {"a", "b"}}, wrap=true})', {}
        )
        expected_data = [(1, "a"), (1, "b"), (2, "a"), (2, "b")]
        assert result["__type"] == "list"
        assert sorted(result["data"]) == sorted(expected_data)

        # Empty cartesian product with wrap
        result = evaluate_expression(
            "generate.cartesian_product({lists={{}}, wrap=true})", {}
        )
        expected = {"__type": "list", "data": []}
        assert result == expected

    def test_generate_combinations_wrap(self):
        """Test combinations operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression(
            "generate.combinations({items={1, 2, 3}, length=2})", {}
        )
        assert len(result) == 3  # C(3,2) = 3

        # With wrap=true
        result = evaluate_expression(
            "generate.combinations({items={1, 2, 3}, length=2, wrap=true})", {}
        )
        assert result["__type"] == "list"
        assert len(result["data"]) == 3

        # Empty combinations with wrap
        result = evaluate_expression(
            "generate.combinations({items={}, length=2, wrap=true})", {}
        )
        expected = {"__type": "list", "data": []}
        assert result == expected

    def test_generate_permutations_wrap(self):
        """Test permutations operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression("generate.permutations({items={1, 2}})", {})
        assert len(result) == 2  # P(2,2) = 2

        # With wrap=true
        result = evaluate_expression(
            "generate.permutations({items={1, 2}, wrap=true})", {}
        )
        assert result["__type"] == "list"
        assert len(result["data"]) == 2

        # Empty permutations with wrap
        result = evaluate_expression("generate.permutations({items={}, wrap=true})", {})
        expected = {"__type": "list", "data": [{"__type": "list", "data": []}]}
        assert result == expected

    def test_generate_powerset_wrap(self):
        """Test powerset operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression("generate.powerset({items={1, 2}})", {})
        assert len(result) == 4  # 2^2 = 4 subsets

        # With wrap=true
        result = evaluate_expression("generate.powerset({items={1, 2}, wrap=true})", {})
        assert result["__type"] == "list"
        assert len(result["data"]) == 4

        # Empty powerset with wrap
        result = evaluate_expression("generate.powerset({items={}, wrap=true})", {})
        expected = {
            "__type": "list",
            "data": [{"__type": "list", "data": []}],
        }  # Powerset of empty set is {∅}
        assert result == expected

    def test_generate_unique_pairs_wrap(self):
        """Test unique_pairs operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression("generate.unique_pairs({items={1, 2, 3}})", {})
        assert len(result) == 3  # C(3,2) = 3 unique pairs

        # With wrap=true
        result = evaluate_expression(
            "generate.unique_pairs({items={1, 2, 3}, wrap=true})", {}
        )
        assert result["__type"] == "list"
        assert len(result["data"]) == 3

        # Empty unique_pairs with wrap
        result = evaluate_expression("generate.unique_pairs({items={}, wrap=true})", {})
        expected = {"__type": "list", "data": []}
        assert result == expected

    def test_generate_windowed_wrap(self):
        """Test windowed operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression(
            "generate.windowed({items={1, 2, 3, 4}, size=2})", {}
        )
        assert len(result) == 3  # 3 windows of size 2

        # With wrap=true
        result = evaluate_expression(
            "generate.windowed({items={1, 2, 3, 4}, size=2, wrap=true})", {}
        )
        assert result["__type"] == "list"
        assert len(result["data"]) == 3

        # Empty windowed with wrap
        result = evaluate_expression(
            "generate.windowed({items={}, size=2, wrap=true})", {}
        )
        expected = {"__type": "list", "data": []}
        assert result == expected

    def test_generate_zip_with_index_wrap(self):
        """Test zip_with_index operation with wrap parameter."""
        # Without wrap
        result = evaluate_expression(
            "generate.zip_with_index({items={10, 20, 30}})", {}
        )
        assert result == [[0, 10], [1, 20], [2, 30]]

        # With wrap=true
        result = evaluate_expression(
            "generate.zip_with_index({items={10, 20, 30}, wrap=true})", {}
        )
        expected = {
            "__type": "list",
            "data": [
                {"__type": "list", "data": [0, 10]},
                {"__type": "list", "data": [1, 20]},
                {"__type": "list", "data": [2, 30]},
            ],
        }
        assert result == expected

        # Empty zip_with_index with wrap
        result = evaluate_expression(
            "generate.zip_with_index({items={}, wrap=true})", {}
        )
        # zip_with_index returns empty dict for empty input, not empty list
        expected = {"__type": "list", "data": []}
        # Actually, let's check what it really returns
        # It might return an empty dict when converted, so let's be flexible
        assert result["__type"] == "list"
        assert len(result["data"]) == 0
