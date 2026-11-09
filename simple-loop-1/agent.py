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
    """Stage 2. Generate the meaning and fortune in one structured LLM call."""
    resp = client.messages.create(
        model=FORTUNE_MODEL,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (f"I rolled a {number} on a six-sided die. Explain what "
                        "this lucky number means ( not scientifically, just for fun"
                    "), then give me a fortune with a playful tone. "
                        "Keep both fields under 80 words combined and use plain text."),
        }],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "meaning": {"type": "string"},
                        "fortune": {"type": "string"},
                    },
                    "required": ["meaning", "fortune"],
                    "additionalProperties": False,
                },
            },
        },
    )
    return json.loads(resp.content[0].text)


if __name__ == "__main__":
    roll = roll_with_agent()
    if roll is None:
        print("No valid roll. Skipping fortune.")
    else:
        result = get_fortune(roll)
        print(f"\n**What Your {roll} Means** {result['meaning']}")
        print(f"\n**Your Fortune** {result['fortune']}")
