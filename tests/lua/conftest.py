from main import LeverMCP
from fastmcp import Client
import pytest
import importlib
import main


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
