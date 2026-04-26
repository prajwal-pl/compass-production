# Compass Backend Comprehensive Analysis and Learning Plan

Date: 2026-04-26
Scope: Whole project review with focus on backend learning, architecture clarity, and FastAPI vs Express strategy.

## 1) Executive Summary

Your frustration is valid. The current backend is uneven:
- Security/auth is significantly more mature than the rest of the API.
- Most product endpoints are still scaffold placeholders.
- The codebase structure looks production-oriented, but feature-level feedback loops (build -> run -> test real behavior) are limited.

This creates a "jarring" first FastAPI experience because you are interacting with advanced concerns (JWT rotation, lockouts, revocation stores) before learning basic backend product development loops (CRUD + business rules + persistence + tests per feature).

## 2) Ground Truth From the Current Codebase

### 2.1 API implementation maturity snapshot

Observed route decorators in backend/api: 56 total
Observed "work in progress" markers in backend/api: 46

Per module:

| Module | Routes | WIP markers | Maturity |
|---|---:|---:|---|
| auth.py | 10 | 0 | Implemented core auth flows + hardening |
| services.py | 8 | 8 | Placeholder business logic |
| deployments.py | 5 | 5 | Placeholder business logic |
| dependencies.py | 6 | 6 | Placeholder business logic |
| docs.py | 4 | 4 | Placeholder business logic |
| ai.py | 5 | 5 | Placeholder AI logic |
| integrations.py | 8 | 8 | Placeholder integration logic |
| metrics.py | 2 | 2 | Placeholder logic |
| templates.py | 4 | 4 | Placeholder logic |
| webhooks.py | 3 | 3 | Placeholder logic |
| search.py | 1 | 1 | Placeholder logic |

Interpretation: almost all non-auth domain value is still unimplemented.

### 2.2 Testing focus snapshot

Observed test functions in backend/tests: 40

Distribution:
- test_auth_routes.py: 21
- test_auth_context.py: 6
- test_auth_schema.py: 5
- test_authorization_guards.py: 6
- test_route_matching.py: 2

Interpretation: tests mostly validate auth and route-guard behavior; very little product behavior is test-driven yet.

### 2.3 Architecture and implementation characteristics

What is comparatively strong now:
- Token model includes access + refresh + reset types.
- Refresh token rotation/reuse detection exists.
- Rate limiting and lockout logic exists.
- Redis-backed security store with in-memory fallback exists.
- Authorization guard utility exists for owner/team/superuser checks.

What is mostly scaffolded:
- Service catalog behavior
- Deployment state machine behavior
- Dependency graph traversal/impact analysis
- Docs ingestion/chunking/search behavior
- AI endpoint behavior
- Integrations/webhook processing behavior

### 2.4 Configuration and project hygiene issues affecting learning

- Requirements list appears environment-frozen and very broad for current implementation stage, making dependency understanding harder.
- No migration framework (Alembic) is present; db/push.py uses create_all-style schema sync.
- Env/documentation drift is present (example naming/provider mismatches in docs vs code).
- A local backend .env currently contains real-looking secrets and should be treated as exposed and rotated.

## 3) Why You Are Not Learning (Root Cause Analysis)

This is not a motivation issue. It is a learning-system design issue.

Primary blockers:
1. Architecture-first, value-later sequencing.
   - You are seeing many files/routes before seeing complete user-visible behavior.

2. Too many domains at once.
   - Auth, docs, AI, integrations, deployments, dependencies, metrics are all present, but mostly skeletal.

3. Missing vertical slices.
   - A beginner learns fastest from complete thin slices (request -> validation -> DB write/read -> response -> test).

4. Advanced auth landed early.
   - Useful in production, but cognitively heavy for a first backend project.

5. Little immediate feedback on non-auth features.
   - Placeholders reduce opportunities to practice debugging and domain modeling.

## 4) Should You Move Core APIs to Express and Keep FastAPI for AI?

Short answer: this is a valid strategy for learning velocity if JavaScript is your strongest base, but only if you enforce clean boundaries.

### 4.1 Decision matrix

| Criterion | Keep one FastAPI backend | Express core + FastAPI AI |
|---|---|---|
| Learning speed (if JS-strong) | Medium | High |
| Operational complexity | Low | Medium/High (two runtimes) |
| Auth complexity | One source of truth | Risk of duplicated auth unless centralized |
| Team scalability | Good | Good if contracts are strict |
| AI experimentation speed | Good | Very good (isolated Python AI stack) |

### 4.2 Recommendation

If your immediate goal is "learn backend deeply and ship features":
- Move traditional CRUD/business APIs to Express.
- Keep FastAPI as an internal AI service only.
- Do not duplicate auth across both services.

## 5) Recommended Hybrid Architecture (Express Core + FastAPI AI)

### 5.1 Service ownership boundaries

Express service (public API + product core):
- auth, services, deployments, dependencies, docs metadata, integrations, webhooks, search

FastAPI service (internal AI engine):
- ai ask/explain/troubleshoot/suggestions
- embedding generation, retrieval/rerank logic
- tool orchestration and AI traces

### 5.2 Data ownership

- Use one Postgres cluster.
- Keep domain tables owned by Express service.
- Keep AI-specific tables (embeddings, traces, prompts, run metadata) owned by FastAPI service.
- Avoid both services writing the same table unless absolutely necessary.

### 5.3 Communication pattern

- Express calls FastAPI over internal network for synchronous AI requests.
- For long-running jobs, queue tasks (Redis + worker model) and poll job status.
- Protect FastAPI with internal auth (service token/mTLS) and never expose it publicly at first.

### 5.4 Auth strategy

- Single issuer/verifier path in Express for user JWTs.
- FastAPI accepts only internal service authentication from Express, not end-user tokens directly (initially).

## 6) If You Stay Fully FastAPI Instead

If you prefer staying Python, reduce complexity aggressively:
- Pause advanced features.
- Keep current auth implementation, but stop expanding it.
- Build 2 complete vertical slices first:
  1) services CRUD with ownership checks
  2) deployments trigger + status timeline

This alone will dramatically improve learning signal.

## 7) 30-Day Learning-First Execution Plan

### Week 1: Simplify and establish one vertical slice
- Implement services create/list/get/update/delete for real.
- Add persistence and domain validation rules.
- Write route + service-layer tests for success/failure paths.

### Week 2: Deployments
- Implement deployment trigger and status transitions.
- Add rollback lineage.
- Add tests for transition validity.

### Week 3: Dependencies + docs baseline
- Add explicit service dependency relation model.
- Add traversal and dependents endpoints.
- Add docs CRUD and basic search fallback (keyword first, vector later).

### Week 4: AI integration path
- Connect AI endpoints to actual retrieval contract.
- Add citation requirement and response schema.
- Add latency/error telemetry.

## 8) Immediate Cleanup Backlog (High Priority)

1. Rotate any exposed local secrets and regenerate keys.
2. Introduce Alembic migrations; stop relying only on create_all-style schema sync.
3. Split requirements into minimal runtime dependencies vs dev extras.
4. Align env variable names and provider names between README and code.
5. Add startup validation for all critical env vars (not just auth fields).

## 9) Practical Anti-Outsourcing Guardrails (To Force Learning)

Use these rules for each feature:
1. Implement first draft yourself (no AI).
2. Run tests and debug failures yourself.
3. Ask AI only for review or edge-case gaps.
4. Write a short "what I learned" note after each feature.
5. Only move to next feature after one complete vertical slice is done.

## 10) Concrete Recommendation for Your Case

Based on current code state and your goal:
- Your discomfort is caused more by project shape than by FastAPI itself.
- Moving traditional APIs to Express is reasonable for your learning velocity.
- Keep FastAPI exclusively for AI and internal workflows.
- Whatever stack you pick, prioritize complete vertical slices over broad scaffolding.

If you want, the next step can be a precise migration map file-by-file from current FastAPI routes to an Express structure while reusing your existing data model and auth rules.
