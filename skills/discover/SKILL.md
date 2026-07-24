---
name: discover
description: Gather and document the context needed to implement a feature, fix a bug, or refactor code in an unfamiliar or large codebase. Use this skill at the start of any non-trivial coding task, before writing or modifying any code — especially when the user asks to "implement", "add", "fix", "refactor", "change how X works", or "look into" something, even if they don't explicitly say "explore" or "investigate". Also use when the user shares a ticket, bug report, or feature request that touches unfamiliar parts of a codebase. Produces a single markdown artifact (`CONTEXT-<slug>.md`) that lists every file, symbol, convention, and constraint relevant to the task. Do NOT use this skill for trivial edits (typo fixes, one-line changes in a file the user pointed to directly) or for tasks that are purely conversational (explaining a concept, reviewing a snippet pasted into chat).
license: MIT
metadata:
  author: "Tim Miles"
  email: "49971977+mlstm@users.noreply.github.com"
  version: "1.0"
model: opus
effort: high
---

# Discover

Context-gathering as an explicit, observable phase. The output is one markdown file the human reviews before any code is written.

## Why this exists

Models are trained to skim. Asked to "implement feature X", an agent typically opens two or three files, pattern-matches, and starts editing — missing the file that defines the convention, the test that encodes the invariant, the migration that constrains the schema. The resulting code looks plausible and breaks something subtle.

This skill forces a separation: **first** produce a context artifact, **then** (in a separate phase, possibly a separate session) implement against it. The artifact is the deliverable of this skill. Not code. Not a partial implementation. A document.

## When this skill is active

Do not write, edit, or rewrite any source file in the project. The only file you create is `CONTEXT-<slug>.md` in the repo root (or `docs/context/` if that directory exists). Read-only commands (`ls`, `grep`/`rg`, `find`/`fd`, `cat`, `git log`, `git blame`) are encouraged. Running tests or builds is fine if it helps you understand behavior. Running migrations, package installs, or anything that mutates state is not.

If the user explicitly asks you to start coding during this phase, stop and confirm: "I'm in discovery mode and have not finished the context document. Do you want me to skip ahead and start coding, or finish discovery first?"

## The procedure

Work through these phases in order. Do not skip ahead.

### Phase 1 — Restate the task

In your first message of the session, write back what you understand the task to be in 2–4 sentences, plus a list of explicit questions for anything ambiguous. Do not start exploring until the user confirms or answers. A wrong premise wastes the entire discovery.

Things almost always worth clarifying:

- What is the user-visible behavior change? (Not the implementation — the observable outcome.)
- Are there constraints not stated? (Backwards compat, performance, must-not-touch areas.)
- Is there a deadline or scope cap?
- Is there prior art in the codebase the user wants you to follow or avoid?

### Phase 2 — Orient

Goal: understand the shape of the codebase, not its contents.

1. List the repo root and read top-level config files: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, whichever exist.
2. Identify: the language(s), the build/test commands, the directory layout convention, whether there's a monorepo structure.
3. Note the test framework and where tests live relative to source.
4. Note the lint/format toolchain.

Record these in the "Project shape" section of the artifact as you go. Do not memorize them — write them down.

### Phase 3 — Traverse

Goal: find every file that the change will touch, plus every file that constrains how the change must be made.

Start from the user's entry points (a file path, a feature name, a function name, a URL route, an error message) and traverse outward. For each candidate file:

1. **Read the whole file.** Do not read the first 100 lines and infer the rest. If a file is over ~1000 lines, read it in chunks but read all of it that's plausibly relevant. The single biggest failure mode of this skill is the agent skimming.
2. Note what the file does in one line.
3. Note which symbols (functions, classes, types, constants) matter for this task.
4. Follow imports/exports, callers, and callees outward. Use `rg` (or `grep -r`) to find references. Use `git log -p <file>` if you need history to understand intent.
5. Stop traversal at a file when you can confidently say: "this file is not affected by the task and does not constrain the task."

For deeper guidance on how to traverse different kinds of codebases (layered, plugin-based, monorepo, etc.) see `references/traversal-strategies.md`.

### Phase 4 — Find the constraints

A constraint is anything that limits how the change can be made. These are easy to miss and expensive to discover late. Check for each:

- **Tests** that exercise the affected code. The test names tell you what invariants must hold.
- **Type definitions / schemas** the change must conform to.
- **Public API surface** — anything exported from a package, exposed via HTTP, or consumed by another service. Breaking it has downstream cost.
- **Migrations / data shape** — if the change touches persisted data, what's the current schema and what's the migration story?
- **Feature flags / config** — is the affected code gated?
- **Conventions** — naming, error-handling, logging, dependency injection patterns the codebase consistently follows. If you violate them, the PR gets rejected even if the code works.
- **Adjacent recent changes** — `git log --since="3 months ago" -- <area>` to see what's been moving. Recent churn often signals the area is under active design and your assumptions may be stale.

### Phase 5 — Write the artifact

Use the template in `assets/CONTEXT-TEMPLATE.md`. Copy it to `CONTEXT-<slug>.md` (or `docs/context/CONTEXT-<slug>.md` if that directory exists) and fill in every section. The `<slug>` is a short kebab-case identifier for the task — e.g. `CONTEXT-oauth-refresh.md`, `CONTEXT-fix-pagination-off-by-one.md`.

### Phase 6 — Self-check

Before handing off to the user, validate your own work against this checklist. If any answer is "no" or "not sure", go back to the relevant phase.

- [ ] Can I name every file that will be modified? (Not "files in `src/auth/`" — actual file paths.)
- [ ] Can I name every file that constrains the change but won't be modified (tests, types, configs)?
- [ ] Did I read each listed file fully, not just skim it?
- [ ] Did I identify the public API surface, if any?
- [ ] Did I check for existing tests that already cover this area?
- [ ] Did I look at recent git history in the affected directories?
- [ ] Are the "Open questions" specific enough that the user can answer yes/no or with a single fact?
- [ ] Is there anything I assumed without verifying? (If yes, list it as a question.)

### Phase 7 — Hand off

End your turn with a short message:

1. Path to the artifact.
2. A 2–3 sentence summary of what you found.
3. The "Open questions" section copied inline so the user doesn't have to open the file.
4. Explicit ask: "Should I revise the context document, or is this ready to use as input to an implementation session?"

Do not start implementing even if the user seems eager. The next phase (implementation) belongs to a separate session or a separate skill, with the artifact as input.

## Gotchas

These are mistakes the skill exists to prevent. If you notice yourself doing any of these, stop.

- **Reading the first N lines of a file and inferring the rest.** The convention you need to follow is often defined at the bottom (re-exports), in the middle (a helper used by everything), or in a sibling file. Read whole files.
- **Trusting filenames.** A file called `utils.ts` may contain the core business logic. A file called `auth.ts` may be a thin re-export. Open it.
- **Stopping at the first match.** `rg "createUser"` returning one hit doesn't mean there's only one definition — there may be overloads, mocks, fixtures, or shadowing exports. Look at every hit.
- **Skipping tests.** Test files are the cheapest way to learn invariants. Read them before reading the implementation when possible.
- **Skipping `git log`.** Recent commits in the affected area often reveal _why_ the code looks the way it does and what's been tried before.
- **Writing the artifact from memory at the end.** Update it incrementally as you traverse. If you defer writing, you will forget half of what you read.
- **Producing a vague "Open questions" section.** "How should auth work?" is useless. "Should refresh tokens rotate on every use or only on access-token expiry?" is answerable.
- **Treating discovery as a first draft of the PR description.** It's not. It's a map of the territory. The PR description comes later, after implementation.

## Output

A single markdown file at `CONTEXT-<slug>.md` (or `docs/context/CONTEXT-<slug>.md`), following `assets/CONTEXT-TEMPLATE.md`. No code changes. No partial implementation. No "I went ahead and started on the easy parts."
