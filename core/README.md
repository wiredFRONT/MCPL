# core: normalize

Not yet written. This folder will hold the single MCPL schema that the upstream mappings reduce to.

Planned parts, in the order they will be written:
1. **Inputs and actions.** One entry per thing the application accepts or does, in the MCP tool-definition shape, so the same entry can be served over MCP and emitted for the web.
2. **Rules.** What a valid result looks like for each action. This is what validates an AI's proposal before anything is applied.
3. **Posture.** Foundational by default; prototype only when stated; ask once when unknown.
4. **Screens and routes.** Declared, so guidance can link to the right place.
5. **Boundary.** What the application declares it knows, and the required answer when a question falls outside it.

Every field will state which upstream it maps to, or that it is an MCPL extension.
