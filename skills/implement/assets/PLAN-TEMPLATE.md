# PLAN: <short task title>

> One-sentence statement of what this plan delivers.
> e.g. "Add refresh-token rotation to the auth service so a refresh token is single-use."

## Goal

What the user-visible outcome is, in 1–3 sentences. Cite the source if there is one: a ticket, a `CONTEXT-*.md`, a Slack thread.

## Non-goals

What this plan is *not* doing, even if related. Pin this down explicitly — it's how scope creep is prevented.

- Not migrating to a different OAuth library.
- Not changing access-token lifetime.
- Not modifying the admin UI's display of token records (separate ticket).

## References

Files / docs this plan is built against. Anyone reviewing the plan should be able to follow the trail.

- `CONTEXT-oauth-refresh.md`
- `src/auth/tests/refresh.test.ts` (encodes the invariants)
- `migrations/2024-08-01-refresh-tokens.sql` (current schema)

## Approach

The numbered list of steps. Keep each step:

- **Small** — one logical change, ideally under 100 lines of diff.
- **Verifiable** — there is a check (a test, a build, a type-check) that proves the step worked.
- **Independent where possible** — earlier steps shouldn't depend on later ones being done.
- **Reversible** — if step N is wrong, you can undo it without unwinding step N+1.

Use this format for each step:

```
### Step N: <verb-led title>
**Files:** path/a.ts, path/b.ts
**Change:** one or two sentences on what's being added/modified.
**Check:** the exact command(s) that prove this step worked.
**Status:** [ ] not started | [~] in progress | [x] done | [!] blocked
```

Example:

### Step 1: Add `rotated_from` column to refresh_tokens
**Files:** `migrations/2026-05-20-rotated-from.sql`
**Change:** New migration adding nullable `rotated_from UUID` column referencing `refresh_tokens.id`. No data backfill — existing rows stay NULL.
**Check:** `npm run db:migrate:test` exits 0 and `psql -c '\d refresh_tokens'` shows the column.
**Status:** [ ] not started

### Step 2: Extend `RefreshTokenRecord` type
**Files:** `src/auth/types.ts`
**Change:** Add optional `rotatedFrom?: string` field. Existing consumers unaffected because field is optional.
**Check:** `npm run typecheck` passes.
**Status:** [ ] not started

### Step 3: Update `rotateRefreshToken` to link new token to old
**Files:** `src/auth/refresh.ts`
**Change:** When issuing a rotated token, set `rotated_from` to the previous token's ID and mark the previous token's `used_at`.
**Check:** `npm test src/auth/tests/refresh.test.ts` passes; the existing "single-use" test still passes.
**Status:** [ ] not started

### Step 4: Add test for the linkage
**Files:** `src/auth/tests/refresh.test.ts`
**Change:** New test asserting that after rotation, the new record's `rotated_from` equals the old record's `id`.
**Check:** The new test passes; full file's suite still passes.
**Status:** [ ] not started

## Current step

Which step you are actively working on. Update this as you progress. "None — all steps done" when finished.

## Risks

What could go wrong during execution, and the watch-out.

- Race condition under concurrent refresh: existing code claims to serialize via `SELECT ... FOR UPDATE`. Verify in step 3.
- Backwards-compat of the response payload: `rotatedFrom` field is internal-only; do not surface it on the HTTP response in this iteration. (See Non-goals.)

## Docs affected

Documentation this change will invalidate. Updating these is part of Phase 4, not a separate planned step. Leave empty if the change is internal and touches no documented surface.

- `README.md` — "Usage" section, the `--example-flag` example will need the new `--rotate` flag added.
- Docstring on `rotateRefreshToken` — current docstring says "returns a new token"; needs to mention the linkage to the previous token.
- `docs/api/auth.md` — `/auth/refresh` response shape is documented; verify it doesn't need updating (probably not — `rotatedFrom` stays internal per Non-goals).

## Verification

The commands that constitute "done" for the whole plan. Run all of these in Phase 4.

- `npm test` — full suite
- `npm run lint`
- `npm run typecheck`
- `npm run build` (sanity)

## Out-of-scope observations

Things noticed during implementation that are *not* part of this plan. Log here as you go; they become follow-up tickets.

- `src/auth/login.ts:42` has a TODO from 2023 about password hashing.
- The migration script doesn't use a transaction; consider adding one in a follow-up.
