import importlib
from main import LeverMCP
from fastmcp import Client
import pytest
import main


@pytest.fixture
async def client():
    """
    Provides an isolated FastMCP client for each test by reloading the main
    module and explicitly resetting the application state for the session.
    """
    importlib.reload(main)
    main.USE_JAVASCRIPT = True

    # Create fresh MCP instance with JavaScript tools
    mcp_instance = LeverMCP("Lever MCP")
    from tools.js import register_js_tools

    register_js_tools(mcp_instance)

    async with Client(mcp_instance) as c:
        yield c
