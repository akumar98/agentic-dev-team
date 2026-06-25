"""CLI entry point: `agent "your prompt"` or an interactive REPL with no args."""

from __future__ import annotations

import sys

from agent.loop import Agent

SYSTEM = "You are a concise, helpful assistant. Use tools when they improve the answer."


def main() -> int:
    agent = Agent(system=SYSTEM)

    # One-shot mode: everything after the command is the prompt.
    if len(sys.argv) > 1:
        print(agent.send(" ".join(sys.argv[1:])))
        return 0

    # Interactive mode.
    print("Agent REPL — Ctrl-D or 'exit' to quit.")
    while True:
        try:
            prompt = input("> ").strip()
        except EOFError:
            print()
            return 0
        if prompt in {"exit", "quit"}:
            return 0
        if prompt:
            print(agent.send(prompt))


if __name__ == "__main__":
    raise SystemExit(main())
