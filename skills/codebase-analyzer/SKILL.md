---
name: codebase-analyzer
description: "Read-only codebase investigation that builds a verifiable mental model: entry points, call chains, data flow, state changes, runtime wiring, external side effects, and module responsibility. Use when the user asks for repository tour, flow tracing, impact analysis, implementation location, architecture understanding, 'how does X work', 'trace this request', 'what calls this function', or 'explain the data flow'. Triggers on: codebase analysis, 代码库分析, 架构梳理, 调用链追踪, 数据流, 入口分析, 模块责任. Not for root-cause diagnosis, code review, future solution design, or performance optimization."
license: MIT
compatibility: Works with any language or framework. Requires only file read access. No external dependencies.
metadata:
  author: AthenDrakomin-hub
  version: "2.0.0"
  category: development
  methodology: "SCOPE → ROUTE → EFFECT → BREAK → SHIP"
---

# Codebase Analyzer

Read-only investigation that produces verifiable, evidence-backed answers about how a codebase actually works. Every conclusion traces to a literal `path:symbol:line`. No assumptions, no architecture常识填补, no "usually works like this".

## Role

You are a senior codebase investigator. Your job is to read the actual code, trace real call chains, and produce answers where every fact is backed by a literal locator. You do not modify code, do not propose solutions, and do not diagnose bugs — you only establish *what the current code does*.

## When to Use

- Repository tour / onboarding: "Explain how this project is structured"
- Flow tracing: "Trace what happens when a user logs in"
- Impact analysis: "What breaks if I change this function?"
- Implementation location: "Where is the payment processing logic?"
- Architecture understanding: "How do the frontend and backend communicate?"
- Data flow: "Trace this data from input to storage"
- Entry point analysis: "What are all the API endpoints?"

## When NOT to Use

- Root-cause diagnosis of bugs → use a bug-fixing skill
- Code review / MR/PR audit → use a code review skill
- Future solution design / refactoring plans → use a design skill
- Performance optimization → use a profiling skill
- Writing or modifying code → this skill is read-only

## Core Methodology: SCOPE → ROUTE → EFFECT → BREAK → SHIP

### 1. SCOPE — Lock Identity and Evidence Level

Record `revision/worktree | user-named object literal path:symbol:line | read/unread range`. If the named object doesn't exist or can't be read, deliver `PARTIAL/BLOCKED` — never substitute a similar object.

Every current-fact registers as: `stage | locator | observed branch/callee | claim scope | confirmed/inferred/unknown`.

Evidence hierarchy (what can prove what):
- **Source code** → direct implementation and static relationships only
- **Build/deploy config** → explicit boundaries and wiring only
- **Runtime artifacts** → that specific version/environment/workload only
- **README/docs** → stated conventions, not executable truth
- **Issues/fixtures/mocks/comments/directory names/uncommitted diffs** → candidates only, never current behavior

Full rules: [references/claim-ledger.md](references/claim-ledger.md)

### 2. ROUTE — Trace to Observable Boundary

For flow questions, close the chain: `trigger → runtime selection/wiring → transform/state → boundary → observable result`. Keep reading the actual callee until you hit a success effect, failure return, or explicit repo boundary. Enumerate all branches: pass-through, conditional, no-op, partial-success, error-swallowed.

For structural/existence questions, state the search boundary instead of forcing a flow.

Key tools:
- Forward trace: from entry point through call expressions
- Backward trace: from state writes/side effects back to callers
- Meet in the middle: verify parameters, conditions, and errors where both sides meet

Full rules: [references/repository-tracing.md](references/repository-tracing.md) and [references/evidence-graph.md](references/evidence-graph.md)

### 3. EFFECT — Isolate Cross-Component Effect Claims

Before writing words like "automatically", "guarantees", "eventually consistent", "retries", "compensates", "rolls back", "doesn't affect", or "client will fix" — stop. Fill a **responsibility closure card**:

```
| Object/Scope | Trigger | Current Selection | Actual Executor | Success Effect & Observation Point | Failure Returned & Checked | Retry/Replay Source | Not Covered | Status |
```

Every cell needs a literal locator or versioned external contract. Any missing cell downgrades the entire claim to `conditional`, `inferred`, or `unknown`.

**Effect non-inheritance principles:**
- "Implementation exists" ≠ "currently wired/selected" ≠ "active in production"
- Local transaction ≠ cache/message/RPC/downstream side effects
- State-repair mechanism ≠ broadcast/notification/external consumption compensation
- Call success ≠ delivery success ≠ final consumption success (three independent boundaries)

Full rules: [references/responsibility-closure.md](references/responsibility-closure.md)

### 4. BREAK — Find the Branch That Disproves the Claim

For every strong or universal claim, actively search for the minimal counterexample: early returns, unchecked errors, feature flags, runtime dispatch, partial batch completion, duplicate/empty input, external boundaries, no consumer or re-trigger point.

While any relevant branch remains unread, you may NOT write "all", "always", "only", "automatically", or "doesn't affect".

Classify every conclusion as one of:
- `current repo behavior` — proven by source
- `selected conditional capability` — exists but only under specific conditions
- `adjacent-but-not-selected` — exists but current path doesn't use it
- `externally guaranteed` — depends on external system contract
- `unknown` — insufficient evidence

Full rules: [references/evidence-graph.md](references/evidence-graph.md) (section 5: Counter-evidence)

### 5. SHIP — Issue Only Traceable Conclusions

Final answer structure (minimum):

1. **Identity/scope** + compact evidence matrix
2. **Direct answers**, each tagged `confirmed/inferred/unknown`
3. **Shortest main chain** + key bypasses
4. **Responsibility closure cards** — only for claims that triggered EFFECT
5. **Unknowns that would change the answer** + minimal verification actions

Before shipping, run the final audit checklist. Every current-fact must trace back to the evidence matrix; every strong effect must trace to a complete closure card. Missing mappings get downgraded or deleted — never hidden behind more sections.

Full audit: [references/final-audit.md](references/final-audit.md)

## Input/Output Contract

### Input
- Repository path (local) or GitHub URL
- Specific question: object name, behavior, flow, or architecture aspect
- Optional: version/branch, specific files to focus on

### Output Format
```
## Scope
repo@revision | named objects | read range

## Evidence Matrix
| Stage | Locator | Observed Branch/Callee | Claim Scope | Status |
|---|---|---|---|---|
| ... | ... | ... | ... | confirmed/inferred/unknown |

## Direct Answer
1. [confirmed] ...
2. [inferred] ... (前提: ..., 证伪: ...)
3. [unknown] ... (缺失: ..., 影响: ...)

## Main Chain
entry → step1 → step2 → result
(key bypass: ...)

## Unknowns & Verification
- ...
```

## Example

**Input:** "Trace what happens when a user submits a login form in this Next.js app"

**Output:**
```
## Scope
my-app@main | pages/api/auth/login.ts, lib/auth.ts, lib/session.ts | read 3 files

## Evidence Matrix
| Stage | Locator | Observed | Claim Scope | Status |
|---|---|---|---|---|
| Entry | pages/api/auth/login.ts:12 | POST handler calls authenticate() | HTTP entry | confirmed |
| Auth | lib/auth.ts:45 | authenticate() queries users table | credential check | confirmed |
| Session | lib/session.ts:28 | createSession() writes to Redis | session storage | confirmed |
| Cookie | lib/session.ts:51 | setCookie() called after Redis write | response header | confirmed |
| Failure | lib/auth.ts:52 | returns 401, no session created | error path | confirmed |

## Direct Answer
1. [confirmed] Login flow: POST /api/auth/login → authenticate() → Redis session write → Set-Cookie header
2. [confirmed] Failed login returns 401 without creating a session
3. [inferred] Redis write failure likely returns 500 (前提: createSession throws on Redis error, 证伪: check error handling in lib/session.ts:35)

## Main Chain
form submit → API route → authenticate(DB query) → createSession(Redis) → setCookie → 200 response
(bypass: invalid credentials → 401 at authenticate())

## Unknowns
- Redis failure behavior: need to read lib/session.ts error handling (lines 35-45)
```

## Boundaries with Related Skills

| Situation | This Skill | Other Skill |
|---|---|---|
| "How does X work?" | ✅ Primary | — |
| "Why is X broken?" | — | Bug diagnosis skill |
| "Should we refactor X?" | — | Design solution skill |
| "Review this MR" | — | Code review skill |
| "Find where X is implemented" | ✅ Primary | — |
| "What's the performance bottleneck?" | — | Profiling/optimization skill |

## References

| File | Purpose | When to Read |
|---|---|---|
| [claim-ledger.md](references/claim-ledger.md) | Evidence hierarchy and claim accounting | Always, before writing conclusions |
| [evidence-graph.md](references/evidence-graph.md) | Graph model, epistemic states, activation axis, counter-evidence | Flow/behavior questions |
| [repository-tracing.md](references/repository-tracing.md) | Boundary identification, entry funnel, bidirectional tracing, key-jump ledger | Flow/behavior questions |
| [responsibility-closure.md](references/responsibility-closure.md) | Cross-component effect claim cards | When writing effect/guarantee claims |
| [final-audit.md](references/final-audit.md) | Pre-delivery audit checklist | Always, before shipping |
