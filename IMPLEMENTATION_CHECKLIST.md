# Compass Implementation Checklist (Priority-Ordered)

## How to use this list
- Priority levels:
  - P0 = blockers and foundations required before scaling features
  - P1 = core product capabilities (MVP-complete IDP)
  - P2 = advanced AI and platform maturity
  - P3 = optimization and scale enhancements
- Execution rule:
  - Finish at least 80 to 90 percent of P0 before starting broad P1 work.
  - Treat AI tuning as a late-stage optimization after retrieval and tools are stable.

---

## P0: Foundation, Correctness, and Safety (Do first)

### 1) Fix API routing correctness
- [x] Reorder docs routes so static paths are matched before dynamic service_id route.
- [x] Reorder metrics routes so overview is matched before dynamic service_id route.
- [ ] Add route tests to prevent regressions in path matching.

### 2) Complete core data model gaps
- [ ] Add explicit service dependency relation model (source_service_id, target_service_id, type, criticality).
- [ ] Add indexes for dependency traversal and impact analysis queries.
- [ ] Add migration strategy for schema evolution (Alembic recommended).

### 3) Secure and harden authentication
- [x] Fix token issuance sequence in register flow (create token only after persisted user id exists).
- [ ] Ensure get_current_user returns typed User object and handles missing user safely.
- [ ] Add role-based authorization guards (owner, team member, superuser).
- [ ] Add integration tests for auth happy path and failure path.

### 4) Environment and secret management
- [ ] Remove embedded secrets from local files and rotate exposed keys.
- [ ] Standardize environment variable names across backend and docs.
- [ ] Add startup validation for required env vars with clear failure messages.

### 5) Observability baseline
- [ ] Add structured logging with request ids and correlation ids.
- [ ] Add basic metrics (latency, error rate, model call count, token usage).
- [ ] Add centralized error tracking policy for API and background jobs.

### 6) Background execution foundation
- [ ] Add Celery worker and queue definitions for long-running tasks.
- [ ] Define job status model and persistence for async operations.
- [ ] Move docs generation and template generation to background workflows.

---

## P1: Core Product Features (MVP functionality)

### 7) Service catalog implementation
- [ ] Implement create/list/get/update/delete service endpoints with filtering and pagination.
- [ ] Add ownership and team validation rules on writes.
- [ ] Implement service health endpoint (HTTP probe + cached status).
- [ ] Implement logs endpoint and minimal websocket stream pipeline.

### 8) Deployments implementation
- [ ] Implement deployment trigger endpoint with environment validation.
- [ ] Persist deployment states and transition rules (pending -> in_progress -> success/failed).
- [ ] Implement rollback endpoint and rollback lineage tracking.
- [ ] Implement deployment status endpoint with latest event timeline.

### 9) Dependency graph and impact analysis
- [ ] Implement full graph endpoint with depth limits and cycle-safe traversal.
- [ ] Implement dependents endpoint for reverse dependency lookups.
- [ ] Implement impact analysis endpoint with blast radius scoring.

### 10) Docs system and search baseline
- [ ] Implement service docs CRUD and versioning semantics.
- [ ] Implement README ingestion from repository.
- [ ] Implement chunking + embedding pipeline for documentation.
- [ ] Implement semantic search endpoint with source citations.

### 11) Integrations and webhooks (minimum viable)
- [ ] GitHub integration: connect, list repos, sync metadata, list commits.
- [ ] Kubernetes integration: connect cluster, list pods/services, sync service inventory.
- [ ] Webhooks: verify signatures, parse events, enqueue processing jobs.

### 12) Global search
- [ ] Implement federated search over services, docs, and deployments.
- [ ] Add type filters and ranking strategy (hybrid keyword + vector).

---

## P1.5: AI System Architecture (Required before advanced AI features)

### 13) Model provider abstraction
- [ ] Build model adapter layer (chat, structured output, tool-calling, optional multimodal).
- [ ] Keep provider-specific settings outside endpoint business logic.
- [ ] Add fallback model policy and timeout/circuit-breaker handling.

### 14) Retrieval and grounding contract
- [ ] Define retrieval contract for AI responses (top-k docs, citations, confidence).
- [ ] Build prompt templates per endpoint task type (ask, explain, troubleshoot, suggestions).
- [ ] Add hallucination guardrails (must cite internal sources for factual claims).

### 15) Tooling layer for agents
- [ ] Implement typed tools for service metadata, deployments, dependencies, metrics, incidents.
- [ ] Enforce tool call budget and max-step limits.
- [ ] Capture full tool traces for audit/debug.

---

## P2: Advanced AI Features and Quality

### 16) Implement AI endpoints end-to-end
- [ ] /ai/ask with retrieval grounding and citations.
- [ ] /ai/explain for code/config/deployment explanations with risk summary.
- [ ] /ai/troubleshoot with multi-step tool use and root-cause ranking.
- [ ] /ai/suggestions/{service_id} with structured prioritized recommendations.
- [ ] /ai/generate-text constrained to safe non-operational generation.

### 17) Kimi K2.5 integration strategy
- [ ] Define where Kimi is primary (high-complexity reasoning + tool workflows).
- [ ] Define where lower-cost model is primary (simple explain/ask requests).
- [ ] Decide instant vs thinking mode per endpoint based on latency budget.
- [ ] Validate multimodal path only for planned features (diagram or screenshot-driven workflows).

### 18) Fine-tuning readiness and evaluation
- [ ] Create benchmark sets from internal incidents, runbooks, and service docs.
- [ ] Define pass/fail metrics: grounded accuracy, tool efficiency, latency, cost.
- [ ] Start with prompt and retrieval tuning before any weight tuning.
- [ ] Run lightweight fine-tuning only if eval plateaus and data quality is high.

### 19) AI safety and policy controls
- [ ] Add permission-aware responses (role and service scope).
- [ ] Add action confirmation for risky recommendations (deploy/rollback changes).
- [ ] Add output filters for secret leakage and sensitive content handling.

---

## P2: Frontend Productization

### 20) Convert landing UI into product shell
- [ ] Add routing, auth guard, and app layout (sidebar/topbar/content).
- [ ] Build pages: services, service detail, dependencies, deployments, docs, AI assistant.
- [ ] Introduce API client and query caching strategy.
- [ ] Add empty/loading/error states for all data surfaces.

### 21) Visualization features
- [ ] Add dependency graph view with interaction controls and impact overlays.
- [ ] Add deployment timelines and status badges.
- [ ] Add metrics dashboards with interval controls.

### 22) AI UX
- [ ] Add conversational assistant UI with citations and tool trace toggle.
- [ ] Add troubleshoot workflow UI (steps, findings, confidence, actions).
- [ ] Add suggestions panel with actionable items and ownership assignment.

---

## P3: Reliability, Scale, and Operations

### 23) Performance and caching
- [ ] Add caching strategy for expensive read paths and model responses.
- [ ] Add async batching for embedding generation.
- [ ] Add database query profiling and index tuning.

### 24) CI/CD and quality gates
- [ ] Add backend and frontend test pipelines in CI.
- [ ] Add lint/type checks as required gates.
- [ ] Add migration checks and schema drift detection in CI.

### 25) Production readiness
- [ ] Define SLOs and alerting thresholds.
- [ ] Add runbooks for incidents and degraded provider scenarios.
- [ ] Add backup/restore drills and disaster recovery validation.

### 26) Governance and auditability
- [ ] Add audit logs for admin actions and AI-assisted recommendations.
- [ ] Add data retention policy for logs, prompts, traces, and embeddings.
- [ ] Add model/provider change management checklist.

---

## Suggested execution milestones
- [ ] Milestone A: Platform core is safe and stable (all P0 complete).
- [ ] Milestone B: MVP IDP is usable end-to-end (sections 7 through 12 complete).
- [ ] Milestone C: AI assistant is trustworthy and measurable (sections 13 through 19 complete).
- [ ] Milestone D: Production hardening complete (sections 23 through 26 complete).

## Definition of done (global)
- [ ] Endpoint contracts are implemented, tested, and documented.
- [ ] AI answers are grounded with citations for factual responses.
- [ ] Security baseline and secret management are validated.
- [ ] Dashboards and alerts exist for both API and model layers.
- [ ] Team can run, debug, and deploy the system from documented playbooks.
