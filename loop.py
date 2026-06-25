"""A minimal, dependency-light agentic loop over the Claude API.

This is the manual loop (not the SDK tool runner) so the control flow is
explicit and easy to extend with approval gates, logging, or custom routing.
"""

from __future__ import annotations

from typing import Any

import anthropic

from agent.tools import TOOLS, run_tool

DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 16_000


class Agent:
    """Holds a Claude client + conversation state and runs the tool loop."""

    def __init__(
        self,
        *,
        system: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client: anthropic.Anthropic | None = None,
    ) -> None:
        self.client = client or anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.system = system
        self.messages: list[dict[str, Any]] = []

    def send(self, user_message: str, *, max_turns: int = 10) -> str:
        """Send a user message and run the loop until Claude stops calling tools.

        Returns the final text. ``max_turns`` bounds the tool loop so a
        misbehaving model can't spin forever.
        """
        self.messages.append({"role": "user", "content": user_message})

        for _ in range(max_turns):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system or anthropic.NOT_GIVEN,
                thinking={"type": "adaptive"},
                output_config={"effort": "high"},
                tools=TOOLS,
                messages=self.messages,
            )

            # Preserve the full response (incl. thinking + tool_use blocks).
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                return _final_text(response)

            tool_results = [
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": run_tool(block.name, block.input),
                }
                for block in response.content
                if block.type == "tool_use"
            ]
            self.messages.append({"role": "user", "content": tool_results})

        raise RuntimeError(f"Tool loop exceeded {max_turns} turns without finishing.")


def _final_text(response: anthropic.types.Message) -> str:
    return "".join(b.text for b in response.content if b.type == "text")
