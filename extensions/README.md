# extensions: extend

What no upstream specification defines. Everything in this folder is labeled MCPL: it is ours, not a standard. Research run R2 found no existing specification for any of these four.

| Extension | What it defines | Nearest precedent to borrow from |
|---|---|---|
| Workflows and navigation | A declared graph of an application's interactions: what follows what, which events chain, which screen each step lives on | Task and run states in other protocols describe execution, not an application's own flow |
| Signal provenance | Where a signal came from and how far to trust it, in a form that can be signed | The identity-card signing method in the agent-to-agent protocol |
| Restraint policy | When MCPL may ask the person something, and when it must not: once per item, never blocking, only on a call already in flight | None. The current MCP revision carries no rate-limit guidance |
| Approval evidence | A record a server can verify that a specific person approved a specific change | Only a page the application serves can observe the act itself |

Not yet written. Each extension gets its own folder with a specification, examples and tests.
