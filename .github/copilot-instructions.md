# Compass - AI-Native Internal Developer Portal

## Project Overview

Compass is an AI-powered Internal Developer Portal (IDP) designed to help engineering teams discover, understand, and manage their services and infrastructure. It provides a unified platform for service catalog management, dependency visualization, AI-powered documentation, and deployment tracking.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with pgvector extension (primary + vector search), Redis (caching/queues)
- **AI**: Claude API (Anthropic) for AI-powered features
- **Authentication**: JWT-based auth with refresh tokens
- **Background Jobs**: Celery with Redis broker

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand (client state), TanStack Query (server state)
- **Visualization**: React Flow (dependency graphs), Recharts (metrics)

## Project Structure

```
compass-production/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   ├── api/                  # API route modules
│   │   ├── auth.py           # Authentication routes (8 endpoints)
│   │   ├── services.py       # Service catalog routes (8 endpoints)
│   │   ├── deployments.py    # Deployment management routes (5 endpoints)
│   │   ├── dependencies.py   # Dependency graph routes (6 endpoints)
│   │   ├── docs.py           # Documentation routes (4 endpoints)
│   │   ├── ai.py             # AI assistant routes (5 endpoints)
│   │   ├── integrations.py   # GitHub/K8s integration routes (8 endpoints)
│   │   ├── metrics.py        # Metrics and monitoring routes (2 endpoints)
│   │   ├── templates.py      # Golden path templates routes (4 endpoints)
│   │   ├── webhooks.py       # Webhook handlers (3 endpoints)
│   │   └── search.py         # Global search routes (1 endpoint)
│   └── db/                   # Database layer
│       ├── db.py             # SQLAlchemy async connection setup
│       ├── models.py         # Database models (to be created)
│       └── schemas.py        # Pydantic schemas (to be created)
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   ├── main.tsx         # React entry point
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom React hooks
│   │   └── lib/             # Utilities and API client
│   ├── package.json
│   └── vite.config.ts
└── .github/
    └── copilot-instructions.md  # This file
```

## Database Architecture

### Simplified Approach (PostgreSQL Only)
Using PostgreSQL for everything with extensions:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";  -- For AI semantic search
```

### Why Not Multiple Databases?
- **Neo4j**: PostgreSQL handles dependency graphs with recursive CTEs for <1000 services
- **Qdrant**: pgvector extension provides vector search within PostgreSQL
- **Result**: Simpler architecture, less DevOps overhead

## API Route Prefixes

| Prefix | Purpose | Endpoints |
|--------|---------|-----------|
| `/auth` | User authentication and account management | 8 |
| `/services` | Service catalog CRUD and health monitoring | 8 |
| `/deployments` | Deployment history and rollback | 5 |
| `/dependencies` | Service dependency graph and impact analysis | 6 |
| `/docs` | AI-generated documentation and search | 4 |
| `/ai` | AI assistant for troubleshooting and suggestions | 5 |
| `/integrations` | GitHub and Kubernetes integrations | 8 |
| `/metrics` | Service and platform metrics | 2 |
| `/templates` | Golden path service templates | 4 |
| `/webhooks` | External webhook receivers | 3 |
| `/search` | Global search across all entities | 1 |

**Total: 54 API endpoints**

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
- Use dependency injection for shared resources (get_db, get_current_user)
- Document endpoints with docstrings for OpenAPI

### TypeScript/React
- Use functional components with hooks
- Prefer TypeScript strict mode
- Use TanStack Query for API calls
- Keep components small and focused
- Use proper TypeScript types, avoid `any`

### General
- All endpoints should return JSON responses
- Use meaningful HTTP status codes
- Include proper CORS configuration for frontend
- Log important operations for debugging

## Environment Variables

```bash
# Backend (.env.local)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/compass
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=your-secret-key
GITHUB_TOKEN=ghp_...

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

## Running the Project

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Current Status

- ✅ All API route structures defined (54 endpoints)
- ✅ Router registration in main.py
- ✅ Database connection setup (db/db.py)
- ⏳ Database models and schemas (pending)
- ⏳ Business logic implementation (all routes return WIP responses)
- ⏳ Frontend development (pending)

## Key Dependencies

### Backend (Current)
- fastapi, uvicorn - Web framework
- sqlalchemy, asyncpg - Async PostgreSQL ORM
- pydantic, pydantic-settings - Data validation
- httpx - Async HTTP client
- sentry-sdk - Error tracking

### Backend (To Add)
- anthropic - Claude AI SDK
- redis, celery - Caching and background jobs
- python-jose, passlib - JWT auth
- PyGithub - GitHub integration

### Frontend
- react, @tanstack/react-query, zustand
- react-router-dom, axios
- tailwindcss, reactflow, recharts
