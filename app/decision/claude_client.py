"""Raw Claude API access — forces a tool call so the reply always has the exact shape we need.

Model: claude-haiku-4-5 — cheapest current-generation model, chosen because this
app's whole point is minimum token spend (see README cost estimate). Override
MODEL below if you want a more capable model instead — that's a cost/quality
tradeoff for you to make, not something to silently change.
"""

from typing import Optional

from anthropic import Anthropic

MODEL = "claude-haiku-4-5"
MAX_TOKENS = 300

SIGNAL_TOOL = {
    "name": "report_signal",
    "description": "Report the trading signal decision for XAU/USD.",
    "input_schema": {
        "type": "object",
        "properties": {
            "signal": {"type": "string", "enum": ["BUY", "SELL", "HOLD"]},
            "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
            "reason": {"type": "string"},
        },
        "required": ["signal", "confidence", "reason"],
        "additionalProperties": False,
    },
    "strict": True,
}


class ClaudeDecisionError(Exception):
    pass


def get_signal(system_prompt: str, user_prompt: str, api_key: Optional[str] = None) -> dict:
    client = Anthropic(api_key=api_key) if api_key else Anthropic()

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        tools=[SIGNAL_TOOL],
        tool_choice={"type": "tool", "name": "report_signal"},
        messages=[{"role": "user", "content": user_prompt}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "report_signal":
            return block.input

    raise ClaudeDecisionError("Claude did not return a tool_use response")
