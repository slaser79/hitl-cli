---
cross_refs:
- ../index.md
- ../products/hitl-cli.md
- ../lessons/cross-repo-mission-delivery.md
last_updated: '2026-06-14'
products:
- hitl-cli
sources:
- hitl-cli:CLAUDE.md (project guidelines, TDD protocol, auth flows, troubleshooting,
  Constitution)
- hitl-cli:AGENTS.md (mirror of CLAUDE.md — agent expectations)
- hitl-cli:README.md (usage patterns, hooks, E2EE proxy)
- hitl-cli:CHANGELOG.md (v1.2.0 / v1.2.1 release notes)
- hitl-cli:pyproject.toml (deps, entry points, pytest config)
- hitl-cli:flake.nix (Nix dev shell spec)
- hitl-cli:.specs/00_vision.md / 01_system_context.md / 02_roadmap.md
- hitl-cli:.specs/knowledge/hitl-cli-architecture.md (module map, gotchas, priority
  matrix)
- gh issue list --repo slaser79/hitl-cli --state all (closed issues
title: hitl-cli Lessons
type: lesson
---
# hitl-cli Lessons

Curated from `hitl-cli`'s own README.md, CLAUDE.md, AGENTS.md, CHANGELOG.md, pyproject.toml, flake.nix, `.specs/knowledge/hitl-cli-architecture.md`, and the 20+ closed issues / merged PRs in `slaser79/hitl-cli` (history snapshot 2026-04-17). Every lesson is traceable to a cited source in the satellite repo. The satellite does not yet have its own `.specs/lessons_learned.md`; this HQ page is the authoritative lessons register until one exists.

## Core lessons

### Mandatory TDD with baseline snapshots — zero tolerance for regressions

- **Why it matters:** hitl-cli's CLAUDE.md §3 explicitly forbids "write code first, test after" — every PR must (1) record a baseline `baseline_tests.txt` before changes, (2) introduce a failing test that captures the requirement, (3) implement the minimum code to pass, then (4) diff the final test output against the baseline. The number of failing tests must not increase.
- **Operational consequence:** Issues dispatched to workers must ship acceptance criteria that reference the baseline/red/green/diff steps explicitly. Workers that skip the baseline step fail CRITIC review.
- **Source:** `hitl-cli:CLAUDE.md §3 Mandatory Test-Driven Development (TDD) Protocol`; `hitl-cli:AGENTS.md` mirror.

### Nix dev shell is canonical — bare `pytest` / `python` skips pinned deps

- **Why it matters:** `nix develop` gives Python 3.12 + uv + project deps reproducibly; `nix develop -c pytest` and `nix develop -c ruff check` are the run commands of record. Manual `uv venv` + `uv sync` is the documented fallback, not the default.
- **Operational consequence:** CI environments and worker worktrees must prefix commands with `nix develop -c` (or install via `uv sync` first). Bare `pytest` in an un-synced venv hides pinned-dep mismatches.
- **Source:** `hitl-cli:CLAUDE.md §2 Getting Started Option 1 & Option 2`; `hitl-cli:flake.nix` (`python = pkgs.python312`; propagated build inputs mirror pyproject.toml); `hitl-cli:.specs/01_system_context.md §Development Constraints`.

### `HITL_API_KEY` must force REST — regression risk is real

- **What happened:** Closed issue #28 "BUG: If `HITL_API_KEY` is set in the environment running HITL-CLI should always use rest API endpoint" shipped a fix ensuring the env var routes the CLI through the REST API unconditionally.
- **Operational consequence:** When changing auth-dispatch logic, verify the `HITL_API_KEY`-present branch still short-circuits to REST. The 4-branch auth dispatch is duplicated six times across the code (`.specs/knowledge/hitl-cli-architecture.md §Authentication Flow`), so a single hot-patch is not sufficient.
- **Source:** `slaser79/hitl-cli#28` (closed); `hitl-cli:.specs/knowledge/hitl-cli-architecture.md §Authentication Flow` + §Priority Matrix Tier 2 IDEA-001.

### 4-branch auth dispatch is duplicated six times — refactor before adding new modes

- **Why it matters:** The four auth modes (e2ee, api_key, oauth, jwt) are routed via the same if/else ladder in six call sites. Adding a new mode without the AuthStrategy refactor (IDEA-001 / closed issue #25 "Create AuthStrategy pattern to decouple authentication logic") bloats the duplication and raises the regression surface.
- **Operational consequence:** Any PR adding a new auth path must land the AuthStrategy refactor first, or explicitly carry the duplication cost and cite the follow-up ticket.
- **Source:** `hitl-cli:.specs/knowledge/hitl-cli-architecture.md §Authentication Flow + §Priority Matrix Tier 2`; `slaser79/hitl-cli#25` (closed).

### Proxy E2EE is partial — `encrypt_arguments()` exists but is not called

- **Why it matters:** The README promotes E2EE proxy mode as a way to stop the server seeing plaintext, but `proxy_handler_v2.py` does not currently invoke `crypto.encrypt_arguments()` on the request arguments path. The wrapper exists; the wiring is incomplete.
- **Operational consequence:** Do not assert "full end-to-end encryption in proxy mode" in new specs, issues, or CEO-facing summaries until IDEA-004 "Complete E2EE in proxy" lands. If the user depends on proxy E2EE, land IDEA-004 first.
- **Source:** `hitl-cli:.specs/knowledge/hitl-cli-architecture.md §Gotchas` #4 "Proxy E2EE is incomplete"; §Priority Matrix Tier 1.

### Docs say `~/.hitl/` but code uses `~/.config/hitl-cli/` — the runtime wins

- **What happened:** README.md, CLAUDE.md, and AGENTS.md all reference `~/.hitl/oauth_client.json` / `oauth_token.json` / `config.json`. The actual paths in `hitl_cli/config.py` point to `~/.config/hitl-cli/`. The CLI uses the latter.
- **Operational consequence:** When troubleshooting auth state, `ls ~/.config/hitl-cli/` first — the canonical docs are stale. Any future cleanup PR should unify paths and correct both the docs and the code in one go, not one or the other.
- **Source:** `hitl-cli:.specs/knowledge/hitl-cli-architecture.md §Gotchas` #1; `hitl-cli:CLAUDE.md §4 Configuration Files`.

### `01_system_context.md` still says "Click" — it is Typer

- **Why it matters:** The CLI framework listed in `.specs/01_system_context.md §Tech Stack` is "Click"; the code is Typer per `pyproject.toml` (`typer>=0.16.0`) and `hitl_cli/main.py`. New specs that copy from `01_system_context.md` inherit the error.
- **Operational consequence:** Treat `01_system_context.md` as provisional until it is resynced with the code; cross-check any tech-stack claim against `pyproject.toml` before citing.
- **Source:** `hitl-cli:.specs/knowledge/hitl-cli-architecture.md §Gotchas` #2; `hitl-cli:pyproject.toml` dependencies; `hitl-cli:.specs/01_system_context.md §Tech Stack`.

### Pytest timeout is 30 s globally — integration tests must opt in to more

- **Why it matters:** `pyproject.toml [tool.pytest.ini_options] timeout = 30` kills any test that runs longer than 30 s. OAuth round-trips and FCM integration can legitimately exceed this on slower networks.
- **Operational consequence:** Integration tests that depend on network or real crypto must annotate with `@pytest.mark.timeout(60)` (or higher) and document the reason. Increasing the global timeout is a regression risk — keep the 30 s default for unit tests.
- **Source:** `hitl-cli:.specs/knowledge/hitl-cli-architecture.md §Gotchas` #5; `hitl-cli:pyproject.toml` `[tool.pytest.ini_options]`.

### `ruff` is not declared in `pyproject.toml` but CI runs it — add it to `[project.optional-dependencies]`

- **Why it matters:** `uv sync` will not install `ruff` into the dev venv, so `ruff check` locally only works inside the Nix shell (which provides it via nixpkgs). CI happens to pass because the workflow installs ruff separately, but local-vs-CI drift trips up every new contributor.
- **Operational consequence:** When touching packaging / dev dependencies, add `ruff` under `[project.optional-dependencies]` so `uv sync --extra dev` (or similar) installs it. Until that lands, contributors need `nix develop -c ruff check` or a manual `uv pip install ruff`.
- **Source:** `hitl-cli:.specs/knowledge/hitl-cli-architecture.md §Gotchas` #6.

### Stop-hook must return only the clean assistant message

- **What happened:** Closed issue #34 "ENHANCE: CC Stop Hook should only return the clean Assistant message from Claude Code" and the follow-up merged PR #58 "fix: stop hook single message and response parsing" narrowed the Claude Code `Stop` hook payload so the human reviewer sees one coherent message, not a noisy transcript fragment.
- **Operational consequence:** Future changes to `hitl_cli/hooks/review_and_continue.py` must preserve the "clean assistant message only" behaviour — treat it as a fixed contract with the HITL mobile UX.
- **Source:** `slaser79/hitl-cli#34` (closed) and merged PR `slaser79/hitl-cli#58`; `hitl-cli:README.md §3D Continuous Interaction Hook for Claude Code`.

### Codex notifications are fire-and-forget — not a conversation hook

- **Why it matters:** Unlike the Claude Code `Stop` hook (interactive), `hitl-codex-notify` is a one-way notification: Codex calls it on completion and does not accept a response back. Registration is `notify = ["hitl-codex-notify"]` in `~/.codex/config.toml`.
- **Operational consequence:** Do not design features that expect bidirectional flow through the Codex hook. Use the SDK / REST endpoints for that. Closed issue #16 "Implement notify hook for codex" established the original contract.
- **Source:** `hitl-cli:README.md §3E Codex CLI Notifications`; `slaser79/hitl-cli#16` (closed).

### Dynamic OAuth client registration only — no static client IDs

- **Why it matters:** Closed issue #1 "Remove static OAUTH client and only dynamic client registration" fixed the model: the CLI registers itself via RFC 7591 on first `hitl-cli login` instead of shipping a hardcoded `client_id`. This is why the zero-config story works.
- **Operational consequence:** PRs that add a fallback "static client ID" env var would regress this invariant. Auth work must go through dynamic registration; failures register as `~/.hitl/oauth_client.json` write errors first (see `hitl-cli:CLAUDE.md §5 Troubleshooting` "OAuth dynamic registration fails").
- **Source:** `slaser79/hitl-cli#1` (closed); `hitl-cli:CLAUDE.md §Flow 1 OAuth 2.1 with Dynamic Registration`; `hitl-cli:README.md §2A`.

### Default request timeout is 15 minutes — don't shorten it silently

- **What happened:** Closed issue #7 "Increase Default time out to 15 Minutes instead of 5 minutes" lifted the HITL request timeout to 15 minutes because human reviewers legitimately need that long.
- **Operational consequence:** Backend-side MCP timeouts (e.g. `hitl-shin-relay` `MCP_CALL_TIMEOUT=1200` per `hitl-shin-relay:CLAUDE.md §Environment Variable Deployment Rules`) must stay in sync with the CLI default. Shortening either side without spec-level coordination breaks multi-minute reviews.
- **Source:** `slaser79/hitl-cli#7` (closed); `hitl-cli:README.md §3 usage`.

### Public release prep is a dependency cliff — respect issues #11 and #12

- **What happened:** Issues #11 "Make hitl-cli public" and #12 "Preparation steps for public release" gated the `v1.2.0` PyPI publication on a checklist of secret scrubs, LICENSE, README, CHANGELOG, and repo-visibility flips. CHANGELOG §[1.2.0] 2025-10-25 records the final release shape.
- **Operational consequence:** Any re-release or major-rev bump must re-run the same public-release checklist (secret scan, LICENSE present, README §2 auth example valid for a fresh user, CHANGELOG entry, version sync across `pyproject.toml` + `flake.nix` — the latter was fixed in `v1.2.1`).
- **Source:** `slaser79/hitl-cli#11` and `#12` (both closed); `hitl-cli:CHANGELOG.md §[1.2.0]` and §[1.2.1]; `hitl-cli:flake.nix` (`version = "1.2.1"`).

## Known hazards

### Auth / crypto / proxy code is a high-blast-radius surface

Authentication, PyNaCl crypto, and the FastMCP proxy are all on the user's security-critical path. Changes here need a spec, a failing test, a CRITIC pass, and CEO sign-off — not a worker one-shot. Security issues listed in `hitl-cli:.specs/knowledge/hitl-cli-architecture.md §Priority Matrix Tier 1` (IDEA-004 / IDEA-005 / IDEA-016 / IDEA-023 / IDEA-027 / IDEA-029) are the canonical "do first" list.

### Documentation-vs-code drift is normal — always verify against the source

Known drift entries: `config.py` path vs docs, Typer vs "Click" in `.specs/01_system_context.md`, `google-auth*` deps being legacy-only despite being required dependencies. Treat satellite docs as provisional when citing; verify against `pyproject.toml`, `hitl_cli/`, and the CHANGELOG before asserting anything in specs or CRITIC reports.

### Cross-repo coordination with `hitl-shin-relay` is required for server-visible changes

New MCP tool surfaces, auth flows, or proxy contracts land in `hitl-cli` AND `hitl-shin-relay` in the same mission. Ship specs to both satellites, use umbrella issues in `agent_workflows`, and follow the cross-repo handoff discipline captured in [cross-repo-mission-delivery.md](cross-repo-mission-delivery.md).

## Agent dispatch hints

- **Codex / Gemini Pro** for auth / crypto / FastMCP refactors (large surface, needs spec + CRITIC).
- **Gemini Flash / Qwen** for docs, CHANGELOG updates, hook small fixes, gitignore / packaging chores (low blast radius).
- **Claude** for spec authoring, CRITIC verification, and any mission that touches the Empire Brain itself (this mission is a canonical example).

## Related HQ lessons

- [cross-repo-mission-delivery.md](cross-repo-mission-delivery.md) — handoff discipline for `hitl-cli` ↔ `hitl-shin-relay` missions.
- [pr-triage.md](pr-triage.md) — PR review and merge discipline shared across the empire.

### Task Completion Knowledge For Slaser79/Hitl-Cli #70
*Added: 2026-06-14*

Task `6fa1efdc-5922-456a-bf9c-935b78315cd5` completed on 2026-06-06.

## Context
- Target: `slaser79/hitl-cli#70`
- Repository: `slaser79/hitl-cli`
- Issue: `#70`
- Title: Stop hook discards the real notify-completion error (e.stderr), making every hook failure undiagnosable
- Source: https://github.com/slaser79/hitl-cli/issues/70
- Triggered by: `cron`

## Session Knowledge
Refined issue #70. Verified that the stop hook in `hitl_cli/hooks/review_and_continue.py` discards stderr from `hitl-cli` subprocess. Updated issue body with detailed hypothesis and acceptance criteria, and applied labels: `bug`, `size:S`, `ready-for-agent`.
