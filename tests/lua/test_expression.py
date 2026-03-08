import importlib
import pytest
import main
from main import LeverMCP
from fastmcp import Client


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


# --- Find By Expression Tests ---


# --- Remove By Expression Tests ---


# --- Group By Expression Tests ---


# --- Sort By Expression Tests ---


# --- Pluck Expression Tests ---


# --- Min/Max By Expression Tests ---


# --- Difference/Intersection By Expression Tests ---


# --- Any Eval Expression Tests ---


# --- Null Handling Expression Tests ---


# --- Null Sentinel Behavior Tests ---


# --- Multi-line Expression Tests ---


# --- Safety Mode Tests ---


# --- Complex Expression Tests ---


# --- New String Operations Expression Tests ---


# --- New List Operations Expression Tests ---


# --- New Dict Operations Expression Tests ---


# --- New Any Operation Expression Tests ---


# --- Complex Expression Tests Using New Operations ---


# --- Complex Null Handling Tests ---


# --- Dicts Map Operations with Lua Expressions ---
