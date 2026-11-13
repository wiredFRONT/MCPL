# extensions: extend

What no upstream specification defines. Everything in this folder is labeled MCPL: it is ours, not a standard. Research run R2 found no existing specification for any of these four. The second-model cross-check of 2026-11-13 challenges that for two of them: SCXML (W3C) for workflows, and PROV-O (W3C) plus the CloudEvents signed-event design for provenance. Compare against those before writing ours.

| Extension | What it defines | Nearest precedent to borrow from |
|---|---|---|
| Workflows and navigation | A declared graph of an application's interactions: what follows what, which events chain, which screen each step lives on | Task and run states in other protocols describe execution, not an application's own flow |
| Signal provenance | Where a signal came from and how far to trust it, in a form that can be signed | The identity-card signing method in the agent-to-agent protocol |
| Restraint policy | When MCPL may ask the person something, and when it must not: once per item, never blocking, only on a call already in flight | None. The current MCP revision carries no rate-limit guidance |
| Approval evidence | A record a server can verify that a specific person approved a specific change | A page the application serves observes the request itself, but an authenticated request does not show whether a person or automation made it. WebAuthn user presence and user verification are the primitives to evaluate (R2 cross-check, 2026-11-13) |

Not yet written. Each extension gets its own folder with a specification, examples and tests.
