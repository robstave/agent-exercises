import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

AGENT_PATH = Path(__file__).resolve().parents[1] / "agent.py"


def tool_response(call_id="roll_1", name="roll_dice", inputs=None):
    return SimpleNamespace(
        stop_reason="tool_use",
        content=[SimpleNamespace(
            type="tool_use", id=call_id, name=name, input=inputs or {}
        )],
    )


@pytest.fixture
def agent(monkeypatch):
    # Avoid loading credentials or constructing a real API client.
    monkeypatch.setattr("dotenv.load_dotenv", Mock())
    monkeypatch.setattr("anthropic.Anthropic", Mock(return_value=Mock()))
    spec = importlib.util.spec_from_file_location("dice_agent", AGENT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
