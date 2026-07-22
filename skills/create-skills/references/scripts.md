# Using scripts in skills

Skills can instruct agents to run shell commands and bundle reusable scripts in `scripts/`. Three levels: one-off commands, self-contained scripts, and well-designed script interfaces.

## One-off commands

When an existing package already does the job, reference it directly in `SKILL.md` — no `scripts/` needed. Use runners that auto-resolve dependencies at runtime:

| Runner | Ships with | Example |
|--------|-----------|---------|
| `uvx` | uv (separate install) | `uvx ruff@0.8.0 check .` |
| `pipx run` | OS pkg managers | `pipx run 'ruff==0.8.0' check .` |
| `npx` | Node.js | `npx eslint@9 --fix .` |
| `bunx` | Bun | `bunx eslint@9 --fix .` |
| `deno run` | Deno | `deno run --allow-read npm:eslint@9 -- --fix .` |
| `go run` | Go | `go run golang.org/x/tools/cmd/goimports@v0.28.0 .` |

Tips:
- **Pin versions** (`npx eslint@9.0.0`) for reproducibility.
- **State prerequisites** in `SKILL.md` ("Requires Node.js 18+"); use the `compatibility` frontmatter field for runtime requirements.
- **Move complex commands into scripts.** A few flags is fine; once a command is hard to get right first try, a tested script is more reliable.

## Referencing scripts from SKILL.md

Use relative paths from the skill root — the agent resolves them automatically. List scripts so the agent knows they exist, then say when to run them:

```markdown
## Available scripts
- **`scripts/validate.sh`** — Validates configuration files
- **`scripts/process.py`** — Processes input data

## Workflow
1. Run validation: `bash scripts/validate.sh "$INPUT_FILE"`
2. Process results: `python3 scripts/process.py --input results.json`
```

The same relative-path convention works in `references/*.md`; the agent runs commands from the skill root.

## Self-contained scripts

Bundle reusable logic in `scripts/` with dependencies declared inline — no separate manifest or install step.

**Python (PEP 723)** — run with `uv run scripts/extract.py`:
```python
# /// script
# dependencies = ["beautifulsoup4>=4.12,<5"]
# requires-python = ">=3.10"
# ///
from bs4 import BeautifulSoup
...
```
`uv lock --script` creates a lockfile for full reproducibility. `pipx run` also supports PEP 723.

**Deno** — `npm:`/`jsr:` specifiers are self-contained by default:
```ts
#!/usr/bin/env -S deno run
import * as cheerio from "npm:cheerio@1.0.0";
```

**Bun** — auto-installs missing packages; pin in the import path: `import x from "cheerio@1.0.0"`.

## Designing scripts for agentic use

Scripts are invoked by an agent, not a human at a terminal. Design the interface accordingly:

- **Avoid interactive prompts.** Never block on stdin for confirmation or input. Take everything as command-line arguments or flags so the agent can run the script non-interactively.
- **Document usage with `--help`.** A clear help message lets the agent discover arguments without reading the source.
- **Write helpful error messages.** State what went wrong and how to fix it, so the agent can self-correct rather than guess.
- **Use structured output.** Emit JSON (or other parseable formats) and meaningful exit codes so the agent can reliably consume results instead of scraping prose.

When evals show every run independently writing a similar helper (a chart builder, a parser), that's a signal to bundle it as a script.
