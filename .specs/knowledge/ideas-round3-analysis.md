# Knowledge: hitl-cli Ideas Round 3 Analysis

**Date:** 2026-03-05
**Author:** Claude (Opus 4.6) - Researcher Agent

## Summary

Round 3 ideation produced 15 new improvement ideas (IDEA-031 through IDEA-045) by analyzing areas NOT covered in rounds 1-2. Focus areas: dependency hygiene, SDK ergonomics, code quality patterns, ecosystem expansion, and packaging compliance.

## Priority Matrix (Round 3 Ideas Only)

### Quick Wins (< 1 hour, high value)
| ID | Title | Effort | Impact |
|----|-------|--------|--------|
| IDEA-031 | Remove dead google-auth deps | 30 min | High (15MB smaller install) |
| IDEA-035 | Add py.typed marker | 10 min | Medium (PEP 561 compliance) |
| IDEA-036 | Add --version flag | 15 min | Medium (standard CLI convention) |
| IDEA-038 | Add ruff to dev deps | 5 min | High (CI parity) |

### Small Improvements (2-4 hours)
| ID | Title | Effort | Impact |
|----|-------|--------|--------|
| IDEA-032 | Extract E2EE request helper | 2h | Medium (DRY ~100 lines) |
| IDEA-033 | Extract MCP result parser | 1h | Medium (DRY 2x19 lines) |
| IDEA-034 | Async context manager for SDK | 2h | Medium (Pythonic API) |
| IDEA-043 | Server health check command | 2h | Medium (debugging) |
| IDEA-044 | Extract BearerAuth class | 30 min | Low (cleanup) |

### Medium Improvements (half day - 1 day)
| ID | Title | Effort | Impact |
|----|-------|--------|--------|
| IDEA-037 | Remove sync wrapper anti-pattern | 1h | Low (code quality) |
| IDEA-039 | --plain/--no-emoji output | 0.5d | Low (accessibility) |
| IDEA-041 | Decouple ApiClient from Typer | 1d | High (SDK usability) |
| IDEA-042 | Request cancellation | 1d | Medium (reliability) |

### Larger Features (1-2 days)
| ID | Title | Effort | Impact |
|----|-------|--------|--------|
| IDEA-040 | Hooks for Gemini/Aider/Windsurf | 1-2d | Medium (ecosystem) |
| IDEA-045 | Document shell completion | 30 min | Low (DX) |

## Recommended Implementation Order

**Phase A: Trivial wins (1 sprint, all < 1h each)**
1. IDEA-038 (ruff in dev deps)
2. IDEA-035 (py.typed)
3. IDEA-036 (--version)
4. IDEA-031 (remove google-auth)
5. IDEA-044 (extract BearerAuth)
6. IDEA-045 (shell completion docs)

**Phase B: Architecture cleanup (1 sprint)**
1. IDEA-041 (decouple ApiClient from Typer) — blocks SDK usability
2. IDEA-033 (MCP result parser extraction)
3. IDEA-032 (E2EE helper extraction)
4. IDEA-034 (async context manager)
5. IDEA-037 (remove sync wrappers)

**Phase C: Features (1-2 sprints)**
1. IDEA-043 (health check)
2. IDEA-042 (request cancellation)
3. IDEA-040 (new agent hooks)
4. IDEA-039 (plain output mode)

## Cross-References with Existing Ideas

| New Idea | Depends On | Enables |
|----------|-----------|---------|
| IDEA-032 | — | IDEA-016 (multi-device E2EE) |
| IDEA-034 | — | IDEA-008 (connection pooling) |
| IDEA-041 | — | IDEA-017 (exception hierarchy) |
| IDEA-038 | — | IDEA-010 (CI coverage threshold) |
| IDEA-031 | — | Cleaner IDEA-022 (auth migration) |

## Cumulative Idea Stats (All 45 Ideas)

| Category | Count | % |
|----------|-------|---|
| Architecture / Tech Debt | 10 | 22% |
| Security / Reliability | 8 | 18% |
| Feature / DX | 9 | 20% |
| UX / Documentation | 6 | 13% |
| Packaging / CI | 4 | 9% |
| Performance | 3 | 7% |
| Ecosystem | 2 | 4% |
| Housekeeping | 3 | 7% |
