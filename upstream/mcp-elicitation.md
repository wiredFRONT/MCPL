# MCP elicitation (form mode and URL mode)

- Need it serves: ask a multiple-choice question; collect non-secret details; collect a secret or a third-party authorization.
- Pin: MCP 2026-07-28 (URL mode was introduced in 2025-11-25 and the page says its design may still change).
- Source: https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation
- Status: UPSTREAM facts below were read from that page on 2026-11-15. Not yet cross-checked by a second model.

## What the specification defines (UPSTREAM)

| Topic | What the page says |
|---|---|
| Modes | `form` (data passes through the client) and `url` (the person is sent to a page; the data does not pass through the client) |
| Declaring support | The client declares `elicitation` with `form` and/or `url` in its per-request capabilities. An empty object means form only. A server must not send a mode the client did not declare |
| Delivery | Inside an input-required result, in answer to a request the client already made. The client then retries that request with the response |
| Form schema | A flat object of primitives only: string (formats `email`, `uri`, `date`, `date-time`), number or integer, boolean, and enums in four shapes (single or multi-select, with or without titles). Every primitive can carry a default. No nested objects |
| Response | `accept` (with the data, in form mode), `decline`, or `cancel` |
| Secrets | A server must not use form mode for passwords, API keys, access tokens or payment credentials, and must use URL mode for those. Name, email address or username are not prohibited in a form |
| URL mode limits | Not for authorizing the client's access to the server itself. The URL must not carry personal data or be pre-authenticated. The client must show the full URL and get consent before opening it |
| What `accept` means in URL mode | Only that the person agreed to open the page. It does not mean the interaction finished |
| Who opened the page | The server must verify that the person who opens the URL is the person the request was made for |
| Identity | A server must not rely on user identification supplied by the client without verifying it |

## What MCPL takes

All of it, unchanged.

## Mapping into `core/`

| Upstream | MCPL | Change |
|---|---|---|
| Form mode, one property | A guard's `ask_message` (`core/guard.schema.json`): the one question asked when context is missing | MCPL limits it to one question per decision |
| Enum with titles | Multiple-choice answers offered to the person | none |
| `decline` and `cancel` | Nothing is applied; the proposal ends | none |
| URL mode | The `served-page` approval route in `core/action.schema.json`, and any secret | none |
| "Accept only means consent to open" | Why a `served-page` approval is decided by what the page records, never by the `accept` | none |
| Verify who opened the page | A requirement on the approval-evidence extension | to be written |
| Delivery only on a call in flight | The restraint extension: MCPL cannot start a conversation | none |

## What it does not cover (goes to `extensions/`)

How often MCPL may ask, proof that a human acted, and a record of the approval that a third party can check.
