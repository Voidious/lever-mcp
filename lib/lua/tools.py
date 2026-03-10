from typing import Any
import lupa
from .converters import lua_to_python, python_to_lua


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
                    params_table = lua_to_python(table_dict, null_sentinel)
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
                            converted_table = lua_to_python(dict(arg), null_sentinel)

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
                            py_args.append(lua_to_python(dict(arg), null_sentinel))
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
