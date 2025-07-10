"""
JavaScript-specific implementation for the 'chain' tool.

This module provides chain functionality that works with JavaScript tools.
"""

from typing import Any, Dict, List
import inspect


async def chain_tool(input: Any, tool_calls: List[Dict[str, Any]], mcp) -> dict:
    """MCP tool wrapper for chaining multiple tool calls."""
    value = input
    for i, step in enumerate(tool_calls):
        tool_name = step.get("tool")
        params = step.get("params", {})
        if not tool_name:
            return {"value": None, "error": f"Step {i}: Missing 'tool' name."}
        try:
            tool_or_coro = mcp._tool_manager.get_tool(tool_name)
            if inspect.isawaitable(tool_or_coro):
                tool = await tool_or_coro
            else:
                tool = tool_or_coro
        except Exception as e:
            return {
                "value": None,
                "error": f"Step {i}: Tool '{tool_name}' not found: {e}",
            }
        if not hasattr(tool, "run") or not callable(getattr(tool, "run", None)):
            return {
                "value": None,
                "error": f"Step {i}: Tool '{tool_name}' is not a valid tool object.",
            }
        param_schema = tool.parameters.get("properties", {})
        required = tool.parameters.get("required", [])
        primary_param = None

        # Prioritize common primary parameter names
        for p_name in ["text", "items", "obj", "value", "options"]:
            if p_name in param_schema:
                primary_param = p_name
                break

        # Fallback to required parameters (excluding 'operation')
        if not primary_param:
            for k in required:
                if k != "operation":
                    primary_param = k
                    break

        # Fallback to first non-'operation' parameter in schema
        if not primary_param and param_schema:
            for k in param_schema:
                if k != "operation":
                    primary_param = k
                    break

        arguments = dict(params)

        # Special handling for the generate tool
        if tool_name == "generate":
            if "options" in arguments:
                return {
                    "value": None,
                    "error": (
                        f"Step {i}: Chaining does not allow specifying the primary "
                        "parameter 'options' in params for generate tool."
                    ),
                }
            # For generate tool, construct the options dict based on operation
            operation = arguments.get("operation")
            unwrapped_value = unwrap_result(value)

            if operation == "repeat":
                count = arguments.get("count")
                if count is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'repeat' operation requires 'count' "
                            "parameter."
                        ),
                    }
                arguments["options"] = {"value": unwrapped_value, "count": count}
                arguments.pop("count", None)
            elif operation == "range":
                # Range doesn't use the input value, just pass the from/to/step
                # parameters
                from_val = arguments.get("from")
                to_val = arguments.get("to")
                step_val = arguments.get("step")
                if from_val is None or to_val is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'range' operation requires 'from' and "
                            "'to' parameters."
                        ),
                    }
                options = {"from": from_val, "to": to_val}
                if step_val is not None:
                    options["step"] = step_val
                arguments["options"] = options
                arguments.pop("from", None)
                arguments.pop("to", None)
                arguments.pop("step", None)
            elif operation == "cycle":
                count = arguments.get("count")
                if count is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'cycle' operation requires 'count' "
                            "parameter."
                        ),
                    }
                arguments["options"] = {"items": unwrapped_value, "count": count}
                arguments.pop("count", None)
            elif operation == "windowed":
                size = arguments.get("size")
                if size is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'windowed' operation requires 'size' "
                            "parameter."
                        ),
                    }
                arguments["options"] = {"items": unwrapped_value, "size": size}
                arguments.pop("size", None)
                arguments.pop("param", None)
            elif operation == "combinations":
                length = arguments.get("length")
                if length is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'combinations' operation requires "
                            "'length' parameter."
                        ),
                    }
                arguments["options"] = {"items": unwrapped_value, "length": length}
                arguments.pop("length", None)
                arguments.pop("param", None)
            elif operation == "permutations":
                length = arguments.get("length")
                # Length is optional for permutations
                options = {"items": unwrapped_value}
                if length is not None:
                    options["length"] = length
                arguments["options"] = options
                arguments.pop("length", None)
                arguments.pop("param", None)
            elif operation in [
                "powerset",
                "unique_pairs",
                "zip_with_index",
                "accumulate",
            ]:
                # These operations only need the items from the previous tool
                arguments["options"] = {"items": unwrapped_value}
            elif operation == "cartesian_product":
                # Cartesian product expects lists parameter
                lists = arguments.get("lists")
                if lists is None:
                    return {
                        "value": None,
                        "error": (
                            f"Step {i}: Generate 'cartesian_product' operation "
                            "requires 'lists' parameter."
                        ),
                    }
                arguments["options"] = {"lists": lists}
                arguments.pop("lists", None)
            else:
                return {
                    "value": None,
                    "error": (
                        f"Step {i}: Generate operation '{operation}' is not supported "
                        "in chains yet."
                    ),
                }
        elif primary_param:
            if primary_param in arguments:
                return {
                    "value": None,
                    "error": (
                        f"Step {i}: Chaining does not allow specifying the "
                        f"primary parameter '{primary_param}' in params. The "
                        "output from the previous tool is always used as input."
                    ),
                }
            # Unwrap the value before passing to the next tool
            arguments[primary_param] = unwrap_result(value)
        elif len(param_schema) == 1:
            only_param = next(iter(param_schema))
            if only_param in arguments:
                return {
                    "value": None,
                    "error": (
                        f"Step {i}: Chaining does not allow specifying the "
                        f"primary parameter '{only_param}' in params. The output "
                        "from the previous tool is always used as input."
                    ),
                }
            arguments[only_param] = unwrap_result(value)
        elif not param_schema:
            arguments = {}
        try:
            result = await tool.run(arguments)
        except Exception as e:
            return {
                "value": None,
                "error": f"Step {i}: Error calling tool '{tool_name}': {e}",
            }
        unwrapped = unwrap_result(result)
        value = unwrapped
        if isinstance(value, dict) and "error" in value:
            return {
                "value": None,
                "error": (
                    f"Step {i}: Error calling tool '{tool_name}': " f"{value['error']}"
                ),
            }
        elif isinstance(value, dict) and "value" in value:
            value = value["value"]
    return {"value": value}


def unwrap_result(result):
    """
    Unwraps the result from a tool call. The result from the client is typically a
    list containing a single Content object. This function extracts the text from
    that object and decodes it from JSON.
    """
    import json

    # The result from client.call_tool is a list of Content objects.
    # For our tools, it's typically a single object in the list.
    if (
        isinstance(result, list)
        and result
        and hasattr(result[0], "text")
        and isinstance(result[0], object)
    ):
        try:
            # The text attribute contains the JSON string of the actual return
            # value.
            unwrapped = json.loads(result[0].text)  # type: ignore[attr-defined]
        except (json.JSONDecodeError, TypeError):
            # If it's not valid JSON, return the text as is.
            unwrapped = getattr(result[0], "text", result[0])
    # Fallback for single Content object or other types passed from tests
    elif (
        not isinstance(result, list)
        and hasattr(result, "text")
        and result.text is not None
    ):
        try:
            unwrapped = json.loads(result.text)  # type: ignore[attr-defined]
        except (json.JSONDecodeError, TypeError):
            unwrapped = result.text  # type: ignore[attr-defined]
    else:
        unwrapped = result

    return unwrapped
