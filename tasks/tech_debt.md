# Tech Debt Queue — article-publisher

*Items Claude can process autonomously during `/idletime` sessions.*
*Created: 2026-02-22*

---

## Legend

- **Risk**: LOW = safe without user input | MEDIUM = changes behavior, verify first
- **Est**: rough time estimate
- **Bucket**: `auto_sprint` = scheduled autonomous | `manual` = needs user | `billy_cron` = overnight | `blocked` = waiting
- **Status**: `open` | `in-progress` | `done` | `blocked`

---

## Priority 1 — Quick Wins (<10 min each)

| ID | Item | Risk | Est | Bucket | Status | Notes |
|----|------|------|-----|--------|--------|-------|
| TD-01 | Review tasks/context.md for stale sections | LOW | 5 min | auto_sprint | open | Update any outdated state |
| TD-02 | Run git log --oneline -10 and verify commit hygiene | LOW | 3 min | auto_sprint | open | Flag uncommitted work >3 days old |

---

## Priority 2 — System Hygiene (10–20 min each)

| ID | Item | Risk | Est | Bucket | Status | Notes |
|----|------|------|-----|--------|--------|-------|
| TD-10 | Audit CLAUDE.md for bloat (target <60 lines) | LOW | 10 min | auto_sprint | open | Run /claude-md-audit if needed |
| TD-11 | Review tasks/lessons.md — promote patterns seen 2+ times to CLAUDE.md | LOW | 15 min | auto_sprint | open | Pattern threshold: 2+ occurrences |

---

## Priority 3 — Requires User Input (never in autonomous batch)

| ID | Item | Risk | Est | Bucket | Status | Notes |
|----|------|------|-----|--------|--------|-------|
| TDU-01 | _Add user-facing items here_ | — | — | manual | blocked | Needs user decision |

---

## Completed

| ID | Item | Completed | Notes |
|----|------|-----------|-------|
| — | tech_debt.md initialized | 2026-02-22 | Phase 2 universal schema rollout |

---

*Add new items with next available ID. Idletime sessions pull P1→P2 in order.*
*Never move TDU-* items into autonomous batch — always requires user.*
