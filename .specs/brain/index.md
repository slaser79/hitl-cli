# Empire Brain Index — `hitl-cli`

This satellite brain lives under `.specs/brain/` and is curated from `hitl-cli`'s own README.md, CLAUDE.md, AGENTS.md, CHANGELOG.md, pyproject.toml, flake.nix, and `.specs/` documents (MISSION-2026-310b Phase 8 — SPEC-AW-310b §4.1).

Entity and cross-product lesson pages are HQ-owned per SPEC-AW-310b §4.1 and live in `slaser79/agent_workflows/.specs/brain/entities/` and `…/lessons/`; they are injected into worker prompts automatically by `build_brain_context()` and do **not** need to be mirrored here.

## Products

| Page | Products | Last Updated | Summary |
|------|----------|--------------|---------|
| [products/hitl-cli.md](products/hitl-cli.md) | hitl-cli | 2026-04-17 | Authoritative product page — Python CLI + SDK + E2EE MCP proxy; Typer/httpx/fastmcp/PyNaCl stack; OAuth 2.1 PKCE + dynamic registration; Claude Code `Stop` + Codex `notify` hooks; config-path discrepancy, Typer-vs-Click stale doc, partial proxy E2EE, and 4-branch auth-dispatch gotchas. |

## Entities

HQ-owned (see `agent_workflows/.specs/brain/entities/`). None curated in this satellite.

## Lessons

HQ-owned (see `agent_workflows/.specs/brain/lessons/`). Product-matched HQ lessons with `products: [hitl-cli]` in frontmatter are injected automatically by `build_brain_context()`.

## Decisions

None yet. Future satellite-local ADRs will live in `decisions/` and be linked from this index.
