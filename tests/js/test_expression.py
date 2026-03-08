import importlib
import pytest
import main
from main import LeverMCP
from fastmcp import Client


@pytest.fixture
async def client():
    """
    Provides an isolated FastMCP client for each test by reloading the main
    module and explicitly configuring it for JavaScript expressions.
    """
    importlib.reload(main)
    main.USE_JAVASCRIPT = True

    # Create fresh MCP instance with JavaScript tools
    mcp_instance = LeverMCP("Lever MCP")
    from tools.js import register_js_tools

    register_js_tools(mcp_instance)

    async with Client(mcp_instance) as c:
        yield c


# --- Find By Expression Tests ---


# --- Filter By Expression Tests ---


# --- Map Expression Tests ---


# --- Group By Expression Tests ---


# --- Sort By Expression Tests ---


# --- Any/Every Expression Tests ---


# --- Unique By Expression Tests ---


# --- Count By Expression Tests ---


# --- Partition Expression Tests ---


# --- Dictionary Expression Tests ---


# --- Any Tool Expression Tests ---


# --- Dictionary Expression Tests with JavaScript Syntax ---


# --- Pluck Expression Tests ---


# --- Min/Max By Expression Tests ---


# --- Difference/Intersection By Expression Tests ---


# --- Remove By Expression Tests ---


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
