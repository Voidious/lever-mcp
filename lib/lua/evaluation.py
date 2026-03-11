from typing import Any, Dict, Optional
import lupa
from .conversion import lua_to_python, lua_to_python_preserve_wrapped, python_to_lua
from .runtime import create_lua_runtime


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
        safe_mode: If True, applies safety rails. If None, uses global
            SAFE_MODE_DEFAULT setting.
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
                is_mcp_tool = hasattr(result, "_mcp_tool_name")

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
