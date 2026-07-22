# Evaluating skill output quality

"It seemed to work once" is not enough. Structured evals tell you whether a skill works reliably across varied prompts, in edge cases, and *better than no skill at all*.

## Designing test cases

A test case has: a realistic **prompt**, a human-readable **expected output**, and optional **input files**. Store them in `evals/evals.json`:

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales in data/sales_2025.csv. Find the top 3 months by revenue and make a bar chart.",
      "expected_output": "A bar chart showing the top 3 months by revenue, with labeled axes.",
      "files": ["evals/files/sales_2025.csv"]
    }
  ]
}
```

- Start with 2–3 cases; expand later.
- Vary phrasing, detail, and formality (casual and precise).
- Cover at least one edge case (malformed input, ambiguous request).
- Use realistic context (file paths, column names). "process this data" tests nothing.
- Don't define pass/fail checks yet — add assertions after seeing the first run.

## Running evals

Run each case **twice**: once **with** the skill, once **without** (or against the previous version). The baseline is what proves the skill adds value.

Workspace layout (separate from the skill dir):
```
csv-analyzer-workspace/
└── iteration-1/
    ├── eval-top-months-chart/
    │   ├── with_skill/    { outputs/  timing.json  grading.json }
    │   └── without_skill/ { outputs/  timing.json  grading.json }
    └── benchmark.json
```

- **Clean context per run** — no leftover state. Use subagents (Claude Code) or a fresh session each time.
- Provide each run: skill path (or none for baseline), prompt, input files, output dir.
- When improving an existing skill, snapshot it first (`cp -r <skill> <workspace>/skill-snapshot/`) and use that as baseline.
- **Capture timing** (`timing.json`: `total_tokens`, `duration_ms`) immediately on completion — it isn't persisted elsewhere.

## Writing assertions

Add verifiable statements *after* seeing the first outputs:

Good: "The output file is valid JSON", "The bar chart has labeled axes", "Includes at least 3 recommendations" (verifiable / observable / countable).
Weak: "The output is good" (vague); "Uses exactly 'Total Revenue: $X'" (brittle).

Not everything needs an assertion — writing style and visual polish are better caught in human review. Add assertions per case in `evals.json`.

## Grading outputs

Evaluate each assertion → PASS/FAIL with concrete **evidence** that quotes the output:

```json
{
  "assertion_results": [
    { "text": "Both axes are labeled", "passed": false,
      "evidence": "Y-axis labeled 'Revenue ($)' but X-axis has no label" }
  ],
  "summary": { "passed": 3, "failed": 1, "total": 4, "pass_rate": 0.75 }
}
```

- Require concrete evidence for a PASS; don't give benefit of the doubt. A "Summary" heading with one vague sentence is a FAIL.
- Use scripts for mechanical checks (valid JSON, row counts, file dimensions) — more reliable than LLM judgment.
- Review the assertions themselves: drop ones too easy, too hard, or unverifiable.
- For comparing two versions, try blind comparison: an LLM judge scores both outputs without knowing which is which.

## Aggregating and analyzing

Compute per-config stats in `benchmark.json` with a **delta** between with/without skill:

```json
{ "delta": { "pass_rate": 0.50, "time_seconds": 13.0, "tokens": 1700 } }
```

The delta shows cost (more time/tokens) vs. benefit (higher pass rate). +50pp pass rate for +13s is worth it; doubling tokens for +2pp may not be.

Patterns to investigate:
- **Always passes in both configs** → remove; inflates with-skill rate without showing value.
- **Always fails in both** → broken assertion or too-hard test; fix it.
- **Passes with, fails without** → where the skill clearly helps; understand why.
- **High stddev across runs** → flaky eval or ambiguous instructions; add examples/specifics.
- **Time/token outliers** → read the transcript to find the bottleneck.

## Human review

Assertions only check what you thought of. A reviewer catches "technically correct but misses the point" issues. Record actionable feedback per case in `feedback.json` ("missing axis labels and months in alphabetical not chronological order"), empty string = looked fine.

## The iteration loop

Three signals feed improvement: failed assertions (specific gaps), human feedback (broad quality), execution transcripts (*why* it went wrong). Give all three plus the current `SKILL.md` to an LLM and ask for changes, instructing it to:

- **Generalize** from feedback — fix underlying issues broadly, not narrow patches per example.
- **Keep it lean** — remove instructions that cause wasted work; if pass rates plateau as you add rules, the skill is over-constrained — try removing rules.
- **Explain the why** — reasoning-based instructions beat rigid directives.
- **Bundle repeated work** — if every run rewrites a similar helper, move it into `scripts/`.

Then: apply changes → rerun all cases in a new `iteration-<N+1>/` → compare. Even one execute-then-revise pass noticeably improves quality.
