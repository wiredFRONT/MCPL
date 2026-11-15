# upstream: collapse

One entry per official specification MCPL aligns to. Each entry will become its own file stating what is taken, the pinned version, and the field-by-field mapping into `core/`. Nothing of ours lives in this folder.

The machine-readable version of this table is `sources.yaml`; it is the source of truth for pins and status. Written mappings so far: `mcp-tools.md` and `mcp-elicitation.md` (3 of 12 sources read first-hand). Every other row was read by research run R2 through a summarizing fetch tool and is not yet cross-checked by a second model.

| MCPL needs | Aligns to | Pin | Canonical source |
|---|---|---|---|
| Ask a multiple-choice question; collect non-secret details | MCP elicitation, form mode | 2026-07-28 (also serve 2025-11-25) | modelcontextprotocol.io/specification/2026-07-28/client/elicitation |
| Collect a secret or third-party authorization | MCP elicitation, URL mode; MCP authorization for sign-in | 2026-07-28 | same; modelcontextprotocol.io/specification/2026-07-28/basic/authorization |
| Rich inline UI; thumbs or slider | MCP Apps | stable 2026-01-26 | github.com/modelcontextprotocol/ext-apps |
| Describe an app's inputs and actions | MCP tool definition shape (JSON Schema 2020-12) | 2026-07-28 | modelcontextprotocol.io/specification/2026-07-28 |
| Always-on context | AGENTS.md | unversioned | agents.md |
| Guidance loaded on demand | Agent Skills | unversioned | agentskills.io/specification |
| Being found | MCP Registry server.json | schema 2025-12-11, preview | modelcontextprotocol.io/registry |
| Packaging | Agent Plugins | 1.0.0 | agent-plugins.org |

## Optional, not aligned by default
| Spec | When it applies | Pin |
|---|---|---|
| A2UI | Only where a host can render it, or inside MCPL's own app view | v1.0 per site; v0.9.1 production per repo (unresolved) |
| AG-UI | Only in embedded mode, where the application owns the frontend | 1.0 |
| WebMCP | Optional web output of the same inputs-and-actions inventory | draft dated 2026-11-11, not standards track |

## Considered and dropped
- Open-JSON-UI: no primary specification could be found.
- OpenAI Apps SDK as a separate item: it implements MCP Apps.
- A2A: for agents delegating to other agents; kept only as the precedent for signing.

## Constraints that come with these
- The server must speak both the pre-July and post-July 2026 MCP revisions.
- Since 2026-07-28 a server cannot open a prompt on its own. A question can only ride a call the AI already made.
- An in-chat accept is reported by the host. It is not proof of a human act.
