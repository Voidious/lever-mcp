import sys
import os
from lib.lua import evaluate_expression


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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


class TestLuaFunctionReturns:
    """Test function returns that apply to current item."""

    def test_string_function_return(self):
        result = evaluate_expression("strings.upper_case", "hello")
        assert result == "HELLO"

        result = evaluate_expression("strings.is_alpha", "hello123")
        assert result is False

    def test_list_function_return(self):
        result = evaluate_expression("lists.head", [1, 2, 3])
        assert result == 1

        result = evaluate_expression("lists.last", ["a", "b", "c"])
        assert result == "c"

    def test_any_function_return(self):
        result = evaluate_expression("any.is_empty", "")
        assert result is True

        result = evaluate_expression("any.is_nil", None)
        assert result is True


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
