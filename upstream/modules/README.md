# Tracked modules

Optional git submodules that track the official repositories MCPL aligns to. They exist so a change upstream shows up as a pin that has fallen behind.

| Path | Repository | Commit pinned 2026-11-13 |
|---|---|---|
| `mcp-spec` | modelcontextprotocol/modelcontextprotocol | `06e9234` |
| `mcp-ext-apps` | modelcontextprotocol/ext-apps | `ea3e9d0` |
| `mcp-registry` | modelcontextprotocol/registry | `115f852` |

- These pins are the head of each default branch on that date. The specification version MCPL aligns to is recorded per source in `../sources.yaml`, which is the source of truth.
- Nothing in MCPL requires the submodules to be checked out. `git clone` without `--recurse-submodules` works.
- To fetch them: `git submodule update --init --depth 1`.
- AGENTS.md, Agent Skills and Agent Plugins are not tracked as modules yet: their official repositories are not confirmed.
