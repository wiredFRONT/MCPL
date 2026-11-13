# core: normalize

The single MCPL schema that the upstream mappings reduce to. Draft; nothing here is accepted until it is in the INCRAM ledger.

| # | Part | Status | File |
|---|---|---|---|
| 1 | **Inputs and actions.** One entry per thing the application accepts or does | draft 0.1 | `action.schema.json` |
| 2 | **Rules.** Named guards run on a proposal after schema validation and before preview | not written | |
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

What it does not do yet: guards such as "do not lock the person out of their own admin page" are only named. They need part 2.
