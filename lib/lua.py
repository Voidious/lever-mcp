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

# Global configuration for Lua safety mode
SAFE_MODE = True  # Default to safe mode, can be overridden by command line


def _unwrap_input(value: Any) -> Any:
    """
    Unwrap input parameters for tool processing.
    Recursively unwraps wrapped lists/dicts to regular Python objects.
    """
    if isinstance(value, dict) and "__type" in value and "data" in value:
        # This is a wrapped object, unwrap it
        return _unwrap_input(value["data"])
    elif isinstance(value, list):
        # Recursively unwrap list contents
        return [_unwrap_input(item) for item in value]
    elif isinstance(value, dict):
        # Recursively unwrap dict contents
        return {k: _unwrap_input(v) for k, v in value.items()}
    else:
        return value


def _apply_wrapping(result: Any, wrap: bool) -> Any:
    """
    Apply wrapping to lists and dicts if wrap=True.
    Recursively wraps ALL nested structures.
    """
    if not wrap:
        return result

    if isinstance(result, list):
        # Wrap as list and recursively wrap ALL contents
        wrapped_items = [_apply_wrapping(item, wrap) for item in result]
        return {"__type": "list", "data": wrapped_items}
    elif isinstance(result, dict):
        # Check if it's already a wrapped object
        if "__type" in result and "data" in result:
            # Already wrapped, just wrap the data recursively
            return {
                "__type": result["__type"],
                "data": _apply_wrapping(result["data"], wrap),
            }
        else:
            # Wrap as dict and recursively wrap ALL contents
            wrapped_items = {k: _apply_wrapping(v, wrap) for k, v in result.items()}
            return {"__type": "dict", "data": wrapped_items}
    else:
        return result


def _wrap_result(result_dict: dict, wrap: bool) -> dict:
    """
    Apply wrapping to the result value if wrap=True and no error occurred.
    """
    if "error" in result_dict or not wrap:
        return result_dict

    wrapped_value = _apply_wrapping(result_dict.get("value"), wrap)
    return {"value": wrapped_value}


def _register_mcp_tools_in_lua(lua_runtime: lupa.LuaRuntime, mcp_tools=None):
    """
    Register MCP tool functions in the Lua runtime to enable calling them as
    functions like strings.is_alpha(s) or lists.filter_by(items, expr).

    Args:
        lua_runtime: The Lua runtime to register tools in
        mcp_tools: Dict containing the MCP tool functions (optional, used to avoid
            circular imports)
    """
    # Import the tool implementation functions here to avoid circular imports
    from tools.lua.strings import _strings_impl
    from tools.lua.lists import _lists_impl
    from tools.lua.dicts import _dicts_impl
    from tools.lua.any import _any_impl
    from tools.lua.generate import _generate_impl

    def create_tool_wrapper(tool_name, operation_name):
        """Create a wrapper function for a specific tool operation."""

        def wrapper(*args):
            # Get null sentinel for proper conversion
            null_sentinel = lua_runtime.eval("null")
            # Support both positional args and table-based args
            if len(args) == 1 and hasattr(args[0], "values"):
                # Check if this is a parameter table or just data
                table_dict = dict(args[0])

                # Parameter tables have tool-specific parameter names as keys
                param_keys = set()
                if tool_name == "strings":
                    param_keys = {"text", "param", "data", "wrap"}
                elif tool_name == "lists":
                    param_keys = {"items", "param", "others", "expression", "wrap"}
                elif tool_name == "dicts":
                    param_keys = {
                        "obj",
                        "param",
                        "path",
                        "value",
                        "default",
                        "expression",
                        "wrap",
                    }
                elif tool_name == "any_tool":
                    param_keys = {"value", "param", "expression", "wrap"}
                elif tool_name == "generate":
                    param_keys = {"options", "wrap"}

                # If any table key matches parameter names, treat as parameter table
                is_param_table = bool(param_keys.intersection(table_dict.keys()))

                if is_param_table:
                    # Single table argument - extract named parameters
                    params_table = lua_to_python(table_dict)
                    if not isinstance(params_table, dict):
                        params_table = {}
                    # Call the tool function with named parameters from the table
                    if tool_name == "strings":
                        wrap_val = params_table.get("wrap", False)
                        result = _strings_impl(
                            text=params_table.get("text"),
                            operation=operation_name,
                            param=params_table.get("param"),
                            data=params_table.get("data"),
                            wrap=wrap_val,
                        )
                    elif tool_name == "lists":
                        wrap_val = params_table.get("wrap", False)
                        result = _lists_impl(
                            items=params_table.get("items"),
                            operation=operation_name,
                            param=params_table.get("param"),
                            others=params_table.get("others"),
                            expression=params_table.get("expression"),
                            wrap=wrap_val,
                        )
                    elif tool_name == "dicts":
                        wrap_val = params_table.get("wrap", False)
                        result = _dicts_impl(
                            obj=params_table.get("obj"),
                            operation=operation_name,
                            param=params_table.get("param"),
                            path=params_table.get("path"),
                            value=params_table.get("value"),
                            default=params_table.get("default"),
                            expression=params_table.get("expression"),
                            wrap=wrap_val,
                        )
                    elif tool_name == "any_tool":
                        wrap_val = params_table.get("wrap", False)
                        result = _any_impl(
                            value=params_table.get("value"),
                            operation=operation_name,
                            param=params_table.get("param"),
                            expression=params_table.get("expression"),
                            wrap=wrap_val,
                        )
                    elif tool_name == "generate":
                        wrap_val = params_table.get("wrap", False)
                        # Extract options from the table, excluding the wrap parameter
                        options = {k: v for k, v in params_table.items() if k != "wrap"}
                        result = _generate_impl(
                            options=options,
                            operation=operation_name,
                            wrap=wrap_val,
                        )
                    else:
                        return None
                else:
                    # Single table that's data, not parameters - treat as positional
                    data_table = lua_to_python(args[0], null_sentinel)

                    # Call with the table as the first positional argument
                    if tool_name == "strings":
                        if mcp_tools and "strings" in mcp_tools:
                            result = mcp_tools["strings"](
                                text=data_table, operation=operation_name
                            )
                        else:
                            result = _strings_impl(
                                text=data_table, operation=operation_name
                            )
                    elif tool_name == "lists":
                        if mcp_tools and "lists" in mcp_tools:
                            result = mcp_tools["lists"](
                                items=data_table, operation=operation_name
                            )
                        else:
                            result = _lists_impl(
                                items=data_table, operation=operation_name
                            )
                    elif tool_name == "dicts":
                        if mcp_tools and "dicts" in mcp_tools:
                            result = mcp_tools["dicts"](
                                obj=data_table, operation=operation_name
                            )
                        else:
                            result = _dicts_impl(
                                obj=data_table, operation=operation_name
                            )
                    elif tool_name == "any_tool":
                        if mcp_tools and "any_tool" in mcp_tools:
                            result = mcp_tools["any_tool"](
                                value=data_table, operation=operation_name
                            )
                        else:
                            result = _any_impl(
                                value=data_table, operation=operation_name
                            )
                    elif tool_name == "generate":
                        result = _generate_impl(
                            options=data_table, operation=operation_name, wrap=False
                        )
                    else:
                        return None
            else:
                # Positional arguments - convert and use positional mapping
                py_args = []
                for i, arg in enumerate(args):
                    if hasattr(arg, "values"):  # Lua table
                        # Check if this is the null sentinel
                        if arg is null_sentinel:
                            py_args.append(None)
                        else:
                            converted_table = lua_to_python(dict(arg))

                            # Special handling for first argument that might be a
                            # parameter table
                            if i == 0 and isinstance(converted_table, dict):
                                # Check if this looks like a parameter table for this
                                # tool
                                if tool_name == "lists" and "items" in converted_table:
                                    # Extract the items value for lists operations
                                    py_args.append(converted_table["items"])
                                elif (
                                    tool_name == "strings" and "text" in converted_table
                                ):
                                    # Extract the text value for strings operations
                                    py_args.append(converted_table["text"])
                                elif tool_name == "dicts" and "obj" in converted_table:
                                    # Extract the obj value for dicts operations
                                    py_args.append(converted_table["obj"])
                                elif (
                                    tool_name == "any_tool"
                                    and "value" in converted_table
                                ):
                                    # Extract the value for any_tool operations
                                    py_args.append(converted_table["value"])
                                elif tool_name == "generate":
                                    # For generate operations, the table itself is the
                                    # options
                                    py_args.append(converted_table)
                                else:
                                    # Not a parameter table, use as-is
                                    py_args.append(converted_table)
                            else:
                                py_args.append(converted_table)
                    elif hasattr(arg, "__iter__") and not isinstance(
                        arg, str
                    ):  # Other Lua tables
                        try:
                            py_args.append(lua_to_python(dict(arg)))
                        except Exception:
                            py_args.append(list(arg))
                    else:
                        py_args.append(arg)

                # Call the tool function directly using .fn to access the
                # underlying implementation
                if tool_name == "strings":
                    # Check for wrap parameter as last argument
                    # Only treat as wrap if: we have 4+ args AND last is boolean
                    # Expected: strings.upper_case(text, param, data, wrap)
                    wrap_arg = False
                    if len(py_args) >= 4 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        # Remove wrap from args for other parameter parsing
                        py_args = py_args[:-1]

                    # Some string operations use 'data' as second argument instead of
                    # 'param'
                    if operation_name in ["slice", "replace", "template"]:
                        result = _strings_impl(
                            text=py_args[0] if py_args else None,
                            operation=operation_name,
                            data=py_args[1] if len(py_args) > 1 else None,
                            wrap=wrap_arg,
                        )
                    else:
                        result = _strings_impl(
                            text=py_args[0] if py_args else None,
                            operation=operation_name,
                            param=py_args[1] if len(py_args) > 1 else None,
                            data=py_args[2] if len(py_args) > 2 else None,
                            wrap=wrap_arg,
                        )
                elif tool_name == "lists":
                    # Handle different argument patterns for lists operations
                    items_arg = py_args[0] if py_args else None

                    # Check for wrap parameter as last argument
                    # Only treat as wrap if: we have 5+ args AND last is boolean
                    # This ensures explicit intent: lists.map(items, expr, nil, nil,
                    # true)
                    wrap_arg = False
                    if len(py_args) >= 5 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        # Remove wrap from args for other parameter parsing
                        py_args = py_args[:-1]

                    # Operations that use 'param' as second or third argument
                    if operation_name in [
                        "join",
                        "min",
                        "max",
                        "sample_size",
                    ]:
                        param_arg = py_args[1] if len(py_args) > 1 else None
                        expression_arg = py_args[2] if len(py_args) > 2 else None
                        others_arg = py_args[3] if len(py_args) > 3 else None
                    elif operation_name in [
                        "contains",
                        "nth",
                        "take",
                        "take_right",
                        "drop",
                        "drop_right",
                        "chunk",
                    ]:
                        # These operations expect param as third argument
                        # (skip nil in second position)
                        param_arg = py_args[2] if len(py_args) > 2 else None
                        expression_arg = py_args[3] if len(py_args) > 3 else None
                        others_arg = py_args[4] if len(py_args) > 4 else None
                    elif operation_name in ["is_equal"]:
                        # is_equal expects the comparison value as param argument
                        # (third position)
                        param_arg = py_args[2] if len(py_args) > 2 else None
                        expression_arg = None
                        others_arg = None
                    elif operation_name in [
                        "difference_by",
                        "intersection_by",
                        "difference",
                        "intersection",
                        "union",
                        "xor",
                        "zip_with",
                    ]:
                        # Operations that use 'others' as second argument
                        others_arg = py_args[1] if len(py_args) > 1 else None
                        expression_arg = py_args[2] if len(py_args) > 2 else None
                        param_arg = py_args[3] if len(py_args) > 3 else None
                    else:
                        # Standard operations: items, expression, param, others
                        expression_arg = py_args[1] if len(py_args) > 1 else None
                        param_arg = py_args[2] if len(py_args) > 2 else None
                        others_arg = py_args[3] if len(py_args) > 3 else None

                    result = _lists_impl(
                        items=items_arg,
                        operation=operation_name,
                        param=param_arg,
                        expression=expression_arg,
                        others=others_arg,
                        wrap=wrap_arg,
                    )
                elif tool_name == "dicts":
                    # Check for wrap parameter as last argument.
                    # Only treat as wrap if: we have 7+ args AND last is boolean
                    # Expected:
                    #    dicts.keys(obj, param, path, value, default, expression, wrap)
                    wrap_arg = False
                    if len(py_args) >= 7 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        # Remove wrap from args for other parameter parsing
                        py_args = py_args[:-1]

                    # Handle different argument patterns for dicts operations
                    if operation_name in ["map_keys", "map_values"]:
                        # These operations use expression as second argument
                        result = _dicts_impl(
                            obj=py_args[0] if py_args else None,
                            operation=operation_name,
                            expression=py_args[1] if len(py_args) > 1 else None,
                            wrap=wrap_arg,
                        )
                    else:
                        # Standard operations: obj, param, path, value
                        result = _dicts_impl(
                            obj=py_args[0] if py_args else None,
                            operation=operation_name,
                            param=py_args[1] if len(py_args) > 1 else None,
                            path=py_args[2] if len(py_args) > 2 else None,
                            value=py_args[3] if len(py_args) > 3 else None,
                            wrap=wrap_arg,
                        )
                elif tool_name == "any_tool":
                    # Check for wrap parameter as last argument
                    # Only treat as wrap if: we have 4+ args AND last is boolean
                    # Expected: any.eval(value, expression, param, wrap)
                    wrap_arg = False
                    if len(py_args) >= 4 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        # Remove wrap from args for other parameter parsing
                        py_args = py_args[:-1]

                    # For any_tool, param vs expression depends on the operation
                    if operation_name in ["contains", "is_equal"]:
                        # These operations use param for second argument
                        result = _any_impl(
                            value=py_args[0] if py_args else None,
                            operation=operation_name,
                            param=py_args[1] if len(py_args) > 1 else None,
                            wrap=wrap_arg,
                        )
                    else:
                        # Operations like 'eval' use expression for second
                        # argument
                        result = _any_impl(
                            value=py_args[0] if py_args else None,
                            operation=operation_name,
                            expression=py_args[1] if len(py_args) > 1 else None,
                            param=py_args[2] if len(py_args) > 2 else None,
                            wrap=wrap_arg,
                        )
                elif tool_name == "generate":
                    # Check for wrap parameter as last argument
                    wrap_arg = False
                    if len(py_args) >= 2 and isinstance(py_args[-1], bool):
                        wrap_arg = py_args[-1]
                        py_args = py_args[:-1]
                    result = _generate_impl(
                        options=py_args[0] if py_args else {},
                        operation=operation_name,
                        wrap=wrap_arg,
                    )
                else:
                    return None

            # Return the value directly, or None if error
            if isinstance(result, dict) and "value" in result:
                value = result["value"]
                # If the value is wrapped (has __type), create a special Lua object
                # that preserves the wrapped format through evaluate_expression
                if isinstance(value, dict) and "__type" in value and "data" in value:
                    # Create a special wrapper that won't be unwrapped by lua_to_python
                    special_wrapper = {
                        "__wrapped_result": True,
                        "__type": value["__type"],
                        "data": value["data"],
                    }
                    return python_to_lua(special_wrapper, lua_runtime)
                else:
                    return python_to_lua(value, lua_runtime)
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

    strings_table = {op: create_tool_wrapper("strings", op) for op in string_ops}
    lua_runtime.globals()["strings"] = lua_runtime.table_from(
        strings_table
    )  # type: ignore  # noqa

    lists_table = {op: create_tool_wrapper("lists", op) for op in list_ops}
    lua_runtime.globals()["lists"] = lua_runtime.table_from(lists_table)  # type: ignore

    dicts_table = {op: create_tool_wrapper("dicts", op) for op in dict_ops}
    lua_runtime.globals()["dicts"] = lua_runtime.table_from(dicts_table)  # type: ignore

    any_table = {op: create_tool_wrapper("any_tool", op) for op in any_ops}
    lua_runtime.globals()["any"] = lua_runtime.table_from(any_table)  # type: ignore

    generate_table = {op: create_tool_wrapper("generate", op) for op in generate_ops}
    lua_runtime.globals()["generate"] = lua_runtime.table_from(
        generate_table
    )  # type: ignore  # noqa


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


def python_to_lua(obj, lua_runtime):
    """
    Convert Python data structures to Lua equivalents. Handles None values,
    lists, dicts, and wrapped list/dict formats. None values become 'null'
    sentinels, enabling consistent null checks with 'item == null'. Lists are
    converted to Lua tables, dicts as tables.
    """
    null_sentinel = lua_runtime.eval("null")
    if obj is None:
        return null_sentinel
    elif isinstance(obj, list):
        # Convert each element and then convert the whole list to a Lua
        # table
        converted_items = [python_to_lua(x, lua_runtime) for x in obj]
        return lua_runtime.table_from(converted_items)
    elif isinstance(obj, dict):
        # Check for special wrapped result marker first
        if "__wrapped_result" in obj and obj["__wrapped_result"] is True:
            # Preserve the special wrapper structure
            wrapper = {
                "__wrapped_result": True,
                "__type": obj["__type"],
                "data": python_to_lua(obj["data"], lua_runtime),
            }
            return lua_runtime.table_from(wrapper)
        # Check for wrapped list/dict format
        elif "__type" in obj and "data" in obj:
            # It's a wrapped object, preserve the wrapper structure
            obj_type = obj["__type"]
            data = obj["data"]

            # Recursively encode the data part
            encoded_data = python_to_lua(data, lua_runtime)

            # Return the wrapped structure
            wrapper = {"__type": obj_type, "data": encoded_data}
            return lua_runtime.table_from(wrapper)
        else:
            # Regular dict handling
            converted_dict = {}
            for k, v in obj.items():
                converted_dict[k] = python_to_lua(v, lua_runtime)
            return lua_runtime.table_from(converted_dict)
    else:
        return obj


def lua_to_python_preserve_wrapped(obj, null_sentinel=None):
    """
    Convert Lua data structures to Python equivalents, preserving wrapped objects.
    This version keeps wrapped list/dict objects in wrapped format instead of unwrapping
    them.
    """
    # Check for null sentinel - handle both identity and empty table cases
    if null_sentinel is not None and obj is null_sentinel:
        return None
    elif isinstance(obj, list):
        return [lua_to_python_preserve_wrapped(x, null_sentinel) for x in obj]
    elif isinstance(obj, dict):
        # Check for wrapped list/dict format - preserve them!
        if "__type" in obj and "data" in obj:
            # This is a wrapped object, preserve it but convert the data part
            obj_type = obj["__type"]
            data = obj["data"]

            # Convert the data part recursively, preserving any nested wrapped objects
            if obj_type == "list":
                # Force conversion to list but preserve wrapped objects within
                if hasattr(data, "keys"):
                    # It's a Lua table, convert to Python list
                    keys = list(data.keys())
                    if not keys:
                        converted_data = []
                    elif all(isinstance(k, int) and k > 0 for k in keys):
                        max_k = max(keys)
                        converted_data = [
                            lua_to_python_preserve_wrapped(
                                data[k] if k in keys else None, null_sentinel
                            )
                            for k in range(1, max_k + 1)
                        ]
                    else:
                        # Non-consecutive keys, convert to list of values
                        converted_data = [
                            lua_to_python_preserve_wrapped(v, null_sentinel)
                            for v in data.values()
                        ]
                elif isinstance(data, list):
                    converted_data = [
                        lua_to_python_preserve_wrapped(x, null_sentinel) for x in data
                    ]
                else:
                    converted_data = []
            elif obj_type == "dict":
                # Force conversion to dict but preserve wrapped objects within
                if hasattr(data, "items"):
                    converted_data = {
                        k: lua_to_python_preserve_wrapped(v, null_sentinel)
                        for k, v in data.items()
                    }
                elif isinstance(data, dict):
                    converted_data = {
                        k: lua_to_python_preserve_wrapped(v, null_sentinel)
                        for k, v in data.items()
                    }
                else:
                    converted_data = {}
            else:
                # Unknown type, use regular conversion
                converted_data = lua_to_python_preserve_wrapped(data, null_sentinel)

            return {"__type": obj_type, "data": converted_data}

        # Check for null sentinel marker first
        if "__null_sentinel" in obj and obj["__null_sentinel"] is True:
            return None

        # Regular dict handling (no wrapper)
        keys = list(obj.keys())
        if not keys:
            # Empty dict - ambiguous, keep as dict
            return {}
        elif all(isinstance(k, int) and k > 0 for k in keys):
            min_k, max_k = min(keys), max(keys)
            if min_k == 1 and max_k == len(keys):
                # Convert to list in order
                return [
                    lua_to_python_preserve_wrapped(obj[k], null_sentinel)
                    for k in range(1, max_k + 1)
                ]
            else:
                # Non-consecutive keys, convert to list of values
                return [
                    lua_to_python_preserve_wrapped(v, null_sentinel)
                    for v in obj.values()
                ]
        else:
            # Regular dict with string/mixed keys
            return {
                k: lua_to_python_preserve_wrapped(v, null_sentinel)
                for k, v in obj.items()
            }
    elif hasattr(obj, "keys"):
        # It's a Lua table, convert to dict first
        table_dict = dict(obj)
        return lua_to_python_preserve_wrapped(table_dict, null_sentinel)
    else:
        return obj


def lua_to_python(obj, null_sentinel=None):
    """
    Convert Lua data structures to Python equivalents. Converts Lua 'null' tables
    back to Python None. Handles wrapped list/dict formats and converts Lua tables
    with consecutive integer keys starting at 1 to lists. Ambiguous empty tables
    default to empty dicts.
    """
    # Check for null sentinel - handle both identity and empty table cases
    if null_sentinel is not None and obj is null_sentinel:
        return None
    elif isinstance(obj, list):
        return [lua_to_python(x, null_sentinel) for x in obj]
    elif isinstance(obj, dict):
        # Check for special wrapped result marker first
        if "__wrapped_result" in obj and obj["__wrapped_result"] is True:
            # This is a wrapped result that should be preserved
            obj_type = obj["__type"]
            data = obj["data"]

            # Use the preserve-wrapped conversion for the data
            if obj_type == "list":
                # Force conversion to list, preserving wrapped objects
                if hasattr(data, "keys"):
                    # It's a Lua table, convert to Python list preserving wrapped
                    # objects
                    keys = list(data.keys())
                    if not keys:
                        converted_data = []
                    elif all(isinstance(k, int) and k > 0 for k in keys):
                        max_k = max(keys)
                        converted_data = [
                            lua_to_python_preserve_wrapped(
                                data[k] if k in keys else None, null_sentinel
                            )
                            for k in range(1, max_k + 1)
                        ]
                    else:
                        # Non-consecutive keys, convert to list of values
                        converted_data = [
                            lua_to_python_preserve_wrapped(v, null_sentinel)
                            for v in data.values()
                        ]
                elif isinstance(data, list):
                    # Preserve wrapped objects within the list
                    converted_data = []
                    for x in data:
                        # Check if this is a Lua table that represents a wrapped object
                        if hasattr(x, "keys"):
                            x_dict = dict(x)
                            if "__type" in x_dict and "data" in x_dict:
                                # This is a wrapped object, preserve the wrapped format
                                # exactly. Convert the data part directly without
                                # unwrapping the whole object.
                                inner_type = x_dict["__type"]
                                inner_data_lua = x_dict["data"]

                                # Convert the inner data preserving its structure
                                if inner_type == "list":
                                    # Force list conversion
                                    if hasattr(inner_data_lua, "keys"):
                                        keys = list(inner_data_lua.keys())
                                        if not keys:
                                            inner_data = []
                                        else:
                                            # Convert Lua table to list, preserving
                                            # wrapped objects
                                            inner_data = []
                                            for k in range(1, max(keys) + 1):
                                                if k in keys:
                                                    item = inner_data_lua[k]
                                                    # Check if this item is a
                                                    # wrapped object
                                                    if hasattr(item, "keys"):
                                                        item_dict = dict(item)
                                                        if (
                                                            "__type" in item_dict
                                                            and "data" in item_dict
                                                        ):
                                                            # Preserve wrapped object
                                                            item_type = item_dict[
                                                                "__type"
                                                            ]
                                                            item_data = lua_to_python(
                                                                item_dict["data"],
                                                                null_sentinel,
                                                            )
                                                            inner_data.append(
                                                                {
                                                                    "__type": item_type,
                                                                    "data": item_data,
                                                                }
                                                            )
                                                        else:
                                                            # Regular item
                                                            inner_data.append(
                                                                lua_to_python(
                                                                    item, null_sentinel
                                                                )
                                                            )
                                                    else:
                                                        # Regular item
                                                        inner_data.append(
                                                            lua_to_python(
                                                                item, null_sentinel
                                                            )
                                                        )
                                    else:
                                        inner_data = []
                                elif inner_type == "dict":
                                    # Force dict conversion
                                    if hasattr(inner_data_lua, "items"):
                                        inner_data = {
                                            k: lua_to_python(v, null_sentinel)
                                            for k, v in inner_data_lua.items()
                                        }
                                    else:
                                        inner_data = {}
                                else:
                                    inner_data = lua_to_python(
                                        inner_data_lua, null_sentinel
                                    )

                                converted_data.append(
                                    {"__type": inner_type, "data": inner_data}
                                )
                            else:
                                # Regular Lua table, convert normally
                                converted_data.append(lua_to_python(x, null_sentinel))
                        else:
                            # Not a table, convert normally
                            converted_data.append(lua_to_python(x, null_sentinel))
                else:
                    converted_data = []
            elif obj_type == "dict":
                # Force conversion to dict
                if hasattr(data, "items"):
                    converted_data = {
                        k: lua_to_python(v, null_sentinel) for k, v in data.items()
                    }
                elif isinstance(data, dict):
                    # Preserve wrapped objects within the dict
                    converted_data = {}
                    for k, v in data.items():
                        # Check if this is a Lua table that represents a wrapped object
                        if hasattr(v, "keys"):
                            v_dict = dict(v)
                            if "__type" in v_dict and "data" in v_dict:
                                # This is a wrapped object, preserve the wrapped format
                                # Use lua_to_python on the whole wrapped object which
                                # will unwrap it, but since we know it's supposed to be
                                # wrapped, re-wrap it
                                unwrapped_inner = lua_to_python(v, null_sentinel)
                                # Re-wrap it with the original type
                                converted_data[k] = {
                                    "__type": v_dict["__type"],
                                    "data": unwrapped_inner,
                                }
                            else:
                                # Regular Lua table, convert normally
                                converted_data[k] = lua_to_python(v, null_sentinel)
                        else:
                            # Not a table, convert normally
                            converted_data[k] = lua_to_python(v, null_sentinel)
                else:
                    converted_data = {}
            else:
                # Unknown type, use regular conversion
                converted_data = lua_to_python(data, null_sentinel)

            return {"__type": obj_type, "data": converted_data}
        # Check for null sentinel marker
        elif "__null_sentinel" in obj and obj["__null_sentinel"] is True:
            return None
        # Check for wrapped list/dict format
        elif "__type" in obj and "data" in obj:
            obj_type = obj["__type"]
            data = obj["data"]

            if obj_type == "list":
                # Force conversion to list regardless of structure
                if hasattr(data, "keys"):
                    # It's a Lua table, convert to Python list
                    keys = list(data.keys())
                    if not keys:
                        return []
                    elif all(isinstance(k, int) and k > 0 for k in keys):
                        max_k = max(keys)
                        return [
                            lua_to_python(data[k] if k in keys else None, null_sentinel)
                            for k in range(1, max_k + 1)
                        ]
                    else:
                        # Non-consecutive keys, convert to list of values
                        return [lua_to_python(v, null_sentinel) for v in data.values()]
                elif isinstance(data, list):
                    return [lua_to_python(x, null_sentinel) for x in data]
                else:
                    return []
            elif obj_type == "dict":
                # Force conversion to dict regardless of structure
                if hasattr(data, "items"):
                    return {k: lua_to_python(v, null_sentinel) for k, v in data.items()}
                elif isinstance(data, dict):
                    return {k: lua_to_python(v, null_sentinel) for k, v in data.items()}
                else:
                    return {}

        # Regular dict handling (no wrapper)
        keys = list(obj.keys())
        if not keys:
            # Empty dict could be either empty list or empty dict
            # We can't determine this from structure alone, so keep as dict
            # The caller should handle type conversion if needed
            return {}
        elif all(isinstance(k, int) and k > 0 for k in keys):
            min_k, max_k = min(keys), max(keys)
            if min_k == 1 and max_k == len(keys):
                # Convert to list in order
                return [
                    lua_to_python(obj[k], null_sentinel) for k in range(1, max_k + 1)
                ]
        # Otherwise, keep as dict
        return {k: lua_to_python(v, null_sentinel) for k, v in obj.items()}
    # Check for LuaTable objects
    elif "LuaTable" in type(obj).__name__:
        try:
            keys = list(obj.keys())
            # Check if this is a null sentinel by looking for the marker
            lua_dict = {k: obj[k] for k in keys}
            if "__null_sentinel" in lua_dict and lua_dict["__null_sentinel"] is True:
                return None
            # Convert to dict and recurse to handle potential wrapped formats
            return lua_to_python(lua_dict, null_sentinel)
        except Exception:
            return obj
    else:
        return obj


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
