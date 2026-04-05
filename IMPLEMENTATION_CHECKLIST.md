# Compass Implementation Checklist (Execution + Learning Plan)

## How to use this list
- Priority levels:
  - P0 = blockers and foundations required before scaling features
  - P1 = core product capabilities (MVP-complete IDP)
  - P1.5 = AI architecture prerequisites
  - P2 = advanced AI + frontend productization
  - P3 = reliability and scale
- Work mode tags:
  - [Build] = I can implement this directly in code
  - [Guide] = I will teach and coach you through concepts, tradeoffs, and production thinking
  - [Joint] = we pair on decisions and implementation
- Execution rule:
  - Finish at least 80 to 90 percent of P0 before broad P1.
  - Do not optimize AI quality before retrieval/tooling foundations are stable.

---

## Completed So Far (Implemented and Verified)

### Routing correctness
- [x] [Build] Reorder docs routes so static paths are matched before dynamic service_id route.
- [x] [Build] Reorder metrics routes so overview is matched before dynamic service_id route.

### Authentication hardening and lifecycle
- [x] [Build] Fix token issuance sequence in register flow (create token only after persisted user id exists).
- [x] [Build] Ensure get_current_user returns typed User object and handles missing user safely.
- [x] [Build] Prevent sensitive auth response leakage by returning safe serialized user payloads.
- [x] [Build] Harden auth request schemas (forbid extra fields, block privilege-field injection in UserUpdate).
- [x] [Build] Implement logout endpoint with token revocation.
- [x] [Build] Implement reset-password request + confirm flow.
- [x] [Build] Keep backward-compatible /auth/reset-password endpoint behavior.
- [x] [Build] Implement delete-account deactivation flow with token revocation.
- [x] [Build] Block inactive users at login/current-user resolution.
- [x] [Build] Add startup validation for JWT auth settings with clear failure messages.
- [x] [Build] Add refresh token endpoint with rotation and reuse detection.
- [x] [Build] Add optional Redis-backed security store for token/session controls (in-memory fallback for local/dev).
- [x] [Build] Add login/reset rate limiting controls with retry-after semantics.
- [x] [Build] Add account lockout policy for repeated login/reset confirmation abuse patterns.

### Cross-router authorization
- [x] [Build] Add authorization guards to services endpoints (owner/team/superuser checks).
- [x] [Build] Add authorization guards to deployments endpoints.
- [x] [Build] Add authorization guards to docs, metrics, and dependencies endpoints.

### Testing and stability checks
- [x] [Build] Add auth route integration tests (register/login/profile/logout/reset/delete).
- [x] [Build] Add auth context unit tests (token type, revocation, UUID handling, inactive users).
- [x] [Build] Add schema validation tests for auth payload hardening.
- [x] [Build] Add route-matching regression tests for docs and metrics static-vs-dynamic paths.
- [x] [Build] Add authorization regression tests for services/deployments/docs/metrics/dependencies.
- [x] [Build] Run backend test suite successfully after changes (38 passed).
- [x] [Build] Add pytest dependency to backend requirements for reproducible local/CI runs.
- [x] [Build] Add redis dependency for production-backed security state.

---

## Current Sprint Focus (Next in Order)
- [x] [Build] Add route regression tests for docs and metrics path matching.
- [x] [Build] Extend authorization guards beyond /auth (owner/team/superuser checks across services, deployments, docs).
- [x] [Build] Replace in-memory token revocation with Redis-backed revocation/session strategy (production-safe multi-instance behavior).
- [x] [Build] Add refresh token rotation and session invalidation model.
- [x] [Build] Add rate limiting for login and password reset endpoints.
- [ ] [Guide] Deep-dive: JWT access + refresh model, revocation strategy, and replay attack mitigation.
- [ ] [Guide] Deep-dive: production password reset flow (email provider, signed links, abuse prevention, auditability).

---

## P0: Foundation, Correctness, and Safety

### 1) API routing correctness
- [x] [Build] Add route tests to prevent regressions in docs path matching.
- [x] [Build] Add route tests to prevent regressions in metrics path matching.

### 2) Complete core data model gaps
- [ ] [Build] Add explicit service dependency relation model (source_service_id, target_service_id, type, criticality).
- [ ] [Build] Add indexes for dependency traversal and impact analysis queries.
- [ ] [Build] Add migration strategy for schema evolution (Alembic).
- [ ] [Guide] Explain relational modeling for service graph workloads and when to choose recursive CTE vs graph DB.

### 3) Secure and harden authentication (remaining)
- [x] [Build] Add integration tests for auth happy path and failure path.
- [x] [Build] Add baseline authorization checks for self vs superuser in profile flows.
- [x] [Build] Add full role-based authorization guards (owner, team member, superuser) across domain routers.
- [x] [Build] Add refresh token issuance, rotation, and reuse detection.
- [x] [Build] Add Redis-backed token revocation/session store.
- [ ] [Build] Replace reset-token API response with email workflow in non-dev environments.
- [x] [Build] Add login/reset endpoint lockout policy.
- [ ] [Guide] Walk through auth threat model: credential stuffing, replay, privilege escalation, reset abuse.

### 4) Environment and secret management
- [ ] [Build] Remove embedded secrets from local files and rotate exposed keys.
- [ ] [Build] Standardize environment variable names across backend and docs.
- [ ] [Build] Extend startup validation to all required env vars (DATABASE_URL, REDIS_URL, GROQ_API_KEY, etc.).
- [ ] [Guide] Explain production secrets management patterns (vaults, rotation cadence, break-glass access).

### 5) Observability baseline
- [ ] [Build] Add structured logging with request ids and correlation ids.
- [ ] [Build] Add basic metrics (latency, error rate, model call count, token usage).
- [ ] [Build] Add centralized error tracking policy for API and background jobs.
- [ ] [Guide] Teach RED/USE metrics, trace correlation, and incident triage workflow.

### 6) Background execution foundation
- [ ] [Build] Add Celery worker and queue definitions for long-running tasks.
- [ ] [Build] Define job status model and persistence for async operations.
- [ ] [Build] Move docs generation and template generation to background workflows.
- [ ] [Guide] Explain sync vs async architecture, retries, idempotency keys, and dead-letter handling.

---

## P1: Core Product Features (MVP)

### 7) Service catalog implementation
- [ ] [Build] Implement create/list/get/update/delete service endpoints with filtering and pagination.
- [ ] [Build] Add ownership and team validation rules on writes.
- [ ] [Build] Implement service health endpoint (HTTP probe + cached status).
- [ ] [Build] Implement logs endpoint and minimal websocket stream pipeline.
- [ ] [Guide] Explain API design choices: pagination strategies, filtering, consistency, and error contracts.

### 8) Deployments implementation
- [ ] [Build] Implement deployment trigger endpoint with environment validation.
- [ ] [Build] Persist deployment state transitions (pending -> in_progress -> success/failed).
- [ ] [Build] Implement rollback endpoint and rollback lineage tracking.
- [ ] [Build] Implement deployment status endpoint with event timeline.
- [ ] [Guide] Explain deployment state machines, rollback safety checks, and blast-radius reduction.

### 9) Dependency graph and impact analysis
- [ ] [Build] Implement full graph endpoint with depth limits and cycle-safe traversal.
- [ ] [Build] Implement dependents endpoint for reverse dependency lookups.
- [ ] [Build] Implement impact analysis endpoint with blast radius scoring.
- [ ] [Guide] Explain graph traversal complexity, cycle handling, and confidence scoring.

### 10) Docs system and search baseline
- [ ] [Build] Implement service docs CRUD and versioning semantics.
- [ ] [Build] Implement README ingestion from repository.
- [ ] [Build] Implement chunking + embedding pipeline for documentation.
- [ ] [Build] Implement semantic search endpoint with source citations.
- [ ] [Guide] Explain chunking strategies, embedding quality tradeoffs, and citation grounding.

### 11) Integrations and webhooks (minimum viable)
- [ ] [Build] GitHub integration: connect, list repos, sync metadata, list commits.
- [ ] [Build] Kubernetes integration: connect cluster, list pods/services, sync service inventory.
- [ ] [Build] Webhooks: verify signatures, parse events, enqueue processing jobs.
- [ ] [Guide] Explain webhook idempotency, signature verification, and replay attack defenses.

### 12) Global search
- [ ] [Build] Implement federated search over services, docs, and deployments.
- [ ] [Build] Add type filters and ranking strategy (hybrid keyword + vector).
- [ ] [Guide] Explain ranking composition and relevance evaluation.

---

## P1.5: AI System Architecture (Required before advanced AI features)

### 13) Model provider abstraction
- [ ] [Build] Build model adapter layer (chat, structured output, tool-calling, optional multimodal).
- [ ] [Build] Keep provider-specific settings outside endpoint business logic.
- [ ] [Build] Add fallback model policy and timeout/circuit-breaker handling.
- [ ] [Guide] Teach provider abstraction design: capability matrix, fallback routing, and failover policy.

### 14) Retrieval and grounding contract
- [ ] [Build] Define retrieval contract for AI responses (top-k docs, citations, confidence).
- [ ] [Build] Build prompt templates per endpoint task type (ask, explain, troubleshoot, suggestions).
- [ ] [Build] Add hallucination guardrails (factual claims require internal citations).
- [ ] [Guide] Teach RAG lifecycle: ingest -> index -> retrieve -> rerank -> answer -> evaluate.

### 15) Tooling layer for agents
- [ ] [Build] Implement typed tools for service metadata, deployments, dependencies, metrics, incidents.
- [ ] [Build] Enforce tool call budget and max-step limits.
- [ ] [Build] Capture full tool traces for audit/debug.
- [ ] [Guide] Teach agent loop safety, bounded autonomy, and tool reliability contracts.

---

## P2: Advanced AI Features and Quality

### 16) Implement AI endpoints end-to-end
- [ ] [Build] /ai/ask with retrieval grounding and citations.
- [ ] [Build] /ai/explain for code/config/deployment explanations with risk summary.
- [ ] [Build] /ai/troubleshoot with multi-step tool use and root-cause ranking.
- [ ] [Build] /ai/suggestions/{service_id} with structured prioritized recommendations.
- [ ] [Build] /ai/generate-text constrained to safe non-operational generation.
- [ ] [Guide] Teach prompt decomposition and response schema design for each endpoint.

### 17) Model strategy and cost/latency governance
- [ ] [Joint] Define where premium reasoning model is primary vs fallback lower-cost model.
- [ ] [Joint] Decide instant vs deep-thinking modes by endpoint latency SLO.
- [ ] [Build] Add model usage telemetry (latency, token count, cost).
- [ ] [Guide] Teach production model routing economics and SLO-driven AI architecture.

### 18) Evaluation and tuning
- [ ] [Build] Create benchmark sets from incidents, runbooks, and service docs.
- [ ] [Build] Define pass/fail metrics: grounded accuracy, tool efficiency, latency, cost.
- [ ] [Build] Implement evaluation runner for regression testing prompts/retrieval changes.
- [ ] [Guide] Teach eval-first development and when fine-tuning is actually justified.

### 19) AI safety and policy controls
- [ ] [Build] Add permission-aware responses (role and service scope).
- [ ] [Build] Add confirmation workflow for risky recommendations (deploy/rollback actions).
- [ ] [Build] Add output filters for secret leakage and sensitive content handling.
- [ ] [Guide] Teach AI safety controls in production: policy layers, abuse monitoring, and escalation.

---

## P2: Frontend Productization

### 20) Convert landing UI into product shell
- [ ] [Build] Add routing, auth guard, and app layout (sidebar/topbar/content).
- [ ] [Build] Build pages: services, service detail, dependencies, deployments, docs, AI assistant.
- [ ] [Build] Introduce API client and query caching strategy.
- [ ] [Build] Add empty/loading/error states for all data surfaces.

### 21) Visualization features
- [ ] [Build] Add dependency graph view with interaction controls and impact overlays.
- [ ] [Build] Add deployment timelines and status badges.
- [ ] [Build] Add metrics dashboards with interval controls.

### 22) AI UX
- [ ] [Build] Add conversational assistant UI with citations and tool trace toggle.
- [ ] [Build] Add troubleshoot workflow UI (steps, findings, confidence, actions).
- [ ] [Build] Add suggestions panel with actionable items and ownership assignment.
- [ ] [Guide] Teach trustworthy AI UX patterns (confidence, evidence, and action safeguards).

---

## P3: Reliability, Scale, and Operations

### 23) Performance and caching
- [ ] [Build] Add caching strategy for expensive read paths and model responses.
- [ ] [Build] Add async batching for embedding generation.
- [ ] [Build] Add database query profiling and index tuning.

### 24) CI/CD and quality gates
- [ ] [Build] Add backend and frontend test pipelines in CI.
- [ ] [Build] Add lint/type checks as required gates.
- [ ] [Build] Add migration checks and schema drift detection in CI.
- [ ] [Guide] Teach release gates and rollback criteria for AI and API changes.

### 25) Production readiness
- [ ] [Build] Define SLOs and alerting thresholds.
- [ ] [Build] Add runbooks for incidents and degraded provider scenarios.
- [ ] [Build] Add backup/restore drills and disaster recovery validation.
- [ ] [Guide] Teach incident command structure and postmortem process.

### 26) Governance and auditability
- [ ] [Build] Add audit logs for admin actions and AI-assisted recommendations.
- [ ] [Build] Add data retention policy for logs, prompts, traces, and embeddings.
- [ ] [Build] Add model/provider change management checklist.
- [ ] [Guide] Teach compliance and governance baseline for internal AI platforms.

---

## Suggested execution milestones
- [ ] Milestone A: Platform core is safe and stable (P0 Build track complete, critical Guide topics covered).
- [ ] Milestone B: MVP IDP is usable end-to-end (sections 7 through 12 complete).
- [ ] Milestone C: AI assistant is trustworthy and measurable (sections 13 through 19 complete + eval baselines passing).
- [ ] Milestone D: Production hardening complete (sections 23 through 26 complete).

## Definition of done (global)
- [ ] Endpoint contracts are implemented, tested, and documented.
- [ ] AI answers are grounded with citations for factual responses.
- [ ] Security baseline and secret management are validated.
- [ ] Dashboards and alerts exist for both API and model layers.
- [ ] Team can run, debug, and deploy the system from documented playbooks.
