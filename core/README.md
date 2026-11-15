# core: normalize

The single MCPL schema that the upstream mappings reduce to. Draft; nothing here is accepted until it is in the INCRAM ledger.

| # | Part | Status | File |
|---|---|---|---|
| 1 | **Inputs and actions.** One entry per thing the application accepts or does | draft 0.1 | `action.schema.json` |
| 2 | **Rules (guards).** Named checks run on a proposal after schema validation and before preview | draft 0.1 | `guard.schema.json` |
| 3 | **Posture.** Foundational by default; prototype only when stated; ask once when unknown | not written (an action can already list its postures) | |
| 4 | **Screens and routes.** Declared, so guidance can link to the right place | not written (an action can already name its screen) | |
| 5 | **Boundary.** What the application declares it knows, and the required answer outside it | not written (an action already carries its outside-boundary answer) | |

## Part 1: the action entry

An entry has two halves and they never mix:

- `tool`: UPSTREAM. The MCP 2026-07-28 tool definition, unchanged. See `../upstream/mcp-tools.md`.
- `mcpl`: MCPL. Consequence, approval route, undo, preview, screen, posture, guards, outside-boundary answer.

What the schema enforces today:

- The input schema must refuse fields the application did not declare.
- A consequential action must have a plain-language preview and an approval; "none" is refused.
- An action with no undo must say why.

## Part 2: the guard entry

A guard catches a proposal that is well-formed but harmful in this person's situation. Everything about a guard is MCPL; no upstream defines it.

- It runs after the input schema and before any preview. Order of decision: schema, then guards, then accepted.
- It reads context the application supplies (for example where the person signs in from). The AI never supplies context.
- It returns pass, fail or unknown. On fail the guard either rejects or requires explicit confirmation. On unknown it asks one question or rejects. A guard never passes on missing context.
- It decides only. It never changes anything.

Worked guard: `../examples/firewall/guards/no-self-lockout.guard.json`, with seven decision cases in `../examples/firewall/cases/`.

Not settled: the guard's code is Python in the example because the validator is. Which languages a real application may write guards in, and how they are sandboxed, is open.
