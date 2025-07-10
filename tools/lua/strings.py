"""
Lua-specific implementation for the 'strings' tool.

This module provides Lua expression evaluation capabilities while using
shared implementations for non-expression operations.
"""

from typing import Any, Optional
from tools.common.strings import strings_operation


def strings_tool(
    text: str,
    operation: str,
    param: Any = None,
    data: Optional[dict] = None,
) -> dict:
    """MCP tool wrapper for string operations."""
    return _strings_impl(text, operation, param, data, wrap=False)


def _strings_impl(
    text: str,
    operation: str,
    param: Any = None,
    data: Optional[dict] = None,
    wrap: bool = False,
) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        from lib.lua import _apply_wrapping
        from . import unwrap_input

        # Unwrap input parameters
        text = unwrap_input(text)
        param = unwrap_input(param)
        data = unwrap_input(data)

        # Delegate to common operation
        result = strings_operation(
            text=text,
            operation=operation,
            param=param,
            data=data,
            wrap=False,
        )

        # Apply wrapping if requested
        if wrap and "value" in result and result["value"] is not None:
            result["value"] = _apply_wrapping(result["value"], wrap)

        return result

    except Exception as e:
        return {"error": f"String operation failed: {str(e)}"}
