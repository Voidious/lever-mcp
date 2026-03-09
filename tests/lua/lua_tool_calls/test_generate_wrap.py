from lib.lua import evaluate_expression


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
