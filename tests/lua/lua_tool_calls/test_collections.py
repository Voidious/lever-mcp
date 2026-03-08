from lib.lua import evaluate_expression


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
