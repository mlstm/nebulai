---
name: commit-messages
description: Use this skill whenever suggesting, writing, or reviewing a git commit message for the nebulai repo. Covers the repo's two commit message styles (minimalist and fun/thematic) and when to use each. Trigger on requests like "commit message for...", "give me a commit name", or when about to commit a change in this repo.
---

# nebulai Commit Message Conventions

When suggesting a commit message for this repo, always offer **two options**:

1. **Minimalist** — plain, lowercase, no period, describes the change concisely.
2. **Fun** — playful, on-theme (see below), still clearly describes the change.

End with a one-line recommendation on which to use, based on the scope of the change (small/config-level changes lean minimalist, milestone/feature changes lean fun).

## Minimalist style

- All lowercase, no trailing period.
- Prefer plain description over conventional-commit prefixes (`feat:`, `fix:`) unless asked for them.
- Format: `<verb> <what changed>`

Examples:
```
add author and email metadata
add model and effort to all skills
add create-skill skill
add MIT license
```

## Fun style

- Theme: **nebulai is "gaining sentience"** — each commit is a step in it becoming self-aware, learning skills, and growing more capable. Lean into this as a running gag across commits.
- Keep it short — one line, no walls of text.
- Use parentheticals to clarify the literal change if the joke alone isn't clear enough.
- Emoji optional, use sparingly (fine for milestone commits like "first commit" or major additions, skip for small/routine ones).
- Lowercase start is fine (matches minimalist convention).

Examples:
```
nebulai gains sentience (and some skills)
nebulai learns to make its own skills
nebulai learns to tidy its own room (justfile: stow + link)
nebulai's skills finally know who made them
skills level up: now with author + metadata
```

## General rules

- Single line/subject only, unless a body is explicitly requested.
- Never invent details about what changed — base the message only on the actual diff or description given.
- Milestone changes (first commit, major new capability) → lean fun as the default recommendation.
- Small, routine, or config-only changes (metadata, license, dependency bump) → lean minimalist as the default recommendation.
