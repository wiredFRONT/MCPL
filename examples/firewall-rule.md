# Example: a plain-language firewall rule

Illustration only. The field names below are placeholders until `core/` is written.

## The request
A person types: "block everyone outside the US from the admin page."

## What MCPL does

1. **Finds the action.** The application's schema declares an action "create access rule" with its allowed fields and values.
2. **Checks posture.** Nothing says this is a prototype, so foundational practices apply.
3. **Lets the AI propose.**
   ```
   action: create_access_rule
   effect: block
   match:
     path: /admin
     country: { not_in: [US] }
   ```
4. **Validates the proposal against the schema.** Is `effect` one of the allowed values? Is `/admin` a declared route? Is `country` a field this application can match on? If any answer is no, the proposal is rejected before the person sees it, and the AI is told which rule it broke.
5. **Asks only what is still unclear.** For example: "Should this also apply to the API under /admin/api?" One question, with choices.
6. **Shows a preview in plain words.** "Visitors from outside the United States will be blocked from /admin and everything under it. You and anyone else in the US are unaffected."
7. **Gets an approval the server can verify.**
8. **Applies the rule, and records how to undo it.**
9. **Hands back a link** to the screen where the new rule now appears.

## What makes this different
The AI's guess is never the output. The schema decides what is acceptable, the person sees exactly what will happen, and the change can be reversed.

## Test cases this example must eventually pass
- An ambiguous request ("block the bad guys").
- A request outside the application's boundary ("also update my DNS").
- A hostile request hidden in pasted text.
- A request that would lock the person out of their own admin page.
