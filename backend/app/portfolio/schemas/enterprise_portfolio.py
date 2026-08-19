"""Pydantic Schemas for Phase 5.2 Enterprise Portfolio Intelligence."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Department & Business Unit Schemas ---

class DepartmentBase(BaseModel):
    name: str = Field(..., description="Department name (e.g. Marketing, Sales, Operations, Product, CS, Finance)")
    code: str = Field(..., description="Department code")
    lead_owner: Optional[str] = Field(None, description="Executive lead owner")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: uuid.UUID
    business_unit_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BusinessUnitBase(BaseModel):
    name: str = Field(..., description="Business Unit name")
    code: str = Field(..., description="Business Unit code")
    lead_owner: Optional[str] = Field(None, description="Executive lead owner")
    budget_allocated: float = Field(0.0, description="Allocated annual budget in USD")
    headcount: int = Field(0, description="Total team headcount")


class BusinessUnitCreate(BusinessUnitBase):
    departments: Optional[List[DepartmentCreate]] = None


class BusinessUnitResponse(BusinessUnitBase):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    departments: List[DepartmentResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Portfolio Schemas ---

class PortfolioBase(BaseModel):
    name: str = Field(..., description="Portfolio name")
    code: str = Field(..., description="Portfolio code")
    description: Optional[str] = Field(None, description="Strategic description")
    currency: str = Field("USD", description="Base reporting currency")
    is_active: bool = Field(True, description="Active status flag")


class PortfolioCreate(PortfolioBase):
    business_units: Optional[List[BusinessUnitCreate]] = None


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PortfolioDatasetLinkRequest(BaseModel):
    dataset_id: uuid.UUID
    business_unit_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    weight: float = Field(1.0, ge=0.1, le=10.0)
    is_primary_benchmark: bool = False


class PortfolioDatasetResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    dataset_id: uuid.UUID
    business_unit_id: Optional[uuid.UUID] = None
    department_id: Optional[uuid.UUID] = None
    weight: float
    is_primary_benchmark: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PortfolioResponse(PortfolioBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PortfolioDetailResponse(PortfolioResponse):
    business_units: List[BusinessUnitResponse] = []
    datasets: List[PortfolioDatasetResponse] = []


# --- Engine Response Schemas ---

class CrossDatasetBenchmarkItem(BaseModel):
    metric_name: str
    baseline_value: float
    target_value: float
    gap_percentage: float
    top_performer_dataset: str
    percentile_rank: float
    explanation: str


class CrossDatasetBenchmarkResponse(BaseModel):
    portfolio_id: uuid.UUID
    baseline_dataset_id: uuid.UUID
    target_dataset_id: uuid.UUID
    generated_at: datetime
    benchmarks: List[CrossDatasetBenchmarkItem]
    overall_gap_summary: str


class DepartmentScorecardItem(BaseModel):
    department_name: str
    lead_owner: Optional[str] = None
    health_score: float
    status: str
    primary_kpis: Dict[str, Any]
    recovery_potential_arr: float
    risk_level: str
    explanation: str


class DepartmentScorecardResponse(BaseModel):
    portfolio_id: uuid.UUID
    generated_at: datetime
    scorecards: List[DepartmentScorecardItem]


class BusinessUnitHealthItem(BaseModel):
    business_unit_id: uuid.UUID
    name: str
    health_score: float
    weight_contribution: float
    dataset_count: int


class PortfolioHealthResponse(BaseModel):
    portfolio_id: uuid.UUID
    overall_health_score: float
    health_tier: str
    confidence_score: float
    business_units: List[BusinessUnitHealthItem]
    generated_at: datetime
    sha256_hash: str


class PortfolioIntelligenceSummaryResponse(BaseModel):
    portfolio_id: uuid.UUID
    overall_health: float
    health_status: str
    strongest_unit: str
    weakest_unit: str
    primary_recovery_vector: str
    projected_arr_recovery: float
    executive_summary: str
    board_directives: List[Dict[str, Any]]
    confidence_score: float
    generated_at: datetime
    sha256_hash: str
