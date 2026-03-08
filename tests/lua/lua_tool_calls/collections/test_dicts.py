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
