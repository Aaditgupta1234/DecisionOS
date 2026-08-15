# 🧠 DecisionOS

> **Explainable AI Business Diagnosis Platform** — Automated metric decomposition, root-cause identification, and conversational intelligence for executives and business analysts.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-8.x-646CFF?logo=vite&logoColor=white)](https://vite.dev)
[![SQLite/PostgreSQL](https://img.shields.io/badge/Database-SQLite%20%2F%20PostgreSQL-003B57?logo=postgresql&logoColor=white)](https://postgresql.org)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Frontend Views](#-frontend-views)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

Modern business leaders are flooded with static BI dashboards (PowerBI, Tableau) that show **what** happened — but not **why**. When a key metric drops unexpectedly, analysts spend days manually slicing data across dimensions to isolate root causes.

**DecisionOS** bridges the gap between raw data analysis, root-cause decomposition, and natural-language executive communication. It automatically decomposes metric variances into their exact sub-driver contributions and lets executives ask natural-language questions — backed by deterministic statistical calculations, not black-box AI claims.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔬 **Root Cause Engine** | Additive & multiplicative driver breakdown — pinpoints exactly why a KPI changed |
| 📊 **KPI Decomposition** | Automatically breaks top-line metrics (Revenue, Profit) into their sub-drivers |
| 📈 **Variance Analysis** | Period-over-Period (PoP) & Year-over-Year (YoY) waterfall calculations |
| 🤖 **Conversational AI** | Ask "Why did profit drop in Q3?" — get chart-backed, validated answers |
| 🔒 **Explainable AI (XAI)** | Every AI assertion is backed by deterministic statistics — no opaque black box |
| 🏠 **Privacy-First LLM** | Works with local Ollama models; sensitive data never leaves your firewall |
| 📁 **Multi-format Ingestion** | Upload CSV, Excel, JSON, and Parquet datasets |
| 🔐 **RBAC** | Role-based access control: Admin, Analyst, Executive, Viewer |
| 🌐 **REST API** | Fully documented OpenAPI/Swagger interface |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│            Frontend: React + Vite + TypeScript          │
└───────────────────────────┬─────────────────────────────┘
                            │  REST API & WebSockets
┌───────────────────────────▼─────────────────────────────┐
│                   FastAPI Gateway                        │
│         (Auth · RBAC · Validation · Routing)            │
└──────┬─────────────────────────────────────┬────────────┘
       │ Async Query Dispatch                │ Auth & Persistence
┌──────▼───────────┐               ┌─────────▼──────────────┐
│  Analytics Engine │               │  Database Layer         │
│  (Pandas · NumPy) │               │  (SQLite / PostgreSQL)  │
└──────┬────────────┘               │  (SQLAlchemy · Alembic) │
       │ Statistical Insights       └────────────────────────┘
┌──────▼────────────────────────────────────┐
│  LLM Layer (Ollama / Local / Cloud LLM)  │
│  Context Injection · Guardrails · Chat   │
└───────────────────────────────────────────┘
```

See [`docs/architecture.md`](docs/architecture.md) for the full specification.

---

## 🛠 Tech Stack

### Backend
| Layer | Technology |
|---|---|
| API Framework | FastAPI >= 0.110 |
| Runtime | Python 3.10+ |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Data Processing | Pandas >= 2.0 |
| Auth | python-jose (JWT) · passlib (Bcrypt) |
| Validation | Pydantic v2 |
| Server | Uvicorn |
| Testing | Pytest · HTTPX |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 19 |
| Language | TypeScript 6 |
| Build Tool | Vite 8 |
| Routing | React Router v7 |
| Icons | Lucide React |
| Testing | Vitest · Testing Library |

---

## 📂 Project Structure

```
DecisionOS/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── ai_chat/            # Conversational AI / Chat module
│   │   ├── ai_insights/        # AI-generated insights
│   │   ├── analytics/          # KPI decomposition & variance engine
│   │   ├── api/v1/             # REST API versioned routes
│   │   ├── core/               # Config, logging, constants
│   │   ├── database/           # DB session & connection
│   │   ├── diagnostics/        # Business diagnostics module
│   │   ├── forecasting/        # Time-series forecasting
│   │   ├── intelligence/       # Intelligence aggregation
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── recommendations/    # Actionable recommendations engine
│   │   ├── repositories/       # Data access layer
│   │   ├── root_cause/         # Root cause analysis engine
│   │   ├── scenario_simulation/# What-if scenario engine
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic & LLM services
│   │   ├── strategy_planner/   # Strategic planning module
│   │   └── utils/              # Shared utilities
│   ├── alembic/                # Database migration scripts
│   ├── tests/                  # Backend test suite
│   ├── uploads/                # Uploaded dataset storage
│   ├── main.py                 # Uvicorn entrypoint
│   ├── requirements.txt        # Python dependencies
│   ├── seed_admin.py           # Admin user seeding script
│   └── seed_metrics.py         # Sample metrics seeding script
│
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── api/                # API client layer
│   │   ├── components/         # Reusable UI components
│   │   ├── context/            # React context providers
│   │   ├── services/           # Frontend service layer
│   │   ├── styles/             # Global styles
│   │   ├── types/              # TypeScript type definitions
│   │   └── views/              # Page-level view components
│   │       ├── dashboard/      # Executive dashboard
│   │       ├── datasets/       # Dataset management
│   │       ├── metrics/        # KPI & metrics explorer
│   │       ├── diagnostics/    # Business diagnostics
│   │       ├── rootCauses/     # Root cause analysis
│   │       ├── aiInsights/     # AI-generated insights
│   │       ├── chat/           # Conversational AI chat
│   │       ├── forecasts/      # Forecasting views
│   │       ├── recommendations/# Recommendations view
│   │       ├── reports/        # Report generation
│   │       ├── scenarios/      # Scenario simulation
│   │       ├── strategy/       # Strategy planner
│   │       └── settings/       # App settings
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                       # Project documentation
│   ├── architecture.md         # System architecture specification
│   ├── decisionos-design.md    # Product design & USP
│   └── roadmap.md              # 10-phase product roadmap
│
└── datasets/                   # Sample / reference datasets
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10 or higher
- **Node.js** 18 or higher & **npm**
- **PostgreSQL** (optional for development — SQLite is used by default)
- **Ollama** (optional — for local LLM features)

---

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env .env.local   # Windows — then edit .env.local with your values

# 5. Run database migrations
alembic upgrade head

# 6. (Optional) Seed admin user and sample metrics
python seed_admin.py
python seed_metrics.py

# 7. Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Base URL**: `http://localhost:8000`
- **Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

---

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

**Other available scripts:**

```bash
npm run build     # Build for production
npm run preview   # Preview production build
npm run lint      # Run ESLint
npm run test      # Run Vitest unit tests
```

---

## 🔧 Environment Variables

The backend is configured via `backend/.env`. Key variables:

| Variable | Default | Description |
|---|---|---|
| `PROJECT_NAME` | `"DecisionOS API"` | Application name shown in API docs |
| `VERSION` | `"1.0.0"` | API version |
| `ENVIRONMENT` | `"development"` | Runtime environment |
| `DATABASE_URL` | SQLite (local) | PostgreSQL or SQLite connection string |
| `SECRET_KEY` | *(change in production)* | JWT signing secret |
| `JWT_ALGORITHM` | `"HS256"` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `115200` | Token expiry (~80 days) |
| `OLLAMA_URL` | `"http://localhost:11434"` | Local Ollama LLM endpoint |

> ⚠️ **Never commit your `.env` file to version control.** Always change `SECRET_KEY` before deploying to production.

---

## 📡 API Reference

All API endpoints are versioned under `/api/v1`. Full interactive documentation is available at `/docs` when the server is running.

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Root status & service info |
| `/health` | GET | Top-level health check |
| `/api/v1/health` | GET | Versioned health check |
| `/api/v1/auth/...` | POST | Authentication & token management |
| `/api/v1/datasets/...` | GET/POST | Dataset upload & management |
| `/api/v1/metrics/...` | GET/POST | KPI & metric definitions |
| `/api/v1/analytics/...` | POST | Variance & decomposition analysis |
| `/api/v1/root-cause/...` | POST | Root cause analysis |
| `/api/v1/chat/...` | POST/WS | Conversational AI interface |
| `/api/v1/recommendations/...` | GET | Actionable recommendations |
| `/api/v1/forecasts/...` | POST | Time-series forecasting |
| `/api/v1/reports/...` | GET/POST | Report generation & export |

---

## 🖥 Frontend Views

| View | Description |
|---|---|
| **Dashboard** | Executive KPI overview & summary |
| **Datasets** | Upload & manage business datasets |
| **Metrics** | KPI tree & metric definitions |
| **Diagnostics** | Business health diagnostics |
| **Root Causes** | Drill-down root cause analysis |
| **AI Insights** | AI-generated business insights |
| **Chat** | Conversational business assistant |
| **Forecasts** | Metric forecasting & trends |
| **Recommendations** | Prioritized corrective actions |
| **Reports** | Generate & export reports |
| **Scenarios** | What-if scenario simulation |
| **Strategy** | Strategic planning workspace |
| **Settings** | Application configuration |

---

## 🗺 Roadmap

DecisionOS is built through **10 sequential phases**:

| Phase | Status | Description |
|---|---|---|
| Phase 1 | ✅ Done | Architecture, documentation & API scaffolding |
| Phase 2 | 🔄 In Progress | Authentication & RBAC (JWT + Bcrypt) |
| Phase 3 | 🔄 In Progress | Database layer & Alembic migrations |
| Phase 4 | 📋 Planned | Dataset ingestion & validation engine |
| Phase 5 | 📋 Planned | KPI engine & metric modeling |
| Phase 6 | 📋 Planned | Root cause & variance analysis engine |
| Phase 7 | 📋 Planned | AI recommendation & report generation |
| Phase 8 | 📋 Planned | Conversational business chat (Text-to-Insight) |
| Phase 9 | 📋 Planned | Interactive frontend dashboard & visualization |
| Phase 10 | 📋 Planned | Production hardening, security & deployment |

See [`docs/roadmap.md`](docs/roadmap.md) for the full phase-by-phase breakdown.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Commit** your changes: `git commit -m 'feat: add your feature'`
4. **Push** to the branch: `git push origin feature/your-feature-name`
5. **Open** a Pull Request

Please ensure:
- Backend code follows PEP 8 style guidelines
- New API endpoints include Pydantic schemas and docstrings
- Frontend components use TypeScript with proper type definitions
- Tests are added for new features

---

## 📄 License

This project is currently **proprietary**. All rights reserved.

---

<p align="center">
  Built with ❤️ by the DecisionOS Team &nbsp;|&nbsp; Empowering data-driven decisions
</p>
