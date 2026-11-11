import runpy
from unittest.mock import Mock

import anthropic
import pytest

from conftest import AGENT_PATH, tool_response


def test_client_has_explicit_timeout(agent):
    anthropic.Anthropic.assert_called_once_with(timeout=30.0, max_retries=0)


@pytest.mark.parametrize("stage", ["roll", "fortune"])
def test_cli_reports_timeout_and_stops(agent, monkeypatch, stage):
    error = anthropic.APITimeoutError(request=Mock())
    responses = [error]
    if stage == "fortune":
        responses = [tool_response(), error]
        monkeypatch.setattr(agent.random, "random", lambda: 0.9)
        monkeypatch.setattr(agent.random, "randint", lambda low, high: 5)
    agent.client.messages.create.side_effect = responses
    with pytest.raises(SystemExit, match="API request timed out") as stopped:
        runpy.run_path(str(AGENT_PATH), run_name="__main__")
    assert stopped.value.code != 0
    assert agent.client.messages.create.call_count == len(responses)
