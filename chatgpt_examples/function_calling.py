"""Let the model call your own Python functions (function calling).

    python -m chatgpt_examples.function_calling "Convert 250 EUR to USD at 1.08 and add 21% VAT"

The loop: send the request with function definitions → run every
`function_call` item in the output → send the results back as
`function_call_output` items (chained with previous_response_id) → repeat
until the model answers in plain text.
"""
from __future__ import annotations

import ast
import datetime as dt
import json
import operator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from chatgpt_examples.common import DEFAULT_MODEL, get_client, prompt_from_args

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv, ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def calculate(expression: str) -> float:
    """Safely evaluate an arithmetic expression (no names, no calls)."""

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            left, right = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("exponent too large")
            return _OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError("only numbers and + - * / // % ** are allowed")

    return ev(ast.parse(expression.replace(",", ""), mode="eval"))


def current_time(timezone: str) -> str:
    try:
        return dt.datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M %Z")
    except ZoneInfoNotFoundError:
        raise ValueError(f"unknown time zone {timezone!r}; use an IANA name like Europe/Madrid")


TOOLS = [
    {
        "type": "function",
        "name": "calculate",
        "description": (
            "Evaluate an arithmetic expression and return the number. Use it for every calculation. "
            "Supports + - * / // % ** and parentheses. Write percentages as multiplication."
        ),
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "e.g. 250 * 1.08 * 1.21"}},
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "current_time",
        "description": "Return the current local date and time in an IANA time zone such as Asia/Tokyo.",
        "parameters": {
            "type": "object",
            "properties": {"timezone": {"type": "string", "description": "IANA zone, e.g. Europe/Madrid"}},
            "required": ["timezone"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

HANDLERS = {"calculate": calculate, "current_time": current_time}


def run_function(name: str, arguments: str) -> str:
    try:
        return json.dumps({"result": HANDLERS[name](**json.loads(arguments))})
    except Exception as exc:  # report errors back to the model instead of crashing
        return json.dumps({"error": str(exc)})


def run(client, prompt: str, model: str = DEFAULT_MODEL, max_rounds: int = 8, log=print) -> str:
    response = client.responses.create(model=model, input=prompt, tools=TOOLS)
    for _ in range(max_rounds):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return response.output_text
        outputs = []
        for call in calls:
            result = run_function(call.name, call.arguments)
            log(f"  [function] {call.name}({call.arguments}) -> {result}")
            outputs.append({"type": "function_call_output", "call_id": call.call_id, "output": result})
        response = client.responses.create(
            model=model, input=outputs, tools=TOOLS, previous_response_id=response.id
        )
    raise RuntimeError(f"no final answer after {max_rounds} function rounds")


def main() -> None:
    prompt = prompt_from_args("What is 250 EUR in USD at a rate of 1.08, plus 21% VAT? And what time is it in Tokyo?")
    print(run(get_client(), prompt))


if __name__ == "__main__":
    main()
