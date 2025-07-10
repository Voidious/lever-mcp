"""
Common operations for the 'strings' tool that don't require expression evaluation.

This module contains shared implementations for string operations that work
the same way regardless of expression language.
"""

import re
import unicodedata
import random
from typing import Any, Dict, Optional, Callable


def op_camel_case(text: str, **kwargs) -> dict:
    """Convert to camelCase."""
    # First normalize: replace non-alphanumeric with spaces, then title case
    cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", text).strip()
    if not cleaned:
        return {"value": ""}

    words = cleaned.split()
    result = words[0].lower() + "".join(word.capitalize() for word in words[1:])
    return {"value": result}


def op_capitalize(text: str, **kwargs) -> dict:
    """Capitalize the first character."""
    return {"value": text.capitalize()}


def op_contains(text: str, param: Any = None, **kwargs) -> dict:
    """Check if string contains a substring."""
    if param is None:
        return {
            "value": None,
            "error": "contains operation requires param (substring to find)",
        }
    return {"value": str(param) in text}


def op_deburr(text: str, **kwargs) -> dict:
    """Remove accents/diacritics."""
    result = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    return {"value": result}


def op_ends_with(text: str, param: Any = None, **kwargs) -> dict:
    """Check if string ends with substring."""
    if param is None:
        return {
            "value": None,
            "error": "ends_with operation requires param (suffix to check)",
        }
    return {"value": text.endswith(str(param))}


def op_is_alpha(text: str, **kwargs) -> dict:
    """Check if string contains only alphabetic characters."""
    return {"value": text.isalpha()}


def op_is_digit(text: str, **kwargs) -> dict:
    """Check if string contains only digits."""
    return {"value": text.isdigit()}


def op_is_empty(text: str, **kwargs) -> dict:
    """Check if string is empty."""
    return {"value": len(text) == 0}


def op_is_equal(text: str, param: Any = None, **kwargs) -> dict:
    """Check if strings are equal."""
    if param is None:
        return {
            "value": None,
            "error": "is_equal operation requires param (string to compare)",
        }
    return {"value": text == str(param)}


def op_is_lower(text: str, **kwargs) -> dict:
    """Check if string is all lowercase."""
    return {"value": text.islower()}


def op_is_upper(text: str, **kwargs) -> dict:
    """Check if string is all uppercase."""
    return {"value": text.isupper()}


def op_kebab_case(text: str, **kwargs) -> dict:
    """Convert to kebab-case."""
    # Handle camelCase, PascalCase, snake_case, and spaces
    # First insert hyphens before capitals that follow lowercase letters or numbers
    result = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
    # Replace underscores and other non-alphanumeric chars with hyphens
    result = re.sub(r"[^a-zA-Z0-9]+", "-", result)
    # Remove leading/trailing hyphens and convert to lowercase
    result = result.strip("-").lower()
    return {"value": result}


def op_lower_case(text: str, **kwargs) -> dict:
    """Convert to lowercase."""
    return {"value": text.lower()}


def op_replace(text: str, data: Optional[dict] = None, **kwargs) -> dict:
    """Replace all occurrences of a substring."""
    if not data or "old" not in data or "new" not in data:
        return {
            "value": None,
            "error": "replace operation requires data with 'old' and 'new' keys",
        }
    result = text.replace(str(data["old"]), str(data["new"]))
    return {"value": result}


def op_reverse(text: str, **kwargs) -> dict:
    """Reverse the string."""
    return {"value": text[::-1]}


def op_sample_size(text: str, param: Any = None, **kwargs) -> dict:
    """Return n random characters."""
    if param is None:
        return {
            "value": None,
            "error": "sample_size operation requires param (number of characters)",
        }
    try:
        n = int(param)
        if n < 0:
            return {
                "value": None,
                "error": "sample_size param must be non-negative",
            }
        elif n == 0:
            return {"value": ""}
        elif n >= len(text):
            return {"value": text}
        else:
            result = "".join(random.sample(text, n))
            return {"value": result}
    except (ValueError, TypeError):
        return {
            "value": None,
            "error": "sample_size param must be a valid integer",
        }


def op_shuffle(text: str, **kwargs) -> dict:
    """Randomly shuffle string characters."""
    char_list = list(text)
    random.shuffle(char_list)
    return {"value": "".join(char_list)}


def op_slice(text: str, data: Optional[dict] = None, **kwargs) -> dict:
    """Extract substring."""
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
        return {"value": result}
    except (ValueError, TypeError, KeyError):
        return {
            "value": None,
            "error": "slice operation requires valid 'from' and optional 'to' indices",
        }


def op_snake_case(text: str, **kwargs) -> dict:
    """Convert to snake_case."""
    # Handle camelCase and PascalCase
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    # Replace non-alphanumeric with underscores
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", s2).strip("_")
    return {"value": cleaned.lower()}


def op_split(text: str, param: Any = None, **kwargs) -> dict:
    """Split string into array by delimiter."""
    if param is None:
        # Default whitespace split
        result = text.split()
    else:
        delimiter = str(param)
        result = text.split(delimiter)
    return {"value": result}


def op_starts_with(text: str, param: Any = None, **kwargs) -> dict:
    """Check if string starts with substring."""
    if param is None:
        return {
            "value": None,
            "error": "starts_with operation requires param (prefix to check)",
        }
    return {"value": text.startswith(str(param))}


def op_template(text: str, data: Optional[dict] = None, **kwargs) -> dict:
    """Interpolate variables using {var} syntax."""
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
        return {"value": template_text}
    except Exception as e:
        return {
            "value": None,
            "error": f"template substitution failed: {str(e)}",
        }


def op_trim(text: str, **kwargs) -> dict:
    """Remove leading and trailing whitespace."""
    return {"value": text.strip()}


def op_upper_case(text: str, **kwargs) -> dict:
    """Convert to uppercase."""
    return {"value": text.upper()}


def op_xor(text: str, param: Any = None, **kwargs) -> dict:
    """String-specific XOR operation."""
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
        return {"value": result}
    except Exception as e:
        return {"value": None, "error": f"xor operation failed: {str(e)}"}


# Operation registry - maps operation names to functions
OPERATIONS: Dict[str, Callable] = {
    "camel_case": op_camel_case,
    "capitalize": op_capitalize,
    "contains": op_contains,
    "deburr": op_deburr,
    "ends_with": op_ends_with,
    "is_alpha": op_is_alpha,
    "is_digit": op_is_digit,
    "is_empty": op_is_empty,
    "is_equal": op_is_equal,
    "is_lower": op_is_lower,
    "is_upper": op_is_upper,
    "kebab_case": op_kebab_case,
    "lower_case": op_lower_case,
    "replace": op_replace,
    "reverse": op_reverse,
    "sample_size": op_sample_size,
    "shuffle": op_shuffle,
    "slice": op_slice,
    "snake_case": op_snake_case,
    "split": op_split,
    "starts_with": op_starts_with,
    "template": op_template,
    "trim": op_trim,
    "upper_case": op_upper_case,
    "xor": op_xor,
}


def strings_operation(
    text: str,
    operation: str,
    param: Any = None,
    data: Optional[dict] = None,
    wrap: bool = False,
) -> dict:
    """
    Execute a strings tool operation.

    Args:
        text: The input string to operate on
        operation: Name of the operation to perform
        param: Optional parameter for some operations
        data: Optional data dict for some operations
        wrap: Whether to wrap the result (for Lua compatibility)

    Returns:
        Dict with 'value' key and optional 'error' key
    """
    # Basic validation
    if not isinstance(text, str):
        return {"value": None, "error": "text must be a string"}

    try:
        if operation not in OPERATIONS:
            return {"value": None, "error": f"Unknown operation: {operation}"}

        # Get the operation function and call it
        op_func = OPERATIONS[operation]
        result = op_func(
            text=text,
            param=param,
            data=data,
        )

        return result

    except Exception as e:
        return {"value": None, "error": f"String operation failed: {str(e)}"}
