# Simple RAG agent

Answer fictional ferry questions with local semantic search and a model-driven tool loop.

## Working conventions

- Keep this example self-contained and easy to read.
- Keep retrieval, the model loop, and conversation handling clear.
- Run the mocked tests after code changes.
- Update the README when documented behavior or commands change.
- Keep API keys in the environment or ignored `.env` files.
- Use short sentences and active voice in documentation. Keep identifiers,
  commands, numbers, and caveats exact.

## Model selection

- Use `claude-haiku-5-5` when a cheaper Claude model is needed.
- Do not use `claude-haiku-4-5` as a cost-saving alternative.
- Respect configured model overrides. Print the resolved model, not a hardcoded label.

## Setup and run

Run these PowerShell commands from the repository root.

```powershell
python -m venv .venv
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python .\agent.py
```

Set `ANTHROPIC_API_KEY` in the environment or in `simple-rag-agent/.env`.
Live chat makes paid API calls. The first semantic index build downloads and
caches embedding model files.

## Tests and semantic smoke check

Tests use mocked APIs and embeddings. They need no key, network, downloads, or
paid calls.

```powershell
.\simple-rag-agent\.venv\Scripts\python.exe -m pytest simple-rag-agent\tests -q
.\simple-rag-agent\.venv\Scripts\python.exe -m pip check
Push-Location simple-rag-agent
.\.venv\Scripts\python.exe smoke_search.py
Pop-Location
```

The smoke check downloads and caches model files. It checks local semantic
retrieval and does not call Claude.
