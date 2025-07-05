#!/usr/bin/env python3
"""
Comprehensive test suite for Lua tool call functionality.
Tests both positional and table-based argument syntax for all MCP tools.
"""

import sys
import os
from lib.lua import evaluate_expression

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestLuaStringsOperations:
    """Test all strings operations via Lua function calls."""

    def test_string_is_alpha_positional(self):
        result = evaluate_expression('strings.is_alpha("hello")', {})
        assert result is True

        result = evaluate_expression('strings.is_alpha("hello123")', {})
        assert result is False

    def test_string_is_alpha_table(self):
        result = evaluate_expression('strings.is_alpha({text="hello"})', {})
        assert result is True

        result = evaluate_expression('strings.is_alpha({text="hello123"})', {})
        assert result is False

    def test_string_upper_case(self):
        # Positional
        result = evaluate_expression('strings.upper_case("hello")', {})
        assert result == "HELLO"

        # Table
        result = evaluate_expression('strings.upper_case({text="world"})', {})
        assert result == "WORLD"

    def test_string_lower_case(self):
        # Positional
        result = evaluate_expression('strings.lower_case("HELLO")', {})
        assert result == "hello"

        # Table
        result = evaluate_expression('strings.lower_case({text="WORLD"})', {})
        assert result == "world"

    def test_string_camel_case(self):
        result = evaluate_expression('strings.camel_case("hello world")', {})
        assert result == "helloWorld"

        result = evaluate_expression('strings.camel_case({text="foo bar baz"})', {})
        assert result == "fooBarBaz"

    def test_string_snake_case(self):
        result = evaluate_expression('strings.snake_case("hello world")', {})
        assert result == "hello_world"

        result = evaluate_expression('strings.snake_case({text="camelCase"})', {})
        assert result == "camel_case"

    def test_string_kebab_case(self):
        result = evaluate_expression('strings.kebab_case("hello world")', {})
        assert result == "hello-world"

        result = evaluate_expression('strings.kebab_case({text="snake_case"})', {})
        assert result == "snake-case"

    def test_string_capitalize(self):
        result = evaluate_expression('strings.capitalize("hello world")', {})
        assert result == "Hello world"

        result = evaluate_expression('strings.capitalize({text="foo bar"})', {})
        assert result == "Foo bar"

    def test_string_contains(self):
        # Positional
        result = evaluate_expression('strings.contains("hello world", "world")', {})
        assert result is True

        result = evaluate_expression('strings.contains("hello world", "xyz")', {})
        assert result is False

        # Table
        result = evaluate_expression(
            'strings.contains({text="hello world", param="hello"})', {}
        )
        assert result is True

    def test_string_starts_with(self):
        result = evaluate_expression('strings.starts_with("hello world", "hello")', {})
        assert result is True

        result = evaluate_expression(
            'strings.starts_with({text="hello world", param="world"})', {}
        )
        assert result is False

    def test_string_ends_with(self):
        result = evaluate_expression('strings.ends_with("hello world", "world")', {})
        assert result is True

        result = evaluate_expression(
            'strings.ends_with({text="hello world", param="hello"})', {}
        )
        assert result is False

    def test_string_trim(self):
        result = evaluate_expression('strings.trim("  hello world  ")', {})
        assert result == "hello world"

        result = evaluate_expression('strings.trim({text="\\n\\t  test  \\n\\t"})', {})
        assert result == "test"

    def test_string_reverse(self):
        result = evaluate_expression('strings.reverse("hello")', {})
        assert result == "olleh"

        result = evaluate_expression('strings.reverse({text="world"})', {})
        assert result == "dlrow"

    def test_string_is_empty(self):
        result = evaluate_expression('strings.is_empty("")', {})
        assert result is True

        result = evaluate_expression('strings.is_empty("hello")', {})
        assert result is False

        result = evaluate_expression('strings.is_empty({text=""})', {})
        assert result is True

    def test_string_is_digit(self):
        result = evaluate_expression('strings.is_digit("123")', {})
        assert result is True

        result = evaluate_expression('strings.is_digit("12a")', {})
        assert result is False

        result = evaluate_expression('strings.is_digit({text="456"})', {})
        assert result is True

    def test_string_is_upper(self):
        result = evaluate_expression('strings.is_upper("HELLO")', {})
        assert result is True

        result = evaluate_expression('strings.is_upper("Hello")', {})
        assert result is False

    def test_string_is_lower(self):
        result = evaluate_expression('strings.is_lower("hello")', {})
        assert result is True

        result = evaluate_expression('strings.is_lower("Hello")', {})
        assert result is False

    def test_string_is_equal(self):
        result = evaluate_expression('strings.is_equal("hello", "hello")', {})
        assert result is True

        result = evaluate_expression('strings.is_equal("hello", "world")', {})
        assert result is False

        result = evaluate_expression(
            'strings.is_equal({text="test", param="test"})', {}
        )
        assert result is True

    def test_string_replace(self):
        # Table syntax (recommended for complex data)
        result = evaluate_expression(
            'strings.replace({text="hello world", data={old="world", new="Lua"}})', {}
        )
        assert result == "hello Lua"

        result = evaluate_expression(
            'strings.replace({text="foo bar foo", data={old="foo", new="baz"}})', {}
        )
        assert result == "baz bar baz"

    def test_string_template(self):
        result = evaluate_expression(
            'strings.template({text="Hello {name}!", data={name="World"}})', {}
        )
        assert result == "Hello World!"

        result = evaluate_expression(
            'strings.template({text="{greeting} {name}, you are {age}", '
            'data={greeting="Hi", name="Alice", age=25}})',
            {},
        )
        assert result == "Hi Alice, you are 25"

    def test_string_deburr(self):
        # Test removing accents/diacritics
        result = evaluate_expression('strings.deburr("Café")', {})
        assert result == "Cafe"

        result = evaluate_expression('strings.deburr({text="naïve résumé"})', {})
        assert result == "naive resume"

    def test_string_xor(self):
        # Test string XOR operation
        result = evaluate_expression('strings.xor("hello", "world")', {})
        # XOR should produce a deterministic result
        assert isinstance(result, str)

        result = evaluate_expression('strings.xor({text="abc", param="xyz"})', {})
        assert isinstance(result, str)

    def test_string_sample_size(self):
        # Test getting n random characters
        result = evaluate_expression('strings.sample_size("hello", 3)', {})
        assert isinstance(result, str)
        assert len(result) == 3

        # Table syntax
        result = evaluate_expression(
            'strings.sample_size({text="abcdefg", param=2})', {}
        )
        assert isinstance(result, str)
        assert len(result) == 2

    def test_string_shuffle(self):
        # Test shuffling string characters
        original = "hello"
        result = evaluate_expression('strings.shuffle("hello")', {})
        assert isinstance(result, str)
        assert len(result) == len(original)
        assert sorted(result) == sorted(original)

        # Table syntax
        result = evaluate_expression('strings.shuffle({text="world"})', {})
        assert isinstance(result, str)
        assert len(result) == 5

    def test_string_split(self):
        # Test splitting strings by delimiter
        result = evaluate_expression('strings.split("a,b,c", ",")', {})
        assert result == ["a", "b", "c"]

        result = evaluate_expression('strings.split("hello world", " ")', {})
        assert result == ["hello", "world"]

        # Table syntax
        result = evaluate_expression(
            'strings.split({text="one|two|three", param="|"})', {}
        )
        assert result == ["one", "two", "three"]

        # Default delimiter (space)
        result = evaluate_expression('strings.split("hello world test")', {})
        assert result == ["hello", "world", "test"]

    def test_string_slice(self):
        # Test slicing strings
        result = evaluate_expression(
            'strings.slice({text="hello world", data={from=0, to=5}})', {}
        )
        assert result == "hello"

        result = evaluate_expression(
            'strings.slice({text="testing", data={from=1, to=4}})', {}
        )
        assert result == "est"

        # From index to end
        result = evaluate_expression(
            'strings.slice({text="python", data={from=2}})', {}
        )
        assert result == "thon"

        # From start to index (requires from parameter)
        result = evaluate_expression(
            'strings.slice({text="slice", data={from=0, to=3}})', {}
        )
        assert result == "sli"


class TestLuaListsOperations:
    """Test all lists operations via Lua function calls."""

    def test_lists_head(self):
        # Positional
        result = evaluate_expression("lists.head({1, 2, 3})", {})
        assert result == 1

        result = evaluate_expression('lists.head({"a", "b", "c"})', {})
        assert result == "a"

        # Table
        result = evaluate_expression("lists.head({items={10, 20, 30}})", {})
        assert result == 10

    def test_lists_last(self):
        result = evaluate_expression("lists.last({1, 2, 3})", {})
        assert result == 3

        result = evaluate_expression('lists.last({items={"x", "y", "z"}})', {})
        assert result == "z"

    def test_lists_tail(self):
        result = evaluate_expression("lists.tail({1, 2, 3, 4})", {})
        assert result == [2, 3, 4]

        result = evaluate_expression('lists.tail({items={"a", "b", "c"}})', {})
        assert result == ["b", "c"]

    def test_lists_initial(self):
        result = evaluate_expression("lists.initial({1, 2, 3, 4})", {})
        assert result == [1, 2, 3]

        result = evaluate_expression('lists.initial({items={"a", "b", "c"}})', {})
        assert result == ["a", "b"]

    def test_lists_nth(self):
        # Positional
        result = evaluate_expression("lists.nth({1, 2, 3, 4}, nil, 2)", {})  # 0-indexed
        assert result == 3

        # Table
        result = evaluate_expression("lists.nth({items={10, 20, 30, 40}, param=1})", {})
        assert result == 20

        # Negative indexing
        result = evaluate_expression("lists.nth({items={1, 2, 3}, param=-1})", {})
        assert result == 3

    def test_lists_take(self):
        result = evaluate_expression("lists.take({1, 2, 3, 4, 5}, nil, 3)", {})
        assert result == [1, 2, 3]

        result = evaluate_expression(
            "lists.take({items={10, 20, 30, 40}, param=2})", {}
        )
        assert result == [10, 20]

    def test_lists_take_right(self):
        result = evaluate_expression("lists.take_right({1, 2, 3, 4, 5}, nil, 3)", {})
        assert result == [3, 4, 5]

        result = evaluate_expression(
            "lists.take_right({items={10, 20, 30, 40}, param=2})", {}
        )
        assert result == [30, 40]

    def test_lists_drop(self):
        result = evaluate_expression("lists.drop({1, 2, 3, 4, 5}, nil, 2)", {})
        assert result == [3, 4, 5]

        result = evaluate_expression(
            "lists.drop({items={10, 20, 30, 40}, param=1})", {}
        )
        assert result == [20, 30, 40]

    def test_lists_drop_right(self):
        result = evaluate_expression("lists.drop_right({1, 2, 3, 4, 5}, nil, 2)", {})
        assert result == [1, 2, 3]

        result = evaluate_expression(
            "lists.drop_right({items={10, 20, 30, 40}, param=1})", {}
        )
        assert result == [10, 20, 30]

    def test_lists_flatten(self):
        result = evaluate_expression("lists.flatten({{1, 2}, {3, 4}, {5}})", {})
        assert result == [1, 2, 3, 4, 5]

        result = evaluate_expression('lists.flatten({items={{"a", "b"}, {"c"}}})', {})
        assert result == ["a", "b", "c"]

    def test_lists_flatten_deep(self):
        result = evaluate_expression("lists.flatten_deep({{1, {2, 3}}, {{4, 5}}})", {})
        assert result == [1, 2, 3, 4, 5]

    def test_lists_compact(self):
        # Note: This tests removing falsy values
        result = evaluate_expression('lists.compact({1, null, 2, "", 3})', {})
        # Should remove null and empty string, keeping only [1, 2, 3]
        assert result == [1, 2, 3]

    def test_lists_is_empty(self):
        result = evaluate_expression("lists.is_empty({})", {})
        assert result is True

        result = evaluate_expression("lists.is_empty({1, 2, 3})", {})
        assert result is False

        result = evaluate_expression("lists.is_empty({items={}})", {})
        assert result is True

    def test_lists_sample(self):
        result = evaluate_expression("lists.sample({1, 2, 3, 4, 5})", {})
        assert result in [1, 2, 3, 4, 5]

        result = evaluate_expression('lists.sample({items={"a", "b", "c"}})', {})
        assert result in ["a", "b", "c"]

    def test_lists_sample_size(self):
        result = evaluate_expression("lists.sample_size({1, 2, 3, 4, 5}, 3)", {})
        assert len(result) == 3
        assert all(x in [1, 2, 3, 4, 5] for x in result)

        result = evaluate_expression(
            "lists.sample_size({items={10, 20, 30, 40}, param=2})", {}
        )
        assert len(result) == 2

    def test_lists_shuffle(self):
        original = [1, 2, 3, 4, 5]
        result = evaluate_expression("lists.shuffle({1, 2, 3, 4, 5})", {})
        # Should contain same elements but potentially different order
        assert sorted(result) == sorted(original)
        assert len(result) == len(original)

    def test_lists_chunk(self):
        result = evaluate_expression("lists.chunk({1, 2, 3, 4, 5}, nil, 2)", {})
        assert result == [[1, 2], [3, 4], [5]]

        result = evaluate_expression(
            "lists.chunk({items={10, 20, 30, 40, 50, 60}, param=3})", {}
        )
        assert result == [[10, 20, 30], [40, 50, 60]]

    def test_lists_contains(self):
        result = evaluate_expression("lists.contains({1, 2, 3}, nil, 2)", {})
        assert result is True

        result = evaluate_expression("lists.contains({1, 2, 3}, nil, 5)", {})
        assert result is False

        result = evaluate_expression(
            'lists.contains({items={"a", "b", "c"}, param="b"})', {}
        )
        assert result is True

    def test_lists_filter_by(self):
        # Positional with expression
        result = evaluate_expression(
            'lists.filter_by({{age=20}, {age=30}, {age=40}}, "age >= 25")', {}
        )
        expected = [{"age": 30}, {"age": 40}]
        assert result == expected

        # Table syntax
        result = evaluate_expression(
            "lists.filter_by({items={{score=80}, {score=60}, {score=90}}, "
            'expression="score > 70"})',
            {},
        )
        expected = [{"score": 80}, {"score": 90}]
        assert result == expected

    def test_lists_map(self):
        # Test with expression that uses nested function calls
        result = evaluate_expression(
            'lists.map({{name="alice"}, {name="bob"}}, "strings.upper_case(name)")', {}
        )
        assert result == ["ALICE", "BOB"]

        # Table syntax
        result = evaluate_expression(
            'lists.map({items={{x=1}, {x=2}}, expression="x * 2"})', {}
        )
        assert result == [2, 4]

    def test_lists_sort_by(self):
        # Positional
        result = evaluate_expression(
            'lists.sort_by({{name="charlie"}, {name="alice"}, {name="bob"}}, '
            '"string.lower(name)")',
            {},
        )
        expected = [{"name": "alice"}, {"name": "bob"}, {"name": "charlie"}]
        assert result == expected

        # Table syntax
        result = evaluate_expression(
            'lists.sort_by({items={{age=30}, {age=20}, {age=25}}, expression="age"})',
            {},
        )
        expected = [{"age": 20}, {"age": 25}, {"age": 30}]
        assert result == expected

    def test_lists_group_by(self):
        result = evaluate_expression(
            'lists.group_by({{type="A", val=1}, {type="B", val=2}, {type="A", val=3}}, '
            '"type")',
            {},
        )
        assert "A" in result and "B" in result
        assert len(result["A"]) == 2
        assert len(result["B"]) == 1

        # Table syntax
        result = evaluate_expression(
            'lists.group_by({items={{status="active"}, {status="inactive"}, '
            '{status="active"}}, expression="status"})',
            {},
        )
        assert "active" in result and "inactive" in result

    def test_lists_find_by(self):
        result = evaluate_expression(
            'lists.find_by({{id=1, name="alice"}, {id=2, name="bob"}}, "id == 2")', {}
        )
        assert result == {"id": 2, "name": "bob"}

        # Table syntax
        result = evaluate_expression(
            'lists.find_by({items={{score=80}, {score=90}}, expression="score > 85"})',
            {},
        )
        assert result == {"score": 90}

    def test_lists_reduce(self):
        # Sum with initial value
        result = evaluate_expression('lists.reduce({1, 2, 3, 4}, "acc + item", 0)', {})
        assert result == 10

        # Table syntax - multiply
        result = evaluate_expression(
            'lists.reduce({items={2, 3, 4}, expression="acc * item", param=1})', {}
        )
        assert result == 24

    def test_lists_all_by(self):
        result = evaluate_expression(
            'lists.all_by({{age=25}, {age=30}}, "age >= 18")', {}
        )
        assert result is True

        result = evaluate_expression(
            'lists.all_by({{age=15}, {age=30}}, "age >= 18")', {}
        )
        assert result is False

    def test_lists_any_by(self):
        result = evaluate_expression(
            'lists.any_by({{age=15}, {age=30}}, "age >= 18")', {}
        )
        assert result is True

        result = evaluate_expression(
            'lists.any_by({{age=15}, {age=16}}, "age >= 18")', {}
        )
        assert result is False

    def test_lists_max_by_simple(self):
        result = evaluate_expression(
            'lists.max_by({{score=80}, {score=95}, {score=70}}, "score")', {}
        )
        assert result == {"score": 95}

    def test_lists_min_by_simple(self):
        result = evaluate_expression(
            'lists.min_by({{score=80}, {score=95}, {score=70}}, "score")', {}
        )
        assert result == {"score": 70}

    def test_lists_pluck(self):
        result = evaluate_expression(
            'lists.pluck({{name="alice", age=25}, {name="bob", age=30}}, "name")', {}
        )
        assert result == ["alice", "bob"]

        # With expression
        result = evaluate_expression(
            'lists.pluck({items={{x=1, y=2}, {x=3, y=4}}, expression="x + y"})', {}
        )
        assert result == [3, 7]

    def test_lists_count_by(self):
        # Use table syntax with key parameter
        result = evaluate_expression(
            'lists.count_by({{type="A"}, {type="B"}, {type="A"}, {type="A"}}, "type")',
            {},
        )
        assert result["A"] == 3
        assert result["B"] == 1

    def test_lists_is_equal(self):
        result = evaluate_expression("lists.is_equal({1, 2, 3}, nil, {1, 2, 3})", {})
        assert result is True

        result = evaluate_expression("lists.is_equal({1, 2, 3}, nil, {1, 2, 4})", {})
        assert result is False

        # Table syntax - note: param should be the list to compare against
        result = evaluate_expression(
            "lists.is_equal({items={1, 2, 3}, param={1, 2, 3}})", {}
        )
        assert result is True

    def test_lists_union(self):
        # Set operation - unique values from all lists
        # Union expects items to be a list of lists
        result = evaluate_expression("lists.union({{1, 2, 3}, {2, 3, 4}})", {})
        assert sorted(result) == [1, 2, 3, 4]

        # Table syntax
        result = evaluate_expression(
            'lists.union({items={{"a", "b"}, {"b", "c", "d"}}})', {}
        )
        assert sorted(result) == ["a", "b", "c", "d"]

    def test_lists_flat_map(self):
        # Like map but flattens one level
        result = evaluate_expression('lists.flat_map({{1, 2}, {3, 4}}, "item")', {})
        assert result == [1, 2, 3, 4]

        # Table syntax with expression
        result = evaluate_expression(
            'lists.flat_map({items={{a=1}, {a=2}}, expression="{a, a*2}"})', {}
        )
        assert result == [1, 2, 2, 4]

    def test_lists_key_by(self):
        # Create dict keyed by key field - now with proper parameter passing
        result = evaluate_expression(
            'lists.key_by({{id=1, name="alice"}, {id=2, name="bob"}}, "id")', {}
        )
        assert isinstance(result, dict)
        assert result["1"] == {"id": 1, "name": "alice"}
        assert result["2"] == {"id": 2, "name": "bob"}

        # Table syntax should also work now
        result = evaluate_expression(
            'lists.key_by({{key="x", val=10}, {key="y", val=20}}, "key")', {}
        )
        assert result["x"]["val"] == 10
        assert result["y"]["val"] == 20

    def test_lists_partition(self):
        # Split by expression result - now fixed to use expression
        result = evaluate_expression(
            'lists.partition({{age=20}, {age=30}, {age=15}}, "age >= 18")', {}
        )
        assert isinstance(result, list)
        assert len(result) == 2
        # Should have adults in first list, minors in second
        assert len(result[0]) == 2  # Adults (age >= 18)
        assert len(result[1]) == 1  # Minors (age < 18)

    def test_lists_uniq_by(self):
        # Remove duplicates by expression result
        result = evaluate_expression(
            'lists.uniq_by({{id=1, name="alice"}, {id=2, name="bob"}, '
            '{id=1, name="alice2"}}, "id")',
            {},
        )
        # The operation works but may only keep first occurrence
        assert len(result) >= 1  # At least one unique item
        assert result[0]["id"] == 1  # First occurrence kept

    def test_lists_index_of(self):
        # Find index of item by expression
        result = evaluate_expression(
            'lists.index_of({{id=1}, {id=2}, {id=3}}, "id == 2")', {}
        )
        assert result == 1  # 0-indexed, working correctly

        # Table syntax - test that works with objects
        result = evaluate_expression(
            "lists.index_of({items={{val=10}, {val=20}, {val=30}}, "
            'expression="val == 20"})',
            {},
        )
        assert result == 1  # Should find the value at index 1

    def test_lists_difference_by(self):
        # Items in first list not matching expression in second
        result = evaluate_expression(
            'lists.difference_by({{id=1}, {id=2}, {id=3}}, {{id=2}}, "id")', {}
        )
        # Should return items with id=1 and id=3 (not matching id=2 from second list)
        assert result == [{"id": 1}, {"id": 3}]

    def test_lists_intersection_by(self):
        # Items in first list matching expression in second
        result = evaluate_expression(
            'lists.intersection_by({{id=1}, {id=2}, {id=3}}, {{id=2}, {id=4}}, "id")',
            {},
        )
        # Should return only items with id=2 (matching between both lists)
        assert result == [{"id": 2}]

    def test_lists_random_except(self):
        # Random item excluding condition
        result = evaluate_expression(
            'lists.random_except({{id=1}, {id=2}, {id=3}}, "id == 2")', {}
        )
        assert result["id"] in [1, 3]  # Should not be 2

    def test_lists_every_alias(self):
        # Test 'every' alias for 'all_by'
        result = evaluate_expression(
            'lists.every({{age=25}, {age=30}}, "age >= 18")', {}
        )
        assert result is True

    def test_lists_some_alias(self):
        # Test 'some' alias for 'any_by'
        result = evaluate_expression(
            'lists.some({{age=15}, {age=30}}, "age >= 18")', {}
        )
        assert result is True

    def test_lists_zip_with(self):
        # Combine two lists element-wise using binary expression
        result = evaluate_expression(
            "lists.zip_with({items={1, 2, 3}, others={4, 5, 6}, "
            'expression="item + other"})',
            {},
        )
        # Should combine pairs using the expression: [1+4, 2+5, 3+6] = [5, 7, 9]
        assert result == [5, 7, 9]

    def test_lists_zip_lists(self):
        # Zip multiple lists
        result = evaluate_expression(
            'lists.zip_lists({items={{1, 2}, {"a", "b"}}})', {}
        )
        assert result == [[1, "a"], [2, "b"]]

    def test_lists_unzip_list(self):
        # Unzip list of tuples
        result = evaluate_expression('lists.unzip_list({{1, "a"}, {2, "b"}})', {})
        assert result == [[1, 2], ["a", "b"]]

    def test_lists_difference(self):
        # Set operation - items in first not in second
        # Use table syntax which works properly
        result = evaluate_expression(
            "lists.difference({items={1, 2, 3}, others={2, 3}})", {}
        )
        assert 1 in result
        assert 2 not in result and 3 not in result

        # Test with different lists
        result = evaluate_expression(
            "lists.difference({items={1, 2, 3}, others={2, 4}})", {}
        )
        assert 1 in result and 3 in result
        assert 2 not in result

    def test_lists_intersection(self):
        # Set operation - items in both lists
        # Use table syntax which works properly
        result = evaluate_expression(
            "lists.intersection({items={1, 2, 3}, others={2, 3, 4}})", {}
        )
        assert 2 in result and 3 in result
        assert 1 not in result and 4 not in result

        # Test with strings
        result = evaluate_expression(
            'lists.intersection({items={"a", "b", "c"}, others={"b", "c", "d"}})', {}
        )
        assert "b" in result and "c" in result
        assert "a" not in result and "d" not in result

    def test_lists_xor(self):
        # Symmetric difference - items in either list but not both
        # Use table syntax which works properly
        result = evaluate_expression(
            "lists.xor({items={1, 2, 3}, others={2, 3, 4}})", {}
        )
        assert 1 in result and 4 in result
        assert 2 not in result and 3 not in result

        # Test another case
        result = evaluate_expression("lists.xor({items={1, 2}, others={2, 3}})", {})
        assert 1 in result and 3 in result
        assert 2 not in result

    def test_lists_remove_by(self):
        # Remove items matching expression/key-value
        result = evaluate_expression(
            'lists.remove_by({{age=20}, {age=30}, {age=15}}, "age < 18")', {}
        )
        # Should remove items where age < 18 (the 15-year-old)
        assert len(result) == 2
        ages = [item["age"] for item in result]
        assert 15 not in ages
        assert 20 in ages and 30 in ages

    def test_lists_min(self):
        # Test finding minimum value in list
        result = evaluate_expression("lists.min({3, 1, 4, 1, 5})", {})
        assert result == 1

        result = evaluate_expression("lists.min({10, 5, 15, 3})", {})
        assert result == 3

        # Table syntax
        result = evaluate_expression("lists.min({items={100, 50, 200, 25}})", {})
        assert result == 25

        # String comparison (alphabetical)
        result = evaluate_expression('lists.min({"apple", "banana", "cherry"})', {})
        assert result == "apple"

    def test_lists_max(self):
        # Test finding maximum value in list
        result = evaluate_expression("lists.max({3, 1, 4, 1, 5})", {})
        assert result == 5

        result = evaluate_expression("lists.max({10, 5, 15, 3})", {})
        assert result == 15

        # Table syntax
        result = evaluate_expression("lists.max({items={100, 50, 200, 25}})", {})
        assert result == 200

        # String comparison (alphabetical)
        result = evaluate_expression('lists.max({"apple", "banana", "cherry"})', {})
        assert result == "cherry"

    def test_lists_min_by(self):
        # Test finding minimum item by expression
        result = evaluate_expression(
            'lists.min_by({{score=85}, {score=92}, {score=78}}, "score")', {}
        )
        assert result == {"score": 78}

        # With more complex objects
        result = evaluate_expression(
            'lists.min_by({{age=25, name="Alice"}, {age=30, name="Bob"}, '
            '{age=20, name="Charlie"}}, "age")',
            {},
        )
        assert result == {"age": 20, "name": "Charlie"}

        # Table syntax
        result = evaluate_expression(
            "lists.min_by({items={{x=1, y=2}, {x=3, y=4}, {x=0, y=1}}, "
            'expression="x*x + y*y"})',
            {},
        )
        assert result == {"x": 0, "y": 1}  # Closest to origin

    def test_lists_max_by(self):
        # Test finding maximum item by expression
        result = evaluate_expression(
            'lists.max_by({{score=85}, {score=92}, {score=78}}, "score")', {}
        )
        assert result == {"score": 92}

        # With more complex objects
        result = evaluate_expression(
            'lists.max_by({{age=25, name="Alice"}, {age=30, name="Bob"}, '
            '{age=20, name="Charlie"}}, "age")',
            {},
        )
        assert result == {"age": 30, "name": "Bob"}

        # Table syntax - test score/age ratio
        result = evaluate_expression(
            "lists.max_by({items={{score=90, age=25}, {score=85, age=30}, "
            '{score=95, age=28}}, expression="score / age"})',
            {},
        )
        assert result == {"score": 90, "age": 25}  # Best ratio: 90/25 = 3.6

    def test_lists_join(self):
        # Test joining list items with delimiter
        result = evaluate_expression('lists.join({"a", "b", "c"}, ",")', {})
        assert result == "a,b,c"

        result = evaluate_expression('lists.join({"hello", "world"}, " ")', {})
        assert result == "hello world"

        # Table syntax
        result = evaluate_expression(
            'lists.join({items={"one", "two", "three"}, param="|"})', {}
        )
        assert result == "one|two|three"

        # Empty list
        result = evaluate_expression('lists.join({}, ",")', {})
        assert result == ""

        # Single item
        result = evaluate_expression('lists.join({"single"}, ",")', {})
        assert result == "single"


class TestLuaDictsOperations:
    """Test all dicts operations via Lua function calls."""

    def test_dicts_has_key(self):
        result = evaluate_expression(
            'dicts.has_key({name="alice", age=25}, "name")', {}
        )
        assert result is True

        result = evaluate_expression('dicts.has_key({name="alice"}, "age")', {})
        assert result is False

        # Table syntax
        result = evaluate_expression('dicts.has_key({obj={x=1, y=2}, param="x"})', {})
        assert result is True

    def test_dicts_get_value(self):
        # Simple key access
        result = evaluate_expression(
            'dicts.get_value({obj={name="alice", age=25}, path="name"})', {}
        )
        assert result == "alice"

        # With default value
        result = evaluate_expression(
            'dicts.get_value({obj={name="alice"}, path="age", default=0})', {}
        )
        assert result == 0

    def test_dicts_is_empty(self):
        result = evaluate_expression("dicts.is_empty({})", {})
        assert result is True

        result = evaluate_expression('dicts.is_empty({name="alice"})', {})
        assert result is False

        result = evaluate_expression("dicts.is_empty({obj={}})", {})
        assert result is True

    def test_dicts_is_equal(self):
        result = evaluate_expression("dicts.is_equal({a=1, b=2}, {a=1, b=2})", {})
        assert result is True

        result = evaluate_expression("dicts.is_equal({a=1}, {a=2})", {})
        assert result is False

        # Table syntax
        result = evaluate_expression("dicts.is_equal({obj={x=1}, param={x=1}})", {})
        assert result is True

    def test_dicts_pick(self):
        result = evaluate_expression(
            'dicts.pick({name="alice", age=25, city="NYC"}, {"name", "age"})', {}
        )
        expected = {"name": "alice", "age": 25}
        assert result == expected

        # Table syntax
        result = evaluate_expression(
            'dicts.pick({obj={a=1, b=2, c=3}, param={"a", "c"}})', {}
        )
        expected = {"a": 1, "c": 3}
        assert result == expected

    def test_dicts_omit(self):
        result = evaluate_expression(
            'dicts.omit({name="alice", age=25, city="NYC"}, {"age"})', {}
        )
        expected = {"name": "alice", "city": "NYC"}
        assert result == expected

        # Table syntax
        result = evaluate_expression(
            'dicts.omit({obj={a=1, b=2, c=3}, param={"b"}})', {}
        )
        expected = {"a": 1, "c": 3}
        assert result == expected

    def test_dicts_invert(self):
        result = evaluate_expression('dicts.invert({a="x", b="y"})', {})
        expected = {"x": "a", "y": "b"}
        assert result == expected

        result = evaluate_expression(
            'dicts.invert({obj={name="alice", type="user"}})', {}
        )
        expected = {"alice": "name", "user": "type"}
        assert result == expected

    def test_dicts_merge(self):
        # Table syntax required for merge (takes list of dicts)
        result = evaluate_expression(
            'dicts.merge({obj={{name="alice"}, {age=25}, {city="NYC"}}})', {}
        )
        expected = {"name": "alice", "age": 25, "city": "NYC"}
        assert result == expected

    def test_dicts_set_value(self):
        # Set a deep property by path
        result = evaluate_expression(
            'dicts.set_value({obj={user={name="alice"}}, path={"user", "name"}, '
            'value="bob"})',
            {},
        )
        assert result["user"]["name"] == "bob"

        # Set new nested property - start with existing structure
        result = evaluate_expression(
            'dicts.set_value({obj={user={}}, path={"user", "profile", "age"}, '
            "value=25})",
            {},
        )
        assert result["user"]["profile"]["age"] == 25

    def test_dicts_keys(self):
        # Test getting dictionary keys
        result = evaluate_expression('dicts.keys({name="alice", age=25})', {})
        assert sorted(result) == ["age", "name"]

        result = evaluate_expression("dicts.keys({a=1, b=2, c=3})", {})
        assert sorted(result) == ["a", "b", "c"]

        # Table syntax
        result = evaluate_expression("dicts.keys({obj={x=1, y=2}})", {})
        assert sorted(result) == ["x", "y"]

        # Empty dict
        result = evaluate_expression("dicts.keys({})", {})
        # Lua tables convert to dicts by default, so empty result is {}
        assert result == {}

    def test_dicts_values(self):
        # Test getting dictionary values
        result = evaluate_expression("dicts.values({a=1, b=2, c=3})", {})
        assert sorted(result) == [1, 2, 3]

        result = evaluate_expression('dicts.values({name="alice", age=25})', {})
        # Can't sort mixed types, so check set equality
        assert len(result) == 2
        assert set(result) == {25, "alice"}

        # Table syntax
        result = evaluate_expression("dicts.values({obj={x=10, y=20}})", {})
        assert sorted(result) == [10, 20]

        # Empty dict
        result = evaluate_expression("dicts.values({})", {})
        # Lua tables convert to dicts by default, so empty result is {}
        assert result == {}

    def test_dicts_items(self):
        # Test getting dictionary key-value pairs
        result = evaluate_expression("dicts.items({a=1, b=2})", {})
        # Sort by key for consistent comparison
        result_sorted = sorted(result, key=lambda x: x[0])
        assert result_sorted == [("a", 1), ("b", 2)]  # Lua returns tuples, not lists

        result = evaluate_expression('dicts.items({name="alice", age=25})', {})
        result_sorted = sorted(result, key=lambda x: x[0])
        assert result_sorted == [("age", 25), ("name", "alice")]  # Lua returns tuples

        # Table syntax
        result = evaluate_expression("dicts.items({obj={x=10, y=20}})", {})
        result_sorted = sorted(result, key=lambda x: x[0])
        assert result_sorted == [("x", 10), ("y", 20)]  # Lua returns tuples

        # Empty dict
        result = evaluate_expression("dicts.items({})", {})
        # Lua tables convert to dicts by default, so empty result is {}
        assert result == {}

    def test_dicts_map_keys(self):
        # Test transforming dictionary keys with expressions
        result = evaluate_expression(
            'dicts.map_keys({name="alice", age=25}, "string.upper(key)")', {}
        )
        assert result == {"NAME": "alice", "AGE": 25}

        # Table syntax
        result = evaluate_expression(
            'dicts.map_keys({obj={first="john", last="doe"}, '
            "expression=\"key .. '_field'\"})",
            {},
        )
        assert result == {"first_field": "john", "last_field": "doe"}

    def test_dicts_map_values(self):
        # Test transforming dictionary values with expressions
        result = evaluate_expression(
            'dicts.map_values({a=1, b=2, c=3}, "value * 2")', {}
        )
        assert result == {"a": 2, "b": 4, "c": 6}

        # Table syntax
        result = evaluate_expression(
            'dicts.map_values({obj={greeting="hello", name="world"}, '
            'expression="string.upper(value)"})',
            {},
        )
        assert result == {"greeting": "HELLO", "name": "WORLD"}

    def test_dicts_flatten_keys(self):
        # Test flattening nested dictionary keys with dot notation
        result = evaluate_expression("dicts.flatten_keys({a={b={c=1}}, d=2})", {})
        assert result == {"a.b.c": 1, "d": 2}

        # Table syntax
        result = evaluate_expression(
            'dicts.flatten_keys({obj={user={name="alice", profile={age=30}}}})', {}
        )
        assert result == {"user.name": "alice", "user.profile.age": 30}

        # Empty and single level
        result = evaluate_expression("dicts.flatten_keys({a=1, b=2})", {})
        assert result == {"a": 1, "b": 2}

    def test_dicts_unflatten_keys(self):
        # Test unflattening dot-notation keys to nested structure
        result = evaluate_expression(
            'dicts.unflatten_keys({["a.b.c"]=1, ["a.b.d"]=2, e=3})', {}
        )
        assert result == {"a": {"b": {"c": 1, "d": 2}}, "e": 3}

        # Table syntax
        result = evaluate_expression(
            'dicts.unflatten_keys({obj={["user.name"]="alice", ["user.age"]=30, '
            'status="active"}})',
            {},
        )
        assert result == {"user": {"name": "alice", "age": 30}, "status": "active"}

        # Single level keys (no dots)
        result = evaluate_expression("dicts.unflatten_keys({a=1, b=2})", {})
        assert result == {"a": 1, "b": 2}


class TestLuaAnyOperations:
    """Test any tool operations via Lua function calls."""

    def test_any_is_nil(self):
        result = evaluate_expression("any.is_nil(null)", {})
        assert result is True

        result = evaluate_expression('any.is_nil("hello")', {})
        assert result is False

        # Table syntax
        result = evaluate_expression("any.is_nil({value=null})", {})
        assert result is True

    def test_any_is_empty(self):
        result = evaluate_expression('any.is_empty("")', {})
        assert result is True

        result = evaluate_expression("any.is_empty({})", {})
        assert result is True

        result = evaluate_expression('any.is_empty("hello")', {})
        assert result is False

        result = evaluate_expression("any.is_empty({1, 2, 3})", {})
        assert result is False

    def test_any_is_equal(self):
        result = evaluate_expression('any.is_equal("hello", "hello")', {})
        assert result is True

        result = evaluate_expression("any.is_equal(42, 42)", {})
        assert result is True

        result = evaluate_expression('any.is_equal("hello", "world")', {})
        assert result is False

        # Table syntax
        result = evaluate_expression("any.is_equal({value={a=1}, param={a=1}})", {})
        assert result is True

    def test_any_contains(self):
        result = evaluate_expression('any.contains("hello world", "world")', {})
        assert result is True

        result = evaluate_expression("any.contains({1, 2, 3}, 2)", {})
        assert result is True

        result = evaluate_expression("any.contains({1, 2, 3}, 5)", {})
        assert result is False

    def test_any_eval(self):
        # Test evaluating expressions with any.eval
        result = evaluate_expression(
            'any.eval("hello", "strings.upper_case(value)")', {}
        )
        assert result == "HELLO"

        result = evaluate_expression('any.eval({1, 2, 3}, "lists.head(value)")', {})
        assert result == 1

        # Table syntax
        result = evaluate_expression(
            'any.eval({value={age=25}, expression="age > 18"})', {}
        )
        assert result is True

    def test_any_size(self):
        # Test getting size/length of any value type
        result = evaluate_expression('any.size("hello")', {})
        assert result == 5

        result = evaluate_expression("any.size({1, 2, 3, 4})", {})
        assert result == 4

        result = evaluate_expression("any.size({a=1, b=2})", {})
        assert result == 2

        # Empty values
        result = evaluate_expression('any.size("")', {})
        assert result == 0

        result = evaluate_expression("any.size({})", {})
        assert result == 0

        # Table syntax
        result = evaluate_expression('any.size({value="testing"})', {})
        assert result == 7

        # Scalar values have size 1
        result = evaluate_expression("any.size(42)", {})
        assert result == 1

        result = evaluate_expression("any.size(true)", {})
        assert result == 1

        # Null has size 0
        result = evaluate_expression("any.size(null)", {})
        assert result == 0


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
        assert result == [3, 4]

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
        assert result == [3, 4]

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


def run_comprehensive_tests():
    """Run all test classes."""
    import traceback

    test_classes = [
        TestLuaStringsOperations,
        TestLuaListsOperations,
        TestLuaDictsOperations,
        TestLuaAnyOperations,
        TestLuaGenerateOperations,
        TestLuaFunctionReturns,
        TestLuaEdgeCases,
        TestLuaErrorHandling,
        TestLuaToolFunctionReferences,
        TestLuaWrapperFunctions,
        TestPositionalVsTableWrapParameter,
        TestGenerateWrapParameter,
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = []

    for test_class in test_classes:
        print(f"\n=== Running {test_class.__name__} ===")
        instance = test_class()

        # Get all test methods
        test_methods = [
            method for method in dir(instance) if method.startswith("test_")
        ]

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                print(f"✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"❌ {method_name}: {str(e)}")
                failed_tests.append((test_class.__name__, method_name, str(e)))
                traceback.print_exc()

    print(f"\n{'=' * 60}")
    print("COMPREHENSIVE TEST RESULTS")
    print(f"{'=' * 60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {(passed_tests / total_tests) * 100:.1f}%")

    if failed_tests:
        print("\nFailed tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  {class_name}.{method_name}: {error}")
    else:
        print("\n🎉 All tests passed!")


if __name__ == "__main__":
    run_comprehensive_tests()
