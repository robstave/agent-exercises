# Agent playground

A playground for learning simple AI agents and loops through small, runnable
Python examples. Explore how a model requests a tool, receives its result,
retries after a failure, and hands an output to the next step.

## Start here

[Simple loop 1 — dice and fortunes](simple-loop-1/README.md) is a two-stage example.
An agent calls a dice tool that sometimes fails and retries until it obtains a
number or reaches a stopping condition. A separate model call turns the number
into a structured meaning and fortune.

The example includes mocked unit tests, live model evaluations, automatic
quality judging, and token tracking. Its small task makes the control flow easy
to inspect while demonstrating patterns that carry over to larger applications.
Follow the example README for setup and commands. The
[evaluation guide](simple-loop-1/evals/README.md) explains scoring and reports.

## Ideas to go further

- Add tool arguments, such as the number of sides on the die, and validate them.
- Offer multiple tools and evaluate whether the agent chooses appropriately.
- Replace dice with an order lookup and check answers against known order data.
- Handle timeouts, malformed responses, and exhausted retries explicitly.
- Build an evaluation dataset from observed failures and realistic user requests.
- Compare prompts and models using the same cases, token totals, and quality rubric.
- Score a small set of outputs yourself and compare your ratings with the model judge.
- Experiment with a cheaper judge and measure its agreement with your ratings.
- Add report comparisons to spot regressions between runs.
