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
