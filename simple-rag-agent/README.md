# Simple RAG agent

A terminal assistant for the entirely fictional **Northstar Ferry Cooperative**.
Ten substantial Markdown documents cover connected policies, schedules, and edge
cases. Haiku chooses when to call `search_docs`, can search repeatedly, and answers
with source citations. Nothing here books real travel.

## Setup (Python 3.11+)

From the repository root on Linux/macOS:

```bash
python3 -m venv simple-rag-agent/.venv
simple-rag-agent/.venv/bin/python -m pip install -r simple-rag-agent/requirements-dev.txt
cp simple-rag-agent/.env.example simple-rag-agent/.env
# Set ANTHROPIC_API_KEY securely in .env or your process environment.
simple-rag-agent/.venv/bin/python simple-rag-agent/agent.py
```

On Windows use `.venv\Scripts\python.exe` instead of `.venv/bin/python`.
`RAG_MODEL` optionally overrides `claude-haiku-4-5`. Live chat makes paid Anthropic
API calls and needs HTTPS access to `api.anthropic.com` and an account with model
access. No Ollama, Chroma server, LangChain, or embedding API key is required.

## Semantic retrieval

FastEmbed runs `BAAI/bge-small-en-v1.5` locally on the CPU through ONNX Runtime.
The first index build downloads model artifacts from Hugging Face and may need
access to its download/CDN hosts. Model weights are cached in the ignored `.cache/`
folder so later runs can reuse them. The model cache is **not conversation memory**.

Markdown files in this project's `docs/` are split into 220-word chunks with
40-word overlap. Passages and queries get embeddings; normalized dot products
rank passages by semantic similarity. Only the top three chunks are returned by
default, with a maximum of five per call. Scores are not calibrated confidence
values, and an irrelevant question still has a nearest match. The agent is
instructed to admit insufficient evidence. Citations are model-generated, not
automatically verified, so inspect sources for consequential decisions.

The document index is rebuilt **in memory at startup**. Edits to docs take effect
after restarting. The last four completed question/answer pairs provide follow-up
context; search traces are not carried into the next question. Type `/clear` to
forget that context, or `exit` to stop. Exiting loses the entire conversation and
index. No chat logs, vectors, or usage records are saved. Retrieved excerpts and
recent conversation text are sent to Anthropic; embeddings stay local.

## Agent loop and limits

For each question, Haiku receives the tool definition and decides whether to
search, refine a search, or answer. Tool results are returned to Haiku as structured
JSON with filename/chunk references. Invalid calls become tool errors so the model
can correct them. Retrieved documents are treated as reference data, not commands.

Defaults: six model turns, 900 output tokens per response, 25 seconds per API call,
and a 90-second overall question deadline. SDK automatic retries are disabled.
The question deadline includes retrieval; initial model download and indexing
happen before chat and are outside that deadline. Local search runs in a worker
thread; cancellation stops waiting but does not forcibly kill native embedding
work already running. EOF/Ctrl-C exits. API failures, truncation, and limits are
reported as incomplete answers and are not added to conversation history.

Each answer prints elapsed time, model turns, and input/output tokens for the
question and session. These are actual usage fields from completed API responses,
including tool-loop turns and resent conversation context. If a timed-out or
failed request incurred server usage without returning it, that usage is unknown
and absent from totals. Local embedding work consumes no Anthropic tokens. Counts
are not a price estimate. `/clear` leaves session token totals intact.

## Tests and a semantic smoke check

```bash
simple-rag-agent/.venv/bin/python -m pytest simple-rag-agent/tests -q
simple-rag-agent/.venv/bin/python -m pip check
```

Tests use mocked APIs and embeddings: no key, network, downloads, or paid calls.
To exercise real local embeddings and download/cache model weights without using
Claude, run from the project folder:

```bash
.venv/bin/python smoke_search.py
```

This checks semantic paraphrases against expected document sources. It is separate
from unit tests because it requires the embedding model artifacts.

Try these questions in chat:

- Can I get my money back if strong winds stop my connecting trip?
- Can a wheelchair traveler reach Mossbank when the gauge reads 1.0 meters?
- What does a member adult pay to reach Mossbank, bringing a bicycle?
- Can someone from Mossbank get home after the late festival sailing?
- How long do you keep assistance notes compared with payment records?
- Do you serve an airport? Can you confirm a seat for tomorrow?
