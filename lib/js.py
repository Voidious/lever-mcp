"""
JavaScript utility functions for MCP tools using PythonMonkey.

This module contains all JavaScript-related functionality including:
- JavaScript runtime creation and safety
- Data conversion between Python and JavaScript
- Expression evaluation
- MCP tool registration in JavaScript
"""

from typing import Any, Dict, Optional
import pythonmonkey as pm

# Global configuration for JavaScript safety mode
try:
    # Try to import from main module if available
    from main import SAFE_MODE
except ImportError:
    # Fallback if main module not available (e.g., in tests)
    SAFE_MODE = True  # Default to safe mode


def _register_mcp_tools_in_js(js_global=None):
    """
    Register MCP tool functions in the JavaScript runtime to enable calling them as
    functions like strings.is_alpha(s) or lists.filter_by(items, expr).

    Args:
        js_global: The JavaScript global object to register tools in
    """
    # Import the tool implementation functions here to avoid circular imports
    from tools.js.strings import _strings_impl
    from tools.js.lists import _lists_impl
    from tools.js.dicts import _dicts_impl
    from tools.js.any import _any_impl
    from tools.js.generate import _generate_impl

    if js_global is None:
        js_global = pm.eval("globalThis")

    def create_tool_wrapper(tool_name, operation_name):
        """Create a wrapper function for a specific tool operation."""

        def wrapper(*args):
            # Safe parameter extraction to avoid conflicts with built-in dict methods
            def safe_get(obj, key):
                try:
                    return obj[key] if key in obj else None
                except (KeyError, TypeError):
                    return obj.get(key) if hasattr(obj, "get") else None

            # Support both positional args and object-based args
            if len(args) == 1 and isinstance(args[0], dict):
                # Check if this is a parameter object or just data
                param_obj = args[0]

                # Parameter objects have tool-specific parameter names as keys
                param_keys = set()
                if tool_name == "strings":
                    param_keys = {"text", "param", "data"}
                elif tool_name == "lists":
                    param_keys = {"items", "param", "others", "expression"}
                elif tool_name == "dicts":
                    param_keys = {
                        "obj",
                        "param",
                        "path",
                        "value",
                        "default",
                        "expression",
                    }
                elif tool_name == "any_tool":
                    param_keys = {"value", "param", "expression"}
                elif tool_name == "generate":
                    # For generate, if the object has "options" key, it's a
                    # parameter object
                    # Otherwise, the object itself is the options parameter
                    param_keys = {"options"}

                # If any object key matches parameter names, treat as parameter object
                is_param_obj = bool(param_keys.intersection(param_obj.keys()))

                # Special case for generate: if no "options" key, treat object
                # as options
                if tool_name == "generate" and not is_param_obj:
                    is_param_obj = True  # Force treating as parameter object

                if is_param_obj:
                    # Single object argument - extract named parameters
                    if tool_name == "strings":
                        result = _strings_impl(
                            text=safe_get(param_obj, "text"),
                            operation=operation_name,
                            param=safe_get(param_obj, "param"),
                            data=safe_get(param_obj, "data"),
                        )
                    elif tool_name == "lists":
                        result = _lists_impl(
                            items=safe_get(param_obj, "items"),
                            operation=operation_name,
                            param=safe_get(param_obj, "param"),
                            others=safe_get(param_obj, "others"),
                            expression=safe_get(param_obj, "expression"),
                        )
                    elif tool_name == "dicts":
                        result = _dicts_impl(
                            obj=safe_get(param_obj, "obj"),
                            operation=operation_name,
                            param=safe_get(param_obj, "param"),
                            path=safe_get(param_obj, "path"),
                            value=safe_get(param_obj, "value"),
                            default=safe_get(param_obj, "default"),
                            expression=safe_get(param_obj, "expression"),
                        )
                    elif tool_name == "any_tool":
                        result = _any_impl(
                            value=safe_get(param_obj, "value"),
                            operation=operation_name,
                            param=safe_get(param_obj, "param"),
                            expression=safe_get(param_obj, "expression"),
                        )
                    elif tool_name == "generate":
                        # Handle generate tool parameters
                        if "options" in param_obj:
                            # Has explicit options key
                            options_value = safe_get(param_obj, "options")
                        else:
                            # Object itself is the options
                            options_value = param_obj

                        result = _generate_impl(
                            options=options_value,
                            operation=operation_name,
                        )
                    else:
                        return None
                else:
                    # Single object that's data, not parameters - treat as positional
                    if tool_name == "strings":
                        result = _strings_impl(text=param_obj, operation=operation_name)
                    elif tool_name == "lists":
                        result = _lists_impl(items=param_obj, operation=operation_name)
                    elif tool_name == "dicts":
                        result = _dicts_impl(obj=param_obj, operation=operation_name)
                    elif tool_name == "any_tool":
                        result = _any_impl(value=param_obj, operation=operation_name)
                    elif tool_name == "generate":
                        result = _generate_impl(
                            options=param_obj, operation=operation_name
                        )
                    else:
                        return None
            else:
                # Positional arguments
                if tool_name == "strings":
                    # Some string operations use 'data' as second argument
                    # instead of 'param'
                    if operation_name in ["slice", "replace", "template"]:
                        result = _strings_impl(
                            text=args[0] if args else None,
                            operation=operation_name,
                            data=args[1] if len(args) > 1 else None,
                        )
                    else:
                        result = _strings_impl(
                            text=args[0] if args else None,
                            operation=operation_name,
                            param=args[1] if len(args) > 1 else None,
                            data=args[2] if len(args) > 2 else None,
                        )
                elif tool_name == "lists":
                    # Handle different argument patterns for lists operations
                    items_arg = args[0] if args else None

                    # Operations that use 'others' as second argument
                    if operation_name in [
                        "difference_by",
                        "intersection_by",
                        "difference",
                        "intersection",
                        "union",
                        "xor",
                        "zip_with",
                    ]:
                        others_arg = args[1] if len(args) > 1 else None
                        expression_arg = args[2] if len(args) > 2 else None
                        param_arg = args[3] if len(args) > 3 else None
                    # Operations that use 'param' as second argument (not expression)
                    elif operation_name in [
                        "take",
                        "drop",
                        "take_right",
                        "drop_right",
                        "sample_size",
                        "nth",
                        "contains",
                        "is_equal",
                        "join",
                        "chunk",
                    ]:
                        param_arg = args[1] if len(args) > 1 else None
                        expression_arg = args[2] if len(args) > 2 else None
                        others_arg = args[3] if len(args) > 3 else None
                    # Operations that take no additional parameters
                    elif operation_name in [
                        "head",
                        "last",
                        "tail",
                        "initial",
                        "flatten",
                        "flatten_deep",
                        "compact",
                        "shuffle",
                        "sample",
                        "is_empty",
                        "min",
                        "max",
                    ]:
                        param_arg = None
                        expression_arg = None
                        others_arg = None
                    else:
                        # Expression-based operations: items, expression, param, others
                        expression_arg = args[1] if len(args) > 1 else None
                        param_arg = args[2] if len(args) > 2 else None
                        others_arg = args[3] if len(args) > 3 else None

                    result = _lists_impl(
                        items=items_arg,
                        operation=operation_name,
                        param=param_arg,
                        expression=expression_arg,
                        others=others_arg,
                    )
                elif tool_name == "dicts":
                    # Handle different argument patterns for dicts operations
                    if operation_name in ["map_keys", "map_values"]:
                        # These operations use expression as second argument
                        result = _dicts_impl(
                            obj=args[0] if args else None,
                            operation=operation_name,
                            expression=args[1] if len(args) > 1 else None,
                        )
                    elif operation_name in ["get_value", "set_value"]:
                        # These operations use path as second argument:
                        # obj, path, [default/value]
                        result = _dicts_impl(
                            obj=args[0] if args else None,
                            operation=operation_name,
                            path=args[1] if len(args) > 1 else None,
                            # For get_value, third arg is default; for set_value,
                            # it's value
                            default=(
                                args[2]
                                if len(args) > 2 and operation_name == "get_value"
                                else None
                            ),
                            value=(
                                args[2]
                                if len(args) > 2 and operation_name == "set_value"
                                else None
                            ),
                        )
                    elif operation_name in ["pick", "omit", "has_key", "is_equal"]:
                        # These operations use param as second argument: obj, param
                        result = _dicts_impl(
                            obj=args[0] if args else None,
                            operation=operation_name,
                            param=args[1] if len(args) > 1 else None,
                        )
                    else:
                        # No-parameter operations: obj only
                        result = _dicts_impl(
                            obj=args[0] if args else None,
                            operation=operation_name,
                        )
                elif tool_name == "any_tool":
                    # For any_tool, param vs expression depends on the operation
                    if operation_name in ["contains", "is_equal"]:
                        # These operations use param for second argument
                        result = _any_impl(
                            value=args[0] if args else None,
                            operation=operation_name,
                            param=args[1] if len(args) > 1 else None,
                        )
                    else:
                        # Operations like 'eval' use expression for second argument
                        result = _any_impl(
                            value=args[0] if args else None,
                            operation=operation_name,
                            expression=args[1] if len(args) > 1 else None,
                            param=args[2] if len(args) > 2 else None,
                        )
                elif tool_name == "generate":
                    result = _generate_impl(
                        options=args[0] if args else {},
                        operation=operation_name,
                    )
                else:
                    return None

            # Return the value directly, or None if error
            if isinstance(result, dict) and "value" in result:
                return result["value"]
            return None

        # Store tool name as attribute for auto-wrap detection
        wrapper._mcp_tool_name = tool_name
        return wrapper

    # String operations
    string_ops = [
        "camel_case",
        "capitalize",
        "contains",
        "deburr",
        "ends_with",
        "is_alpha",
        "is_digit",
        "is_empty",
        "is_equal",
        "is_lower",
        "is_upper",
        "kebab_case",
        "lower_case",
        "replace",
        "reverse",
        "sample_size",
        "shuffle",
        "slice",
        "snake_case",
        "split",
        "starts_with",
        "template",
        "trim",
        "upper_case",
        "xor",
    ]

    # List operations
    list_ops = [
        "all_by",
        "every",
        "any_by",
        "some",
        "count_by",
        "difference_by",
        "filter_by",
        "find_by",
        "flat_map",
        "group_by",
        "intersection_by",
        "join",
        "key_by",
        "map",
        "max",
        "max_by",
        "min",
        "min_by",
        "partition",
        "pluck",
        "reduce",
        "remove_by",
        "sort_by",
        "uniq_by",
        "zip_with",
        "chunk",
        "compact",
        "contains",
        "drop",
        "drop_right",
        "flatten",
        "flatten_deep",
        "head",
        "index_of",
        "initial",
        "is_empty",
        "is_equal",
        "last",
        "nth",
        "random_except",
        "sample",
        "sample_size",
        "shuffle",
        "tail",
        "take",
        "take_right",
        "difference",
        "intersection",
        "union",
        "xor",
        "unzip_list",
        "zip_lists",
    ]

    # Dict operations
    dict_ops = [
        "flatten_keys",
        "get_value",
        "has_key",
        "invert",
        "is_empty",
        "is_equal",
        "items",
        "keys",
        "map_keys",
        "map_values",
        "merge",
        "omit",
        "pick",
        "set_value",
        "unflatten_keys",
        "values",
    ]

    # Any operations
    any_ops = ["contains", "eval", "is_empty", "is_equal", "is_nil", "size"]

    # Generate operations
    generate_ops = [
        "accumulate",
        "cartesian_product",
        "combinations",
        "cycle",
        "permutations",
        "powerset",
        "range",
        "repeat",
        "unique_pairs",
        "windowed",
        "zip_with_index",
    ]

    # Create and register tool objects
    strings_obj = {}
    for op in string_ops:
        strings_obj[op] = create_tool_wrapper("strings", op)
    js_global["strings"] = strings_obj

    lists_obj = {}
    for op in list_ops:
        lists_obj[op] = create_tool_wrapper("lists", op)
    js_global["lists"] = lists_obj

    dicts_obj = {}
    for op in dict_ops:
        dicts_obj[op] = create_tool_wrapper("dicts", op)
    js_global["dicts"] = dicts_obj

    any_obj = {}
    for op in any_ops:
        any_obj[op] = create_tool_wrapper("any_tool", op)
    js_global["any"] = any_obj

    generate_obj = {}
    for op in generate_ops:
        generate_obj[op] = create_tool_wrapper("generate", op)
    js_global["generate"] = generate_obj


def create_js_runtime(safe_mode: Optional[bool] = None):
    """
    Create a JavaScript runtime with optional sandboxing and MCP tool function
    registration.

    Args:
        safe_mode: If True, applies safety rails. If None, uses global SAFE_MODE
            setting.
    """
    if safe_mode is None:
        safe_mode = SAFE_MODE

    # Get the global object
    js_global = pm.eval("globalThis")

    if safe_mode:
        # Apply safety rails - disable dangerous functions but keep useful ones

        # Disable dangerous global objects and functions
        dangerous_globals = [
            # Disable Python bridge (critical security issue)
            "python",
            # Disable dynamic code execution
            "eval",
            "Function",
            # Disable WebAssembly
            "WebAssembly",
            # Disable dangerous constructors
            "Proxy",
            "Reflect",
            # Disable worker/thread creation
            "Worker",
            "SharedWorker",
            "ServiceWorker",
            # Disable import/require functionality
            "import",
            "require",
            "importScripts",
        ]

        for global_name in dangerous_globals:
            try:
                pm.eval(f"delete globalThis.{global_name}")
            except Exception:
                # Some globals might not exist, that's fine
                pass

        # Disable XMLHttpRequest and fetch for network access
        try:
            pm.eval("delete globalThis.XMLHttpRequest")
            pm.eval("delete globalThis.fetch")
        except Exception:
            pass

        # Disable setTimeout/setInterval to prevent async code execution
        try:
            pm.eval("delete globalThis.setTimeout")
            pm.eval("delete globalThis.setInterval")
            pm.eval("delete globalThis.setImmediate")
        except Exception:
            pass

    # Register MCP tool functions in JavaScript runtime
    _register_mcp_tools_in_js(js_global)

    return js_global


def evaluate_expression(
    expression: str,
    item: Any,
    context: Optional[Dict] = None,
    safe_mode: Optional[bool] = None,
) -> Any:
    """
    Evaluate a JavaScript expression against an item.

    Args:
        expression: JavaScript expression to evaluate (can return any value)
        item: The data item to evaluate against
        context: Dict of variables to set in the JavaScript context
        safe_mode: If True, applies safety rails. If None, uses global SAFE_MODE
            setting.
    """
    try:
        # Create a fresh context for this evaluation
        js_global = create_js_runtime(safe_mode)

        def convert_python_to_js(value):
            """Convert Python values to proper JavaScript equivalents."""
            if value is None:
                # Convert Python None to JavaScript null
                return pm.eval("null")
            elif isinstance(value, list):
                # Recursively convert None values in lists
                return [convert_python_to_js(item) for item in value]
            elif isinstance(value, dict):
                # Recursively convert None values in dicts
                return {key: convert_python_to_js(val) for key, val in value.items()}
            return value

        # Set up context - make dict keys available for direct access
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(key, str) and key.isidentifier():
                    js_global[key] = convert_python_to_js(value)

        # Set up additional context variables (may override dict keys)
        if context is not None:
            for k, v in context.items():
                js_global[k] = convert_python_to_js(v)

        # Evaluate the expression
        try:
            # First try as expression (wrapped in parentheses)
            result = pm.eval(f"({expression})")
        except Exception:
            try:
                # Try as statement/function body - create a function and call it
                func_body = f"(function() {{ {expression} }})()"
                result = pm.eval(func_body)
            except Exception:
                try:
                    # Try as direct statement
                    result = pm.eval(expression)
                except Exception:
                    result = None

        # Check if the result is a JavaScript function - if so, call it with the item
        if callable(result):
            try:
                # Check if this is one of our MCP tool functions
                is_mcp_tool = hasattr(result, "_mcp_tool_name")

                if is_mcp_tool:
                    # For MCP tool functions, pass an object with the correct
                    # parameter name
                    tool_name = getattr(result, "_mcp_tool_name", None)

                    if tool_name == "strings":
                        param_obj = {"text": item}
                    elif tool_name == "lists":
                        param_obj = {"items": item}
                    elif tool_name == "dicts":
                        param_obj = {"obj": item}
                    elif tool_name == "any_tool":
                        param_obj = {"value": item}
                    else:
                        # Fallback to generic "item" parameter
                        param_obj = {"item": item}

                    result = result(param_obj)
                else:
                    # For regular functions, call with the item as argument
                    result = result(item)
            except Exception:
                # If calling the function fails, return the original result
                pass

        # Convert JavaScript values to proper Python equivalents
        # This fixes issues where:
        # 1. JavaScript numbers become Python floats and get stringified as
        #    "1.0" instead of "1"
        # 2. JavaScript null becomes pythonmonkey.null instead of Python None
        def convert_js_values(obj):
            """Recursively convert JavaScript values to proper Python equivalents."""
            # Convert pythonmonkey.null to None
            if obj is pm.null:
                return None
            # Convert float integers to ints
            elif isinstance(obj, float) and obj.is_integer():
                return int(obj)
            elif isinstance(obj, list):
                return [convert_js_values(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_js_values(value) for key, value in obj.items()}
            else:
                return obj

        result = convert_js_values(result)

        return result
    except Exception:
        return None
