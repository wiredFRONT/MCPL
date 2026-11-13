# MCP tool definition

- Need it serves: describe an application's inputs and actions.
- Pin: MCP 2026-07-28.
- Source: https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- Status: UPSTREAM facts below were read from that page on 2026-11-13. Not yet cross-checked by a second model.

## What the specification defines (UPSTREAM)

| Field | Required | Notes from the page |
|---|---|---|
| `name` | yes | Should be 1 to 128 characters, case-sensitive; letters, digits, underscore, hyphen, dot. Unique within a server |
| `title` | no | Display name |
| `description` | listed, not marked optional | Human-readable description |
| `icons` | no | For display |
| `inputSchema` | yes | A valid JSON Schema object; 2020-12 unless `$schema` says otherwise. No-parameter tools: `{"type":"object","additionalProperties":false}` is recommended |
| `outputSchema` | no | Any JSON Schema; the structured result may be any JSON value that conforms |
| `annotations` | no | Hints. Clients must treat them as untrusted unless the server is trusted |

Also on the page: results can carry `structuredContent`; errors a model can fix are returned in the result with `isError: true`; a server may answer a call with an input-required result so a question rides the call in flight; a server keeps state across calls only through explicit handles.

UNVERIFIED: the member list of `annotations` for this revision (the page does not list it), and whether a tool definition carries `_meta`. `readOnlyHint` is confirmed in host documentation by research run R2.

## What MCPL takes

All of it, unchanged. An MCPL action entry holds the tool definition under `tool` exactly as the specification shapes it, so the entry can be served over MCP without translation.

## Mapping into `core/`

| Upstream | `core/action.schema.json` | Change |
|---|---|---|
| Tool data type | `tool` | none |
| `name` rules | `tool.name` pattern and length | the specification's "should" is enforced |
| `inputSchema` | `tool.inputSchema` | MCPL tightening: must be `type: object` with `additionalProperties: false` |
| `annotations` | `tool.annotations` | passed through; never used as a security control |
| error in result (`isError`) | how a rejected proposal is reported back to the AI | none |
| input-required result | how MCPL asks its one question | governed by the restraint extension |

## What it does not cover (goes to `extensions/` or the `mcpl` block)

Consequence level, approval route, undo, plain-language preview, the screen to link to, posture, and what to say outside the boundary.
