"""
Comprehensive tests for wrap parameter behavior across all tool operations.

This test suite ensures that:
1. Operations returning lists/dicts are properly wrapped when wrap=true
2. Operations returning scalar values are NOT wrapped when wrap=true
3. All operations work correctly with wrap=false (default behavior)
4. Consistent wrap behavior across lists, strings, dicts, any, and generate tools
"""

from lib.lua import evaluate_expression


class TestListsWrapBehavior:
    """Test wrap parameter behavior for all lists operations."""

    def test_list_returning_operations_with_wrap_true(self):
        """Test that operations returning lists are properly wrapped when wrap=true."""

        # Pure operations returning lists
        test_cases = [
            # operation, input_expression, expected_wrapped_type
            ("shuffle", "lists.shuffle({items={1, 2, 3}, wrap=true})", "list"),
            ("tail", "lists.tail({items={1, 2, 3}, wrap=true})", "list"),
            ("initial", "lists.initial({items={1, 2, 3}, wrap=true})", "list"),
            ("drop", "lists.drop({items={1, 2, 3, 4}, param=2, wrap=true})", "list"),
            ("take", "lists.take({items={1, 2, 3, 4}, param=2, wrap=true})", "list"),
            ("flatten", "lists.flatten({items={{1, 2}, {3, 4}}, wrap=true})", "list"),
            ("compact", 'lists.compact({items={1, 0, 2, "", 3}, wrap=true})', "list"),
            ("chunk", "lists.chunk({items={1, 2, 3, 4}, param=2, wrap=true})", "list"),
            ("union", "lists.union({items={{1, 2}, {2, 3}}, wrap=true})", "list"),
            (
                "difference",
                "lists.difference({items={1, 2, 3}, others={2, 3}, wrap=true})",
                "list",
            ),
            (
                "intersection",
                "lists.intersection({items={1, 2, 3}, others={2, 3}, wrap=true})",
                "list",
            ),
        ]

        for operation, expression, expected_type in test_cases:
            result = evaluate_expression(expression, {})
            assert isinstance(
                result, dict
            ), f"{operation} should return wrapped structure"
            assert (
                result.get("__type") == expected_type
            ), f"{operation} should wrap as {expected_type}"
            assert "data" in result, f"{operation} should have data field when wrapped"

    def test_expression_based_list_operations_with_wrap_true(self):
        """Test expression-based operations returning lists are properly wrapped."""

        test_cases = [
            (
                "filter_by",
                (
                    "lists.filter_by({items={1, 2, 3, 4}, "
                    'expression="item > 2", wrap=true})'
                ),
                "list",
            ),
            (
                "map",
                'lists.map({items={1, 2}, expression="item * 2", wrap=true})',
                "list",
            ),
            (
                "sort_by",
                (
                    "lists.sort_by({items={{age=30}, {age=20}}, "
                    'expression="age", wrap=true})'
                ),
                "list",
            ),
            (
                "uniq_by",
                (
                    "lists.uniq_by({items={{id=1}, {id=2}, {id=1}}, "
                    'expression="id", wrap=true})'
                ),
                "list",
            ),
            (
                "pluck",
                (
                    'lists.pluck({items={{name="a"}, {name="b"}}, '
                    'expression="name", wrap=true})'
                ),
                "list",
            ),
            (
                "partition",
                (
                    "lists.partition({items={1, 2, 3, 4}, "
                    'expression="item > 2", wrap=true})'
                ),
                "list",
            ),
            (
                "flat_map",
                'lists.flat_map({items={1, 2}, expression="{item, item}", wrap=true})',
                "list",
            ),
        ]

        for operation, expression, expected_type in test_cases:
            result = evaluate_expression(expression, {})
            assert isinstance(
                result, dict
            ), f"{operation} should return wrapped structure"
            assert (
                result.get("__type") == expected_type
            ), f"{operation} should wrap as {expected_type}"
            assert "data" in result, f"{operation} should have data field when wrapped"

    def test_dict_returning_operations_with_wrap_true(self):
        """Test that operations returning dicts are properly wrapped when wrap=true."""

        test_cases = [
            (
                "group_by",
                (
                    "lists.group_by({items={1, 2, 3, 4}, "
                    'expression="item > 2 and \\"big\\" or \\"small\\"", '
                    "wrap=true})"
                ),
                "dict",
            ),
            (
                "count_by",
                (
                    'lists.count_by({items={"a", "b", "a", "c"}, '
                    'expression="item", wrap=true})'
                ),
                "dict",
            ),
            (
                "key_by",
                (
                    'lists.key_by({items={{id=1, name="a"}, {id=2, name="b"}}, '
                    'expression="id", wrap=true})'
                ),
                "dict",
            ),
        ]

        for operation, expression, expected_type in test_cases:
            result = evaluate_expression(expression, {})
            assert isinstance(
                result, dict
            ), f"{operation} should return wrapped structure"
            assert (
                result.get("__type") == expected_type
            ), f"{operation} should wrap as {expected_type}"
            assert "data" in result, f"{operation} should have data field when wrapped"

    def test_scalar_returning_operations_with_wrap_true(self):
        """Test that operations returning scalars are NOT wrapped when wrap=true."""

        # These operations return scalar values and should NOT be wrapped
        test_cases = [
            ("is_empty", "lists.is_empty({items={}, wrap=true})", True),
            ("head", "lists.head({items={5, 6, 7}, wrap=true})", 5),
            ("last", "lists.last({items={5, 6, 7}, wrap=true})", 7),
            ("nth", "lists.nth({items={10, 20, 30}, param=1, wrap=true})", 20),
            ("contains", "lists.contains({items={1, 2, 3}, param=2, wrap=true})", True),
            (
                "is_equal",
                "lists.is_equal({items={1, 2}, param={1, 2}, wrap=true})",
                True,
            ),
            ("min", "lists.min({items={3, 1, 4}, wrap=true})", 1),
            ("max", "lists.max({items={3, 1, 4}, wrap=true})", 4),
            (
                "join",
                'lists.join({items={"a", "b", "c"}, param=",", wrap=true})',
                "a,b,c",
            ),
            (
                "find_by",
                'lists.find_by({items={1, 2, 3}, expression="item > 2", wrap=true})',
                3,
            ),
            (
                "index_of",
                (
                    "lists.index_of({items={10, 20, 30}, "
                    'expression="item == 20", wrap=true})'
                ),
                1,
            ),
            (
                "all_by",
                (
                    "lists.all_by({items={2, 4, 6}, "
                    'expression="item % 2 == 0", wrap=true})'
                ),
                True,
            ),
            (
                "any_by",
                (
                    "lists.any_by({items={1, 3, 5}, "
                    'expression="item % 2 == 0", wrap=true})'
                ),
                False,
            ),
        ]

        for operation, expression, expected_value in test_cases:
            result = evaluate_expression(expression, {})
            # Should return the scalar value directly, not wrapped
            assert result == expected_value, (
                f"{operation} should return unwrapped scalar: "
                f"{expected_value}, got: {result}"
            )
            assert (
                not isinstance(result, dict) or "__type" not in result
            ), f"{operation} should NOT be wrapped"

    def test_operations_with_wrap_false_default(self):
        """Test that operations work correctly with wrap=false (default behavior)."""

        # Test a few representative operations to ensure wrap=false works
        test_cases = [
            (
                "filter_by",
                'lists.filter_by({items={1, 2, 3, 4}, expression="item > 2"})',
                [3, 4],
            ),
            ("map", 'lists.map({items={1, 2}, expression="item * 2"})', [2, 4]),
            (
                "group_by",
                "lists.group_by({items={1, 2, 3}, "
                'expression="item > 1 and \\"big\\" or \\"small\\""})',
                {"small": [1], "big": [2, 3]},
            ),
            ("head", "lists.head({items={5, 6, 7}})", 5),
            ("is_empty", "lists.is_empty({items={}})", True),
        ]

        for operation, expression, expected_value in test_cases:
            result = evaluate_expression(expression, {})
            assert result == expected_value, (
                f"{operation} with wrap=false should return: "
                f"{expected_value}, got: {result}"
            )

    def test_operations_with_explicit_wrap_false(self):
        """Test that operations work correctly with explicit wrap=false."""

        # Test that explicitly setting wrap=false works the same as default
        test_cases = [
            (
                "filter_by",
                (
                    "lists.filter_by({items={1, 2, 3, 4}, "
                    'expression="item > 2", wrap=false})'
                ),
                [3, 4],
            ),
            (
                "group_by",
                (
                    "lists.group_by({items={1, 2}, "
                    'expression="item > 1 and \\"big\\" or \\"small\\"", '
                    "wrap=false})"
                ),
                {"small": [1], "big": [2]},
            ),
        ]

        for operation, expression, expected_value in test_cases:
            result = evaluate_expression(expression, {})
            assert result == expected_value, (
                f"{operation} with explicit wrap=false should return: "
                f"{expected_value}, got: {result}"
            )

    def test_edge_cases_with_wrap(self):
        """Test edge cases for wrap behavior."""

        # Empty list operations with wrap=true
        result = evaluate_expression(
            'lists.filter_by({items={}, expression="true", wrap=true})', {}
        )
        assert result == {
            "__type": "list",
            "data": [],
        }, "Empty filtered list should be wrapped"

        # Nil result with wrap=true (should not be wrapped)
        result = evaluate_expression("lists.head({items={}, wrap=true})", {})
        assert result is None, "Nil result should not be wrapped"

        # Single item list with wrap=true
        result = evaluate_expression(
            'lists.filter_by({items={5}, expression="true", wrap=true})', {}
        )
        assert result == {
            "__type": "list",
            "data": [5],
        }, "Single item list should be wrapped"


class TestStringsWrapBehavior:
    """Test wrap parameter behavior for strings operations."""

    def test_list_returning_strings_operations_with_wrap_true(self):
        """
        Test that strings operations returning lists are properly wrapped
        when wrap=true.
        """

        # Only split returns a list in strings tool
        result = evaluate_expression(
            'strings.split({text="a,b,c", param=",", wrap=true})', {}
        )
        assert isinstance(result, dict), "split should return wrapped structure"
        assert result.get("__type") == "list", "split should wrap as list"
        assert result.get("data") == ["a", "b", "c"], "split should have correct data"

    def test_scalar_returning_strings_operations_with_wrap_true(self):
        """
        Test that strings operations returning scalars are NOT wrapped
        when wrap=true.
        """

        test_cases = [
            ("upper_case", 'strings.upper_case({text="hello", wrap=true})', "HELLO"),
            ("lower_case", 'strings.lower_case({text="HELLO", wrap=true})', "hello"),
            (
                "camel_case",
                'strings.camel_case({text="hello world", wrap=true})',
                "helloWorld",
            ),
            (
                "snake_case",
                'strings.snake_case({text="hello world", wrap=true})',
                "hello_world",
            ),
            (
                "contains",
                'strings.contains({text="hello", param="ell", wrap=true})',
                True,
            ),
            ("is_empty", 'strings.is_empty({text="", wrap=true})', True),
            (
                "is_equal",
                'strings.is_equal({text="hello", param="hello", wrap=true})',
                True,
            ),
            ("trim", 'strings.trim({text="  hello  ", wrap=true})', "hello"),
        ]

        for operation, expression, expected_value in test_cases:
            result = evaluate_expression(expression, {})
            assert result == expected_value, (
                f"strings.{operation} should return unwrapped scalar: "
                f"{expected_value}, got: {result}"
            )
            assert (
                not isinstance(result, dict) or "__type" not in result
            ), f"strings.{operation} should NOT be wrapped"


class TestDictsWrapBehavior:
    """Test wrap parameter behavior for dicts operations."""

    def test_dict_returning_operations_with_wrap_true(self):
        """
        Test that dicts operations returning dicts are properly wrapped
        when wrap=true.
        """

        test_cases = [
            (
                "pick",
                'dicts.pick({obj={a=1, b=2, c=3}, param={"a", "b"}, wrap=true})',
                "dict",
            ),
            (
                "omit",
                'dicts.omit({obj={a=1, b=2, c=3}, param={"c"}, wrap=true})',
                "dict",
            ),
            ("merge", "dicts.merge({obj={{a=1}, {b=2}}, wrap=true})", "dict"),
            ("invert", "dicts.invert({obj={a=1, b=2}, wrap=true})", "dict"),
            (
                "set_value",
                'dicts.set_value({obj={a=1}, path="b", value=2, wrap=true})',
                "dict",
            ),
        ]

        for operation, expression, expected_type in test_cases:
            result = evaluate_expression(expression, {})
            assert isinstance(
                result, dict
            ), f"dicts.{operation} should return wrapped structure"
            assert (
                result.get("__type") == expected_type
            ), f"dicts.{operation} should wrap as {expected_type}"
            assert (
                "data" in result
            ), f"dicts.{operation} should have data field when wrapped"

    def test_list_returning_dicts_operations_with_wrap_true(self):
        """
        Test that dicts operations returning lists are properly wrapped
        when wrap=true.
        """

        test_cases = [
            ("keys", "dicts.keys({obj={a=1, b=2}, wrap=true})", "list"),
            ("values", "dicts.values({obj={a=1, b=2}, wrap=true})", "list"),
            ("items", "dicts.items({obj={a=1, b=2}, wrap=true})", "list"),
        ]

        for operation, expression, expected_type in test_cases:
            result = evaluate_expression(expression, {})
            assert isinstance(
                result, dict
            ), f"dicts.{operation} should return wrapped structure"
            assert (
                result.get("__type") == expected_type
            ), f"dicts.{operation} should wrap as {expected_type}"
            assert (
                "data" in result
            ), f"dicts.{operation} should have data field when wrapped"

    def test_scalar_returning_dicts_operations_with_wrap_true(self):
        """
        Test that dicts operations returning scalars are NOT wrapped
        when wrap=true.
        """

        test_cases = [
            ("has_key", 'dicts.has_key({obj={a=1}, param="a", wrap=true})', True),
            ("is_empty", "dicts.is_empty({obj={}, wrap=true})", True),
            ("is_equal", "dicts.is_equal({obj={a=1}, param={a=1}, wrap=true})", True),
            ("get_value", 'dicts.get_value({obj={a=1}, path="a", wrap=true})', 1),
        ]

        for operation, expression, expected_value in test_cases:
            result = evaluate_expression(expression, {})
            assert result == expected_value, (
                f"dicts.{operation} should return unwrapped scalar: "
                f"{expected_value}, got: {result}"
            )
            assert (
                not isinstance(result, dict) or "__type" not in result
            ), f"dicts.{operation} should NOT be wrapped"


class TestAnyWrapBehavior:
    """Test wrap parameter behavior for any operations."""

    def test_scalar_returning_any_operations_with_wrap_true(self):
        """Test that any operations returning scalars are NOT wrapped when wrap=true."""

        test_cases = [
            ("is_empty", "any.is_empty({value={}, wrap=true})", True),
            ("is_nil", "any.is_nil({value=nil, wrap=true})", True),
            ("is_equal", "any.is_equal({value=5, param=5, wrap=true})", True),
            ("contains", 'any.contains({value="hello", param="ell", wrap=true})', True),
            ("size", "any.size({value={1, 2, 3}, wrap=true})", 3),
        ]

        for operation, expression, expected_value in test_cases:
            result = evaluate_expression(expression, {})
            assert result == expected_value, (
                f"any.{operation} should return unwrapped scalar: "
                f"{expected_value}, got: {result}"
            )
            assert (
                not isinstance(result, dict) or "__type" not in result
            ), f"any.{operation} should NOT be wrapped"


class TestGenerateWrapBehavior:
    """Test wrap parameter behavior for generate operations."""

    def test_list_returning_generate_operations_with_wrap_true(self):
        """
        Test that generate operations returning lists are properly wrapped
        when wrap=true.
        """

        test_cases = [
            ("range", "generate.range({from=1, to=4, wrap=true})", "list"),
            ("repeat", 'generate["repeat"]({value="x", count=3, wrap=true})', "list"),
            ("powerset", "generate.powerset({items={1, 2}, wrap=true})", "list"),
            (
                "combinations",
                "generate.combinations({items={1, 2, 3}, length=2, wrap=true})",
                "list",
            ),
            (
                "permutations",
                "generate.permutations({items={1, 2}, wrap=true})",
                "list",
            ),
        ]

        for operation, expression, expected_type in test_cases:
            result = evaluate_expression(expression, {})
            assert isinstance(
                result, dict
            ), f"generate.{operation} should return wrapped structure"
            assert (
                result.get("__type") == expected_type
            ), f"generate.{operation} should wrap as {expected_type}"
            assert (
                "data" in result
            ), f"generate.{operation} should have data field when wrapped"

    def test_generate_operations_with_wrap_false(self):
        """Test that generate operations work correctly with wrap=false."""

        test_cases = [
            ("range", "generate.range({from=1, to=4})", [1, 2, 3]),
            ("repeat", 'generate["repeat"]({value="x", count=2})', ["x", "x"]),
        ]

        for operation, expression, expected_value in test_cases:
            result = evaluate_expression(expression, {})
            assert result == expected_value, (
                f"generate.{operation} with wrap=false should return: "
                f"{expected_value}, got: {result}"
            )
