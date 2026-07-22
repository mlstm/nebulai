# CONTEXT: <short task title>

> One sentence stating what this document is for.
> e.g. "Context for implementing OAuth refresh-token rotation in the auth service."

## Task

What the user asked for, in your own words. 2–4 sentences. Include the user-visible behavior change.

## Non-goals

What this task is explicitly _not_ doing. Equally important as the goal. e.g. "Not migrating to a different OAuth library." "Not changing the existing access-token lifetime."

## Project shape

- **Language(s) / runtime:** e.g. TypeScript / Node 20
- **Build:** `<command>`
- **Test:** `<command>` (framework: <name>)
- **Lint / format:** `<command>`
- **Layout convention:** e.g. "monorepo, packages under `packages/`, each with its own `src/` and `tests/`"
- **AGENTS.md / contributor docs present?** yes / no — and what they say that's relevant

## Files that will be modified

For each file: path, one-line purpose, and the symbols within it that are relevant.

- `src/auth/refresh.ts` — refresh-token issuance and rotation. Symbols: `issueRefreshToken`, `rotateRefreshToken`, `RefreshTokenRecord`.
- `src/auth/index.ts` — public exports of the auth package. Symbols: re-exports of the above.
- ...

## Files that constrain the change (read-only)

Files that won't be modified but whose contents shape what the change must look like.

- `src/auth/tests/refresh.test.ts` — existing test suite. Invariants encoded: "a refresh token can only be used once", "rotation preserves the original `sub` claim".
- `src/auth/types.ts` — shared type definitions; `RefreshTokenRecord` shape must remain backwards-compatible.
- `migrations/2024-08-01-refresh-tokens.sql` — current table schema for `refresh_tokens`.
- ...

## Public API surface

What does this change expose or modify across module boundaries? e.g.

- Exported from `@org/auth`: `rotateRefreshToken(token: string): Promise<RefreshTokenPair>` — currently consumed by `@org/api-gateway` and `@org/admin-ui`.
- HTTP: `POST /auth/refresh` — request/response shape documented in `docs/api/auth.md`.

If there is no cross-module surface, say so explicitly: "Internal change only; no exported symbols affected."

## Conventions to follow

Project-specific patterns the change must conform to. Cite the file where each convention is established.

- **Error handling:** custom errors from `src/errors.ts`, never bare `Error`. See `src/auth/login.ts:42` for the pattern.
- **Logging:** structured logger from `src/log.ts`. Never `console.log`.
- **DB access:** all queries go through the `db` client in `src/db/index.ts`, with `params` arrays — never string-concatenated SQL. See `src/users/repo.ts` for the pattern.
- ...

## Data model

Only fill in if the change touches persisted data, otherwise write "N/A".

- Current schema: ...
- Required changes: ...
- Migration story: ...

## Recent history

What's been changing in this area lately? `git log --since="3 months ago" --oneline -- <paths>` output, annotated.

- `a3f2b1c` — "refactor: extract token-validation helper" (2 weeks ago) — moved validation logic into `src/auth/validate.ts`. Affects this task because: ...
- ...

If nothing relevant: "No relevant changes in the last 3 months."

## Approach sketch

The minimum sketch of how the change will be made. Not a full plan — that comes later. 3–6 bullets. e.g.

- Add a `rotated_from` column to `refresh_tokens` (migration).
- Update `rotateRefreshToken` to insert a new row referencing the old one and mark the old as `used_at = now()`.
- Update the `/auth/refresh` handler to call the new rotation logic.
- Update the existing test for "single-use" to also assert the `rotated_from` linkage.

## Risks

What could go wrong, and what to watch for.

- Race condition: two simultaneous refresh requests with the same token. Existing code handles this via ... (verify).
- Backwards-compat: clients on older versions may expect the old response shape. Check `@org/sdk` for the consumer.

## Open questions

Specific, answerable questions for the user. Do not leave this empty unless you are certain. If empty, write "None."

- Should the rotation also invalidate all _previously-rotated_ tokens in the chain, or just the immediate predecessor?
- Is there an existing rate limit on `/auth/refresh`, or should this task add one?
- The admin UI surfaces refresh-token records to operators — does the `rotated_from` chain need to be visible there in this iteration, or is that a follow-up?

## Out-of-scope observations

Things I noticed during discovery that are _not_ part of this task but might be worth a separate ticket. Keep brief.

- `src/auth/login.ts` has a TODO from 2023 about replacing the password hash function.
- The test suite for `src/auth/` runs in ~8s; could likely be parallelized.
