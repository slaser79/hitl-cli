# Empire Brain

## Local Brain Conventions
This directory contains the curated knowledge base for this satellite. It follows the same structure as the HQ Empire Brain:
- `lessons/`: Non-trivial lessons learned during development.
- `entities/`: Knowledge about specific system components, libraries, or patterns.
- `decisions/`: Architecture Decision Records (ADR).
- `_pending/`: Staging area for new knowledge.

## 🧠 MEMORY WRITE LOCK
Contribute to the brain on completion. Any non-trivial lesson, friction, or new entity knowledge goes to `.specs/brain/_pending/{task_id}.md` before calling `task_complete` / `mission_complete`. 
If there are no new lessons, state "No new lessons" explicitly. 
The HQ Librarian drains these pending files daily and synthesizes them into the cross-product brain at HQ.
