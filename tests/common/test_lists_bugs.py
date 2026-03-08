from tools.lua.lists import _lists_impl as lua_lists
from tools.js.lists import _lists_impl as js_lists


def test_sort_by_duplicates_lua():
    # In Lua, it will use item + index
    # Correct indices: 1, 2, 3 -> results: 11, 22, 13
    # -> sorted: [10 (idx 1), 10 (idx 3), 20 (idx 2)]

    # Use item * 100 - index to make it more obvious
    # Correct: [10*100-1=999, 20*100-2=1998, 10*100-3=997]
    # -> sorted indices: 3, 1, 2 -> values: [10 (idx 3), 10 (idx 1), 20]

    # Let's use index directly as sort key
    # Correct: [1, 2, 3] -> [10, 20, 10]
    # Correct (desc): [3, 2, 1] -> [10 (idx 3), 20 (idx 2), 10 (idx 1)]
    result = lua_lists([10, 20, 10], "sort_by", expression="-index")
    # item1: index 1, key -1
    # item2: index 2, key -2
    # item3: index 3, key -3
    # Sorted keys: -3, -2, -1 -> items at idx 3, 2, 1
    assert result["value"] == [10, 20, 10]

    # Verify that the second '10' actually got index 3
    # We can do this by having it return something unique for index 3
    result = lua_lists([10, 20, 10], "sort_by", expression="index == 3 and -1 or index")
    # idx 1: 1
    # idx 2: 2
    # idx 3: -1
    # Sorted keys: -1 (idx 3), 1 (idx 1), 2 (idx 2)
    # Expected: [10 (the second one), 10 (the first one), 20]
    # If bug: idx 3 gets index 1 -> key 1. idx 1 gets key 1.
    assert result["value"][0] == 10


def test_reduce_lua():
    # Verify reduce uses provided context
    result = lua_lists([1, 2, 3], "reduce", expression="acc + item", param=10)
    assert result["value"] == 16  # 10+1+2+3


def test_zip_with_lua():
    # Verify zip_with uses provided context
    result = lua_lists([1, 2], "zip_with", others=[10, 20], expression="item + other")
    assert result["value"] == [11, 22]


def test_sort_by_duplicates_js():
    # In JS, index is 0-based.
    # [10, 20, 10]
    # idx 0: 0
    # idx 1: 1
    # idx 2: 2
    result = js_lists([10, 20, 10], "sort_by", expression="index == 2 ? -1 : index")
    # keys: 0, 1, -1
    # sorted keys: -1 (idx 2), 0 (idx 0), 1 (idx 1)
    assert result["value"][0] == 10


def test_reduce_js():
    result = js_lists([1, 2, 3], "reduce", expression="acc + item", param=10)
    assert result["value"] == 16


def test_zip_with_js():
    result = js_lists([1, 2], "zip_with", others=[10, 20], expression="item + other")
    assert result["value"] == [11, 22]
