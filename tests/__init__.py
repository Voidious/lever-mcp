from typing import Any, Optional
from mcp.types import TextContent


async def make_tool_call(*args, **kwargs) -> tuple[Optional[Any], Optional[str]]:
    def _get_tool_data(response: Any) -> dict:
        import json

        if isinstance(response, list):
            data = response[0]
        else:
            data = response
        if isinstance(data, TextContent):
            data = json.loads(data.text)
        assert (
            isinstance(data, dict) and "value" in data
        ), f"Tool did not return a dict with 'value': {data}"
        return data

    response = await args[0].call_tool(*args[1:], **kwargs)
    data = _get_tool_data(response)
    value = data["value"]
    error = data.get("error", None)
    return value, error
