# Step sizing

How to decide where one step ends and the next begins. Load this when drafting `PLAN.md`.

## The heuristic

A good step is the smallest unit of change that:

1. Leaves the codebase in a buildable, testable state.
2. Has an obvious, runnable check that proves it worked.
3. You could explain to a reviewer in two sentences.
4. Produces a diff under ~100 lines (this is a soft guideline, not a hard rule).

If a step doesn't meet all four, it's probably two steps in disguise.

## Common splits

These are step-splittings that pay off in practice.

**Schema changes vs. code that uses the schema.**
Step N: add the migration. Step N+1: update the code that reads/writes the new shape. Combining them makes the migration hard to roll back independently and bloats the diff.

**Types vs. implementation.**
Step N: add or modify the type/interface. Step N+1: update the implementation. The type change alone gives you a clean failure message — every callsite the change affects becomes a type error, which is a free list of what needs touching.

**New feature vs. wiring it up.**
Step N: write the new function/class with its own unit test. Step N+1: wire it into the caller(s). Two small reviewable diffs beat one large one, and the unit test for step N is much easier to write in isolation.

**Tests for existing behavior vs. behavior change.**
If you're about to change behavior that lacks test coverage: step N is "add a test for the current behavior" (which passes), step N+1 is "change the behavior" (which intentionally breaks the test, and you update it). This way the test diff makes the behavior change visible to reviewers.

**Refactor vs. feature.**
If a feature is hard to add because the code shape is wrong: step N is "refactor to make the change easy" (no behavior change, all tests still pass), step N+1 is "make the easy change". The refactor in step N is a pure shape change — if any test breaks during step N, you got the refactor wrong.

**Config / flags vs. usage.**
If the feature is gated behind a flag: step N: introduce the flag (defaulting to off, no behavior change). Step N+1: implement the gated behavior. Step N+2: turn the flag on by default (or leave that for a later PR).

## When a step is too big

Signs:

- The "Files" list has more than ~5 entries.
- The "Change" description needs more than two sentences.
- The "Check" is "the whole test suite" rather than a specific test or build.
- You can't picture the diff in your head.

Split it. The most common useful splits: types-before-implementation, scaffold-before-fill, test-before-change-of-behavior.

## When a step is too small

Steps can be too small too — though this is rarer.

- "Rename the variable" by itself is a step only if the rename touches many files. A one-line rename in one file is usually part of the next step.
- "Add an import" is never a step on its own.

Roll trivially-small steps into the substantive step they support.

## Order

A few rules of thumb:

- **Migrations and schema changes first.** They're the hardest to roll back if later steps fail.
- **Types before implementation.** The type errors guide the implementation.
- **Implementation before tests for the new behavior**, but **tests before changes to existing behavior** (the test pins down what behavior you're changing).
- **Wiring last.** Connect the new code to its callers after the new code itself is working.
- **Cleanup (deleting old code, removing flags) at the very end**, once the new path is proven.
