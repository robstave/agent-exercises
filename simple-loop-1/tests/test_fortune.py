import json
import runpy
from types import SimpleNamespace

import pytest

from conftest import AGENT_PATH, tool_response


def fortune_response(text):
    return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)])


@pytest.mark.parametrize("number", range(1, 7))
def test_structured_fortune(agent, number):
    expected = {"meaning": "Curiosity.", "fortune": "Explore somewhere new."}
    agent.client.messages.create.return_value = fortune_response(json.dumps(expected))
    assert agent.get_fortune(number) == expected
    request = agent.client.messages.create.call_args.kwargs
    assert f"rolled a {number}" in request["messages"][0]["content"]
    schema = request["output_config"]["format"]["schema"]
    assert set(schema["required"]) == {"meaning", "fortune"}
    assert schema["additionalProperties"] is False
    assert all(field["type"] == "string" for field in schema["properties"].values())


def test_malformed_json_raises(agent):
    # Documents current failure behavior.
    agent.client.messages.create.return_value = fortune_response('{"meaning":')
    with pytest.raises(json.JSONDecodeError):
        agent.get_fortune(5)


def test_api_failure_propagates(agent):
    agent.client.messages.create.side_effect = RuntimeError("API unavailable")
    with pytest.raises(RuntimeError, match="API unavailable"):
        agent.get_fortune(5)


def test_cli_formats_fortune(agent, monkeypatch, capsys):
    monkeypatch.setattr(agent.random, "random", lambda: 0.9)
    monkeypatch.setattr(agent.random, "randint", lambda low, high: 5)
    agent.client.messages.create.side_effect = [
        tool_response(),
        fortune_response(json.dumps({"meaning": "Curiosity.", "fortune": "Explore."})),
    ]
    runpy.run_path(str(AGENT_PATH), run_name="__main__")
    assert capsys.readouterr().out.endswith(
        "\n**What Your 5 Means** Curiosity.\n\n**Your Fortune** Explore.\n"
    )
    assert agent.client.messages.create.call_count == 2


def test_cli_skips_fortune_without_roll(agent, capsys):
    agent.client.messages.create.return_value = SimpleNamespace(stop_reason="end_turn", content=[])
    runpy.run_path(str(AGENT_PATH), run_name="__main__")
    assert capsys.readouterr().out == "No valid roll. Skipping fortune.\n"
    agent.client.messages.create.assert_called_once()
