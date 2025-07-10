"""
JavaScript-specific implementation for the 'generate' tool.

This module uses shared implementations for all generate operations
since they are all pure algorithmic operations without expressions.
"""

from tools.common.generate import generate_operation


def generate_tool(options: dict, operation: str) -> dict:
    """MCP tool wrapper for generating sequences or derived data."""
    return _generate_impl(options, operation)


def _generate_impl(options: dict, operation: str) -> dict:
    """Internal implementation that delegates to common operations."""
    try:
        # Convert PythonMonkey objects to pure Python objects to avoid itertools issues
        def clean_options(obj):
            if isinstance(obj, dict):
                return {key: clean_options(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [clean_options(item) for item in obj]
            elif isinstance(obj, float) and obj.is_integer():
                return int(obj)
            else:
                return obj

        cleaned_options = clean_options(options)

        # Delegate to common operation (no wrapping needed for JS)
        result = generate_operation(
            options=cleaned_options,
            operation=operation,
            wrap=False,
        )

        return result

    except Exception as e:
        return {"error": f"Generate operation failed: {str(e)}"}
