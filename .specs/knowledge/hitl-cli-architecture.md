# Knowledge Doc: hitl-cli Architecture & Improvement Opportunities

**Created:** 2026-03-03
**Updated:** 2026-03-04
**Author:** Claude (The Researcher)
**Purpose:** Guide for future Builder agents working on hitl-cli improvements

## Architecture Overview

hitl-cli operates in three modes:
1. **Direct CLI** — User runs `hitl-cli request --prompt "..."` from terminal
2. **MCP Proxy** — Runs as stdio server for Claude/Gemini agent integration
3. **Python SDK** — `from hitl_cli import HITL` for programmatic use

### Module Map

```
hitl_cli/
├── main.py          (442 LOC) CLI entry + 9 commands via Typer
├── auth.py          (545 LOC) OAuth 2.1 PKCE + dynamic registration + legacy JWT
├── api_client.py    (265 LOC) REST client (API key + E2EE paths)
├── mcp_client.py    (376 LOC) MCP tool calls + OAuth token refresh
├── proxy_handler_v2.py (447 LOC) FastMCP proxy server + E2EE (partial)
├── crypto.py        (280 LOC) PyNaCl key management + encryption
├── sdk.py           (233 LOC) High-level HITL class (wraps above)
├── config.py        (13 LOC)  Path constants + env var
└── hooks/
    ├── review_and_continue.py (189 LOC) Claude Code stop hook
    └── codex_notify.py        (111 LOC) Codex notification hook
```

**Total:** ~2,900 LOC | **Tests:** 124 passing across 11 files

### Authentication Flow (Critical Path)

```
Login:
  Dynamic Client Registration (RFC 7591)
  → PKCE Authorization (RFC 7636)
  → Token stored at ~/.hitl/oauth_token.json (mode 600)
  → E2EE keypair generated + registered with server

Request:
  CLI args → Auth dispatch (4-branch: e2ee | api_key | oauth | jwt)
  → ApiClient (REST) or MCPClient (MCP protocol)
  → Server response → Display to user
```

**Key gotcha:** The 4-branch auth dispatch is duplicated 6 times. See IDEA-001.

## Priority Matrix for Ideas (30 total)

### Tier 1: Security & Correctness (Do First)
| ID | Title | Effort | Risk if Ignored |
|----|-------|--------|-----------------|
| IDEA-004 | Complete E2EE in proxy | 1 day | E2EE claims partially false |
| IDEA-005 | Token refresh lock | 2 hours | Race condition under load |
| IDEA-016 | Multi-device E2EE fallback | 1 day | Silent encryption failure |
| IDEA-023 | Proxy tool registration race | 2 hours | Empty tool list on connect |
| IDEA-027 | File permissions validation | 2 hours | Token files potentially exposed |
| IDEA-029 | Silent E2EE key registration fix | 2 hours | Mysterious E2EE failures |

### Tier 2: Architecture (Reduce Debt)
| ID | Title | Effort | Benefit |
|----|-------|--------|---------|
| IDEA-001 | Auth Strategy Pattern | 1-2 days | Eliminates 6x duplication |
| IDEA-002 | Native async commands | 0.5 day | Cleaner code, proper cleanup |
| IDEA-003 | Centralized Config | 1 day | Foundation for all settings |
| IDEA-017 | Custom exception hierarchy | 1 day | Precise error handling for SDK |
| IDEA-025 | Centralize timeout constants | 1 hour | DRY, prerequisite for IDEA-009 |

### Tier 3: User-Facing Features
| ID | Title | Effort | Benefit |
|----|-------|--------|---------|
| IDEA-006 | `status` command | 0.5 day | Self-service debugging |
| IDEA-007 | SDK docs in README | 2 hours | SDK discoverability |
| IDEA-009 | Configurable timeouts | 0.5 day | User flexibility |
| IDEA-012 | Request history | 1 day | Local audit trail |
| IDEA-022 | Auth migration command | 0.5 day | Smooth JWT→OAuth upgrade |
| IDEA-024 | Token expiry warning | 2 hours | Proactive auth management |
| IDEA-028 | CLI help text + examples | 2 hours | Better discoverability |
| IDEA-030 | Hook registry commands | 1 day | Hook ecosystem discoverability |

### Tier 4: Reliability & Scale
| ID | Title | Effort | Benefit |
|----|-------|--------|---------|
| IDEA-008 | Connection pooling | 2 hours | Perf for batch ops |
| IDEA-011 | Batch notifications | 2-3 days | Agent fleet scaling |
| IDEA-014 | Retry w/ backoff | 0.5 day | Transient failure resilience |
| IDEA-019 | Config schema validation | 0.5 day | Fail fast on misconfiguration |
| IDEA-021 | Request deduplication | 0.5 day | Prevent duplicate HITL prompts |
| IDEA-026 | Hook error propagation | 2 hours | Faster hook debugging |

### Tier 5: Housekeeping & Quality
| ID | Title | Effort | Benefit |
|----|-------|--------|---------|
| IDEA-010 | CI coverage threshold | 1 hour | Prevent silent regression |
| IDEA-013 | Stale branch cleanup | 30 min | Repo hygiene |
| IDEA-015 | Real async tests | 1-2 days | Catch race conditions |

### Tier 6: Future / Nice-to-Have
| ID | Title | Effort | Benefit |
|----|-------|--------|---------|
| IDEA-018 | Telemetry hooks | 1-2 days | Production observability |
| IDEA-020 | Streaming responses | 2-3 days | Better long-wait UX |

## Gotchas for Builders

1. **`config.py` path discrepancy** — CLAUDE.md says tokens are at `~/.hitl/`, but `config.py` uses `~/.config/hitl-cli/`. The actual code uses `config.py` paths. Documentation is wrong.

2. **`01_system_context.md` says "Click"** — The CLI framework is actually **Typer** (not Click). The spec is outdated.

3. **Google Auth deps are legacy** — `google-auth` and `google-auth-oauthlib` in pyproject.toml are for the deprecated Firebase flow. They're still imported but only used in the legacy JWT path.

4. **Proxy E2EE is incomplete** — `encrypt_arguments()` exists but isn't called. Don't claim E2EE in proxy mode without wiring this in first.

5. **Tests use `pytest-timeout=30s`** — Some real async tests may need longer. Override with `@pytest.mark.timeout(60)` for integration tests.

6. **ruff is not in pyproject.toml** — CI uses it but `uv sync` doesn't install it. Add to `[project.optional-dependencies]`.

## Recommended Implementation Order

### Sprint 1: Quick Security Wins (~1 day)
1. **IDEA-005** (2h) — Token refresh lock. Quick win, prevents real bugs.
2. **IDEA-029** (2h) — E2EE key registration fix. Prevents silent failures.
3. **IDEA-023** (2h) — Proxy tool registration race. Fixes intermittent bug.
4. **IDEA-027** (2h) — File permissions validation. Security hardening.

### Sprint 2: Architecture Foundation (~2 days)
5. **IDEA-025** (1h) — Centralize timeouts. DRY prerequisite.
6. **IDEA-010** (1h) — CI coverage threshold. One-line change, permanent guard.
7. **IDEA-017** (1d) — Exception hierarchy. Foundation for retry/error handling.
8. **IDEA-002** (0.5d) — Native async. Simplifies all commands.

### Sprint 3: Major Refactors (~2 days)
9. **IDEA-001** (1-2d) — Auth Strategy. Biggest architectural improvement.
10. **IDEA-003** (1d) — Centralized Config. Foundation for all settings.

### Sprint 4: User-Facing Polish (~1.5 days)
11. **IDEA-006** (0.5d) — Status command. Visible user-facing improvement.
12. **IDEA-028** (2h) — CLI help text. Low effort, high discoverability.
13. **IDEA-007** (2h) — SDK docs in README. Makes SDK visible.
14. **IDEA-022** (0.5d) — Auth migration command. Smooth upgrade path.

Total: ~6.5 days across 4 sprints for comprehensive improvement.
