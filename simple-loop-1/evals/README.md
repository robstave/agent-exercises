# Live evaluations

Run from the repository root:

```powershell
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/evals/run_evals.py
```

Requires ANTHROPIC_API_KEY in the environment or simple-loop-1/.env.
This uses paid calls for the agent and the judge. Each repeat includes four
scripted dice scenarios, six fortune generations, and a judging call for each
fortune with valid fields. Use --repeats 5 for repeated sampling.
Use --output path/to/report.json to choose the report location.

The judge defaults to the fortune model in a separate call. Choose another
available model with --judge-model MODEL_ID. It receives the die roll, generated
meaning and fortune, and a rubric. It returns scores from 1 to 5 with reasons:
- Number relevance: 1 unrelated, 3 plausible, 5 clearly and creatively tied to the roll.
- Playfulness: 1 flat or unpleasant, 3 pleasant, 5 imaginative and fun.
- Clarity: 1 confusing, 3 understandable, 5 concise and easy to read.

Quality ratings are model opinions. Inspect saved reasons to assess whether
they match your taste. Quality scores have no pass threshold. PASS means the
deterministic checks succeeded and any required judging completed successfully.
Judge errors fail that case while preserving the generated output and checks.

Reports in results/ include requests, responses, models, source hash, tool
history, checks, errors, quality scores and reasons, and average scores.
The console prints the averages and number of fortunes judged. Failed or skipped
judgments are excluded from averages. Persistent failure passes if the agent
attempts the dice tool and stops without a number within the turn limit.

Total token usage includes both generation and judging. Judge usage is also
reported separately as a subset. Totals cover usage returned by the API;
requests that fail without returning usage cannot be counted.
Reports are saved after each case. Compare reports using the same repeat count,
model settings, and rubric. These evaluations run separately from pytest.
