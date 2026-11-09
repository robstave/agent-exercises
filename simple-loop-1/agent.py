"""Two-stage pipeline: flaky dice tool in an agent loop, then a fortune LLM.
Stage 1: agent loop (small model) rolls the die, retrying on failure.
Stage 2: a separate LLM call turns a valid roll into a lucky-number fortune.
pip install anthropic python-dotenv
"""
import json
import random
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))
client = anthropic.Anthropic()
ROLL_MODEL = "claude-haiku-4-5"       # cheap model drives the tool loop
FORTUNE_MODEL = "claude-sonnet-5-5"   # better writer for the fortune
MAX_STEPS = 10
WARN_REPEATS = 5
ABORT_REPEATS = 8

TOOLS = [{
    "name": "roll_dice",
    "description": "Roll a six-sided die and return the number. "
                   "Sometimes fails; if so, you may roll again.",
    "input_schema": {"type": "object", "properties": {}},
}]


def run_tool(name, args):
    if name == "roll_dice":
        if random.random() < 1 / 3:
            return "ERROR: the die fell off the table. Please roll again."
        return str(random.randint(1, 6))
    return f"ERROR: unknown tool {name}"


def roll_with_agent():
    """Stage 1. Returns a valid int roll, or None if the loop gave up."""
    messages = [{"role": "user",
                 "content": "Roll the die. Keep rolling until you get a valid number."}]
    seen = {}
    last_valid = None

    for step in range(MAX_STEPS):
        resp = client.messages.create(
            model=ROLL_MODEL, max_tokens=512, tools=TOOLS, messages=messages
        )
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            break

        results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue

            key = (block.name, json.dumps(block.input, sort_keys=True))
            seen[key] = seen.get(key, 0) + 1
            print(f"[step {step}] {block.name} call #{seen[key]}")

            if seen[key] >= ABORT_REPEATS:
                print("ABORTED: too many repeated calls.")
                return None

            output = run_tool(block.name, block.input)
            print(f"          -> {output}")

            # Deterministic check: we validate the result ourselves,
            # we don't trust the model to say whether the roll worked.
            if output.isdigit():
                last_valid = int(output)

            if seen[key] >= WARN_REPEATS:
                output += " NOTE: many repeated calls. Consider stopping."

            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
            })

        messages.append({"role": "user", "content": results})

        if last_valid is not None:
            return last_valid   # got a good roll, no need to keep looping

    return last_valid


def get_fortune(number):
    """Stage 2. Plain single LLM call, no tools, no loop."""
    resp = client.messages.create(
        model=FORTUNE_MODEL,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (f"I rolled a {number} on a six-sided die. Tell me what "
                        f"my lucky number {number} means, then give me a short, "
                        f"playful fortune. Keep it under 80 words."),
        }],
    )
    return resp.content[0].text


if __name__ == "__main__":
    roll = roll_with_agent()
    if roll is None:
        print("No valid roll. Skipping fortune.")
    else:
        print(f"\nYou rolled a {roll}.\n")
        print(get_fortune(roll))