---
name: create-skills
description: Create, update, or review Agent Skills that conform to the agentskills.io specification. Use this skill whenever the user asks to "create a skill", "make a skill", "write a SKILL.md", "update/fix/improve a skill", "review a skill", or describes wanting to package a repeatable workflow, procedure, or domain expertise into a reusable skill for an agent. Covers directory structure, SKILL.md frontmatter, writing effective descriptions that trigger reliably, progressive disclosure, bundling scripts, and evaluating skill quality.
license: MIT
metadata:
  version: "2.0"
  source: https://agentskills.io/specification
---

# create-skills

Create and refine Agent Skills that follow the [agentskills.io specification](https://agentskills.io/specification).

A skill is a directory containing a `SKILL.md` file (required) plus optional support files. Agents load only the `name` and `description` at startup, then read the full `SKILL.md` into context when a task matches. This is **progressive disclosure** — design every skill around it.

## Workflow for creating a skill

1. **Ground it in real expertise.** Do not generate a skill from generic LLM knowledge — that produces vague advice ("handle errors appropriately"). Instead, extract the skill from a real task you completed with the agent, or synthesize it from project artifacts (runbooks, API specs, code review comments, version history, real failure cases). Capture the specific steps, corrections, input/output formats, and project conventions the agent would not otherwise know.
2. **Scope it as one coherent unit of work.** Like a function: not so narrow that many skills must load for one task, not so broad it cannot be triggered precisely. "Query a database and format results" is coherent; adding "database administration" is too much.
3. **Pick the directory name** = the `name` field (see constraints below). Create `<skill-name>/SKILL.md`.
4. **Write the frontmatter**, especially a high-quality `description` (see `references/descriptions.md`).
5. **Write the body** — concise, imperative instructions that add what the agent lacks (see Body content below).
6. **Add support files only if needed** — `references/`, `scripts/`, `assets/`.
7. **Validate** the format (see Validation below).
8. **Refine with real execution.** Run the skill on real tasks, read the execution traces (not just outputs), and revise. For rigorous iteration, see `references/evaluating.md`.

## Directory structure

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable, reusable code
├── references/       # Optional: docs loaded on demand
├── assets/           # Optional: templates, resources
└── ...               # Any additional files
```

## SKILL.md frontmatter

YAML frontmatter followed by Markdown body. Fields:

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | 1–64 chars. Lowercase `a-z`, `0-9`, hyphens only. No leading/trailing/consecutive hyphens. **Must match the parent directory name.** |
| `description` | Yes | 1–1024 chars. Non-empty. Describes **what** it does **and when** to use it; include trigger keywords. |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | Max 500 chars. Environment requirements (intended product, system packages, network access, runtime versions). |
| `metadata` | No | Arbitrary key-value mapping (author, version, etc.). |
| `allowed-tools` | No | Space-separated pre-approved tools (experimental). |

Minimal:

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

The `description` is the single most important field — it carries the entire burden of triggering. See `references/descriptions.md` for how to write and test it.

## Body content

The body loads into the agent's context whenever the skill activates, competing for attention with everything else. Spend tokens wisely:

- **Add what the agent lacks; omit what it knows.** Do not explain what a PDF is or how HTTP works. Jump straight to project-specific conventions, domain procedures, non-obvious edge cases, and the exact tools/APIs to use. For each sentence ask: "Would the agent get this wrong without this?" If not, cut it.
- **Aim for moderate detail.** Concise, stepwise guidance with one working example beats exhaustive documentation. When you find yourself covering every edge case, let the agent's own judgment handle most of them.
- **Keep `SKILL.md` under ~500 lines / ~5,000 tokens.** Move longer reference material to `references/` (progressive disclosure).
- **Calibrate control to fragility.** Give the agent freedom where multiple approaches are valid; be prescriptive only where the task is fragile. Prefer explaining *why* ("Do X because Y causes Z") over rigid directives ("ALWAYS X, NEVER Y") — agents follow reasoned instructions more reliably.
- **Provide defaults, not menus.** Offering many options without a clear default makes the agent waste time choosing. Recommend one path.
- **Use effective patterns:** Gotchas sections for known pitfalls; templates for required output formats; checklists for multi-step workflows; plan→validate→execute loops for risky operations.

## Progressive disclosure

Move detailed content into separate files and tell the agent *when* to read each one:

> Read references/api-errors.md if the API returns a non-200 status code.

This is far better than a generic "see references/ for details" — it lets the agent load context on demand. Use relative paths from the skill root; the agent resolves them automatically.

## Optional directories

- **`scripts/`** — reusable executable code. List scripts in `SKILL.md` so the agent knows they exist, then instruct when to run them. See `references/scripts.md`.
- **`references/`** — documentation loaded on demand via progressive disclosure.
- **`assets/`** — templates and other resources the skill outputs or copies.

## Validation

Before finishing, verify:

- `name` matches the parent directory, is 1–64 chars, lowercase/digits/hyphens only, no leading/trailing/consecutive hyphens.
- `description` is non-empty, ≤1024 chars, and states both what the skill does and when to use it.
- Frontmatter is valid YAML between `---` fences.
- All referenced files (`references/*`, `scripts/*`, `assets/*`) exist at the given relative paths.
- `SKILL.md` is lean; bulky material is moved to `references/`.

Run `scripts/validate.py <skill-dir>` to check these mechanically.

## Reference files

- `references/descriptions.md` — Writing and testing descriptions that trigger reliably.
- `references/scripts.md` — One-off commands, self-contained scripts, and designing script interfaces for agents.
- `references/evaluating.md` — Eval-driven iteration to measure and improve skill quality.
