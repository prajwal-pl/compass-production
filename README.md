# Compass - AI-Native Internal Developer Portal

Compass is an enterprise-grade Internal Developer Portal (IDP) designed to help engineering teams discover, understand, and manage their services and infrastructure. The platform provides a unified interface for service catalog management, dependency visualization, AI-powered documentation, and deployment tracking.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Features](#core-features)
6. [API Reference](#api-reference)
7. [Installation](#installation)
8. [Configuration](#configuration)
9. [Development](#development)
10. [License](#license)

---

## Overview

Compass addresses the challenges faced by engineering organizations in managing distributed systems at scale. It serves as the central hub for:

- **Service Discovery**: A comprehensive catalog of all microservices with metadata, ownership, and health status.
- **Dependency Management**: Visualization and impact analysis of service dependencies.
- **Documentation**: AI-generated and semantically searchable documentation.
- **Deployment Tracking**: Complete history of deployments with rollback capabilities.
- **Infrastructure Integration**: Native integrations with GitHub, Kubernetes, and other developer tools.

---

## Architecture

The following diagram illustrates the system architecture, including user authentication, service relationships, documentation management, and deployment workflows:

![Architecture Diagram](backend/public/design-file.png)

### Key Architectural Concepts

| Component | Description |
|-----------|-------------|
| **Auth** | JWT-based authentication system supporting standard and Google OAuth authentication |
| **Users** | User entities with role-based access control (owner, staff, superuser) |
| **Services** | Microservice registry with ownership and staff assignments |
| **Docs** | Documentation system with vector embeddings for semantic search via pgvector |
| **Deployments** | Deployment records across environments (staging, preview, production) |

### Access Control Model

- **Owner**: Full administrative access to a service (requires superuser privileges for certain operations)
- **Staff**: Collaborative access to service management and documentation
- **Superuser**: Platform-wide administrative capabilities

---

## Technology Stack

### Backend

| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Runtime environment |
| FastAPI | Web framework for building APIs |
| PostgreSQL | Primary relational database |
| pgvector | Vector similarity search extension for AI features |
| SQLAlchemy | Async ORM for database operations |
| Redis | Caching and message queue |
| Celery | Distributed task queue for background jobs |
| Anthropic Claude API | AI-powered features and documentation generation |

### Frontend

| Technology | Purpose |
|------------|---------|
| React 19 | UI component framework |
| TypeScript | Type-safe JavaScript |
| Vite | Build tool and development server |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Component library |
| TanStack Query | Server state management |
| Zustand | Client state management |
| React Flow | Dependency graph visualization |
| Recharts | Metrics and analytics charts |

---

## Project Structure

```
compass-production/
├── README.md
├── docs/
│   └── architecture-diagram.png
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── api/                    # API route modules
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── services.py         # Service catalog endpoints
│   │   ├── deployments.py      # Deployment management endpoints
│   │   ├── dependencies.py     # Dependency graph endpoints
│   │   ├── docs.py             # Documentation endpoints
│   │   ├── ai.py               # AI assistant endpoints
│   │   ├── integrations.py     # External integration endpoints
│   │   ├── metrics.py          # Metrics and monitoring endpoints
│   │   ├── templates.py        # Golden path template endpoints
│   │   ├── webhooks.py         # Webhook handler endpoints
│   │   └── search.py           # Global search endpoints
│   └── db/                     # Database layer
│       ├── db.py               # SQLAlchemy async connection configuration
│       └── models.py           # Database models and schemas
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx            # React entry point
│       ├── App.tsx             # Root application component
│       ├── components/         # Reusable UI components
│       ├── pages/              # Page-level components
│       ├── hooks/              # Custom React hooks
│       ├── lib/                # Utilities and API client
│       └── assets/             # Static assets
└── .github/
    └── copilot-instructions.md
```

---

## Core Features

### 1. Service Catalog

A centralized registry for all microservices within the organization. Each service entry includes:

- Service metadata (name, description, repository URL)
- Ownership and team assignments
- Health status monitoring
- Technical specifications and configurations

### 2. Golden Path Generator

AI-powered service scaffolding that generates new services from predefined templates, ensuring consistency across the organization and adherence to best practices.

### 3. AI-Powered Documentation

Automatic documentation generation using Claude AI, with semantic search capabilities powered by pgvector for natural language queries.

### 4. AI Assistant

A conversational interface for:

- Troubleshooting service issues
- Querying system state and dependencies
- Generating reports and summaries
- Providing architectural recommendations

### 5. Infrastructure Integration Engine

Native integrations with:

- **GitHub**: Repository synchronization, webhook handling
- **Kubernetes**: Cluster state monitoring, deployment status
- **Additional Providers**: Extensible integration framework

---

## API Reference

The API is organized into the following modules with a total of 54 endpoints:

| Prefix | Module | Endpoints | Description |
|--------|--------|-----------|-------------|
| `/auth` | Authentication | 8 | User registration, login, token management |
| `/services` | Service Catalog | 8 | CRUD operations for services |
| `/deployments` | Deployments | 5 | Deployment history and rollback |
| `/dependencies` | Dependencies | 6 | Dependency graph and impact analysis |
| `/docs` | Documentation | 4 | AI-generated documentation and search |
| `/ai` | AI Assistant | 5 | Conversational AI interface |
| `/integrations` | Integrations | 8 | GitHub and Kubernetes integrations |
| `/metrics` | Metrics | 2 | Service and platform metrics |
| `/templates` | Templates | 4 | Golden path service templates |
| `/webhooks` | Webhooks | 3 | External webhook receivers |
| `/search` | Search | 1 | Global search across all entities |

### API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 15+ with pgvector extension
- Redis 7+

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
# (Migration commands to be configured)

# Start the development server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

---

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/compass

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET=your-secure-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
ANTHROPIC_API_KEY=sk-ant-...

# Integrations
GITHUB_TOKEN=ghp_...
```

Create a `.env` file in the frontend directory:

```bash
VITE_API_URL=http://localhost:8000
```

---

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Backend linting
cd backend
ruff check .

# Frontend linting
cd frontend
npm run lint
```

### Building for Production

```bash
# Frontend production build
cd frontend
npm run build
```

---

## License

This project is proprietary software. All rights reserved.

---

For questions or support, please contact the platform engineering team.
