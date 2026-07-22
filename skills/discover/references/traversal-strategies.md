# Traversal strategies

How to traverse the codebase depends on its shape. Diagnose the shape first, then pick the strategy.

## Diagnosing the shape

Look at the top-level layout and configs:

- **Monorepo:** multiple packages under `packages/`, `apps/`, `services/`, or similar, each with its own manifest. Often has a workspace declaration in the root manifest (`workspaces` in `package.json`, `[workspace]` in `Cargo.toml`, etc.).
- **Layered:** single package, directories named for layers — `controllers/`, `services/`, `repositories/`, `models/`, or `api/`, `domain/`, `infra/`.
- **Feature-sliced:** single package, directories named for features — `auth/`, `billing/`, `users/`, each containing its own controllers, models, and tests.
- **Plugin / extensible:** a core directory plus a `plugins/`, `extensions/`, or `integrations/` directory where each subdir is a self-contained module loaded via a registry.
- **Framework-driven:** the layout is dictated by a framework convention (Rails `app/`, Next.js `app/` or `pages/`, Django apps, Spring components). The framework's docs tell you where things live.

Sometimes the shape is a mix — e.g. a monorepo of feature-sliced packages.

## Strategy: monorepo

1. Read the root manifest to enumerate packages.
2. Identify which package(s) the change lives in. Often only one or two.
3. Identify which packages _depend on_ the target package(s) — these are downstream consumers and constrain the public API. Look for `dependencies` entries referencing the target.
4. Read the target package's own README/AGENTS.md before its source.
5. Then traverse within the target package using the layered or feature-sliced strategy below, depending on its internal shape.

Gotcha: monorepos often have shared `tsconfig` / `tsconfig.base.json` or `Cargo.toml` workspace settings that affect builds. Skim these so you don't hit a compile error from path-alias mismatch later.

## Strategy: layered

1. Find the layer where the user-visible change starts (usually the controller / API layer).
2. Trace downward through service → repository → model. Each layer typically has a strict dependency direction (controller depends on service, never the reverse). Violating this is a common rejection reason in PRs.
3. Read the corresponding test directory in parallel with the source — layered codebases often have unit tests next to each layer.

Gotcha: cross-cutting concerns (auth, logging, error mapping) often live in middleware or filters, not in any layer. Search for these by name (`middleware`, `interceptor`, `filter`, `decorator`) before assuming the layers are the whole picture.

## Strategy: feature-sliced

1. Find the feature directory the change belongs to.
2. Read its internal layout — most feature slices replicate the same internal structure (handlers, services, types, tests).
3. Find one or two _other_ feature slices and skim them. The convention you must follow is whatever's common across slices, not whatever's in this one slice.
4. Identify the "shared" or "common" directory (often `shared/`, `common/`, `core/`, `lib/`). This is where conventions live.

Gotcha: feature slices sometimes import from each other directly when they shouldn't. Note this if you see it, but do not propagate the anti-pattern.

## Strategy: plugin / extensible

1. Find the registry / loader — the code that discovers and wires up plugins. Often called `registry.ts`, `loader.py`, `plugins/index.*`, or named after the framework.
2. Read the interface or base class every plugin implements. This _is_ the contract.
3. Find 2–3 existing plugins and read them in full. The convention is whatever's common across them.
4. Note any plugin lifecycle hooks (`init`, `register`, `shutdown`) — your new code must implement the ones that are required.

Gotcha: some plugin systems load lazily (on first use) and others eagerly (at startup). This affects what initialization-time state you can rely on. Check the loader to find out.

## Strategy: framework-driven

1. Identify the framework and its version.
2. Trust the framework's conventions before the codebase's idiosyncrasies. If the framework says "models go in `app/models/`", they probably do.
3. Look for framework-specific config files (e.g. `next.config.js`, `settings.py`, `config/application.rb`) — these often dictate behavior that isn't visible in the source.

Gotcha: framework upgrades sometimes leave behind deprecated patterns mixed with new ones. Check the framework version against the patterns in use and prefer the modern pattern for new code, but match the surrounding file's style.

## When the codebase resists traversal

Some signs the codebase is fighting you, and what to do:

- **No tests, or tests don't run locally.** Note this as a risk in the artifact. Don't try to fix the test setup as part of discovery.
- **Generated code mixed with hand-written code.** Find the generator (look for `// DO NOT EDIT`, `*.generated.*`, `codegen/` directories). Read the generator's input/config, not the generated output.
- **Heavy dependency injection / inversion of control.** The call graph isn't visible from `grep`. Find the DI container/config file (often `module.ts`, `bindings.py`, or wherever providers are registered) and read it before tracing calls.
- **Macros / decorators that rewrite code.** The thing you `grep` for may not be what runs. Note the macro/decorator and look up what it expands to.
- **Dead code.** If you find a function that nothing calls, don't assume it's unused — check for dynamic dispatch (string-based lookups, reflection, framework auto-discovery). When unsure, ask the user.

In all of these cases, document what you found _and what you couldn't determine_, and add a specific open question. Don't paper over the uncertainty.
