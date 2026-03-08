"""
Lua utility functions for MCP tools.

This module contains all Lua-related functionality including:
- Lua runtime creation and safety
- Data conversion between Python and Lua
- Expression evaluation
- MCP tool registration in Lua
- Wrapping/unwrapping utilities
"""

from typing import Any, Dict, Optional
import lupa
from .conversion import (
    SAFE_MODE,
    lua_to_python,
    lua_to_python_preserve_wrapped,
    python_to_lua,
)
from .conversion import _apply_wrapping  # fmt: skip # noqa: F401, E501
from .conversion import _unwrap_input  # fmt: skip # noqa: F401, E501
from .tools import _register_mcp_tools_in_lua


def create_lua_runtime(
    safe_mode: Optional[bool] = None, mcp_tools=None
) -> lupa.LuaRuntime:
    """
    Create a Lua runtime with optional sandboxing and MCP tool function
    registration.

    Args:
        safe_mode: If True, applies safety rails. If None, uses global SAFE_MODE
            setting.
    """
    if safe_mode is None:
        safe_mode = SAFE_MODE

    lua_runtime = lupa.LuaRuntime()

    # Always define a global 'null' table as the None sentinel with a unique marker
    lua_runtime.execute("null = {__null_sentinel = true}")

    if safe_mode:
        # Apply safety rails - disable dangerous functions but keep useful ones
        lua_runtime.execute(
            """
            -- Disable dangerous file/system operations
            os = {
                -- Keep safe time/date functions
                time = os.time,
                date = os.date,
                clock = os.clock,
                difftime = os.difftime,
                -- Remove dangerous ones: execute, exit, getenv, remove, rename, etc.
            }

            -- Disable file I/O
            io = nil

            -- Disable module loading that could access filesystem
            require = nil
            dofile = nil
            loadfile = nil

            -- Keep package.loaded for accessing already loaded safe modules
            if package then
                package.loadlib = nil
                package.searchpath = nil
                package.searchers = nil
                package.path = nil
                package.cpath = nil
            end

            -- Disable debug library (could be used for introspection attacks)
            debug = nil
        """
        )

    # Register MCP tool functions in Lua runtime
    _register_mcp_tools_in_lua(lua_runtime, mcp_tools)

    # Register utility functions for type disambiguation
    def lua_list(table):
        """
        Creates a list-typed wrapper for explicit type disambiguation.

        Usage: list({1, 2, 3}) or list({})
        Returns: A wrapped object that will be converted to Python list

        Use this when you need to ensure an empty table {} becomes an empty list []
        in the JSON output, rather than an empty dict {}.
        """
        if table is None:
            return lua_runtime.table_from(
                {"__type": "list", "data": lua_runtime.table_from([])}
            )

        # Create wrapper with list type
        wrapper = {"__type": "list", "data": table}
        return lua_runtime.table_from(wrapper)

    def lua_dict(table):
        """
        Creates a dict-typed wrapper for explicit type disambiguation.

        Usage: dict({a=1, b=2}) or dict({})
        Returns: A wrapped object that will be converted to Python dict

        Use this when you need to ensure an empty table {} is explicitly
        treated as an empty dict {} in the JSON output.
        """
        if table is None:
            return lua_runtime.table_from(
                {"__type": "dict", "data": lua_runtime.table_from({})}
            )

        # Create wrapper with dict type
        wrapper = {"__type": "dict", "data": table}
        return lua_runtime.table_from(wrapper)

    def lua_unwrap(obj):
        """
        Unwraps a wrapped object to access the underlying data.

        Usage: unwrap(list({1, 2, 3})) or unwrap(dict({a=1}))
        Returns: The original Lua table without the wrapper

        Use this to extract the data from wrapped objects for further processing.
        For non-wrapped objects, returns the object unchanged.
        """
        if obj is None:
            return None

        # Convert to Python dict to check structure
        if hasattr(obj, "values"):
            obj_dict = dict(obj)
        else:
            obj_dict = obj if isinstance(obj, dict) else {}

        # Check if it's a wrapped object
        if "__type" in obj_dict and "data" in obj_dict:
            return obj_dict["data"]

        # If not wrapped, return as-is
        return obj

    # Register the functions in Lua runtime
    lua_runtime.globals()["list"] = lua_list
    lua_runtime.globals()["dict"] = lua_dict
    lua_runtime.globals()["unwrap"] = lua_unwrap

    return lua_runtime


def evaluate_expression_preserve_wrapped(
    expression: str,
    item: Any,
    safe_mode: Optional[bool] = None,
    context: Optional[Dict] = None,
) -> Any:
    """
    Evaluate a Lua expression against an item, preserving wrapped objects.
    This version preserves list({})/dict({}) wrapped objects instead of unwrapping them.
    """
    try:
        lua_runtime = create_lua_runtime(safe_mode)
        # Set up context - always make dict keys available for direct access
        if isinstance(item, dict):
            for key, value in item.items():
                if (
                    isinstance(key, str)
                    and key.isidentifier()
                    and key not in ["and", "or", "not", "if", "then", "else", "end"]
                ):
                    lua_runtime.globals()[key] = python_to_lua(
                        value, lua_runtime
                    )  # type: ignore  # noqa

        # Set up additional context variables (may override dict keys)
        if context is not None:
            for k, v in context.items():
                lua_runtime.globals()[k] = python_to_lua(
                    v, lua_runtime
                )  # type: ignore  # noqa
        # Evaluate the expression
        try:
            result = lua_runtime.execute("return (" + expression + ")")
        except lupa.LuaError:
            result = lua_runtime.execute(expression)

        # Convert result back to Python, preserving wrapped objects
        null_sentinel = lua_runtime.eval("null")
        return lua_to_python_preserve_wrapped(result, null_sentinel)
    except Exception:
        # Fallback to regular expression evaluation on error
        return evaluate_expression(expression, item, safe_mode, context)


def evaluate_expression(
    expression: str,
    item: Any,
    safe_mode: Optional[bool] = None,
    context: Optional[Dict] = None,
) -> Any:
    """
    Evaluate a Lua expression against an item. No default parameter name is set -
    callers must specify parameter names via context. Dict keys are directly accessible.
    All None (JSON null) values are converted to 'null' table for consistent
    null checks.

    Args:
        expression: Lua expression to evaluate (can return any value)
        item: The data item to evaluate against (None values become 'null')
        safe_mode: If True, applies safety rails. If None, uses global SAFE_MODE
            setting.
        context: Dict of variables to set in the Lua context (e.g., {"item": item}).
            Required for parameter access in expressions.
    """
    try:
        lua_runtime = create_lua_runtime(safe_mode)
        # Set up context - always make dict keys available for direct access
        if isinstance(item, dict):
            for key, value in item.items():
                if (
                    isinstance(key, str)
                    and key.isidentifier()
                    and key not in ["and", "or", "not", "if", "then", "else", "end"]
                ):
                    lua_runtime.globals()[key] = python_to_lua(
                        value, lua_runtime
                    )  # type: ignore  # noqa

        # Set up additional context variables (may override dict keys)
        if context is not None:
            for k, v in context.items():
                lua_runtime.globals()[k] = python_to_lua(
                    v, lua_runtime
                )  # type: ignore  # noqa
        # Evaluate the expression
        try:
            result = lua_runtime.execute("return (" + expression + ")")
        except lupa.LuaError:
            result = lua_runtime.execute(expression)

        # Check if the result is a Lua function - if so, call it with the item
        if callable(result):
            try:
                # Check if this is one of our MCP tool functions
                is_mcp_tool = False
                try:
                    # Check if the function is one of our registered MCP tool wrappers
                    # by examining if it has the characteristic wrapper function
                    # structure
                    func_str = str(result)
                    # Our tool wrappers are created by create_tool_wrapper and have
                    # this signature
                    if "create_tool_wrapper" in func_str and "wrapper" in func_str:
                        is_mcp_tool = True
                except Exception:
                    pass

                if is_mcp_tool:
                    # For MCP tool functions, pass a table with wrap=True to ensure
                    # proper JSON serialization. Map the generic "item" to the correct
                    # parameter name based on tool type.
                    tool_name = getattr(result, "_mcp_tool_name", None)

                    if tool_name == "strings":
                        param_table = {
                            "text": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }
                    elif tool_name == "lists":
                        param_table = {
                            "items": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }
                    elif tool_name == "dicts":
                        param_table = {
                            "obj": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }
                    elif tool_name == "any_tool":
                        param_table = {
                            "value": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }
                    else:
                        # Fallback to generic "item" parameter
                        param_table = {
                            "item": python_to_lua(item, lua_runtime),
                            "wrap": True,
                        }

                    result = result(lua_runtime.table_from(param_table))
                else:
                    # For regular functions, call with the item as argument
                    result = result(python_to_lua(item, lua_runtime))
            except Exception:
                # If calling the function fails, return the original result
                pass

        # Convert Lua results back to Python
        null_sentinel = lua_runtime.eval("null")
        return lua_to_python(result, null_sentinel)
    except Exception:
        return None
