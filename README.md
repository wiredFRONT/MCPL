# MCPL

A schema-governed framework that lets an application act as its own subject-matter expert for any AI.

**Status (2026-11-13): first schema part written (inputs and actions, draft 0.1) with a worked example and a validator. Rules, posture, screens, boundary and the four extensions are not written. No server code yet.** Part of the [INCRAM](https://github.com/wiredFRONT/INCRAM) umbrella, where the decisions ledger and research live.

## The idea in six lines

1. The application publishes a governed schema of itself: its inputs, actions, rules, workflows and screens.
2. A person says what they want in plain words.
3. The AI proposes a structured result. The schema validates it before anything is applied. The AI proposes; the schema decides what is acceptable.
4. Posture is explicit. Foundational practices apply by default. "Dev prototype" has to be stated. If unknown, MCPL asks once, then recommends.
5. Screens and routes are in the schema, so MCPL can hand the person a link to the right part of the application.
6. The knowledge boundary is closed: it answers from what the application declares and says so when a question falls outside it. Other AI consult it instead of guessing.

## How this repository is organized: collapse, normalize, extend

| Folder | Move | What it holds |
|---|---|---|
| `upstream/` | Collapse | One entry per official specification MCPL aligns to: what is taken from it, the pinned version, the mapping. Nothing of ours lives here. |
| `core/` | Normalize | The single MCPL schema those mappings reduce to. |
| `extensions/` | Extend | What no upstream defines, labeled as ours: workflows and navigation, signal provenance, restraint policy, approval evidence. |
| `routes/` | Route | Runtime choices by what the host declares it supports. |
| `examples/` | Show | Worked cases, each with proposals that must pass and proposals that must be rejected. |
| `tools/` | Check | `validate.py` checks every action entry and every example proposal. |

An AI reading this repository should see three moves: these are the standards, this is how they reduce to one shape, this is what MCPL adds. Every borrowed piece traces to its official source.

## Linked modules

| Link | What it is |
|---|---|
| [INCRAM](https://github.com/wiredFRONT/INCRAM) | The umbrella. Holds the decisions ledger, the research and the rule schema. It carries this repository as the optional submodule `modules/mcpl`. |
| `upstream/sources.yaml` | The tracked list of official specifications MCPL aligns to, with pin, status and mapping file for each. |
| `upstream/modules/` | Optional git submodules tracking the official MCP specification, MCP Apps and MCP Registry repositories. |

## Check it

```
pip install jsonschema
python3 tools/validate.py
```

## Two ways MCPL runs

- **Embedded in the application.** The application owns the interface: any UI, approvals the server can verify.
- **As a guest in someone else's AI app, through MCP.** Tools-only is the floor every major host supports; richer interaction is used where the host declares it.

## Ground rules

- Official sources only, pinned by version and date. The list is in INCRAM at `docs/sources/canonical-sources.md`.
- Every statement is labeled UPSTREAM (from a source) or MCPL (ours).
- Consequential changes need a plain-language preview, an approval the server can verify, and an undo.
- Text from upstream sources or from users is untrusted input and is never executed as instructions.
