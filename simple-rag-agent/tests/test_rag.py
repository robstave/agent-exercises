import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import numpy as np
import pytest
import anthropic
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent import RagAgent
from retrieval import SemanticIndex, load_chunks


class Block(SimpleNamespace):
    def model_dump(self):
        return vars(self)


def reply(tool=False, stop=None, inputs=None, name="search_docs"):
    block = (Block(type="tool_use", id="lookup", name=name,
                   input=inputs if inputs is not None else {"query": "refunds"}) if tool else
             Block(type="text", text="Refunds take five business days. [04-weather-refunds.md#chunk-2]"))
    return SimpleNamespace(content=[block], stop_reason=stop or ("tool_use" if tool else "end_turn"),
                           usage=SimpleNamespace(input_tokens=20, output_tokens=10))


class Index:
    def __init__(self):
        self.queries = []

    def search(self, query, k=3):
        self.queries.append(query)
        return [{"source": "04-weather-refunds.md#chunk-2", "text": "Five business days."}]


def setup_agent(responses, **kwargs):
    client = SimpleNamespace(messages=SimpleNamespace(create=AsyncMock(side_effect=responses)))
    return RagAgent(client, Index(), **kwargs)


def test_multiple_searches_usage_and_followup():
    agent = setup_agent([reply(tool=True), reply(tool=True, inputs={"query": "connections"}), reply(), reply()])
    result = asyncio.run(agent.ask("What if my connection is canceled?"))
    assert not result.error and result.turns == 3
    assert agent.index.queries == ["refunds", "connections"]
    assert (result.usage.input_tokens, result.usage.output_tokens) == (60, 30)
    assert "[04-weather-refunds.md#chunk-2]" in result.text
    assert len(agent.history) == 2
    asyncio.run(agent.ask("How long does that take?"))
    messages = agent.client.messages.create.call_args.kwargs["messages"]
    assert messages[0]["content"] == "What if my connection is canceled?"
    assert agent.session_usage.input_tokens == 80


def test_turn_limit_preserves_usage_and_does_not_save_failed_exchange():
    agent = setup_agent([reply(tool=True)] * 3, max_turns=3)
    result = asyncio.run(agent.ask("Keep searching"))
    assert result.error and result.turns == 3
    assert result.usage.input_tokens == 60
    assert agent.history == []


@pytest.mark.parametrize("kwargs", [{"request_timeout": 0.01}, {"question_timeout": 0.01}])
def test_timeouts(kwargs):
    async def slow(**request):
        await asyncio.sleep(0.2)
        return reply()
    agent = setup_agent(slow, **kwargs)
    result = asyncio.run(agent.ask("A slow request"))
    assert result.error and "deadline" in result.text
    assert result.seconds < 0.15
    assert agent.history == []


def test_usage_survives_timeout_after_search():
    count = 0
    async def responses(**request):
        nonlocal count
        count += 1
        if count == 1:
            return reply(tool=True)
        await asyncio.sleep(0.2)
    agent = setup_agent(responses, request_timeout=0.01)
    result = asyncio.run(agent.ask("Refund"))
    assert result.error and result.usage.input_tokens == 20
    assert agent.session_usage.output_tokens == 10


@pytest.mark.parametrize("inputs,name", [({"query": "x"}, "other"), ({"surprise": True}, "search_docs"), ({}, "search_docs")])
def test_invalid_tools_return_error_to_model(inputs, name):
    agent = setup_agent([reply(tool=True, inputs=inputs, name=name), reply()])
    result = asyncio.run(agent.ask("Search"))
    assert not result.error
    messages = agent.client.messages.create.call_args.kwargs["messages"]
    assert messages[-1]["content"][0]["is_error"] is True


def test_truncation_is_not_a_complete_answer():
    agent = setup_agent([reply(stop="max_tokens")])
    assert asyncio.run(agent.ask("Question")).error
    assert agent.history == []


def test_api_failure_is_reported_without_saving_history():
    error = anthropic.APIConnectionError(request=httpx.Request("POST", "https://api.anthropic.com"))
    agent = setup_agent([error])
    result = asyncio.run(agent.ask("Question"))
    assert result.error and "APIConnectionError" in result.text
    assert result.usage.input_tokens == 0 and agent.history == []


def test_question_deadline_includes_search():
    import time
    agent = setup_agent([reply(tool=True)], question_timeout=0.01)
    def slow_search(**kwargs):
        time.sleep(0.05)
        return []
    agent.index.search = slow_search
    result = asyncio.run(agent.ask("Search"))
    assert result.error and "deadline" in result.text
    assert result.seconds < 0.04
    assert result.usage.input_tokens == 20


def test_bounded_conversation():
    agent = setup_agent([reply()] * 4, history_pairs=2)
    for number in range(4):
        asyncio.run(agent.ask(str(number)))
    assert len(agent.history) == 4
    assert agent.history[0]["content"] == "2"


def test_bad_question_never_calls_api():
    agent = setup_agent([])
    with pytest.raises(ValueError):
        asyncio.run(agent.ask(" "))
    agent.client.messages.create.assert_not_called()


def test_chunk_overlap_sources_and_empty_directory(tmp_path):
    with pytest.raises(ValueError, match="No nonempty"):
        load_chunks(tmp_path)
    (tmp_path / "guide.md").write_text("one two three four five six seven")
    chunks = load_chunks(tmp_path, size=4, overlap=1)
    assert [c.text for c in chunks] == ["one two three four", "four five six seven"]
    assert chunks[1].source == "guide.md" and chunks[1].number == 2


def test_semantic_index_ranks_vectors_not_shared_words(tmp_path):
    (tmp_path / "a.md").write_text("Money returned to the original payment card.")
    (tmp_path / "b.md").write_text("The boat has two bicycle spaces.")
    class Embeddings:
        def passage_embed(self, texts):
            assert len(list(texts)) == 2
            return [np.array([2., 0.]), np.array([0., 3.])]
        def query_embed(self, text):
            return [np.array([4., 0.])]
    index = SemanticIndex(tmp_path, embedder=Embeddings())
    assert index.search("Reimbursement", k=1)[0]["source"] == "a.md#chunk-1"
    assert index.search("Reimbursement", k=1)[0]["score"] == 1.0
    for query, k in [("", 1), ("hi", 8), ("hi", True)]:
        with pytest.raises(ValueError):
            index.search(query, k)


def test_document_collection_has_substance():
    docs = Path(__file__).resolve().parents[1] / "docs"
    files = list(docs.glob("*.md"))
    assert len(files) == 10
    assert all(len(path.read_text().split()) >= 250 for path in files)
