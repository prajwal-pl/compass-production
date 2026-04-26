# Compass - AI-Native Internal Developer Portal

## Project Overview

Compass is an AI-powered Internal Developer Portal (IDP) designed to help engineering teams discover, understand, and manage their services and infrastructure.

Current execution direction (April 2026):
- Use Express as the primary public backend for domain and product APIs.
- Use FastAPI as an internal AI platform service for retrieval, generation, and agent orchestration.
- Keep one frontend-facing API origin by routing through Express.

## Architecture Direction

### Backend split of responsibilities

Express service (primary public API):
- auth
- services
- deployments
- dependencies
- docs (metadata and CRUD)
- integrations
- webhooks
- metrics
- search

FastAPI service (internal AI and workflow engine):
- ai ask/explain/troubleshoot/suggestions/generate-text
- internal docs generation workflows
- internal template generation workflows
- retrieval and embeddings pipeline
- AI tool traces and evaluation support

### Service communication rules

- Express is the single public API gateway for frontend consumers.
- FastAPI is internal-facing and called by Express through service authentication.
- Correlation and request ids must propagate from Express to FastAPI.
- Timeouts and graceful fallback behavior are required on all Express to FastAPI calls.

## Tech Stack

### Backend Core Service
- Framework: Express with Node.js and TypeScript
- API role: public domain APIs and auth boundary
- Data: PostgreSQL (domain tables), Redis (sessions, rate limits, queues)

### Backend AI Service
- Framework: FastAPI (Python 3.11+)
- AI stack: Groq API, LangGraph, sentence-transformers
- Data: PostgreSQL with pgvector (chunks, vectors, traces), Redis (queue coordination)

### Frontend
- Framework: React 18+ with TypeScript
- Build Tool: Vite
- Styling: Tailwind CSS plus shadcn/ui
- State Management: Zustand and TanStack Query
- Visualization: React Flow and Recharts

## Project Structure

Current repo contains a legacy FastAPI backend at backend/. During migration, target layout should move toward:

compass-production/
- backend-express/
    - src/
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
        - db/
        - lib/
- backend-ai/
    - main.py
    - api/
        - ai.py
        - retrieval.py
        - generation.py
        - internal_jobs.py
    - agents/
    - embeddings/
    - workers/
    - db/
- frontend/
- .github/
    - copilot-instructions.md

## API Ownership Matrix

| Prefix | Owner Service | Notes |
|--------|---------------|-------|
| /auth | Express | Single source of truth for user auth and JWT lifecycle |
| /services | Express | Domain CRUD and service lifecycle |
| /deployments | Express | Deployment and rollback state machine |
| /dependencies | Express | Graph relations and impact endpoints |
| /docs | Express + FastAPI internal | Express owns public contract, FastAPI handles AI generation/retrieval internals |
| /ai | FastAPI via Express facade | Express proxies or orchestrates calls to internal FastAPI |
| /integrations | Express | External system integrations and sync controls |
| /metrics | Express | Platform and service operational metrics APIs |
| /templates | Express + FastAPI internal | Express command endpoint, FastAPI generation backend |
| /webhooks | Express | Signature validation, idempotency, enqueueing |
| /search | Express + FastAPI internal | Federated response with optional semantic enrichment |

## Database Architecture

PostgreSQL remains the primary system of record with pgvector extension enabled.

Required extensions:
- uuid-ossp
- vector

Data ownership rule:
- Domain tables are owned by Express.
- AI retrieval and trace tables are owned by FastAPI.
- Avoid dual writes to the same table from both services.

## Coding Guidelines

### Express and TypeScript
- Use TypeScript strict mode and typed request/response contracts.
- Keep business logic outside controllers.
- Add centralized error handling middleware.
- Enforce request validation for all mutable endpoints.
- Keep auth, authorization, and rate limiting middleware reusable and testable.

### FastAPI and Python
- Use async route handlers and typed Pydantic models.
- Keep AI orchestration logic modular (retrieval, prompting, tool use, output shaping).
- Return structured AI responses with citations for factual claims.
- Isolate external model provider concerns behind adapter modules.

### Shared engineering rules
- All endpoints return JSON with stable contracts.
- Use meaningful HTTP status codes.
- Add structured logs and correlation ids across services.
- Never duplicate auth source-of-truth logic across both backends.

## Environment Variables

Express service:
- DATABASE_URL
- REDIS_URL
- JWT_SECRET_KEY
- AI_SERVICE_BASE_URL
- AI_SERVICE_TOKEN

FastAPI AI service:
- DATABASE_URL
- REDIS_URL
- GROQ_API_KEY
- INTERNAL_SERVICE_TOKEN
- VECTOR_DIMENSION

Frontend:
- VITE_API_URL

## Running the Project

Express core service:
- cd backend-express
- npm install
- npm run dev

FastAPI AI service:
- cd backend-ai
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- uvicorn main:app --reload --port 8001

Frontend:
- cd frontend
- npm install
- npm run dev

## Migration Guidance for Contributors

When implementing backend features:
1. Build new non-AI product endpoints in Express.
2. Keep AI-heavy logic in FastAPI and call it from Express.
3. Maintain backward-compatible contracts during endpoint cutovers.
4. Add or update tests in the owning service before merge.
5. Prefer complete vertical slices over broad scaffolding.

Reference migration plan:
- EXPRESS_FASTAPI_MIGRATION_PLAYBOOK.md

## Current Status

- Legacy FastAPI backend exists and includes hardened auth/security foundations.
- Most non-auth domain endpoints remain placeholder-level in legacy backend.
- Migration path is active: Express for core APIs, FastAPI for AI internals.
- Priority is end-to-end implementation depth, not expansion of placeholder routes.

## AI Architecture (FastAPI Service)

Patterns by endpoint:
- ai explain: direct LLM call
- ai ask: retrieval-augmented generation
- ai troubleshoot: tool-using agent workflow
- ai suggestions: structured recommendation output
- docs and templates generation: async agent workflows with job tracking

Embedding pipeline:
- Content ingestion to chunks
- sentence-transformers embedding generation
- pgvector storage and similarity retrieval

Agent design:
- LangGraph workflows with bounded tool use
- typed tool interfaces
- trace capture for debugging and auditability

## Key Dependencies

Express side:
- express
- typescript
- zod or equivalent validation library
- jsonwebtoken and secure password hashing
- redis client
- postgres driver and ORM/query layer

FastAPI side:
- fastapi and uvicorn
- sqlalchemy and asyncpg
- pydantic and pydantic-settings
- langchain-core and langchain-groq
- langgraph
- sentence-transformers
- redis and celery
- sentry-sdk

Frontend side:
- react
- tanstack query
- zustand
- react-router-dom
- axios
- tailwindcss
- reactflow
- recharts
