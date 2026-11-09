import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

spec = importlib.util.spec_from_file_location(
    "run_evals", Path(__file__).resolve().parents[1] / "evals" / "run_evals.py"
)
evals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evals)


def response(payload):
    result = Mock()
    result.stop_reason = "end_turn"
    result.content = [SimpleNamespace(text=json.dumps(payload))]
    result.model_dump.return_value = {
        "usage": {"input_tokens": 20, "output_tokens": 10}
    }
    return result


def test_judge_scores_and_tokens_are_recorded(agent):
    output = {"meaning": "Five means curiosity.", "fortune": "Explore a new path."}
    ratings = {field: {"score": 4, "reason": "Fits the rubric."} for field in evals.QUALITY_FIELDS}
    agent.client.messages.create.side_effect = [response(output), response(ratings)]
    result = evals.evaluate(agent, {"kind": "fortune", "number": 5}, "judge-model")
    assert result["passed"]
    assert result["quality"] == ratings
    assert result["input_tokens"] == 40
    assert result["output_tokens"] == 20
    assert result["judge_tokens"] == {"input_tokens": 20, "output_tokens": 10}
    assert result["calls"][1]["request"]["model"] == "judge-model"
    assert json.loads(result["calls"][1]["request"]["messages"][0]["content"]) == {
        "roll": 5, "output": output
    }


def test_failed_judge_preserves_fortune(agent):
    output = {"meaning": "Curiosity.", "fortune": "Explore."}
    agent.client.messages.create.side_effect = [response(output), RuntimeError("judge unavailable")]
    result = evals.evaluate(agent, {"kind": "fortune", "number": 5})
    assert not result["passed"]
    assert result["output"] == output
    assert result["checks"]["required_fields"]
    assert "quality" not in result
    assert "judge unavailable" in result["error"]


def test_invalid_judge_score_is_rejected():
    ratings = {field: {"score": 6, "reason": "Too high."} for field in evals.QUALITY_FIELDS}
    with pytest.raises(ValueError, match="invalid score"):
        evals.judge_fortune(Mock(return_value=response(ratings)), "judge", 5, {})


def test_invalid_fortune_skips_judging(agent):
    agent.client.messages.create.return_value = response({"meaning": ""})
    result = evals.evaluate(agent, {"kind": "fortune", "number": 5})
    assert not result["passed"]
    assert "quality" not in result
    agent.client.messages.create.assert_called_once()
