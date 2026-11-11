# Live evaluations

[Back to the example](../README.md)

Run from the repository root.

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
meaning and fortune, and a rubric. It returns scores from 1 to 5 with reasons.

- **Number relevance** — 1 unrelated, 3 plausible, 5 clearly and creatively tied to the roll.
- **Playfulness** — 1 flat or unpleasant, 3 pleasant, 5 imaginative and fun.
- **Clarity** — 1 confusing, 3 understandable, 5 concise and easy to read.

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


## How the tool is controlled

During loop scenarios, the runner temporarily patches `agent.run_tool` to return
scripted errors and successes. The model calls remain live. A separate wrapper
records API requests, responses, and usage while forwarding calls to the real
API. Both patches are restored after each case. Fortune cases generate and
judge real model output.

## Where human ratings fit

No manual scoring step is required to run these evaluations. The judge receives
the rubric, the roll, and the generated text and returns scores and explanations.

Human ratings can help validate the judge. For example, independently score 20
fortunes, let the judge score the same outputs, and inspect disagreements.
Refine the rubric when its wording produces inconsistent interpretations. A few
human-scored examples can demonstrate your standards in a future judge prompt.
The current implementation sends no human-scored examples and does not ingest
human ratings or calculate agreement automatically.

## Managing evaluation cost

Each valid fortune requires one generation call and one judging call. The rubric
and generated output contribute input tokens; scores and explanations contribute
output tokens. Existing reports preserve the judge's usage separately.

- Start with one repeat while developing and increase sampling for comparisons.
- Run quality evaluations when changing the prompt, model, or rubric.
- Keep structural checks in Python so they require no additional judging calls.
- Compare a cheaper judge using `--judge-model` after checking its ratings against yours.
- For a larger application, consider adding representative sampling of outputs.

Model judgments are estimates. A high automatic score is most useful when the
rubric reflects what you value and the judge's ratings agree with your reviews.


## API timeouts

Generation and judging use `API_TIMEOUT_SECONDS` from `agent.py`, currently 30
seconds, with SDK retries disabled. Timeout exceptions fail the current case
and are saved in its report. The runner continues with the next case. This
network timeout setting is separate from the overall duration of the eval run.
