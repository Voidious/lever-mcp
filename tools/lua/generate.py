"""
Lua-specific implementation for the 'generate' tool.

This module uses shared implementations for all generate operations
since they are all pure algorithmic operations without expressions.
"""

from tools.common.generate import generate_operation


def generate_tool(options: dict, operation: str) -> dict:
    """MCP tool wrapper for generating sequences or derived data."""
    return _generate_impl(options, operation, wrap=False)


def _generate_impl(options: dict, operation: str, wrap: bool = False) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        from lib.lua import _apply_wrapping
        from . import unwrap_input

        # Unwrap input parameters
        options = unwrap_input(options)

        # Delegate to common operation
        result = generate_operation(
            options=options,
            operation=operation,
            wrap=False,
        )

        # Apply wrapping if requested
        if wrap and "value" in result and result["value"] is not None:
            result["value"] = _apply_wrapping(result["value"], wrap)

        return result

    except Exception as e:
        return {"error": f"Generate operation failed: {str(e)}"}
