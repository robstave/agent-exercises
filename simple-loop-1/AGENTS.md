# Simple loop 1

This example retries a dice tool, then asks a model for a structured fortune.
`agent.py` contains both stages. `tests/` contains mocked pytest tests.
`evals/run_evals.py` runs live scenarios and a model judge.

## Working conventions

- Keep this example self-contained and easy to read.
- Keep the dice loop and fortune generation separate.
- Keep deterministic checks and quality scores explicit in evals.
- Include judge tokens in total usage. Report judge usage separately.
- Run mocked tests after code changes. Run all tests when changes affect both
  stages or shared configuration.
- Update the README and evaluation guide when documented behavior changes.
- Use short sentences and active voice in documentation. Keep identifiers,
  commands, numbers, and caveats exact.

## Model selection

- Use `claude-haiku-5-5` when a cheaper Claude model is needed.
- Do not use `claude-haiku-4-5` as a cost-saving alternative.
- Respect configured model overrides. Print the resolved model, not a hardcoded label.

## Run and test

Run these PowerShell commands from the repository root.

```powershell
python -m venv simple-loop-1\.venv
.\simple-loop-1\.venv\Scripts\python.exe -m pip install -r simple-loop-1\requirements-dev.txt

# Run the agent. It currently accepts no command-line flags.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1\agent.py

# Run all mocked tests.
.\simple-loop-1\.venv\Scripts\python.exe -m pytest simple-loop-1\tests -q

# Select timeout tests and stop on the first failure.
.\simple-loop-1\.venv\Scripts\python.exe -m pytest simple-loop-1\tests -k timeout -x -v

# Run evaluation-runner tests without live API calls.
.\simple-loop-1\.venv\Scripts\python.exe -m pytest simple-loop-1\tests\test_evals.py -q
```

Live calls require `ANTHROPIC_API_KEY` in the environment or
`simple-loop-1/.env`. `agent.py` configures model names and
`API_TIMEOUT_SECONDS`. The default timeout is 30 seconds. SDK retries are disabled.

## Live evaluations

```powershell
# One repeat of all scenarios, using the fortune model as the judge.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1\evals\run_evals.py

# Five repeats with an explicit report path.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1\evals\run_evals.py --repeats 5 --output simple-loop-1\evals\results\comparison.json

# Choose a judge model. Replace MODEL_ID with an available model ID.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1\evals\run_evals.py --judge-model MODEL_ID

.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1\evals\run_evals.py --help
```

- `--repeats` is a positive integer and defaults to 1.
- `--output` chooses the JSON report file and overwrites that file during the run.
  Omit it to create a timestamped report under `evals/results/`.
- `--judge-model` defaults to the fortune model.

Live evaluations incur API costs. They use scripted tool outcomes with real
model calls, report deterministic checks separately from quality averages, and
save token usage and judging explanations. Tests mock API calls and need no key.
