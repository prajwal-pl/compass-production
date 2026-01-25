# Compass - AI-Native Internal Developer Portal

## Project Overview

Compass is an AI-powered Internal Developer Portal (IDP) designed to help engineering teams discover, understand, and manage their services and infrastructure. It provides a unified platform for service catalog management, dependency visualization, AI-powered documentation, and deployment tracking.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (primary), Neo4j (dependency graphs), Qdrant (vector search), Redis (caching)
- **AI**: Claude API (Anthropic) for AI-powered features
- **Authentication**: JWT-based auth with refresh tokens

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS (preferred)
- **State Management**: React Query for server state

## Project Structure

```
compass-production/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   └── api/                  # API route modules
│       ├── auth.py           # Authentication routes
│       ├── services.py       # Service catalog routes
│       ├── deployments.py    # Deployment management routes
│       ├── dependencies.py   # Dependency graph routes
│       ├── docs.py           # Documentation routes
│       ├── ai.py             # AI assistant routes
│       ├── integrations.py   # GitHub/K8s integration routes
│       ├── metrics.py        # Metrics and monitoring routes
│       ├── templates.py      # Golden path templates routes
│       ├── webhooks.py       # Webhook handlers
│       └── search.py         # Global search routes
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   └── main.tsx         # React entry point
│   ├── package.json
│   └── vite.config.ts
```

## API Route Prefixes

| Prefix | Purpose |
|--------|---------|
| `/auth` | User authentication and account management |
| `/services` | Service catalog CRUD and health monitoring |
| `/deployments` | Deployment history and rollback |
| `/dependencies` | Service dependency graph and impact analysis |
| `/docs` | AI-generated documentation and search |
| `/ai` | AI assistant for troubleshooting and suggestions |
| `/integrations` | GitHub and Kubernetes integrations |
| `/metrics` | Service and platform metrics |
| `/templates` | Golden path service templates |
| `/webhooks` | External webhook receivers |
| `/search` | Global search across all entities |

## Core Systems

1. **Service Catalog**: Central registry of all microservices with metadata, ownership, and health status
2. **Golden Path Generator**: AI-powered service scaffolding from templates
3. **AI-Powered Documentation**: Automatic documentation generation and semantic search
4. **AI Assistant**: Natural language interface for troubleshooting and queries
5. **Infrastructure Integration Engine**: Syncs with GitHub, Kubernetes, and other tools

## Coding Guidelines

### Python/FastAPI
- Use async/await for all route handlers
- Use Pydantic models for request/response validation
- Follow RESTful API conventions
- Include proper error handling with HTTPException
- Use dependency injection for shared resources
- Document endpoints with docstrings for OpenAPI

### TypeScript/React
- Use functional components with hooks
- Prefer TypeScript strict mode
- Use React Query for API calls
- Keep components small and focused
- Use proper TypeScript types, avoid `any`

### General
- All endpoints should return JSON responses
- Use meaningful HTTP status codes
- Include proper CORS configuration for frontend
- Log important operations for debugging
- Write descriptive commit messages

## Environment Variables

```
# Backend
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
NEO4J_URI=bolt://...
QDRANT_URL=http://...
ANTHROPIC_API_KEY=sk-...
JWT_SECRET=...
GITHUB_TOKEN=...

# Frontend
VITE_API_URL=http://localhost:8000
```

## Running the Project

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Current Status

The project is in early development. All API endpoints have stub implementations marked with "WIP" comments that need to be filled in with actual business logic.

## Key Dependencies

### Backend (Python)
- fastapi, uvicorn - Web framework
- sqlalchemy, asyncpg - PostgreSQL ORM
- neo4j - Graph database driver
- qdrant-client - Vector database
- redis, aioredis - Caching
- anthropic - Claude AI SDK
- python-jose, passlib - JWT auth
- httpx - Async HTTP client
- pydantic - Data validation

### Frontend (TypeScript)
- react, react-dom - UI framework
- @tanstack/react-query - Server state
- react-router-dom - Routing
- axios - HTTP client
- tailwindcss - Styling
