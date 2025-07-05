from typing import Any, Dict, Optional
import re
import unicodedata
import random


def strings_tool(
    text: str,
    operation: str,
    param: Any = None,
    data: Optional[dict] = None,
) -> dict:
    """
    MCP tool wrapper for string operations.
    """
    return _strings_impl(text, operation, param, data, wrap=False)


def _strings_impl(
    text: str,
    operation: str,
    param: Any = None,
    data: Optional[Dict[str, Any]] = None,
    wrap: bool = False,
) -> dict:
    """Core implementation of string operations and mutations."""
    try:
        from lib.lua import _unwrap_input, _apply_wrapping

        # Unwrap input parameters
        text = _unwrap_input(text)
        param = _unwrap_input(param)
        data = _unwrap_input(data)

        # Basic validation
        if not isinstance(text, str):
            return {"value": None, "error": "text must be a string"}

        result = None

        if operation == "camel_case":
            # Convert to camelCase
            # First normalize: replace non-alphanumeric with spaces, then title case
            cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", text).strip()
            if not cleaned:
                result = ""
            else:
                words = cleaned.split()
                result = words[0].lower() + "".join(
                    word.capitalize() for word in words[1:]
                )

        elif operation == "capitalize":
            result = text.capitalize()

        elif operation == "contains":
            if param is None:
                return {
                    "value": None,
                    "error": "contains operation requires param (substring to find)",
                }
            result = str(param) in text

        elif operation == "deburr":
            # Remove accents/diacritics
            result = "".join(
                c
                for c in unicodedata.normalize("NFD", text)
                if unicodedata.category(c) != "Mn"
            )

        elif operation == "ends_with":
            if param is None:
                return {
                    "value": None,
                    "error": "ends_with operation requires param (suffix to check)",
                }
            result = text.endswith(str(param))

        elif operation == "is_alpha":
            result = text.isalpha()

        elif operation == "is_digit":
            result = text.isdigit()

        elif operation == "is_empty":
            result = len(text) == 0

        elif operation == "is_equal":
            if param is None:
                return {
                    "value": None,
                    "error": "is_equal operation requires param (string to compare)",
                }
            result = text == str(param)

        elif operation == "is_lower":
            result = text.islower()

        elif operation == "is_upper":
            result = text.isupper()

        elif operation == "kebab_case":
            # Convert to kebab-case: handle camelCase, PascalCase, snake_case, and
            # spaces. First insert hyphens before capitals that follow lowercase letters
            # or numbers.
            result = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
            # Replace underscores and other non-alphanumeric chars with hyphens
            result = re.sub(r"[^a-zA-Z0-9]+", "-", result)
            # Remove leading/trailing hyphens and convert to lowercase
            result = result.strip("-").lower()

        elif operation == "lower_case":
            result = text.lower()

        elif operation == "replace":
            if not data or "old" not in data or "new" not in data:
                return {
                    "value": None,
                    "error": (
                        "replace operation requires data with 'old' and 'new' keys"
                    ),
                }
            result = text.replace(str(data["old"]), str(data["new"]))

        elif operation == "reverse":
            result = text[::-1]

        elif operation == "sample_size":
            if param is None:
                return {
                    "value": None,
                    "error": (
                        "sample_size operation requires param (number of characters)"
                    ),
                }
            try:
                n = int(param)
                if n < 0:
                    return {
                        "value": None,
                        "error": "sample_size param must be non-negative",
                    }
                elif n == 0:
                    result = ""
                elif n >= len(text):
                    result = text
                else:
                    result = "".join(random.sample(text, n))
            except (ValueError, TypeError):
                return {
                    "value": None,
                    "error": "sample_size param must be a valid integer",
                }

        elif operation == "shuffle":
            char_list = list(text)
            random.shuffle(char_list)
            result = "".join(char_list)

        elif operation == "slice":
            if not data:
                return {
                    "value": None,
                    "error": "'data' with 'from' is required for slice operation",
                }
            try:
                from_idx = int(data.get("from", 0))
                to_idx = data.get("to", None)
                if to_idx is not None:
                    to_idx = int(to_idx)
                    result = text[from_idx:to_idx]
                else:
                    result = text[from_idx:]
            except (ValueError, TypeError, KeyError):
                return {
                    "value": None,
                    "error": (
                        "slice operation requires valid 'from' and optional 'to' "
                        "indices"
                    ),
                }

        elif operation == "snake_case":
            # Convert to snake_case
            # Handle camelCase and PascalCase
            s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
            s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
            # Replace non-alphanumeric with underscores
            cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", s2).strip("_")
            result = cleaned.lower()

        elif operation == "split":
            if param is None:
                # Default whitespace split (empty string produces empty list)
                result = text.split()
            else:
                delimiter = str(param)
                result = text.split(delimiter)

        elif operation == "starts_with":
            if param is None:
                return {
                    "value": None,
                    "error": "starts_with operation requires param (prefix to check)",
                }
            result = text.startswith(str(param))

        elif operation == "template":
            if not data:
                return {
                    "value": None,
                    "error": "template operation requires data with variable values",
                }
            try:
                # Simple template substitution using {var} syntax
                template_text = text
                for key, value in data.items():
                    placeholder = "{" + str(key) + "}"
                    template_text = template_text.replace(placeholder, str(value))
                result = template_text
            except Exception as e:
                return {
                    "value": None,
                    "error": f"template substitution failed: {str(e)}",
                }

        elif operation == "trim":
            result = text.strip()

        elif operation == "upper_case":
            result = text.upper()

        elif operation == "xor":
            if param is None:
                return {
                    "value": None,
                    "error": "xor operation requires param (string to XOR with)",
                }
            try:
                other = str(param)
                # XOR as symmetric difference of character sets
                set_a = set(text)
                set_b = set(other)
                xor_chars = set_a.symmetric_difference(set_b)
                result = "".join(sorted(xor_chars))
            except Exception as e:
                return {"value": None, "error": f"xor operation failed: {str(e)}"}

        else:
            return {"value": None, "error": f"Unknown operation: {operation}"}

        # Apply wrapping if requested
        if wrap:
            result = _apply_wrapping(result, wrap)

        return {"value": result}

    except Exception as e:
        return {"error": f"String operation failed: {str(e)}"}
