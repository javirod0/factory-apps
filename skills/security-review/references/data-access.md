# Data access and row-level security

## Postgres RLS traps

These cause silent, complete authorization failures. Check every one on any
change to policies, tables, or views.

| Trap | Consequence |
|---|---|
| RLS not enabled on a new table | Everything is readable. The most common cause of cross-user leaks. |
| `ENABLE` without `FORCE ROW LEVEL SECURITY` | Table owner bypasses all policies. |
| A view without `security_invoker = true` | The view runs as its creator and bypasses the caller's policies entirely. |
| `UPDATE` policy with no matching `SELECT` policy | Updates silently affect zero rows and return success. Fails open in the worst way: no error, no effect. |
| Policy referencing user-editable metadata | User-editable claims must never drive authorization. Use the server-controlled claims field. |
| `USING` without `WITH CHECK` on write policies | Users can write rows they cannot read, including rows attributed to others. |
| Function marked `SECURITY DEFINER` unnecessarily | Runs with the definer's privileges, bypassing the caller's policies. |

## Every new table

1. `ENABLE` and `FORCE` row level security in the same migration that creates
   the table. Not a follow-up migration — the same one.
2. A policy for every operation the table supports: select, insert, update,
   delete. An operation without a policy is denied, which is correct; an
   operation with a wrong policy is the danger.
3. A test that a second user cannot read, write, or delete the first user's
   rows. Not a unit test with mocks — a test that connects as each user.

## Multi-user tests are mandatory

A policy is not verified until a test proves the negative case. For every access
rule, one test that the authorized user succeeds and one that an unauthorized
user fails.

The negative test is the important one. Positive tests pass on a table with no
policies at all.

## API layer

- Authorization is enforced server-side on every endpoint. Client checks are UX,
  not security.
- Any identifier that arrives from the client is untrusted. Never trust a user
  identifier in a request body; derive identity from the verified token.
- IDOR: for every endpoint taking a resource identifier, confirm the handler
  checks that the caller may access that specific resource.
- Enumeration: not-found and not-permitted should be indistinguishable to the
  caller where the existence of a record is itself sensitive.
- Rate limiting on anything that can be used to guess or enumerate.
- Idempotency keys must be scoped to the caller, or one user can interfere with
  another's requests.

## Deletion and export

For every data type added:

- Is it removed on account deletion, including from backups within the stated
  window, derived tables, caches, and analytics?
- Is it included in a data export request?
- If it references a person who is not the account holder, what happens to it
  when that person objects?

These are compliance obligations, and they are almost always discovered late.
Check them at the point the data type is created, not before release.
