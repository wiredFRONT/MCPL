# routes

Runtime choices. A route is picked per request from the capabilities the host declares, never from the host's name. This table is synthesis from research run R2, not something any specification states; it is to be tested and corrected.

| Need | First choice | If not available | Floor |
|---|---|---|---|
| Multiple-choice question | Host form prompt | Inline app view | Options as text in the tool result |
| Non-secret details | Host form prompt | Inline app view | Ask in text |
| Secret or third-party sign-in | Link to a page the application serves | Plain link in the tool result | Never a form |
| Approval, routine | The host's own tool-approval prompt | | |
| Approval, recorded | Host form accept, labeled host-attested | | |
| Approval, must be a human act | Page the application serves | | |
| Thumbs or scale | Inline app view | One optional choice on a call already in flight | Text invitation |
| Rich UI | Inline app view | | Text |
| Default behavior of the AI | Server guidance text, essentials in the first 512 characters | A first-call guidance tool | Tool descriptions and results |

The floor every major host documents: a remote server, its tools, and the host's own approval prompt.

In embedded mode the application owns the interface, so none of these fallbacks apply.
