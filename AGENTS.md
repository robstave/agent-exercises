# Repository guidance

These instructions apply to all projects in this repository.

## Model selection

- Use `claude-haiku-5-5` as the default when a cheaper Claude model is needed.
- Per the repository owner's guidance, Haiku 4-5 is older and costs more; do not
  select `claude-haiku-4-5` as a cost-saving alternative.
- Respect explicitly configured model overrides. When displaying the model in
  agent output, print the resolved configuration rather than a hardcoded label.

## README style

- Explain things at about 80% of the way to ASD-STE100.
- Use short sentences, active voice, and one idea per sentence.
- Keep identifiers, commands, numbers, and every caveat exactly as written.
- If something is uncertain, say so in one plain sentence.
