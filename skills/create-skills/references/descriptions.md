# Optimizing skill descriptions

A skill only helps if it gets activated. The `description` field is the primary mechanism agents use to decide whether to load a skill. Under-specified → it won't trigger when it should. Over-broad → it triggers when it shouldn't.

## How triggering works

At startup the agent loads only each skill's `name` and `description`. When a task matches a description, it reads the full `SKILL.md`. The description therefore carries the entire triggering burden.

Nuance: agents usually only reach for skills on tasks needing knowledge beyond their built-in ability. A trivial one-step request ("read this PDF") may not trigger a skill even on a perfect description, because the agent handles it alone. Skills shine on specialized knowledge: unfamiliar APIs, domain workflows, uncommon formats.

## Writing effective descriptions

- **Use imperative phrasing.** "Use this skill when…" rather than "This skill does…". The agent is deciding whether to *act*.
- **Focus on user intent, not implementation.** Describe what the user wants to achieve; the agent matches against the request, not internal mechanics.
- **Err on the side of pushy.** Explicitly list contexts where it applies, including when the user doesn't name the domain: "even if they don't explicitly mention 'CSV' or 'analysis'."
- **Keep it concise.** A few sentences to a short paragraph. Hard limit: 1024 characters.

Good:
```
description: Extracts text and tables from PDF files, fills PDF forms, and merges
  multiple PDFs. Use when working with PDF documents or when the user mentions PDFs,
  forms, or document extraction.
```

Poor:
```
description: Helps with PDFs.
```

## Testing whether a description triggers

Build ~20 realistic eval queries labeled `should_trigger` true/false (8–10 each):

```json
[
  { "query": "I've got a spreadsheet in ~/data/q4.xlsx with revenue in col C — can you add a profit margin column and highlight anything under 10%?", "should_trigger": true },
  { "query": "whats the quickest way to convert this json file to yaml", "should_trigger": false }
]
```

**Should-trigger queries** — vary along axes:
- Phrasing: formal, casual, typos, abbreviations.
- Explicitness: some name the domain ("analyze this CSV"), some describe the need without naming it ("my boss wants a chart from this data file").
- Detail: terse vs. context-heavy (file paths, column names, backstory).
- Complexity: single-step and multi-step, including the task buried in a larger chain.
- Most valuable: cases where the skill helps but the connection isn't obvious — these are where wording matters.

**Should-not-trigger queries** — the valuable ones are near-misses sharing keywords but needing something else:
- Weak: "Write a fibonacci function" (irrelevant, tests nothing).
- Strong: "I need to update the formulas in my Excel budget spreadsheet" (shares "spreadsheet" but needs Excel editing, not CSV analysis); "write a python script that reads a csv and uploads each row to postgres" (involves CSV but is DB ETL, not analysis).

**Realism:** include file paths (`~/Downloads/report_final_v2.xlsx`), personal context ("my manager asked me to…"), specific details, casual language and occasional typos.

## The optimization loop

1. Run the eval queries against the current description; record which triggered.
2. Run multiple times — triggering has randomness.
3. Avoid overfitting: split into train/validation sets; tune on train, confirm on validation.
4. Adjust wording for false negatives (broaden/add keywords) and false positives (tighten/add boundaries).
5. Repeat until accuracy holds on the validation set.
