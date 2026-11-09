

<mermaid>

flowchart TD
    A([Start]) --> B["Ask the model to roll the die"]
    B --> C{"Model requests the dice tool?"}
    C -->|No| H([Skip the fortune])
    C -->|Yes| D{"Eighth identical request?"}
    D -->|Yes| H
    D -->|No| E["Run the dice tool"]
    E --> F{"Python gets a valid roll?"}
    F -->|Yes| I["Ask a separate model to write a fortune"]
    I --> J([Print the roll and fortune])
    F -->|No| G{"Model turns remaining?"}
    G -->|No| H
    G -->|Yes| K([Return to the model with the error])

    </mermaid>

## Tests

Run from the repository root. Tests mock API calls and require no API credentials.

```powershell
.\simple-loop-1\.venv\Scripts\python.exe -m pytest simple-loop-1/tests -q
```

## Live evaluations

Run from the repository root with `ANTHROPIC_API_KEY` configured in the environment
or `simple-loop-1/.env`. Evaluations make paid API calls for generation and judging.

```powershell
.\simple-loop-1\.venv\Scripts\python.exe simple-loop-1/evals/run_evals.py
```

Add `--repeats 5` for repeated sampling. Each repeat evaluates four dice scenarios
and generates a fortune for each of the six die faces.

The dice scenarios temporarily replace the tool implementation with predictable
outcomes, including failures followed by success. The real model decides whether
to request the tool and retry. Checks cover tool selection, expected results,
execution counts for successful scenarios, and the turn limit.

Fortune evaluations check the required fields and combined word limit. Each
fortune with valid fields also goes to a separate model call that grades its
quality and explains each score.

| Dimension | Score 1 | Score 3 | Score 5 |
| --- | --- | --- | --- |
| Number relevance | Unrelated to the roll | Plausible connection | Clearly and creatively tied to the number |
| Playfulness | Flat or unpleasant | Pleasant | Imaginative and fun |
| Clarity | Confusing | Understandable | Concise and easy to read |

The judge defaults to the fortune model. Add `--judge-model MODEL_ID` to use
another available model. Scores are subjective model judgments; inspect the
saved explanations to see whether they match your expectations.

The final console summary reports average quality scores, the number of fortunes
judged, and total input and output tokens. Judge tokens appear separately and are
included in the overall total. Usage covers API responses that return token counts.

Quality scores have no pass threshold. PASS means the deterministic checks passed
and any required judging completed successfully. A judging error fails the case
and preserves its generated output and checks. Failed or skipped judgments are
excluded from quality averages.

JSON reports are saved under `simple-loop-1/evals/results/` after each case. They
include requests, responses, model names, checks, ratings, explanations, timing,
and token totals. Use `--output path/to/report.json` to choose a report location.

See [the evaluation guide](evals/README.md) for additional details.
