from tools.common.lists import op_min_by, op_max_by


def test_min_by_uses_correct_index():
    items = ["a", "b", "c"]

    # Expression that returns the index itself
    def expr_handler(expr, item, index, items_list):
        return index

    # min_by should return "a" because its index is 1 (minimum)
    result = op_min_by(items, "index", expr_handler)
    assert result["value"] == "a"

    # Use an expression depending on the index that would fail if index is always 1
    # Return 10 - index. Indices are 1, 2, 3. Results: 9, 8, 7.
    # Min result is 7, which corresponds to "c" (index 3).
    def expr_handler_inv(expr, item, index, items_list):
        return 10 - index

    result = op_min_by(items, "10 - index", expr_handler_inv)
    # If index is hardcoded to 1, expr_handler_inv always returns 9.
    # min(["a", "b", "c"], key=lambda x: 9) will return "a".
    # If index is correct, it should return "c".
    assert (
        result["value"] == "c"
    ), f"Expected 'c', got {result['value']}. Index might be hardcoded."


def test_max_by_uses_correct_index():
    items = ["a", "b", "c"]

    def expr_handler(expr, item, index, items_list):
        return index

    # max_by should return "c" because its index is 3 (maximum)
    result = op_max_by(items, "index", expr_handler)
    assert (
        result["value"] == "c"
    ), f"Expected 'c', got {result['value']}. Index might be hardcoded."
