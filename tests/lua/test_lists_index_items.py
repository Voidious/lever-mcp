import pytest
import importlib
import main
from main import LeverMCP
from fastmcp import Client
from tests import make_tool_call


@pytest.fixture
async def client():
    """
    Provides an isolated FastMCP client for each test by reloading the main
    module and explicitly configuring it for Lua expressions.
    """
    importlib.reload(main)
    main.USE_JAVASCRIPT = False

    # Create fresh MCP instance with Lua tools
    mcp_instance = LeverMCP("Lever MCP")
    from tools.lua import register_lua_tools

    register_lua_tools(mcp_instance)

    async with Client(mcp_instance) as c:
        yield c


@pytest.mark.asyncio
async def test_lists_map_with_index(client):
    """Test that lists.map provides index parameter."""
    items = ["a", "b", "c"]
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "map", "expression": "item .. index"},
    )
    assert error is None
    assert result == ["a1", "b2", "c3"]


@pytest.mark.asyncio
async def test_lists_map_with_items_access(client):
    """Test that lists.map provides items parameter."""
    items = ["x", "y", "z"]
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "map", "expression": "item .. (#items)"},
    )
    assert error is None
    assert result == ["x3", "y3", "z3"]


@pytest.mark.asyncio
async def test_lists_filter_by_with_index(client):
    """Test that lists.filter_by can use index."""
    items = ["a", "b", "c", "d", "e"]
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "operation": "filter_by",
            "expression": "index % 2 == 1",
        },  # odd indices (1, 3, 5)
    )
    assert error is None
    assert result == ["a", "c", "e"]


@pytest.mark.asyncio
async def test_lists_find_by_with_index(client):
    """Test that lists.find_by can use index."""
    items = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}]
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "operation": "find_by",
            "expression": "index == 2",
        },  # second item
    )
    assert error is None
    assert result == {"name": "Bob"}


@pytest.mark.asyncio
async def test_lists_group_by_with_index(client):
    """Test that lists.group_by can use index."""
    items = ["a", "b", "c", "d"]
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "operation": "group_by",
            "expression": "index <= 2 and 'first_half' or 'second_half'",
        },
    )
    assert error is None
    assert "first_half" in result
    assert "second_half" in result
    assert result["first_half"] == ["a", "b"]
    assert result["second_half"] == ["c", "d"]


@pytest.mark.asyncio
async def test_lists_pluck_with_items_context(client):
    """Test that lists.pluck can access the full items list."""
    items = [{"value": 10}, {"value": 20}, {"value": 30}]
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "operation": "pluck",
            "expression": "value / #items",
        },  # value divided by total count
    )
    assert error is None
    expected = [10 / 3, 20 / 3, 30 / 3]
    assert len(result) == 3
    for i in range(3):
        assert abs(result[i] - expected[i]) < 0.0001


@pytest.mark.asyncio
async def test_lists_all_by_with_index(client):
    """Test that lists.all_by can use index."""
    items = ["a", "b", "c"]
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "operation": "all_by",
            "expression": "index <= #items",
        },  # all indices should be <= length
    )
    assert error is None
    assert result is True


@pytest.mark.asyncio
async def test_lists_any_by_with_index(client):
    """Test that lists.any_by can use index."""
    items = ["a", "b", "c"]
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "operation": "any_by",
            "expression": "index == 2",
        },  # check if any item is at index 2
    )
    assert error is None
    assert result is True


@pytest.mark.asyncio
async def test_lists_complex_expression_with_all_params(client):
    """Test complex expression using item, index, and items."""
    items = [
        {"name": "Alice", "score": 85},
        {"name": "Bob", "score": 92},
        {"name": "Charlie", "score": 78},
    ]
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "operation": "map",
            "expression": "name .. '_rank' .. index .. '_of' .. #items",
        },
    )
    assert error is None
    assert result == ["Alice_rank1_of3", "Bob_rank2_of3", "Charlie_rank3_of3"]


@pytest.mark.asyncio
async def test_lists_index_starts_at_one(client):
    """Test that index starts at 1, not 0."""
    items = ["first", "second", "third"]
    result, error = await make_tool_call(
        client,
        "lists",
        {"items": items, "operation": "map", "expression": "index"},
    )
    assert error is None
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_lists_uniq_by_with_index(client):
    """Test that lists.uniq_by can use index."""
    items = ["a", "b", "a", "c", "b"]
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "operation": "uniq_by",
            "expression": "item .. index",
        },  # make each unique by adding index
    )
    assert error is None
    # Each item becomes unique because of the index
    assert len(result) == 5
    # Should keep all items since they're all unique with index
    assert result == ["a", "b", "a", "c", "b"]


@pytest.mark.asyncio
async def test_lists_partition_with_index(client):
    """Test that lists.partition can use index."""
    items = ["a", "b", "c", "d", "e", "f"]
    result, error = await make_tool_call(
        client,
        "lists",
        {
            "items": items,
            "operation": "partition",
            "expression": "index % 2 == 1",
        },  # odd indices
    )
    assert error is None
    assert len(result) == 2
    assert result[0] == ["a", "c", "e"]  # items at odd indices (1, 3, 5)
    assert result[1] == ["b", "d", "f"]  # items at even indices (2, 4, 6)
