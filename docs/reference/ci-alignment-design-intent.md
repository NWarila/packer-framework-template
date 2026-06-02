# CI Alignment Design Intent

CI in this portfolio is divided by repository responsibility. The goal is not for every repository to run every possible check. The goal is for each repository to prove the behavior it owns and inherit the rest from the correct control plane or type template.

## Responsibility Split

| Repository type | Owns | CI should prove |
| --------------- | ---- | --------------- |
| Framework template | Reusable framework logic and stack-specific workflows | Code quality, policy correctness, template contract, framework build or validation, release evidence |
| Runner template | Data-only execution shape and caller contract | Contract shape, inherited org policy through thin callers, runtime validation appropriate to the runner |
| Runner consumer | Repository-specific variables/resources and actual execution | Secret safety, inherited drift, outcome verification, and narrow runtime checks |

## Non-Goals

- Runner consumers should not re-test framework internals that the framework repository owns.
- Framework templates should not duplicate universal org reusable workflow bodies.
- Namespace control planes should not own another namespace's org governance.
- Drift-gate should not force repo-specific docs, diagrams, inventories, or mature configs into byte identity.

## Design Heuristics

- A check belongs where the behavior is authored.
- A caller belongs where the repository needs to invoke inherited behavior.
- A byte-identical manifest entry belongs where local edits would be drift.
- A starter entry belongs where local edits would be maturity.
- A reusable workflow needs source-side smoke coverage before consumers depend on it.

## Reviewer Shortcut

When CI looks surprising, ask what the repository owns. Missing checks are real gaps only when the repository owns the behavior and no inherited or local gate covers it.
