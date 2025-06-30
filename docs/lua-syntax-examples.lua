-- Enhanced Lua Integration Examples for Lever MCP
-- Shows both positional and table-based argument syntax

-- SIMPLE OPERATIONS (positional args are fine)
local is_valid = strings.is_alpha("hello")
local uppercase = strings.upper_case("world")
local first_item = lists.head({1, 2, 3})

-- COMPLEX OPERATIONS (table args are clearer and less error-prone)

-- String operations with multiple parameters
local replaced = strings.replace({
    text = "hello world",
    data = {old = "world", new = "Lua"}
})

local templated = strings.template({
    text = "Hello {name}, you are {age} years old",
    data = {name = "Alice", age = 25}
})

-- List operations with expressions and parameters
local filtered = lists.filter_by({
    items = {{age = 20}, {age = 30}, {age = 40}},
    expression = "age >= 25"
})

local grouped = lists.group_by({
    items = {{type = "A", value = 1}, {type = "B", value = 2}, {type = "A", value = 3}},
    expression = "type"
})

local sorted = lists.sort_by({
    items = {{name = "Charlie"}, {name = "Alice"}, {name = "Bob"}},
    expression = "string.lower(name)"
})

-- Dictionary operations
local merged = dicts.merge({
    obj = {
        {name = "Alice", age = 25},
        {city = "NYC", country = "USA"}
    }
})

local nested_value = dicts.get_value({
    obj = {user = {profile = {name = "Alice"}}},
    path = {"user", "profile", "name"}
})

-- Generate operations
local number_range = generate.range({
    from = 1,
    to = 10,
    step = 2
})

local combinations = generate.combinations({
    items = {"A", "B", "C"},
    length = 2  -- combinations of length 2
})

-- FUNCTION RETURNS (apply operation to current item)
-- These return functions that get applied to the current context item

-- Simple function returns
return strings.upper_case  -- applies upper_case to current item
return lists.head         -- gets first element of current item

-- Complex function returns with parameters
return function(item)
    return lists.filter_by({
        items = item,
        expression = "age > 25"
    })
end
