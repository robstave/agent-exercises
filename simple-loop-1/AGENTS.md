# Simple loop 1

This is a standalone dice-and-fortune example. `agent.py` contains the tool loop
and structured fortune generation. `tests/` contains mocked pytest tests.
`evals/run_evals.py` runs live scenarios and a model judge.

## Working conventions

- Keep this example self-contained and easy to read.
- Preserve the separation between the dice loop and fortune generation.
- Keep deterministic checks and subjective quality scores explicit in evals.
- Account for judge tokens in overall usage and keep judge usage visible.
- After code changes, run the relevant mocked tests. Run the full suite when
  changes affect both stages or shared configuration.
- Update the README and evaluation guide when their documented behavior changes.

## Run and test

All commands below run from the repository root in PowerShell. Setup commands
are in the root `AGENTS.md`. Live calls require `ANTHROPIC_API_KEY` in the
environment or `simple-loop-1/.env`.

```powershell
# Run the agent. It currently accepts no command-line flags.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/agent.py

# Run all mocked tests.
.\simple-loop-1\.venv\Scripts\python.exe -m pytest simple-loop-1/tests -q

# Select timeout tests and stop on the first failure.
.\simple-loop-1\.venv\Scripts\python.exe -m pytest simple-loop-1/tests -k timeout -x -v

# Run evaluation-runner tests without live API calls.
.\simple-loop-1\.venv\Scripts\python.exe -m pytest simple-loop-1/tests/test_evals.py -q
```

Model names and `API_TIMEOUT_SECONDS` are configured in `agent.py`. The API
timeout is currently 30 seconds and SDK retries are disabled.

## Live evaluations

```powershell
# One repeat of all scenarios, using the fortune model as the judge.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/evals/run_evals.py

# Five repeats with an explicit report path.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/evals/run_evals.py --repeats 5 --output simple-loop-1/evals/results/comparison.json

# Choose a judge model. Replace MODEL_ID with an available model ID.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/evals/run_evals.py --judge-model MODEL_ID

.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/evals/run_evals.py --help
```

- `--repeats` is a positive integer and defaults to 1.
- `--output` chooses the JSON report file and overwrites that file during the run.
  Omit it to create a timestamped report under `evals/results/`.
- `--judge-model` defaults to the fortune model.

Live evaluations incur API costs. They use scripted tool outcomes with real
model calls, report deterministic checks separately from quality averages, and
save token usage and judging explanations. Tests mock API calls and need no key.
