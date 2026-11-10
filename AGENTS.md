# Repository guidance

These instructions apply to all projects in this repository.

## Model selection

- Use `claude-haiku-5-5` as the default when a cheaper Claude model is needed.
- Per the repository owner's guidance, Haiku 4-5 is older and costs more; do not
  select `claude-haiku-4-5` as a cost-saving alternative.
- Respect explicitly configured model overrides. When displaying the model in
  agent output, print the resolved configuration rather than a hardcoded label.
