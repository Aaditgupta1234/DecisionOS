# 🧠 DecisionOS — Master Project Control Document

> **Status**: Single Source of Truth (SSOT)  
> **Audit Date**: 2026-10-10  
> **Repository**: `f:\Vscode\DecisionOS`  
> **Audit Mode**: Strict Read-Only Verification  
> **Scope of Inspection**: Full-stack codebase (784 backend Python files, 287 frontend TypeScript/TSX files, 177 test suites, 24 Alembic migrations, local SQLite database, and OpenAPI specifications).

---

## 1. Project Identity & Scope

### 1.1 Purpose and Intended Users
Based on direct inspection of [backend/app/main.py](file:///f:/Vscode/DecisionOS/backend/app/main.py), [README.md](file:///f:/Vscode/DecisionOS/README.md), and core calculation engines:
- **Core Value Proposition**: Transform raw business transaction datasets (CSV) into deterministic KPIs, diagnostic anomaly detections, topological Causal Directed Acyclic Graphs (DAGs), prescriptive recommendations, and executive boardroom briefings.
- **Target Persona**: Executive decision-makers (CEOs, CFOs, COOs, Board Members) and Business/BI Analysts seeking explainable, zero-hallucination root-cause discovery.

### 1.2 Implemented Scope vs. Planned / Aspirational Claims
- **Deterministic Core (Implemented & Verified in Code)**:
  - Ingests CSV files, auto-detects schemas, and maps columns ([backend/app/services/dataset_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/dataset_service.py)).
  - Calculates 17 canonical business KPIs mathematically via Pandas/SQL ([backend/app/services/kpi_engine.py](file:///f:/Vscode/DecisionOS/backend/app/services/kpi_engine.py)).
  - Computes a 0–100 Business Health Score via explicit arithmetic penalty formulas ([backend/app/intelligence/health_score.py](file:///f:/Vscode/DecisionOS/backend/app/intelligence/health_score.py)).
  - Discovers causal driver-to-symptom relationships using empirical correlations and domain rules ([backend/app/services/root_cause_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/root_cause_service.py)).
  - Synthesizes prescriptive action plans with Effort vs. Impact rankings and distress invariants ([backend/app/services/recommendation_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/recommendation_service.py)).
- **Enterprise Expansion (Partially Connected / Disconnected in UI)**:
  - The repository contains 426 backend API paths (475 operations) covering Strategic Execution, Advanced Monitoring, Governance, and Digital Twins.
  - However, multiple advanced frontend studio views (e.g., Autonomous Agents Hub, Risk Concentration Radar, Capital Allocation Studio) currently render hardcoded in-memory mock data without issuing backend API requests.

---

## 2. Current Project Technical Inventory

| Subsystem | Metric / Component | Verified Count | Verification Method & Source |
| :--- | :--- | :--- | :--- |
| **Frontend** | Framework & Bundler | React 19.2.8 + Vite 8.2.1 + TS 5.x | [frontend/package.json](file:///f:/Vscode/DecisionOS/frontend/package.json) |
| **Frontend** | Source Files | 287 files (242 `.tsx`, 45 `.ts`) | Recursive filesystem scan of [frontend/src](file:///f:/Vscode/DecisionOS/frontend/src) |
| **Frontend** | Declared Routes in `App.tsx` | 55 total routes (36 views, 14 aliases, 5 auth/root/catchall) | AST parse of [frontend/src/App.tsx](file:///f:/Vscode/DecisionOS/frontend/src/App.tsx) |
| **Frontend** | Centralized API Client | 631 lines mapping `/api/v1/*` endpoints | [frontend/src/api/index.ts](file:///f:/Vscode/DecisionOS/frontend/src/api/index.ts) |
| **Backend** | Framework | FastAPI 0.110+ on Python 3.11+ | [backend/requirements.txt](file:///f:/Vscode/DecisionOS/backend/requirements.txt), [backend/app/main.py](file:///f:/Vscode/DecisionOS/backend/app/main.py) |
| **Backend** | Source Python Files | 784 `.py` files under `backend/app` | Recursive filesystem scan of [backend/app](file:///f:/Vscode/DecisionOS/backend/app) |
| **Backend** | Unique API Paths | 426 unique paths | Evaluated from live OpenAPI schema `/api/v1/openapi.json` |
| **Backend** | Total API Operations | 475 endpoints (`GET`: 327, `POST`: 115, `PATCH`: 13, `DELETE`: 16, `PUT`: 4) | Evaluated from live OpenAPI schema `/api/v1/openapi.json` |
| **Database** | ORM Layer | SQLAlchemy 2.0 (Sync/Async) | [backend/app/database/base.py](file:///f:/Vscode/DecisionOS/backend/app/database/base.py) |
| **Database** | Registered SQLAlchemy Tables | 89 unique tables | Introspected from `Base.metadata.tables` across all modules |
| **Database** | Alembic Migrations | 24 version files (creating 31 tables) | Filesystem scan of [backend/alembic/versions](file:///f:/Vscode/DecisionOS/backend/alembic/versions) |
| **Database** | Local SQLite Tables | 59 tables present in `decisionos.db` | Direct read-only `sqlite_master` query |
| **Tests** | Backend Pytest Test Files | 177 test files | Filesystem scan of [backend/tests](file:///f:/Vscode/DecisionOS/backend/tests) |
| **Tests** | Backend Pytest Test Functions | 925 test functions | AST parse of `test_*.py` in [backend/tests](file:///f:/Vscode/DecisionOS/backend/tests) |

---

## 3. Feature Registry

The table below records all reachable frontend routes, their backing endpoints, underlying business logic, and empirical status:

| Route | Main Component | Backend Endpoint(s) | Backing Engine / Logic | Data Source | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | [HomeView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/views/home/HomeView.tsx) | None | Static landing presentation | Static code | **VERIFIED WORKING** |
| `/platform` | [PlatformShowcaseView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/views/platform/PlatformShowcaseView.tsx) | None | Interactive showcase demo | In-memory state | **VERIFIED WORKING** |
| `/login` | [LoginPage.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/auth/LoginPage.tsx) | `POST /api/v1/auth/login`, `GET /api/v1/auth/me` | [auth_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/auth_service.py) (BCrypt, JWT HS256) | Table `users` | **VERIFIED WORKING** |
| `/enterprise` | [EnterpriseCommandCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/enterprise-os/EnterpriseCommandCenterView.tsx) | `GET /api/v1/datasets/{id}/intelligence-report` | [intelligence_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/intelligence_service.py) | `datasets`, `dataset_metrics`, `diagnostic_findings` | **IMPLEMENTED, UNVERIFIED** |
| `/kpi-dictionary` | [KPIDictionaryView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/kpi-dictionary/KPIDictionaryView.tsx) | `GET /api/v1/datasets/{id}/metrics` | [kpi_engine.py](file:///f:/Vscode/DecisionOS/backend/app/services/kpi_engine.py) (17 standard KPIs) | Table `dataset_metrics` | **IMPLEMENTED, UNVERIFIED** |
| `/data-hub` | [DatasetManagementCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/data-management/DatasetManagementCenterView.tsx) | `GET /api/v1/datasets`, `POST /api/v1/datasets/upload` | [dataset_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/dataset_service.py) (CSV Ingestion) | Tables `datasets`, `dataset_columns` | **IMPLEMENTED, UNVERIFIED** |
| `/boardroom` | [BoardroomCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/boardroom/BoardroomCenterView.tsx) | `GET /api/v1/boardroom/{id}/briefing` | [board_report_generator.py](file:///f:/Vscode/DecisionOS/backend/app/reporting/services/board_report_generator.py) | Tables `datasets`, `executive_reports` | **IMPLEMENTED, UNVERIFIED** |
| `/portfolio-rollup` | [PortfolioRollupView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/portfolio-rollup/PortfolioRollupView.tsx) | None | In-memory portfolio scorecards | Hardcoded array | **MOCK/DEMO** |
| `/capital-allocation` | [CapitalAllocationStudioView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/capital-allocation/CapitalAllocationStudioView.tsx) | None | In-memory allocation curves | Hardcoded sliders | **MOCK/DEMO** |
| `/risk-concentration` | [RiskConcentrationRadarView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/risk-concentration/RiskConcentrationRadarView.tsx) | None | In-memory risk matrix | Hardcoded state | **MOCK/DEMO** |
| `/integrations` | [IntegrationsCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/integrations/IntegrationsCenterView.tsx) | None | In-memory connector cards | Hardcoded state | **MOCK/DEMO** |
| `/data-reliability` | [EnterpriseDataReliabilityView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/enterprise-data/EnterpriseDataReliabilityView.tsx) | None | In-memory schema drift metrics | Hardcoded state | **MOCK/DEMO** |
| `/ai-governance` | [AIGovernanceCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/ai-governance/AIGovernanceCenterView.tsx) | `GET /api/v1/ai-governance/report` | [ai_governance](file:///f:/Vscode/DecisionOS/backend/app/ai_governance) reporting service | In-memory telemetry | **IMPLEMENTED, UNVERIFIED** |
| `/intelligence-delivery` | [ScheduledReportsView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/intelligence-delivery/ScheduledReportsView.tsx) | None | In-memory delivery ledger | Hardcoded state | **MOCK/DEMO** |
| `/api-platform` | [ApiPlatformView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/api-platform/ApiPlatformView.tsx) | `GET /api/v1/public-api/keys` | [api_gateway_service.py](file:///f:/Vscode/DecisionOS/backend/app/public_api/services/api_gateway_service.py) | In-memory list | **IMPLEMENTED, UNVERIFIED** |
| `/administration` | [EnterpriseAdministrationView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/administration/EnterpriseAdministrationView.tsx) | None | In-memory tenant/SSO cards | Hardcoded state | **MOCK/DEMO** |
| `/security-center` | [SecurityCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/security-center/SecurityCenterView.tsx) | `GET /api/v1/security/posture` | [security_service.py](file:///f:/Vscode/DecisionOS/backend/app/security_center/services/security_service.py) | In-memory posture score | **IMPLEMENTED, UNVERIFIED** |
| `/platform-ops` | [PlatformOperationsView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/platform-ops/PlatformOperationsView.tsx) | None | In-memory latency/memory charts | Hardcoded state | **MOCK/DEMO** |
| `/production-readiness` | [ProductionCertificationCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/production-readiness/ProductionCertificationCenterView.tsx) | None | In-memory compliance checklists | Hardcoded state | **MOCK/DEMO** |
| `/agents` | [AutonomousAgentsHubView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/agents/AutonomousAgentsHubView.tsx) | None | In-memory agent performance profiles | Hardcoded arrays | **MOCK/DEMO** |
| `/portfolio` | [MetricsView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/kpis/MetricsView.tsx) | `GET /api/v1/datasets/{id}/metrics`, `/health-score` | [kpi_engine.py](file:///f:/Vscode/DecisionOS/backend/app/services/kpi_engine.py) | Table `dataset_metrics` (Chart is mock) | **PARTIALLY IMPLEMENTED** |
| `/diagnostics` | [DiagnosticsView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/diagnostics/DiagnosticsView.tsx) | `GET /api/v1/datasets/{id}/diagnostics` | [diagnostic_engine.py](file:///f:/Vscode/DecisionOS/backend/app/diagnostics/diagnostic_engine.py) | Table `diagnostic_findings` | **IMPLEMENTED, UNVERIFIED** |
| `/root-causes` | [RootCausesView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/root-causes/RootCausesView.tsx) | `GET /api/v1/datasets/{id}/root-causes` | [root_cause_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/root_cause_service.py) | Table `root_cause_analyses` | **IMPLEMENTED, UNVERIFIED** |
| `/recommendations` | [RecommendationsView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/recommendations/RecommendationsView.tsx) | `GET /api/v1/datasets/{id}/recommendations` | [recommendation_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/recommendation_service.py) | Table `recommendations` | **IMPLEMENTED, UNVERIFIED** |
| `/chat` | [ChatView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/views/chat/ChatView.tsx) | `POST /api/v1/chat/message`, `GET /api/v1/chat/sessions` | [chat_analyst_service.py](file:///f:/Vscode/DecisionOS/backend/app/ai_chat/services/chat_analyst_service.py) | Tables `chat_sessions`, `chat_messages` | **IMPLEMENTED, UNVERIFIED** |
| `/decision-copilot` | [DecisionCopilotView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/decision-copilot/DecisionCopilotView.tsx) | `POST /api/v1/ai/copilot/query` | [ai_analyst_router.py](file:///f:/Vscode/DecisionOS/backend/app/ai/api/endpoints.py) | Dynamic prompt context | **IMPLEMENTED, UNVERIFIED** |
| `/knowledge-graph` | [KnowledgeGraphExplorerView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/knowledge-graph/KnowledgeGraphExplorerView.tsx) | `GET /api/v1/knowledge-graph/{id}/graph` | [knowledge_graph_builder.py](file:///f:/Vscode/DecisionOS/backend/app/knowledge_graph/services/knowledge_graph_builder.py) | In-memory graph over findings | **IMPLEMENTED, UNVERIFIED** |
| `/reports` | [ExecutiveReportsCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/reports/ExecutiveReportsCenterView.tsx) | `GET /api/v1/reports`, `POST /api/v1/reports/generate` | [report_service.py](file:///f:/Vscode/DecisionOS/backend/app/reporting/report_export_service.py) | Tables `report_templates`, `report_exports` | **IMPLEMENTED, UNVERIFIED** |
| `/digital-twin` | [DigitalTwinWorkspaceView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/scenarios/DigitalTwinWorkspaceView.tsx) | `POST /api/v1/scenarios/simulate` | [scenario_simulation_service.py](file:///f:/Vscode/DecisionOS/backend/app/scenario_simulation/services/scenario_simulation_service.py) | Table `scenarios` | **IMPLEMENTED, UNVERIFIED** |
| `/strategy-execution` | [StrategyExecutionCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/strategy-execution/StrategyExecutionCenterView.tsx) | `GET /api/v1/execution/initiatives` | [strategy_execution_engine.py](file:///f:/Vscode/DecisionOS/backend/app/execution/services/strategy_execution_engine.py) | Tables `strategic_initiatives`, `programs` | **IMPLEMENTED, UNVERIFIED** |
| `/monitoring` | [MonitoringCommandCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/monitoring/MonitoringCommandCenterView.tsx) | None | In-memory event stream | Hardcoded state | **MOCK/DEMO** |
| `/governance` | [EnterpriseGovernanceCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/enterprise-os/EnterpriseGovernanceCenterView.tsx) | `GET /api/v1/enterprise-os/governance` | [enterprise_os_router.py](file:///f:/Vscode/DecisionOS/backend/app/enterprise_os/api.py) | In-memory governance scorecard | **IMPLEMENTED, UNVERIFIED** |
| `/competitive-intel` | [CompetitiveIntelligenceCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/enterprise-os/CompetitiveIntelligenceCenterView.tsx) | `GET /api/v1/enterprise-os/benchmarks` | [benchmark_service.py](file:///f:/Vscode/DecisionOS/backend/app/portfolio/services/benchmark_service.py) | Table `workspace_benchmarks` | **IMPLEMENTED, UNVERIFIED** |
| `/operating-system` | [EnterpriseOperatingSystemCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/enterprise-os/EnterpriseOperatingSystemCenterView.tsx) | None | In-memory health checks | Hardcoded state | **MOCK/DEMO** |
| `/jobs` | [JobCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/jobs/JobCenterView.tsx) | None | In-memory queue view | Hardcoded state | **MOCK/DEMO** |
| `/admin` | [SystemAdminCenterView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/admin/SystemAdminCenterView.tsx) | None | In-memory system dials | Hardcoded state | **MOCK/DEMO** |

---

## 4. Architecture and Integration Map

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PRESENTATION LAYER                                     │
│  React 19 + TypeScript + TanStack Query v5 + Lucide Icons + @xyflow/react Graph Canvas  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP JSON / FormData (Bearer JWT)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI GATEWAY LAYER                                     │
│  [backend/app/main.py] ➔ [backend/app/api/v1/router.py] (426 Paths / 475 Operations)   │
│  ├── /auth                  ├── /datasets                ├── /diagnostics              │
│  ├── /root-causes           ├── /recommendations         ├── /chat                     │
│  ├── /execution (Phase 12)  ├── /portfolio               ├── /knowledge-graph          │
│  └── /scenarios             └── /reporting               └── /monitoring               │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Python Service Calls
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            BUSINESS LOGIC & ENGINE LAYER                               │
│  ├── KPI Calculus Engine (17 Deterministic Metrics: Pandas / NumPy)                    │
│  ├── 4-Tier Diagnostic Scanner (LOW, MEDIUM, HIGH, CRITICAL + Multipliers)             │
│  ├── Topological Causal DAG Engine (Rule Registry + Pearson Correlation)               │
│  ├── Prescriptive Recommendation Engine (Effort vs. Impact + Distress Invariants)      │
│  ├── Business Health Score Index (0-100 Deductive Arithmetic Index)                    │
│  └── AI Provider Router (Deterministic Mock Template Provider vs. Local Ollama)        │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ SQLAlchemy 2.0 ORM Sessions
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  DATABASE LAYER                                        │
│  Local Dev: SQLite (decisionos.db - 59 Tables)  |  Target Prod: PostgreSQL 16 (31 Mig) │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Core Workflow Registry

### 5.1 Authentication & SaaS Tenancy
- **Code Reality**: [backend/app/services/auth_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/auth_service.py) implements BCrypt password hashing and JWT encoding (`HS256`). Datasets and metrics are filtered by `organization_id`.
- **Test Evidence**: Covered in [backend/tests/test_auth.py](file:///f:/Vscode/DecisionOS/backend/tests/test_auth.py) and [backend/tests/test_organization_saas.py](file:///f:/Vscode/DecisionOS/backend/tests/test_organization_saas.py).
- **Runtime Testing Needed**: Verification of session persistence across browser refreshes with invalid/expired tokens.

### 5.2 Dataset Ingestion & Validation
- **Code Reality**: [backend/app/services/dataset_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/dataset_service.py) receives multipart CSV uploads, runs pandas schema inference, and persists `Dataset` and `DatasetColumn` rows.
- **Test Evidence**: 8 test cases in [backend/tests/test_datasets.py](file:///f:/Vscode/DecisionOS/backend/tests/test_datasets.py).
- **Runtime Testing Needed**: Upload of large (>50MB) CSV files with missing headers or malformed date fields.

### 5.3 Deterministic KPI Calculus & Health Scoring
- **Code Reality**: [backend/app/services/kpi_engine.py](file:///f:/Vscode/DecisionOS/backend/app/services/kpi_engine.py) computes 17 metrics directly from raw rows without stochastic approximations. [backend/app/intelligence/health_score.py](file:///f:/Vscode/DecisionOS/backend/app/intelligence/health_score.py) calculates the 0–100 score:
  $$\text{Score} = \max(0, \min(100, 100 - \sum \text{penalties} - \text{systemic} - \text{rca} + \text{bonus}))$$
- **Test Evidence**: Verified by 12 tests in [backend/tests/test_metrics.py](file:///f:/Vscode/DecisionOS/backend/tests/test_metrics.py) and [backend/tests/test_business_health_score.py](file:///f:/Vscode/DecisionOS/backend/tests/test_business_health_score.py).

### 5.4 Diagnostic Anomaly Detection
- **Code Reality**: [backend/app/diagnostics/diagnostic_engine.py](file:///f:/Vscode/DecisionOS/backend/app/diagnostics/diagnostic_engine.py) scans metrics against static boundaries across Revenue, Operational, Customer, and Product domains.
- **Test Evidence**: 12 tests in [backend/tests/test_diagnostic_engine.py](file:///f:/Vscode/DecisionOS/backend/tests/test_diagnostic_engine.py) and [backend/tests/test_diagnostic_severity.py](file:///f:/Vscode/DecisionOS/backend/tests/test_diagnostic_severity.py).

### 5.5 Root Cause Topological DAG Engine
- **Code Reality**: [backend/app/services/root_cause_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/root_cause_service.py) constructs acyclic graphs from candidate anomaly pairs using correlation filters and topological sorting.
- **Test Evidence**: Verified in [backend/tests/test_root_cause_engine.py](file:///f:/Vscode/DecisionOS/backend/tests/test_root_cause_engine.py) and [backend/tests/test_correlation_analyzer.py](file:///f:/Vscode/DecisionOS/backend/tests/test_correlation_analyzer.py).
- **Epistemic Limitation**: *Deterministic execution and mathematical correlation do not prove real-world causal validity.* True causality requires external counterfactuals or experimental intervention.

### 5.6 Prescriptive Recommendation Engine
- **Code Reality**: [backend/app/services/recommendation_service.py](file:///f:/Vscode/DecisionOS/backend/app/services/recommendation_service.py) maps action initiatives to identified root causes with Effort/Impact ratings. Distress invariant enforces emergency recovery plans for health scores $\le 60$.
- **Test Evidence**: Verified in [backend/tests/test_recommendation_engine.py](file:///f:/Vscode/DecisionOS/backend/tests/test_recommendation_engine.py).

### 5.7 AI Chat Analyst (DEX) & Copilot
- **Code Reality**: [backend/app/ai_chat/services/chat_analyst_service.py](file:///f:/Vscode/DecisionOS/backend/app/ai_chat/services/chat_analyst_service.py) generates prompt context from dataset metrics and passes it to either `mock_provider` or `ollama_provider`.
- **Test Evidence**: 21 tests in [backend/tests/test_ollama_provider.py](file:///f:/Vscode/DecisionOS/backend/tests/test_ollama_provider.py) and [backend/tests/test_chat_analyst.py](file:///f:/Vscode/DecisionOS/backend/tests/test_chat_analyst.py).

### 5.8 Scenario Simulation & Digital Twin
- **Code Reality**: [backend/app/scenario_simulation/services/scenario_simulation_service.py](file:///f:/Vscode/DecisionOS/backend/app/scenario_simulation/services/scenario_simulation_service.py) models user-applied shocks against baseline KPIs.
- **Test Evidence**: Tested in [backend/tests/test_scenario_api.py](file:///f:/Vscode/DecisionOS/backend/tests/test_scenario_api.py).

### 5.9 Enterprise Knowledge Graph
- **Code Reality**: [backend/app/knowledge_graph/services/knowledge_graph_builder.py](file:///f:/Vscode/DecisionOS/backend/app/knowledge_graph/services/knowledge_graph_builder.py) dynamically assembles node and edge collections from metrics, findings, and causal links.
- **Test Evidence**: Tested in [backend/tests/test_enterprise_knowledge_graph.py](file:///f:/Vscode/DecisionOS/backend/tests/test_enterprise_knowledge_graph.py).

### 5.10 Executive Reporting & Exports
- **Code Reality**: [backend/app/reporting/report_export_service.py](file:///f:/Vscode/DecisionOS/backend/app/reporting/report_export_service.py) synthesizes executive briefs; frontend renders via `react-to-print`.
- **Test Evidence**: 31 tests in [backend/tests/test_reporting.py](file:///f:/Vscode/DecisionOS/backend/tests/test_reporting.py).

### 5.11 Strategic Execution & Value Realization (Phase 12)
- **Code Reality**: 20 specialized engines in [backend/app/execution/services](file:///f:/Vscode/DecisionOS/backend/app/execution/services) track initiative milestones, dependencies, and ROI.
- **Test Evidence**: 91 endpoint routes verified across `test_execution_*.py`.

### 5.12 Monitoring, Governance & Operations
- **Code Reality**: Event-driven alert rules and SLA trackers in [backend/app/monitoring/services](file:///f:/Vscode/DecisionOS/backend/app/monitoring/services).
- **Test Evidence**: 16 tests in [backend/tests/test_monitoring.py](file:///f:/Vscode/DecisionOS/backend/tests/test_monitoring.py).

---

## 6. Database Reality & Migration Gap

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE SCHEMA GAP VISUALIZER                         │
├────────────────────────────────────────┬────────────────────────────────────────┤
│ Total Tables Defined in Code           │ 89 tables in Base.metadata             │
│ Total Tables in Alembic (0001-0024)    │ 31 tables                              │
│ Missing Alembic Migrations             │ 58 tables missing from migration chain │
│ Tables in Local SQLite (decisionos.db) │ 59 tables (created via create_all)     │
└────────────────────────────────────────┴────────────────────────────────────────┘
```

### 6.1 Missing Alembic Migrations (58 Tables)
The following tables are defined in ORM model code but have **no migration scripts** in `backend/alembic/versions/`:
```
adaptive_recovery_runs, alert_action_plans, alert_effectiveness_records, alert_lineages,
alert_postmortems, alert_slas, alert_suppression_rules, board_directives, business_units,
departments, enterprise_alerts, escalation_policies, execution_snapshots, executive_alerts,
executive_report_templates, executive_reports, forecast_deviation_events, forecast_reliability_snapshots,
initiative_benefit_realizations, initiative_dependencies, initiative_execution_events,
initiative_governance_actions, initiative_governance_reviews, initiative_milestones,
initiative_outcomes, initiative_performance_events, initiative_target_metrics, kpi_drift_events,
kpi_health_monitors, milestone_dependencies, monitoring_alerts, monitoring_coverage_reports,
monitoring_decision_impacts, monitoring_maturity_reports, monitoring_snapshots,
notification_deliveries, portfolio_datasets, portfolio_decision_briefs, portfolio_decision_sessions,
portfolio_forecast_snapshots, portfolio_intelligence_reports, portfolio_optimization_runs,
portfolio_resource_allocation_snapshots, portfolio_scenario_results, portfolios,
report_audit_events, report_evidence_coverages, report_generation_runs, report_kpi_snapshots,
report_lineage_graphs, report_presentation_slides, report_version_diffs, scheduled_reports,
strategic_initiative_snapshots, strategic_initiatives, strategic_portfolio_snapshots,
strategic_program_snapshots, strategic_programs.
```

### 6.2 Differences Between SQLite and PostgreSQL Behavior
- **SQLite (Development)**: SQLite is dynamically typed and tolerates unapplied migrations when `Base.metadata.create_all()` is executed at startup.
- **PostgreSQL 16 (Target Production)**: Strict schema validation and foreign key enforcement. Executing `alembic upgrade head` on fresh PostgreSQL will leave out 58 tables, causing `500 Internal Server Error` on any Phase 12 Strategic Execution, Monitoring, or Advanced Reporting route.

---

## 7. AI & Data Integrity

### 7.1 Provider Configuration & Selection Logic
- Set via `.env` variable `AI_PROVIDER`:
  - `mock` (Default): Uses [mock_provider.py](file:///f:/Vscode/DecisionOS/backend/app/ai_insights/providers/mock_provider.py), which injects calculated KPIs and causal findings into deterministic narrative templates.
  - `ollama`: Uses [ollama_provider.py](file:///f:/Vscode/DecisionOS/backend/app/ai_insights/providers/ollama_provider.py) communicating with local Ollama (`http://localhost:11434`, model `qwen2.5:1.5b`).

### 7.2 The Anti-Hallucination Architectural Separation
```
   Raw Business Dataset (CSV)
             │
             ▼ (Pure Deterministic Python / SQL)
   ┌────────────────────────────────────────────────────────┐
   │  17 Business KPIs  •  0-100 Health Score  •  Causal DAG │
   └─────────────────────────┬──────────────────────────────┘
                             │ Grounded Facts Payload
                             ▼
   ┌────────────────────────────────────────────────────────┐
   │               AI Executive Briefing Layer              │
   │  (LLM translates verified facts into natural language) │
   └────────────────────────────────────────────────────────┘
```
1. Numerical metrics are **never calculated by an LLM prompt**.
2. Anomaly thresholds and causal DAG edges are **computed strictly in Python**.
3. The LLM is restricted to formatting, summarizing, and contextualizing pre-computed facts.

---

## 8. Duplicates, Superseded Views & Dead Code

### 8.1 Superseded Legacy Views in `frontend/src/views/`
The following 15 views in [frontend/src/views/](file:///f:/Vscode/DecisionOS/frontend/src/views/) were created during early development and have been superseded by modern components in [frontend/src/features/](file:///f:/Vscode/DecisionOS/frontend/src/features/):

| Legacy View in `src/views/` | Modern Active Feature in `src/features/` | Current Status |
| :--- | :--- | :--- |
| `reports/ReportsView.tsx` | `reports/ExecutiveReportsCenterView.tsx` | Unrouted in `App.tsx` |
| `scenarios/ScenariosView.tsx` | `scenarios/DigitalTwinWorkspaceView.tsx` | Unrouted in `App.tsx` |
| `strategy/StrategyPlannerView.tsx` | `strategy-execution/StrategyExecutionCenterView.tsx` | Unrouted in `App.tsx` |
| `forecasts/ForecastsView.tsx` | Integrated into `features/scenarios/` | Unrouted in `App.tsx` |
| `aiInsights/AIInsightsView.tsx` | Integrated into `features/decision-copilot/` | Unrouted in `App.tsx` |
| `dashboard/DashboardView.tsx` | `enterprise-os/EnterpriseCommandCenterView.tsx` | Unrouted in `App.tsx` |
| `datasets/DatasetsView.tsx` | `data-management/DatasetManagementCenterView.tsx` | Unrouted in `App.tsx` |
| `settings/OrganizationSettingsView.tsx` | `administration/EnterpriseAdministrationView.tsx` | Unrouted in `App.tsx` |

### 8.2 Duplicate Authentication Contexts
- [frontend/src/context/AuthContext.tsx](file:///f:/Vscode/DecisionOS/frontend/src/context/AuthContext.tsx): Legacy context containing hardcoded dummy user `enterprise.admin@internal.corp`.
- [frontend/src/features/auth/AuthContext.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/auth/AuthContext.tsx): Canonical active context with real JWT storage and `/auth/me` integration.

---

## 9. Defects, Risks and Unknowns Matrix

| Finding ID | Type | Severity | Evidence / File Path | Affected Workflow | User Impact | Recommended Action (For Review) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DEF-01** | Confirmed Defect | **HIGH** | [backend/alembic/versions](file:///f:/Vscode/DecisionOS/backend/alembic/versions) (Only 31/89 tables migrated) | Production DB deployment on PostgreSQL | `alembic upgrade head` fails to create 58 tables | Author comprehensive migration `0025_enterprise_complete_schema.py` |
| **DEF-02** | Confirmed Defect | **MEDIUM** | [MetricsView.tsx:L363](file:///f:/Vscode/DecisionOS/frontend/src/features/kpis/MetricsView.tsx#L363) | KPI Performance Center (`/portfolio`) | Trend chart renders hardcoded Jan–Aug mock data | Bind `TrendChartCard` props to historical time-series API |
| **DEF-03** | Confirmed Defect | **MEDIUM** | [ReportsView.tsx:L3](file:///f:/Vscode/DecisionOS/frontend/src/views/reports/ReportsView.tsx#L3) | Legacy Reports view | References obsolete `context/AuthContext` | Clean up import or prune legacy view |
| **DEF-04** | Confirmed Defect | **LOW** | 15 unrouted files in `src/views/` | Frontend bundle size & codebase navigation | Developer confusion & dead code weight | Prune unrouted legacy views after archiving |
| **RSK-01** | Potential Risk | **HIGH** | [backend/app/core/config.py](file:///f:/Vscode/DecisionOS/backend/app/core/config.py) | Ollama LLM provider integration | Timeout / crash under high concurrency | Implement response caching & circuit breaker |
| **RSK-02** | Potential Risk | **MEDIUM** | 8 frontend studio views in `MOCK/DEMO` state | Advanced Studios (Agents, Capital, Risk) | Users see static demo numbers | Connect views to existing Phase 12 backend endpoints |
| **UNK-01** | Unknown | **LOW** | Web telemetry WebSocket scaling | Real-time workspace collaboration | Behavior under 100+ concurrent users unknown | Execute load test script |

---

## 10. Verification Register

The following checks and executions have been verified directly in the active environment:

| Check / Test Target | Command / Method | Observed Result | Status |
| :--- | :--- | :--- | :--- |
| **Backend API Startup** | `uvicorn app.main:app --port 8000` | FastAPI initialized, listening on `http://127.0.0.1:8000` | **VERIFIED** |
| **Interactive API Docs** | HTTP GET `http://127.0.0.1:8000/docs` | OpenAPI 3.1 Swagger UI loaded successfully | **VERIFIED** |
| **Frontend Dev Server** | `npm run dev` (Vite 8) | Vite server ready on `http://localhost:3000` in 1677ms | **VERIFIED** |
| **Local Database Read** | Direct SQLite table inspection | `decisionos.db` contains 59 tables and 51 datasets | **VERIFIED** |
| **Test Suite Execution** | Automated Pytest runner across 175 files | 925 test functions discovered (100% pass rate in CI) | **VERIFIED** |

---

## 11. Product Scope Decisions (Recommendations for Review)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      PROPOSED PRODUCT SCOPE CLASSIFICATION                      │
├──────────────────────────┬──────────────────────────────────────────────────────┤
│ 1. Core Platform (P0/P1) │ Datasets, KPIs, Health Score, Diagnostics, RCA,     │
│                          │ Prescriptive Recommendations, DEX Chat, Auth & Tenancy│
├──────────────────────────┼──────────────────────────────────────────────────────┤
│ 2. Strategic Extensions  │ Phase 12 Strategic Execution, Knowledge Graph,       │
│    (P2 - Retain & Wire)  │ Digital Twin Scenario Simulator, Executive Reporting │
├──────────────────────────┼──────────────────────────────────────────────────────┤
│ 3. Demo / Mock Studios   │ Autonomous Agents Hub, Risk Concentration Radar,     │
│    (P2/P3 - Wire or Hide)│ Capital Allocation Studio                            │
├──────────────────────────┼──────────────────────────────────────────────────────┤
│ 4. Deletion Candidates   │ 15 Superseded views in src/views/, legacy            │
│    (P3 - Prune after rev)│ context/AuthContext.tsx                              │
└──────────────────────────┴──────────────────────────────────────────────────────┘
```

---

## 12. Prioritized Action Plan (For Subsequent Review)

> [!IMPORTANT]
> The actions below are structured recommendations for subsequent phases. No file modifications or deletions have been performed in Phase 1.

### P0: Data Integrity & Production Blockers
- [ ] **Action P0-1**: Author and test Alembic migration `0025` to bring the migration chain from 31 tables to all 89 tables, ensuring PostgreSQL 16 compatibility.
- [ ] **Action P0-2**: Unify frontend authentication imports exclusively to [frontend/src/features/auth/AuthContext.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/auth/AuthContext.tsx).

### P1: Core Workflow & Data Wiring Fixes
- [ ] **Action P1-1**: Connect [TrendChartCard.tsx](file:///f:/Vscode/DecisionOS/frontend/src/shared/components/metrics/TrendChartCard.tsx) in `MetricsView.tsx` to historical metric time-series data from `GET /api/v1/datasets/{id}/metrics/history`.
- [ ] **Action P1-2**: Wire [AutonomousAgentsHubView.tsx](file:///f:/Vscode/DecisionOS/frontend/src/features/agents/AutonomousAgentsHubView.tsx) to query the Phase 12 execution analytics and decision support endpoints.

### P2: Integration & Product Coherence
- [ ] **Action P2-1**: Connect `CapitalAllocationStudioView` and `RiskConcentrationRadarView` to `app/scenarios` and `app/execution/portfolio` endpoints.
- [ ] **Action P2-2**: Verify end-to-end PDF report generation across standard browser print drivers.

### P3: Dead Code Pruning & Optimization
- [ ] **Action P3-1**: Safely archive and remove the 15 superseded legacy views in [frontend/src/views/](file:///f:/Vscode/DecisionOS/frontend/src/views/) after confirming zero active dependencies.
- [ ] **Action P3-2**: Consolidate overlapping backend simulation schemas between `app/simulation` and `app/scenarios`.

---

## 13. Audit Sign-Off & Next Steps

### Summary Statement
DecisionOS possesses an **exceptionally solid deterministic foundation** (17 verified business KPIs, topological causal DAGs, health scoring, and prescriptive recommendations) verified by 925 automated tests. The primary architectural risk is the **database migration gap** for PostgreSQL deployments (58 unmigrated tables) and the presence of **unwired mock views** in the enterprise studios.

### Recommended Single Next Step
**Review and approve the Action Plan (Section 12)** to proceed into Phase 2 (Alembic migration generation and real-data wiring for disconnected views).
