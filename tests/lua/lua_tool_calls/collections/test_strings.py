from lib.lua import evaluate_expression


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
