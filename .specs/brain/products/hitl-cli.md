---
title: "hitl-cli — HITL CLI & SDK"
type: product
products: [hitl-cli]
last_updated: 2026-04-17
sources:
  - README.md (features, installation, authentication, usage patterns, E2EE proxy, Claude Code + Codex hooks)
  - CLAUDE.md (project overview, Nix + manual dev setup, TDD protocol, auth flows, configuration files, troubleshooting, Constitution)
  - AGENTS.md (mirror of CLAUDE.md — project guidelines & Constitution)
  - CHANGELOG.md (v1.2.0 initial PyPI publish 2025-10-25, v1.2.1 version sync 2025-10-26)
  - pyproject.toml (package metadata, dependencies, entry-point scripts, pytest config)
  - flake.nix (Nix dev shell — Python 3.12 + uv + hatchling build)
  - .specs/00_vision.md (Executive Summary + Core Value Proposition)
  - .specs/01_system_context.md (Tech Stack + Development Constraints + Architecture modes)
  - .specs/02_roadmap.md (Phase 1 Bootstrapping + Phase 2 Enhancement)
  - .specs/knowledge/hitl-cli-architecture.md (authoritative module map, LOC, 6-way auth-dispatch gotcha, 30-idea priority matrix, doc-vs-code discrepancies)
  - hitl_cli/ directory listing (gh api repos/slaser79/hitl-cli/contents/hitl_cli)
  - tests/ directory listing (subfolders: commands/, core/, hooks/)
cross_refs:
  - ../index.md
---

# hitl-cli — HITL Command-Line Interface & SDK

## What it is

`hitl-cli` is the open-source, MIT-licensed Python CLI and SDK that serves as the official reference MCP client for the HITL (Human-in-the-Loop) platform (README.md §intro; CLAUDE.md §1 Project Overview; pyproject.toml `license = {text = "MIT"}`). Published to PyPI as `hitl-cli` v1.2.1 (pyproject.toml `version = "1.2.1"`; CHANGELOG.md §[1.2.1]; flake.nix `version = "1.2.1"`). Talks to the backend at `https://hitlrelay.app` (README.md §3C example `mcp_servers.json`), which is served by the sibling `hitl-shin-relay` satellite.

The CLI operates in three modes (README.md §3 Usage Patterns; .specs/01_system_context.md §Architecture; .specs/knowledge/hitl-cli-architecture.md §Architecture Overview):

1. **Direct CLI** — `hitl-cli request --prompt "…"`, `hitl-cli notify --message "…"`, `hitl-cli login --name "…"` (README.md §3A + §2A).
2. **E2EE MCP Proxy** — stdio FastMCP proxy for Claude Desktop / Claude Code that auto-encrypts prompts and decrypts responses; server relays ciphertext only (README.md §3C; pyproject.toml `fastmcp>=0.3.0`).
3. **Python SDK** — `from hitl_cli import HITL` → `await hitl.request_input(…)` / `await hitl.notify(…)` / `await hitl.notify_completion(…)` (README.md §3B; .specs/knowledge/hitl-cli-architecture.md §Architecture Overview).

## Tech Stack

- **Runtime:** `requires-python = ">=3.10"` (pyproject.toml) with Nix dev shell pinned to Python 3.12 (flake.nix `python = pkgs.python312`; CLAUDE.md §Option 1 Nix Environment).
- **Build + Packaging:** `hatchling` via `pyproject` (pyproject.toml `[build-system] requires = ["hatchling"]`; flake.nix `nativeBuildInputs = [hatchling]`). Distribution is PyPI — `pip install hitl-cli` (README.md §1 Installation; CHANGELOG.md §[1.2.0] "Initial PyPI publication").
- **CLI Framework:** `typer>=0.16.0` (pyproject.toml dependencies). Note: `.specs/01_system_context.md §Tech Stack` still says "Click" — that is stale; the code is Typer per `.specs/knowledge/hitl-cli-architecture.md §Gotchas` #2 and `hitl_cli/main.py` presence.
- **HTTP + MCP:** `httpx>=0.28.1` for REST, `fastmcp>=0.3.0` for MCP tool calls + proxy (pyproject.toml dependencies).
- **Auth:** `authlib>=1.3.0` + `pyjwt>=2.9.0` for OAuth 2.1 / JWT; `google-auth>=2.40.3` + `google-auth-oauthlib>=1.2.2` retained only for the legacy Firebase/JWT exchange path (pyproject.toml; `.specs/knowledge/hitl-cli-architecture.md §Gotchas` #3 "Google Auth deps are legacy").
- **Crypto:** `pynacl>=1.5.0` for libsodium-backed keypair generation and authenticated encryption in the E2EE proxy (pyproject.toml; `.specs/knowledge/hitl-cli-architecture.md §Module Map` — `crypto.py ~280 LOC`).
- **Dev / Test:** `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, `pytest-cov>=5.0.0`, `pytest-timeout>=2.4.0` under `[tool.uv] dev-dependencies` (pyproject.toml). Suite-wide `timeout = 30` seconds under `[tool.pytest.ini_options]` — override with `@pytest.mark.timeout(60)` for integration tests (`.specs/knowledge/hitl-cli-architecture.md §Gotchas` #5).
- **Entry-point scripts** (pyproject.toml `[project.scripts]`):
  - `hitl-cli` / `hitl` — main Typer CLI (both resolve to `hitl_cli.main:main`).
  - `hitl-hook-review-and-continue` — Claude Code `Stop` hook (`hitl_cli.hooks.review_and_continue:main`).
  - `hitl-codex-notify` — Codex CLI notify hook (`hitl_cli.hooks.codex_notify:main`).
  - `hitl-daily-report` — daily report entry point (`hitl_cli.main:daily_report`).

## Architecture

Module map (all paths under `hitl_cli/`; LOC + responsibilities cited to `.specs/knowledge/hitl-cli-architecture.md §Module Map`; file existence verified via `gh api repos/slaser79/hitl-cli/contents/hitl_cli`):

| Module | LOC | Responsibility |
|---|---|---|
| `main.py` | 442 | Typer CLI entry + 9 commands (`login`, `logout`, `request`, `notify`, `notify-completion`, `proxy`, …) — CHANGELOG.md §[1.2.0] "CLI commands"|
| `auth.py` | 545 | OAuth 2.1 with PKCE + RFC 7591 dynamic client registration + legacy Firebase/JWT exchange (CLAUDE.md §Authentication Flows) |
| `api_client.py` | 265 | REST client (API-key header + E2EE endpoint paths ending in `…e2ee`) — README.md §3C "The llm will still use the unencrypted endpoints and the hit-cli proxy will use the endpoints ending in e2ee" |
| `mcp_client.py` | 376 | MCP tool calls with OAuth token refresh |
| `proxy_handler_v2.py` | 447 | FastMCP proxy server + E2EE wrapping (partial — `encrypt_arguments()` exists but is not called per `.specs/knowledge/hitl-cli-architecture.md §Gotchas` #4) |
| `crypto.py` | 280 | PyNaCl keypair management + authenticated encryption |
| `sdk.py` | 233 | High-level `HITL` class that wraps the above (README.md §3B SDK example) |
| `config.py` | 13 | Path constants + env-var lookup |
| `hooks/review_and_continue.py` | 189 | Claude Code `Stop` hook (README.md §3D; PR #58 "fix: stop hook single message and response parsing") |
| `hooks/codex_notify.py` | 111 | Codex CLI `notify` hook (README.md §3E; closed issue #16 "Implement notify hook for codex") |

Total ≈ 2,900 LOC, 124 passing tests across 11 files in `tests/commands/`, `tests/core/`, `tests/hooks/` (`.specs/knowledge/hitl-cli-architecture.md §Module Map`; `gh api repos/slaser79/hitl-cli/contents/tests` lists `commands/`, `core/`, `hooks/`).

### Authentication flow (critical path)

```
Login  : Dynamic Client Registration (RFC 7591)
       → PKCE Authorization (RFC 7636)
       → Token stored with 600 perms
       → E2EE keypair generated + registered with server

Request: CLI args → 4-branch auth dispatch
         (e2ee | api_key | oauth | jwt)
       → ApiClient (REST) or MCPClient (MCP)
       → Server response → Display to user
```

Reference: `.specs/knowledge/hitl-cli-architecture.md §Authentication Flow` — the 4-branch dispatch is duplicated six times across commands and is the subject of IDEA-001 "Auth Strategy Pattern" (also tracked in closed issue #25 "Create AuthStrategy pattern to decouple authentication logic"). CLAUDE.md §4 §Authentication Flows documents both modern OAuth 2.1 and legacy Firebase/JWT flows.

### Configuration files

All per-user state lives under `~/.hitl/` (CLAUDE.md §4 Configuration Files):

- `oauth_client.json` — dynamic client registration record.
- `oauth_token.json` — OAuth 2.1 bearer + refresh tokens, stored with mode `600`.
- `config.json` — general CLI configuration.

⚠️ `config.py` uses `~/.config/hitl-cli/` rather than `~/.hitl/`; the README/CLAUDE docs are the source of truth the user sees, and the code is the truth the runtime uses — see `.specs/knowledge/hitl-cli-architecture.md §Gotchas` #1 "config.py path discrepancy".

Env-var precedence (CLAUDE.md §4 Configuration — "loaded with the following precedence"): CLI args → env vars → config files → defaults. Required: `HITL_SERVER_URL`. Legacy-only: `GOOGLE_CLIENT_ID`. Optional: `HITL_LOG_LEVEL`. Non-interactive services set `HITL_API_KEY` instead of logging in (README.md §2B).

## Key Patterns

- **Spec-First Doctrine — satellite of the HITL Empire.** Managed from HQ (`slaser79/agent_workflows`); every code change starts from a spec + GitHub issue. CoS creates specs and issues; workers (Gemini/Codex/Qwen) write code in isolated worktrees (CLAUDE.md §Constitution §Chain of Command; AGENTS.md mirror).
- **Mandatory TDD with baseline snapshots.** Record `baseline_tests.txt`, write a failing test, implement, re-run and diff to confirm no regressions (CLAUDE.md §3 Mandatory Test-Driven Development Protocol). Zero-tolerance for regressions.
- **Nix-first dev shell.** `nix develop` auto-creates the venv, installs `uv`, and syncs project deps; `nix develop -c pytest` and `nix develop -c ruff check` are the canonical run commands (CLAUDE.md §2 Getting Started Option 1; .specs/01_system_context.md §Development Constraints). `uv sync` is the manual fallback.
- **Zero-config OAuth via dynamic client registration (RFC 7591).** No manual OAuth client setup; the CLI registers itself on first `hitl-cli login` and stores credentials under `~/.hitl/` with `600` perms (CLAUDE.md §Flow 1; README.md §2A; closed issue #1 "Remove static OAUTH client and only dynamic client registration").
- **E2EE proxy delivers ciphertext-only relay.** Agents (Claude Desktop/Code) call `hitl-cli proxy https://hitlrelay.app/mcp-server/mcp/` over stdio; prompt + choices are encrypted with PyNaCl before hitting the server's `…e2ee` endpoints, so the backend never sees plaintext (README.md §3C; closed issue #9 "End-to-End Encryption for REST API Clients").
- **Agent hooks for continuous interaction.** `hitl-hook-review-and-continue` is a Claude Code `Stop` hook that intercepts the stop event, pushes a review prompt to the mobile app, and feeds the human response back as the next instruction (README.md §3D). `hitl-codex-notify` is a fire-and-forget Codex CLI notification hook registered via `notify = ["hitl-codex-notify"]` in `~/.codex/config.toml` (README.md §3E).
- **Dual auth for humans + services.** OAuth 2.1 + PKCE for interactive users (`hitl-cli login`); `HITL_API_KEY` env var for CI/CD, services, and automation that cannot launch a browser (README.md §2; CLAUDE.md §Authentication Flows; closed issue #28 "BUG: If HITL_API_KEY is set in the environment running HITL-CLI should always use rest API endpoint").
- **Async-friendly SDK.** The SDK exposes `await hitl.request_input(…)`, `await hitl.notify(…)`, `await hitl.notify_completion(…)`; Typer commands are being refactored to native async (README.md §3B; `.specs/knowledge/hitl-cli-architecture.md §Recommended Implementation Order` "IDEA-002 Native async"; closed issue #24 "Refactor Typer commands to use native async support").

## Known Gotchas

- **`config.py` path ≠ CLAUDE.md docs.** CLAUDE.md says tokens live at `~/.hitl/oauth_token.json`; the code in `hitl_cli/config.py` uses `~/.config/hitl-cli/`. The runtime wins — docs are stale (`.specs/knowledge/hitl-cli-architecture.md §Gotchas` #1).
- **`01_system_context.md` says "Click".** It is Typer; the spec is outdated (`.specs/knowledge/hitl-cli-architecture.md §Gotchas` #2; pyproject.toml `typer>=0.16.0`).
- **`google-auth*` deps are legacy-only.** They are still imported but only exercised in the Firebase/JWT exchange path — not needed for OAuth 2.1 + PKCE (`.specs/knowledge/hitl-cli-architecture.md §Gotchas` #3).
- **Proxy E2EE is incomplete.** `crypto.encrypt_arguments()` exists but is not wired into `proxy_handler_v2.py`; do not claim "full E2EE in proxy mode" without finishing IDEA-004 "Complete E2EE in proxy" (`.specs/knowledge/hitl-cli-architecture.md §Gotchas` #4, §Priority Matrix Tier 1).
- **Pytest timeout is 30 s globally.** Real async tests that exercise OAuth/FCM may hit it — override with `@pytest.mark.timeout(60)` or longer (`.specs/knowledge/hitl-cli-architecture.md §Gotchas` #5; pyproject.toml `[tool.pytest.ini_options] timeout = 30`).
- **`ruff` is not declared in `pyproject.toml`.** CI runs it but `uv sync` does not install it — add to `[project.optional-dependencies]` if you depend on it locally (`.specs/knowledge/hitl-cli-architecture.md §Gotchas` #6).
- **4-branch auth dispatch is duplicated six times.** Hot-patching one branch leaves the other five stale; prefer the IDEA-001 AuthStrategy refactor before adding new auth modes (`.specs/knowledge/hitl-cli-architecture.md §Authentication Flow` + §Priority Matrix Tier 2).
- **`HITL_API_KEY` must force REST.** If the env var is set, the CLI must route through the REST API regardless of other state — bug fixed in closed issue #28 and must not regress.

## Distribution & Environments

- **PyPI:** `pip install hitl-cli` → v1.2.1 at <https://pypi.org/project/hitl-cli/> (README.md §1; CHANGELOG.md §[1.2.0] "Initial PyPI publication").
- **Source:** `slaser79/hitl-cli`, main branch `main`, MIT license (pyproject.toml `[project.urls] Repository`; CLAUDE.md §1 "Open Source"). Issues + PRs flow through the HITL Empire (CoS → workers → PR review).
- **Dev environments:** Nix dev shell (`flake.nix`) or manual `uv venv` + `uv sync` (CLAUDE.md §2). Nix shell installs Python 3.12 + uv automatically and produces a reproducible build.
- **Backend dependency:** HITL relay at `https://hitlrelay.app/mcp-server/mcp/` (README.md §3C Claude Desktop `mcp_servers.json` example), served by `hitl-shin-relay`. The CLI also targets the generic REST surface via `HITL_SERVER_URL` (CLAUDE.md §Environment Variables — "`HITL_SERVER_URL`: **(Required)** The base URL for the backend API").

## Status

- **Phase 1 Bootstrapping** (.specs/02_roadmap.md): Core CLI (`login`, `ask`, `notify`, `proxy`) ✅, OAuth 2.1 with PKCE ✅, E2EE ✅, MCP proxy mode ✅; `.specs/` governance structure still in flight.
- **Phase 2 Enhancement** (.specs/02_roadmap.md): service-account auth improvements, batch notifications, response streaming — not started.
- **Recently shipped** (CHANGELOG.md §[1.2.0] 2025-10-25 + §[1.2.1] 2025-10-26): initial PyPI publication, OAuth 2.1 + PKCE + dynamic client registration, E2EE MCP proxy, Claude Code `Stop` hook, Codex `notify` hook, `HITL` SDK, 94-test suite (now 124 per `.specs/knowledge/hitl-cli-architecture.md §Module Map`), version-sync fix across `pyproject.toml` + `flake.nix`.
- **Open themes** (`.specs/knowledge/hitl-cli-architecture.md §Priority Matrix`): Tier 1 security (IDEA-004 complete E2EE in proxy, IDEA-005 token refresh lock, IDEA-027 file-perm validation), Tier 2 architecture (IDEA-001 AuthStrategy, IDEA-003 centralized config — closed issue #27), Tier 3 UX (IDEA-006 `status` command, IDEA-009 configurable timeouts — closed issue #7 "Increase Default time out to 15 Minutes").
- **Recent closed issues** (gh issue list — authoritative activity snapshot 2026-04-17): #60 gitignore fix, #34 stop-hook clean-message, #31 bootstrap `.specs/`, #28 `HITL_API_KEY` REST routing, #27 centralized config, #26 shared MCP client base, #25 AuthStrategy, #24 native async Typer, #16 Codex notify hook, #14 E2EE-via-API-key docs, #12 public release prep, #11 make public, #9 E2EE REST, #7 15-min default timeout.
