# Example: a plain-language firewall rule

The action entry and test proposals for this walk-through are in `firewall/` and are checked by `tools/validate.py`. Steps 5 to 9 below are still illustration: they need parts of `core/` and `extensions/` that are not written.

## The request
A person types: "block everyone outside the US from the admin page."

## What MCPL does

1. **Finds the action.** The application's schema declares an action "create access rule" with its allowed fields and values.
2. **Checks posture.** Nothing says this is a prototype, so foundational practices apply.
3. **Lets the AI propose.**
   ```json
   { "effect": "block", "path": "/admin", "country": { "not_in": ["US"] } }
   ```
   (`firewall/proposals/valid-block-admin-outside-us.json`)
4. **Validates the proposal against the schema.** Is `effect` one of the allowed values? Is `/admin` a declared route? Is `country` a field this application can match on? If any answer is no, the proposal is rejected before the person sees it, and the AI is told which rule it broke.
5. **Asks only what is still unclear.** For example: "Should this also apply to the API under /admin/api?" One question, with choices.
6. **Shows a preview in plain words.** "Visitors from outside the United States will be blocked from /admin and everything under it. You and anyone else in the US are unaffected."
7. **Gets an approval the server can verify.**
8. **Applies the rule, and records how to undo it.**
9. **Hands back a link** to the screen where the new rule now appears.

## What makes this different
The AI's guess is never the output. The schema decides what is acceptable, the person sees exactly what will happen, and the change can be reversed.

## Test cases

| Case | Status |
|---|---|
| A proposal carrying a field the application never declared ("also update my DNS") | rejected today: `firewall/proposals/invalid-undeclared-field.json` |
| A proposal naming a route the application does not have | rejected today: `invalid-undeclared-route.json` |
| A proposal with an effect outside the allowed values | rejected today: `invalid-effect.json` |
| An ambiguous request ("block the bad guys") | not covered: needs the restraint extension |
| A hostile request hidden in pasted text | not covered: needs signal provenance |
| A request that would lock the person out of their own admin page | named as the guard `no-self-lockout`; not enforced until rules are written |
