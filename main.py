from fastmcp import FastMCP
import argparse

# Global configuration
SAFE_MODE = True  # Default to safe mode, can be overridden by command line
USE_JAVASCRIPT = (
    True  # Default to JavaScript expressions, can be overridden by command line
)


# --- MCP Server Setup ---


class LeverMCP(FastMCP):
    pass


mcp = LeverMCP("Lever MCP")

# Register default tools (JavaScript) on import, unless explicitly configured otherwise
if USE_JAVASCRIPT:
    from tools.js import register_js_tools

    register_js_tools(mcp)
else:
    from tools.lua import register_lua_tools

    register_lua_tools(mcp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Lever MCP server.")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Start the server with Streamable HTTP (instead of stdio)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for HTTP server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP server (default: 8000)",
    )
    parser.add_argument(
        "--unsafe",
        action="store_true",
        help="Disable safety rails for both Lua and JavaScript (allows file I/O, "
        "system commands, and dangerous operations)",
    )
    parser.add_argument(
        "--lua",
        action="store_true",
        help="Use Lua expressions instead of JavaScript expressions "
        "(default is JavaScript)",
    )
    args = parser.parse_args()

    # Update global configuration based on command line args
    SAFE_MODE = not args.unsafe
    USE_JAVASCRIPT = not args.lua

    # Switch to Lua tools if --lua flag is specified (JavaScript is default)
    if args.lua:
        # Clear existing JavaScript tools and register Lua tools
        mcp._tool_manager._tools.clear()
        from tools.lua import register_lua_tools

        register_lua_tools(mcp)

    if args.http:
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        mcp.run()
