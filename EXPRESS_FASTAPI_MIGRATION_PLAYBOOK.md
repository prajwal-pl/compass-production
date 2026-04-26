# Compass Migration Playbook: Express Core + FastAPI AI

Date: 2026-04-26
Owner: Platform team
Status: Proposed execution plan

## 1) Objective

Migrate Compass from a single mixed FastAPI backend to a hybrid architecture:
- Express service owns product and platform APIs.
- FastAPI service owns AI inference, retrieval, tool orchestration, and AI-specific workflows.

Primary goal:
- Increase developer learning velocity and implementation speed on core backend features.

Secondary goals:
- Keep Python where it provides high leverage (LLM workflows, LangGraph, embeddings).
- Reduce cognitive load by separating CRUD/business backend concerns from AI system concerns.

## 2) Target Architecture

### 2.1 Service boundaries

Express (public API gateway + domain core):
- /auth
- /services
- /deployments
- /dependencies
- /docs (metadata and non-AI CRUD)
- /integrations
- /webhooks
- /metrics (non-AI operational metrics)
- /search (federated/domain search)

FastAPI (internal AI platform service):
- /ai/ask
- /ai/explain
- /ai/troubleshoot
- /ai/suggestions
- /ai/generate-text
- /internal/docs/generate
- /internal/templates/generate
- /internal/retrieval/*

### 2.2 Data ownership

Single PostgreSQL cluster, clear table ownership:
- Express-owned tables: users, teams, services, deployments, dependencies, docs metadata, webhook events.
- FastAPI-owned tables: document chunks, embeddings, retrieval indices, prompt runs, tool traces, AI evaluations.

Rule:
- A table has one owning service. Other service accesses via API contract or read-only views when necessary.

### 2.3 Auth model

- Express is the only public JWT issuer/verifier for end users.
- FastAPI accepts internal service authentication only (service token or mTLS).
- FastAPI is not publicly exposed in initial phase.

## 3) Endpoint Migration Map

| Current Prefix | Target Service | Migration Notes |
|---|---|---|
| /auth | Express | Port existing logic and tests first. Keep refresh rotation and lockout behavior. |
| /services | Express | Implement real CRUD and health/logs behavior in Express. |
| /deployments | Express | Implement trigger, status timeline, rollback lineage. |
| /dependencies | Express | Implement relation model and traversal endpoints. |
| /docs/search | FastAPI (retrieval) via Express facade | Express endpoint calls FastAPI retrieval API and returns normalized response. |
| /docs/{service_id}/generate | FastAPI async workflow via Express command endpoint | Express validates auth/ownership, enqueues AI job in FastAPI. |
| /templates/{id}/generate | FastAPI async workflow via Express command endpoint | Same command pattern as docs generation. |
| /ai/* | FastAPI (public through Express proxy) | Keep response contract stable while moving implementation. |
| /integrations | Express | Keep external integrations and webhook validation in Express. |
| /webhooks | Express | Signature verification and idempotency in Express. |
| /search | Express + FastAPI hybrid | Express aggregates domain search plus AI semantic results. |

## 4) Phased Execution Plan

## Phase 0: Foundation and Guardrails (3 to 5 days)

Deliverables:
- Create backend-express workspace with TypeScript and strict mode.
- Create backend-ai workspace from existing FastAPI code.
- Define OpenAPI contracts for all externally consumed endpoints.
- Establish service-to-service auth and network policy.
- Add correlation id propagation between services.

Exit criteria:
- Both services boot locally.
- Health endpoints pass.
- Contract lint checks pass.

## Phase 1: Auth and Shared Identity (4 to 6 days)

Deliverables:
- Port /auth to Express.
- Preserve refresh rotation, reuse detection, rate limits, and lockouts.
- Move token/session state to Redis with same semantics as existing behavior.
- Port and adapt auth tests.

Exit criteria:
- Login/register/logout/refresh/reset/delete flows pass parity tests.
- No auth logic remains exposed via FastAPI public routes.

## Phase 2: Core Domain APIs in Express (7 to 10 days)

Deliverables:
- Implement services, deployments, dependencies, docs metadata endpoints in Express.
- Add real persistence and business validation (remove work in progress placeholders).
- Add role-aware authorization middleware equivalent to current owner/team/superuser checks.
- Add integration tests per endpoint group.

Exit criteria:
- 80 percent plus of core route handlers return real behavior.
- Core domain tests are green in CI.

## Phase 3: AI Service Isolation (5 to 8 days)

Deliverables:
- Keep AI logic in FastAPI only.
- Expose internal APIs for retrieval, generation, troubleshooting orchestration.
- Add job queue and status polling for long-running AI tasks.
- Add citation-first response schema and confidence fields.

Exit criteria:
- Express successfully calls FastAPI AI endpoints with service auth.
- AI endpoints produce grounded responses with source references.

## Phase 4: Unified API Surface and Frontend Stability (3 to 5 days)

Deliverables:
- Express serves as single public API base URL for frontend.
- Route adapters/proxies hide dual-service complexity from frontend.
- Add failure fallbacks and timeout policy when FastAPI is degraded.

Exit criteria:
- Frontend uses one API origin.
- AI degradation does not break non-AI product flows.

## Phase 5: Decommission Legacy FastAPI Domain Routes (2 to 3 days)

Deliverables:
- Remove non-AI route modules from FastAPI.
- Keep only AI and internal orchestration routes.
- Freeze old route paths with deprecation policy and sunset date.

Exit criteria:
- No duplicate ownership of public routes.
- Documentation updated and validated.

## 5) Proposed Repository Layout

compass-production/
- backend-express/
  - src/
    - app.ts
    - server.ts
    - modules/
      - auth/
      - services/
      - deployments/
      - dependencies/
      - docs/
      - integrations/
      - metrics/
      - search/
      - webhooks/
    - middleware/
    - lib/
    - db/
- backend-ai/
  - main.py
  - api/
    - ai.py
    - retrieval.py
    - generation.py
    - internal_jobs.py
  - agents/
  - embeddings/
  - prompts/
  - workers/
  - db/
- frontend/

## 6) Contract and Reliability Rules

1. Contract first:
- Define request/response schemas before moving each endpoint.

2. One owner per endpoint:
- No long-term dual writes, no duplicated source of truth.

3. Correlation ids mandatory:
- Every inbound request gets request id and correlation id propagated downstream.

4. Timeouts and retries:
- Express to FastAPI calls must use bounded timeout, limited retries, and circuit-breaker behavior.

5. AI response grounding:
- Factual answers include citations and confidence metadata.

## 7) Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Auth behavior drift during migration | High | Build parity test suite and run against both implementations before cutover. |
| Two-service operational overhead | Medium | Keep Express as public gateway, standardize local docker compose setup. |
| Data ownership ambiguity | High | Explicit table ownership matrix and codeowners per module. |
| Frontend API instability | Medium | Preserve external contracts and use compatibility adapters. |
| FastAPI AI latency spikes | Medium | Add job mode fallback and clear timeout budget policy. |

## 8) Testing Strategy

- Contract tests:
  - Validate Express public responses against agreed schemas.

- Parity tests:
  - For migrated routes, compare old FastAPI outputs with new Express outputs where behavior must remain.

- Integration tests:
  - Express to FastAPI call path, including timeout and error mapping.

- Security tests:
  - JWT replay attempts, refresh token reuse, rate limit and lockout verification.

- Load tests:
  - AI route pressure with fallback behavior enabled.

## 9) Cutover Plan

1. Deploy Express in shadow mode.
2. Mirror selected traffic and compare responses.
3. Migrate endpoint groups one by one:
   - auth -> services -> deployments -> dependencies -> docs metadata -> integrations/webhooks -> search.
4. Keep feature flags for fallback to previous path during each migration wave.
5. After stability window, retire old non-AI FastAPI routes.

## 10) Definition of Done

- Express owns all non-AI public APIs.
- FastAPI owns all AI and retrieval/generation internals.
- Frontend uses one stable API origin.
- Auth and authorization semantics remain intact after migration.
- Observability dashboards cover both services with shared correlation ids.
- Runbooks and onboarding docs are updated for the hybrid architecture.

## 11) Immediate Next Actions

1. Scaffold backend-express with strict TypeScript, lint, and test tooling.
2. Port auth first with test parity requirement.
3. Add service-to-service auth for Express to FastAPI calls.
4. Start services endpoint migration using complete vertical slice approach.
5. Track migration in a checklist with owner and due date per endpoint group.
