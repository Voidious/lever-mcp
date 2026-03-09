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
