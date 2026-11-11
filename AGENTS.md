# Agent playground

This repository contains small, independent examples for learning agents and
loops. Each example lives in its own directory with its own setup, dependencies,
tests, and documentation. `simple-loop-1` is the first example.

## Working conventions

- Keep changes scoped to the requested example. Read its `AGENTS.md` first.
- Prefer straightforward code and comments that explain the learning objective.
- Give new examples their own directory and README, and link them from the root
  README. Keep their environments and dependencies local to that directory.
- Update relevant documentation when commands or behavior change.
- Keep API keys in environment variables or ignored `.env` files.
- Use mocked tests for routine verification. Live runs and evals consume API
  credits; report clearly whether verification used mocks or live calls.

## Commands

PowerShell commands below run from the repository root. Use the example's virtual
environment explicitly.

```powershell
# Set up the first example.
python -m venv simple-loop-1/.venv
.\simple-loop-1\.venv\Scripts\python.exe -m pip install -r simple-loop-1/requirements-dev.txt

# Run the agent and its mocked tests.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/agent.py
.\simple-loop-1\.venv\Scripts\python.exe -m pytest simple-loop-1/tests -q

# Run live evaluations or inspect their flags.
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/evals/run_evals.py
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/evals/run_evals.py --help
```

See `simple-loop-1/AGENTS.md` for evaluation flags and focused test commands.
