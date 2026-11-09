from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from conftest import tool_response


@pytest.mark.parametrize("number", range(1, 7))
def test_dice_returns_each_face(agent, monkeypatch, number):
    monkeypatch.setattr(agent.random, "random", lambda: 0.9)
    randint = Mock(return_value=number)
    monkeypatch.setattr(agent.random, "randint", randint)
    assert agent.run_tool("roll_dice", {}) == str(number)
    randint.assert_called_once_with(1, 6)


def test_dice_failure(agent, monkeypatch):
    monkeypatch.setattr(agent.random, "random", lambda: 0.1)
    assert agent.run_tool("roll_dice", {}).startswith("ERROR:")


def test_unknown_tool(agent):
    assert agent.run_tool("unknown", {}) == "ERROR: unknown tool unknown"


def test_success_stops_after_one_call(agent, monkeypatch):
    agent.client.messages.create.return_value = tool_response()
    tool = Mock(return_value="5")
    monkeypatch.setattr(agent, "run_tool", tool)
    assert agent.roll_with_agent() == 5
    tool.assert_called_once_with("roll_dice", {})
    agent.client.messages.create.assert_called_once()


def test_failures_are_sent_back_with_matching_ids(agent, monkeypatch):
    histories = []

    def respond(**kwargs):
        histories.append(deepcopy(kwargs["messages"]))
        return tool_response(f"roll_{len(histories)}")

    agent.client.messages.create.side_effect = respond
    monkeypatch.setattr(agent, "run_tool", Mock(side_effect=["ERROR: failed", "ERROR: failed", "5"]))
    assert agent.roll_with_agent() == 5
    assert len(histories) == 3
    for turn in (1, 2):
        assert histories[turn][-1] == {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": f"roll_{turn}",
                "content": "ERROR: failed",
            }],
        }


def test_no_tool_request_stops(agent, monkeypatch):
    agent.client.messages.create.return_value = SimpleNamespace(stop_reason="end_turn", content=[])
    tool = Mock()
    monkeypatch.setattr(agent, "run_tool", tool)
    assert agent.roll_with_agent() is None
    tool.assert_not_called()


def test_warning_and_abort_thresholds(agent, monkeypatch, capsys):
    histories = []

    def respond(**kwargs):
        histories.append(deepcopy(kwargs["messages"]))
        return tool_response(f"roll_{len(histories)}")

    agent.client.messages.create.side_effect = respond
    tool = Mock(return_value="ERROR: failed")
    monkeypatch.setattr(agent, "run_tool", tool)
    assert agent.roll_with_agent() is None
    assert len(histories) == 8
    assert tool.call_count == 7
    assert "NOTE:" not in histories[4][-1]["content"][0]["content"]
    assert "NOTE:" in histories[5][-1]["content"][0]["content"]
    assert "ABORTED" in capsys.readouterr().out


def test_turn_limit_with_distinct_requests(agent):
    agent.client.messages.create.side_effect = [
        tool_response(str(step), name=f"unknown_{step}")
        for step in range(agent.MAX_STEPS)
    ]
    assert agent.roll_with_agent() is None
    assert agent.client.messages.create.call_count == agent.MAX_STEPS
