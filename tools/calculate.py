"""Tool for evaluating arithmetic expressions safely."""

import math


calculate_tool_def = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a mathematical expression and return the result.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression, e.g. '2 + 2' or 'sqrt(16)'",
                }
            },
            "required": ["expression"],
        },
    },
}


def calculate(expression):
    """
    Evaluate a mathematical expression and return the numeric result as a string.

    >>> calculate('2 + 2')
    '4'
    >>> calculate('10 * 5')
    '50'
    >>> calculate('sqrt(16)')
    '4.0'
    >>> calculate('1 / 0')
    'Error: division by zero'
    >>> calculate('__import__("os")')
    'Error: invalid expression'
    """
    try:
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed)  # noqa: S307
        return str(result)
    except ZeroDivisionError as e:
        return f"Error: {e}"
    except Exception:
        return "Error: invalid expression"
