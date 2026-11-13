# Instructions for AI agents working in this repository

Read the decisions ledger in the INCRAM umbrella first: https://github.com/wiredFRONT/INCRAM/blob/main/docs/decisions/ledger.md

## Rules
- Keep the three moves separate. `upstream/` holds only what official specifications say. `core/` holds the normalized schema. `extensions/` holds only what MCPL defines itself. Never mix them.
- Cite official sources only, with version and date. Mark anything not confirmed from the primary source as UNVERIFIED.
- Label every statement UPSTREAM or MCPL.
- Choose a route from the capabilities a host declares on the request, never from the host's name.
- An in-chat approval is the host's report, not proof of a human act. Anything that must be a human act goes through a page the application serves.
- Secrets never go through an in-chat form.
- Do not change decisions. They belong to the founder. Propose changes in the ledger's corrections table.
- One decision per pass. Commit and push at least hourly while working.
