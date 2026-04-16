---
id: SPEC-AW-310
title: "Empire Brain — Persistent Knowledge Base (Inspired by Karpathy LLM Wiki)"
status: "Approved"
owner: "agent_workflows"
created_by: "xo"
last_updated: 2026-04-13
products: ["agent_workflows", "hitl-app", "hitl-shin-relay", "ai_homeworkmarker", "shin-web", "resume-tailor", "voice_chat", "shin_hedge_fund_trader", "hitl-web", "hitl-cli", "ai_assistant"]
depends_on: [".specs/features/SPEC-AW-245_mission_control_ux_cohesion.md"]
---

# 1. Executive Summary

Upgrade the empire's knowledge management from a flat append-only lessons file to a curated, cross-referenced, persistent knowledge base ("Empire Brain"). Inspired by Karpathy's LLM Wiki pattern, the brain sits as a curated layer on top of existing raw artifacts (.specs/knowledge, lessons_learned, mission reports). Agents read from and write to the brain, making every mission compound the empire's collective intelligence. Delivered in 3 phases: structure, ingestion, and empire-wide protocol upgrade.

# 2. CEO Business Outcomes

- [ ] Any agent dispatched to any satellite immediately has relevant empire knowledge (no re-learning)
- [ ] Knowledge compounds across missions — a lesson from MISSION-200 prevents the same mistake in MISSION-310
- [ ] CEO can search and browse the empire brain from Mission Control dashboard
- [ ] Stale knowledge is automatically detected and flagged (no more outdated lessons poisoning decisions)
- [ ] Cross-product patterns are synthesised (e.g., "how we handle CI across all Flutter repos")

# 3. User Stories

- As a pCoS starting a hitl-app mission, I want to see all known hitl-app patterns, gotchas, and past failures so I don't repeat them
- As the CEO, I want to search "what do we know about Gemini quota issues?" and get a curated answer from the brain
- As a worker agent, I want to know the correct patterns for this repo before writing code
- As the XO, I want the brain to automatically update when missions complete, not require manual curation
- As the Librarian playbook, I want to periodically check for contradictions, stale content, and missing cross-references

# 4. Architecture

## 4.1 Three Layers (Karpathy Pattern)

**Layer 1: Raw Sources (existing, unchanged)**
- `.specs/lessons_learned.md` — chronological append-only log
- `.specs/knowledge/*.md` — researcher output
- `.specs/features/*.md` — feature specs
- `.specs/missions/*.md` — mission manifests
- `.specs/reports/*.md` — CRITIC reports
- `.specs/active_sprint.md` — current state
- GitHub issues, PRs, commit history

**Layer 2: The Brain (NEW — curated, cross-referenced)**
```
.specs/brain/
├── index.md                  # Master catalog — searchable by product, topic, entity
├── products/                 # Per-satellite knowledge summaries
│   ├── hitl-app.md           # Architecture, tech stack, patterns, gotchas
│   ├── hitl-shin-relay.md
│   ├── ai_homeworkmarker.md
│   ├── shin-web.md
│   ├── resume-tailor.md
│   ├── voice_chat.md
│   ├── shin_hedge_fund_trader.md
│   └── agent_workflows.md    # HQ itself
├── entities/                 # Cross-cutting concepts
│   ├── gemini-oauth.md       # How Gemini auth works, quota patterns
│   ├── sqlite-wal.md         # DB locking, WAL mode, concurrency
│   ├── flutter-ci.md         # CI patterns across Flutter repos
│   ├── tailscale-funnel.md   # Networking, webhooks, connectivity
│   └── ...
├── decisions/                # ADRs — why we chose X
│   ├── adr-001-sqlite-over-postgres.md
│   ├── adr-002-gemini-oauth-not-apikey.md
│   └── ...
├── lessons/                  # Curated, deduplicated, cross-referenced
│   ├── agent-reliability.md  # Patterns for dispatch, retry, fallback
│   ├── ci-cd-patterns.md     # What works across repos
│   ├── pr-triage.md          # Merge strategies, cascade handling
│   └── ...
└── log.md                    # Brain maintenance log (ingests, lint passes)
```

**Layer 3: The Schema (existing, upgraded)**
- `CLAUDE.md` — updated to reference brain
- `prompts/chief_of_staff.md` — updated with brain read/write protocol
- `prompts/OPERATOR.md` — updated
- Agent prompts — updated to read brain on dispatch

## 4.2 Delegation: HQ vs Satellites

**HQ (`agent_workflows/.specs/brain/`) owns:**
- `index.md` — master catalog across all products
- `products/*.md` — high-level summaries (synthesised from satellite brains)
- `entities/*.md` — cross-cutting concepts
- `decisions/*.md` — empire-wide ADRs
- `lessons/*.md` — cross-product curated lessons

**Each satellite (`{repo}/.specs/brain/`) owns:**
- Deep product-specific knowledge (component patterns, test strategies, deployment)
- Local lessons that only matter for that repo
- Its own `index.md` scoped to that product

**Sync model:**
- Satellites are source of truth for their own deep knowledge
- HQ Librarian reads satellite brains via existing `SpecRouter` / `mount_remote_specs` infrastructure (same mechanism used for spec-sync) and synthesises cross-product pages
- HQ `products/{satellite}.md` is a summary pointing to satellite for details

## 4.3 Brain Page Format

Each brain page uses consistent frontmatter:

```yaml
---
title: "Gemini OAuth Authentication"
type: entity | product | lesson | decision
products: [agent_workflows, hitl-app]
last_updated: 2026-04-13
sources: [lessons_learned.md#L73, MISSION-2026-282]
cross_refs: [sqlite-wal.md, agent-reliability.md]
---
```

# 5. Operations

## 5.1 Write (CoS/pCoS on Mission Completion)

**Updated MEMORY WRITE LOCK:**
Before calling `task_complete` or `mission_complete`:
1. Review session for new knowledge, errors, patterns
2. Append to `lessons_learned.md` FIRST (raw log always preserved — this is the safe fallback)
3. Write brain updates to a temporary file: `.specs/brain/_pending/{agent_task_id}.md`
4. Librarian merges pending files into brain pages on next run
5. Append entry to `brain/log.md`

**Why pending files instead of direct writes:** Avoids git merge conflicts when multiple agents finish simultaneously. Each agent writes to its own pending file. The Librarian is the single writer that merges into the canonical brain pages.

**Failure mode:** If brain write fails (step 3-5), the lesson is still in `lessons_learned.md` (step 2). Log the failure for Librarian to pick up later. Never block `task_complete` on brain write failure.

## 5.2 Read (Agent Dispatch)

When dispatching an agent to a satellite:
1. Read satellite's `.specs/brain/index.md` (local knowledge)
2. Read HQ's `brain/products/{satellite}.md` (cross-product context)
3. Inject relevant entity pages based on the task topic
4. Inject relevant lesson pages based on the task type

**Smart injection algorithm** (3-tier, simple to start):
1. **Always inject**: `brain/products/{satellite}.md` (product page for the target repo)
2. **Keyword match**: scan issue title + labels against entity page titles → inject matching entity pages
3. **Label match**: map `f:{feature}` labels to lesson categories → inject matching lesson pages

Example: dispatching to hitl-app issue "Fix Gemini quota handling in chat service" with labels `f:chat, agent:gemini`:
- Always: `brain/products/hitl-app.md`
- Keyword: `brain/entities/gemini-oauth.md` (matches "Gemini")
- Label: `brain/lessons/agent-reliability.md` (matches `agent:gemini`)

Target: ~200-500 lines of curated content per dispatch (vs 1,259 lines of raw lessons today).

## 5.3 Librarian (Upgraded doc_update Playbook)

Reposition existing `doc_update` playbooks as the Brain Librarian:
- **Ingest**: Process new raw sources (recent lessons, CRITIC reports, completed missions) into curated brain pages
- **Cross-reference**: Update links between pages, ensure entity pages reference all relevant products
- **Lint**: Check for contradictions, stale content (pages not updated in 30+ days with active missions), orphan pages, missing entity pages for frequently-mentioned concepts
- **Synthesise**: Update HQ product summaries from satellite brains
- **Index**: Regenerate `index.md` after changes

## 5.4 Query (Mission Control Dashboard)

New dashboard feature: Brain Query (two tiers)

**Tier 1 (Phase 3 — in scope):** Deterministic text search + browse
- Search box that searches brain pages (title, content, frontmatter tags)
- Browse by product, entity, or lesson category
- View brain pages rendered as markdown
- Fast, no LLM required

**Tier 2 (Future — out of scope for this spec):** Natural language Q&A
- CEO asks question → agent dispatched to search brain and synthesise answer
- Requires agent task pipeline, not just a search endpoint
- Deferred to follow-up spec

# 6. Delivery Phases

## Phase 1: Structure (Size S)
- Create `.specs/brain/` directory structure in HQ with index.md and empty category folders
- Create `.specs/brain/` in each active satellite
- Define page format (frontmatter schema)
- Create `brain/log.md`
- Update `CLAUDE.md` to reference brain structure

## Phase 2: Ingestion (Size L — Night Watch Mission)

**Partition strategy** — 8 parallel worker tasks by product:
1. Worker 1: `hitl-app` — process hitl-app lessons, knowledge pages, CRITIC reports → product page + entity pages
2. Worker 2: `hitl-shin-relay` — same
3. Worker 3: `ai_homeworkmarker` — same
4. Worker 4: `agent_workflows` (HQ infra) — process infra lessons, budget/scheduler knowledge
5. Worker 5: `shin-web` + `resume-tailor` + `hitl-web` (smaller satellites, combined)
6. Worker 6: `voice_chat` + `ai_assistant` + `hitl-cli` (smaller satellites, combined)
7. Worker 7: Cross-cutting entities — process lessons about Gemini, Codex, Jules, SQLite, Tailscale into entity pages
8. Worker 8: Decisions + index — create ADR pages from key architectural decisions, generate final `index.md`

Each worker reads from `lessons_learned.md` (filtered by product mentions), relevant `.specs/knowledge/` pages, and recent CRITIC reports. Librarian does final cross-referencing pass after all workers complete.

## Phase 3: Empire Upgrade (Size M)
- Update CoS/pCoS/XO prompts with brain read/write protocol
- Update MEMORY WRITE LOCK to write to brain pages
- Reposition doc_update playbooks as Librarian
- Update agent dispatch to inject brain pages instead of flat lessons
- Add brain query UI to Mission Control dashboard
- Update CRITIC spec_reviewer to check brain references
- Create `.specs/brain/` in remaining satellites
- CEO sign-off after verification

# 7. Acceptance Criteria

- [ ] `.specs/brain/` exists in HQ and all active satellites (11 products) with correct structure
- [ ] Brain has curated pages for each in-scope product (12 products — excludes only e2e-sandbox)
- [ ] Brain has entity pages for top 10 cross-cutting concepts
- [ ] Brain has curated lesson pages (not just raw dump)
- [ ] `index.md` is searchable and complete
- [ ] CoS/pCoS prompts reference brain for read and write
- [ ] Agent dispatch injects relevant brain pages (not full lessons_learned)
- [ ] Librarian playbook runs periodically and maintains brain quality
- [ ] Mission Control dashboard has brain query feature
- [ ] Knowledge compounds — new mission results update brain pages

# 8. Implementation Notes

- Brain pages are markdown files — git-tracked, diffable, no database needed
- Start with HQ brain, expand to satellites incrementally
- The Librarian is a playbook, not a new service — leverages existing infrastructure
- Smart injection can start simple (product-based filtering) and get smarter over time
- Phase 2 ingestion is the biggest effort — farm to multiple workers in parallel
- Reference: Karpathy's "LLM Wiki" pattern (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

# 9. Risks

- **Context window bloat**: Brain pages must be concise. Each page <500 lines. Librarian lint checks page sizes and flags violations.
- **Maintenance decay**: If Librarian playbook stops running, brain goes stale. Monitor via lint health checks.
- **Log growth**: `brain/log.md` rotates — keep last 100 entries, archive older to `brain/_log_archive/`.

# 10. Index Format

Sample `brain/index.md`:

```markdown
# Empire Brain Index

## Products
| Page | Product | Last Updated | Summary |
|------|---------|-------------|---------|
| [hitl-app](products/hitl-app.md) | hitl-app | 2026-04-13 | Flutter mobile app — architecture, state mgmt, CI patterns |
| [hitl-shin-relay](products/hitl-shin-relay.md) | hitl-shin-relay | 2026-04-12 | Python relay server — eval engine, agent runtime, Cloud SQL |

## Entities
| Page | Products | Last Updated | Summary |
|------|----------|-------------|---------|
| [gemini-oauth](entities/gemini-oauth.md) | all | 2026-04-11 | OAuth-only auth, never API keys, quota management |
| [sqlite-wal](entities/sqlite-wal.md) | agent_workflows | 2026-04-10 | WAL mode, locking, concurrency patterns |

## Lessons
| Page | Products | Last Updated | Summary |
|------|----------|-------------|---------|
| [agent-reliability](lessons/agent-reliability.md) | all | 2026-04-12 | Dispatch, retry, fallback, quota patterns |

## Decisions
| Page | Date | Summary |
|------|------|---------|
| [adr-001-sqlite](decisions/adr-001-sqlite.md) | 2026-01 | SQLite over Postgres for task DB |
```

# 11. Product Scope

| Product | In Scope | Rationale |
|---------|----------|-----------|
| agent_workflows | Yes | HQ — owns master brain |
| hitl-app | Yes | Primary satellite, most active |
| hitl-shin-relay | Yes | Backend relay, active missions |
| ai_homeworkmarker | Yes | Active satellite |
| shin-web | Yes | Active satellite |
| resume-tailor | Yes | Active satellite |
| voice_chat | Yes | Active satellite |
| shin_hedge_fund_trader | Yes | Active but dark — brain captures what we know |
| hitl-web | Yes | Active satellite |
| hitl-cli | Yes | Active satellite |
| ai_assistant | Yes | Active satellite |
| e2e-sandbox | No | Test-only repo, no persistent knowledge |
| hitl-channel | Yes | Claude Code plugin — brain captures architecture and MCP patterns |
- **Contradictions**: Brain may contradict raw sources if not properly sourced. All brain pages must cite sources.
