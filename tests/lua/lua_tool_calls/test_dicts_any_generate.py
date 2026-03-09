from lib.lua import evaluate_expression


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
