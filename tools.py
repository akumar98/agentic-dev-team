"""Tool definitions and their handlers.

Each tool is a JSON-schema definition (sent to the API) plus a Python callable
that executes it. The registry maps tool name -> handler so the agent loop can
dispatch ``tool_use`` blocks without a big if/else.

To add a tool: write a handler, then append its schema to ``TOOLS`` and register
the handler in ``HANDLERS``. Keep descriptions prescriptive about *when* to call
the tool, not just what it does.
"""

from __future__ import annotations

from typing import Any, Callable

# --- handlers ---------------------------------------------------------------


def get_current_time(timezone: str = "UTC") -> str:
    """Return the current time. Imported lazily so the module stays import-safe."""
    from datetime import datetime, timezone as tz
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    try:
        zone = tz.utc if timezone.upper() == "UTC" else ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        return f"Error: unknown timezone {timezone!r}."
    return datetime.now(zone).isoformat()


def calculate(expression: str) -> str:
    """Evaluate a basic arithmetic expression safely (no names, no calls)."""
    import ast
    import operator

    ops: dict[type, Callable[..., Any]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval(node.operand))
        raise ValueError("unsupported expression")

    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except (ValueError, SyntaxError, ZeroDivisionError) as exc:
        return f"Error: {exc}"


# --- registry ---------------------------------------------------------------

TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_current_time",
        "description": (
            "Get the current date and time. Call this whenever the answer "
            "depends on the present moment (today's date, current time)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone, e.g. 'America/New_York'. Defaults to UTC.",
                }
            },
        },
    },
    {
        "name": "calculate",
        "description": (
            "Evaluate an arithmetic expression (+, -, *, /, **, %). Call this "
            "instead of doing multi-step arithmetic in your head."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "e.g. '(3 + 4) * 12'",
                }
            },
            "required": ["expression"],
        },
    },
]

HANDLERS: dict[str, Callable[..., str]] = {
    "get_current_time": get_current_time,
    "calculate": calculate,
}


def run_tool(name: str, tool_input: dict[str, Any]) -> str:
    """Dispatch a tool call to its handler, returning the result as a string."""
    handler = HANDLERS.get(name)
    if handler is None:
        return f"Error: unknown tool {name!r}."
    try:
        return handler(**tool_input)
    except TypeError as exc:
        return f"Error: bad arguments for {name!r}: {exc}"
