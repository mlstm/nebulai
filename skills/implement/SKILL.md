---
name: implement
description: >-
  Implement a feature, bug fix, or refactor in an existing codebase by writing or modifying code against a known plan. Use this skill when the user asks to "implement", "build", "add", "write the code for", "make the change", or "do it" — and the task is concrete enough that you know what files to touch. If a CONTEXT-<task>.md document already exists for this task, load it; if not, and the task is non-trivial, recommend running the discovery skill first instead of guessing. Also use when the user explicitly hands off from a discovery or planning session ("here's the context doc, go implement it"). Do NOT use this skill for exploration or context-gathering (use discovery), trivial one-line edits the user pointed at directly, code review, debugging without a plan, or tasks where the user is still deciding what they want. Produces working code with tests, validated by running the project's test and lint commands before handing back.
license: MIT
metadata:
  author: "Tim Miles"
  email: "49971977+mlstm@users.noreply.github.com"
  version: "1.0"
---

# Implement

Write code against a known plan, in small reversible steps, with the plan visible on disk the whole time.

## Why this exists

Asked to "implement feature X", agents tend to: skim a few files, start editing, lose track of what they're doing halfway through, silently fix unrelated things they noticed, declare victory without running the full test suite, and produce a diff that's twice the size of what was asked for. This skill exists to prevent each of those failure modes by externalizing the plan and gating progress on small verifiable steps.

This is the second half of a two-phase workflow. The first half (`discovery`) produces a context artifact. This skill consumes that artifact. If there is no artifact and the task is non-trivial, recommend running discovery first rather than implementing blind.

## When this skill is active

You may write, edit, and run code. You may not:

- Commit, push, open pull requests, or merge anything unless the user explicitly asks in the current turn.
- Modify files outside the scope established in `PLAN.md` without updating the plan first.
- Install packages, run migrations, or do anything that mutates state outside the repo working directory without asking.
- Touch `.env`, secrets, anything under `~/.ssh`, `~/.aws`, etc.
- Run destructive commands (`rm -rf`, `git reset --hard`, `git push --force`, `DROP TABLE`) without explicit confirmation in the current turn.

## The procedure

### Phase 1 — Load context

In your first action, look for an existing `CONTEXT-<slug>.md` for this task (in the repo root or `docs/context/`). If it exists, read the whole thing.

If no context document exists:

- If the task is trivial (a one-line fix, a rename in a single file the user pointed at), skip to Phase 2 with a one-paragraph "scope" note instead of a full context doc.
- If the task is non-trivial, stop and recommend: "I don't see a `CONTEXT-*.md` for this task. The `discovery` skill produces one — running it first will make the implementation more accurate. Want me to do discovery first, or proceed without it?" Wait for the answer. If they say proceed, do a minimal context pass yourself (read the files the change will touch, end-to-end) before any edits — but tell the user this is faster-and-riskier than discovery.

Either way, do not start writing code until you can answer: which files will I touch, which files constrain the change, and what conventions does this codebase follow?

### Phase 2 — Draft `PLAN.md`

Use `assets/PLAN-TEMPLATE.md`. Copy it to `PLAN.md` at the repo root and fill in every section. Keep steps small — see `references/step-sizing.md` for the heuristic.

The plan is the contract. Show it to the user and wait for sign-off before any code changes. A short message — "Here's the plan, OK to proceed?" — is enough. If the user is non-interactive (e.g. this is a scripted run), proceed but keep `PLAN.md` updated as the source of truth.

### Phase 3 — Execute one step at a time

For each step in `PLAN.md`:

1. **Re-read the files you're about to touch.** Even if you read them during discovery. Files change; your memory of them is stale.
2. **Make the change.** Prefer surgical edits (replace a specific block) over full-file rewrites. Use full-file rewrites only when genuinely replacing the file or creating a new one.
3. **Run the local check for this step.** That's usually: the relevant test file, the relevant build target, or a type-check on the affected files. Don't run the entire test suite after every step — that's Phase 4. Run the minimum check that proves the step worked.
4. **If the check passes:** update `PLAN.md` — mark the step done, advance "Current step".
5. **If the check fails:** see `references/recovery.md`. Do not move on to the next step with a broken build.

Do not bundle steps. Even when a step feels trivial, doing it on its own gives you a clean checkpoint and a small diff to review.

### Phase 4 — Full verification

Only run this after all `PLAN.md` steps are done.

1. Run the full test suite (the command in `CONTEXT-*.md` "Project shape", or the project's standard `test` command).
2. Run the linter and formatter. Apply formatter changes if they're auto-fixable; review and apply linter changes manually if not.
3. Run the type-checker (if the project has one).
4. **Sync affected documentation.** For each file in your diff, ask: did this change invalidate anything documented elsewhere? Check at minimum: `README.md` (usage examples, feature list, install/setup steps), `CHANGELOG.md` if the project keeps one, inline doc comments / docstrings on modified public APIs, and any docs the modified file links to or is linked from. Update only what the *current change* invalidated — do not rewrite docs that are unrelated-but-stale (log those in `NOTES.md` instead). Doc-only edits in this step don't need their own `PLAN.md` step.
5. Re-read your full diff (`git diff` against the base branch). Look for: debug prints, `console.log`, `print()`, commented-out code, TODO comments you added and didn't resolve, unrelated changes that crept in, hardcoded paths or values that shouldn't be there.
6. Verify the change does what was asked. Re-read the "Task" section of `CONTEXT-*.md` (or `PLAN.md`'s goal) and confirm the change addresses it.

If anything in steps 4–6 fails, you are not done. Either fix it or revise `PLAN.md` and continue.

### Phase 5 — Hand off

End with a short message:

1. One paragraph: what changed, in plain English.
2. The files modified (paths only, no content — the user can read the diff).
3. The verification commands you ran and their results.
4. Anything the user should know before reviewing: open questions, deferred items, follow-up TODOs you logged in `NOTES.md`.
5. Explicit ask: "Ready for review. Want me to commit, or do you want to look at the diff first?"

Do not commit. Do not push. Do not open a PR. The handoff is the deliverable.

## Gotchas

Mistakes this skill exists to prevent. If you catch yourself doing any of these, stop.

- **Implementing without a plan.** "It's a small change, I'll just do it" produces twice the diff you expected and unrelated drive-by edits. Write the plan even if it's three bullets.
- **Reading a file once and editing it three times.** After every successful edit, the in-context view of that file is stale. Re-read before the next edit to the same file.
- **Silent scope creep.** Noticed a typo, a stale comment, an inefficient query in a file you opened? Add it to `NOTES.md`. Do not fix it in this change. Mixed-purpose diffs get rejected.
- **"While I was there" refactors.** Same as above. The PR is about one thing. Refactors are their own task with their own discovery and their own plan.
- **Shipping a change that invalidates the README.** The opposite of scope creep, equally bad. If the change adds a flag, changes a default, renames a command, or modifies setup steps, the docs that describe those things are now wrong. Update them as part of this change, not "later". Scope limited: only docs the *current* change invalidated; pre-existing staleness goes to `NOTES.md`.
- **Declaring victory after the unit tests pass.** Unit tests are necessary, not sufficient. Run the full suite, the linter, and the type-checker before claiming done.
- **Skipping the diff re-read.** Reading your own diff before handoff catches: debug logging, accidentally-committed scratch files, edits to files you didn't mean to touch, and TODO comments you forgot about.
- **Updating `PLAN.md` from memory at the end.** Update it as you go. Each step's status changes when the step's check passes — not at the end of the session.
- **Bundling failing tests with passing changes.** If a test you added or modified is failing because the production code isn't right yet, fine — that's mid-step. If a previously-passing test breaks because of your change and you "fix" it by editing the test to match the new behavior, stop. Either the test was wrong (justify why, in `NOTES.md`) or your change is wrong.
- **Quietly disabling tests, type errors, or lints.** `// @ts-ignore`, `# noqa`, `it.skip`, suppressed warnings — these are signals you don't yet understand the problem. Acceptable only with a one-line explanation in the diff and a `NOTES.md` entry.
- **Continuing after three failed attempts at the same step.** If a step fails three times, the plan is wrong. Stop, update `PLAN.md`, and ask the user. See `references/recovery.md`.

## Output

A diff against the base branch that does what `PLAN.md` says it does, with the full test suite and linter passing, and a `PLAN.md` whose every step is checked off. Plus a short handoff message. No commits, no pushes, no PRs unless explicitly requested.
