# Recovery

What to do when a step fails. Load this file when:

- A step's check command fails after you made the change.
- You're about to attempt the same step a third time.
- A test you didn't touch is suddenly failing.
- The plan and reality have diverged and you're not sure which to trust.

## First failure on a step

Don't loop. Diagnose before re-attempting.

1. **Read the failure output in full.** Not just the last line. Stack traces, assertion diffs, and compiler errors usually point at the right file and often at the right line. Models systematically under-read error output.
2. **Locate the failure in the diff.** Is the failure in code you just changed, or in code that *consumes* what you changed? The fix is usually in the producer side (your change), not the consumer.
3. **Re-read the file you edited.** Often the edit didn't go where you thought it did, or whitespace/indentation got mangled.
4. **Make one targeted fix.** Not a rewrite. Not a "let me try a different approach". The smallest change that addresses the specific error.
5. **Re-run the same check.**

## Second failure on the same step

Now stop and think — don't just re-attempt with another guess.

1. **State the failure in plain English to yourself.** Often the act of restating reveals the real cause.
2. **Check your assumptions against reality.**
   - Is the file you edited the one that's actually being executed? (Build artifacts, cached compiled output, multiple files with similar names.)
   - Is the test framework picking up your test? (Filtering, naming conventions, file-glob patterns.)
   - Is the runtime you expect actually being used? (Virtualenv, Node version, language version mismatch.)
3. **Add a minimal probe.** A `console.log` / `print` / `dbg!` at the point of failure to confirm what's actually happening. Remove it before finalizing.
4. **Try the fix once more.**

## Third failure on the same step

The plan is wrong. Stop attempting.

1. **Do not re-attempt.** A third try at the same approach is almost certainly going to fail too.
2. **Update `PLAN.md`.** Mark the step as `[!] blocked` and write a 2–3 sentence note explaining what was tried and why it didn't work.
3. **Tell the user.** Include: what you tried, what the failure was, what you think the issue might be, and either (a) a concrete alternative approach to try, or (b) a specific question.
4. **Wait for input.** Don't bulldoze through with a different approach the user didn't sanction. The plan changing is normal — silent plan deviation is not.

## A test you didn't touch is failing

Two possibilities:

- **Your change broke it.** Likely if the test is in or imports from the area you edited. Read the test, understand what invariant it asserts, and check whether your change violates it. Usually the answer is: your change is wrong, not the test.
- **It was already broken.** Run the test on the base branch (`git stash && <test command> && git stash pop`) to find out. If it was already failing, log it in `NOTES.md` and note it in your handoff — do not fix it as part of this change.

Do not "fix" a previously-passing test by editing the test to match your new behavior unless you can justify in `NOTES.md` why the test was wrong. The test usually encodes intent that's older and more carefully considered than your change.

## The plan and the code have diverged

You did a step, then realized step N+2 doesn't make sense anymore. This is normal. What's not normal is to keep going as if the plan still applied.

1. Stop coding.
2. Re-read the relevant portion of `PLAN.md`.
3. Edit the plan: rewrite the remaining steps to fit reality. Mark obsolete steps `[~] obsolete` rather than deleting them — the history is useful.
4. Confirm the new plan with the user (a one-line message, "I had to revise steps 3–5, see PLAN.md, OK to continue?") unless this is a non-interactive run.
5. Resume.

## Rolling back

When a step is so broken that the cleanest path forward is to undo it:

- If the change is uncommitted (which it should be — this skill doesn't commit): `git checkout -- <files>` for tracked files; `rm` for files you created.
- If you've already moved on to a later step that depends on the broken one, you may need to roll back multiple steps. Mark them `[ ] not started` again in `PLAN.md` as you undo them.
- Do not use `git reset --hard`, `git clean -fdx`, or anything that can destroy uncommitted work elsewhere in the tree. Use targeted file-level commands.

## When everything is on fire

Sometimes the working tree is in a state where you can't even tell what's wrong. Symptoms: nothing builds, multiple unrelated tests fail, the dev server won't start.

1. Stash everything: `git stash push -u -m "implement-skill-recovery"`.
2. Verify the base branch builds and tests pass clean. If it doesn't, the problem isn't yours.
3. Pop the stash back: `git stash pop`.
4. Bring back changes one file at a time (`git checkout stash@{0} -- <file>`) and check after each. The first file that breaks things tells you where the issue is.

This is slow but it converges. Flailing does not.
