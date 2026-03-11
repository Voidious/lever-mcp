import importlib
from fastmcp import Client
from main import LeverMCP
import main
import pytest


@pytest.fixture(params=["lua", "javascript"])
async def client(request):
    """
    Provides an isolated FastMCP client for each test by reloading the main
    module and configuring it for the specified engine (Lua or JavaScript).
    """
    engine = request.param

    # Reload main module to get fresh instance
    importlib.reload(main)

    # Set the global configuration before importing tools
    main.USE_JAVASCRIPT = engine == "javascript"

    # Create fresh MCP instance
    mcp_instance = LeverMCP("Lever MCP")

    # Register appropriate tools based on engine
    if engine == "javascript":
        from tools.js import register_js_tools

        register_js_tools(mcp_instance)
    else:
        from tools.lua import register_lua_tools

        register_lua_tools(mcp_instance)

    async with Client(mcp_instance) as c:
        yield c
