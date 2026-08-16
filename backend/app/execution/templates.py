"""System-defined Program Templates seed data for Phase 12: Strategic Execution Layer."""

from typing import Any, Dict, List, Optional
from app.execution.constants import (
    InitiativePriority,
    ProgramTemplateCode,
    TargetDirection,
)


SYSTEM_PROGRAM_TEMPLATES: Dict[ProgramTemplateCode, Dict[str, Any]] = {
    ProgramTemplateCode.OPERATIONAL_TURNAROUND: {
        "code": ProgramTemplateCode.OPERATIONAL_TURNAROUND,
        "name": "Operational Turnaround Program",
        "description": "Multi-initiative operational intervention program targeting declining business units to arrest negative score drift and restore positive velocity.",
        "category": "PERFORMANCE_GROWTH",
        "estimated_duration_days": 180,
        "default_initiatives": [
            {
                "title": "Root-Cause Diagnostic Sprint",
                "description": "Deploy deep diagnostic root-cause DAG tracing across trailing operational units.",
                "objective": "Identify primary constraint nodes driving metric degradation.",
                "priority": InitiativePriority.P1,
                "expected_health_gain": 8.0,
                "target_metrics": [
                    {
                        "metric_name": "Defect Rate",
                        "target_direction": TargetDirection.DECREASE,
                        "unit": "%",
                    },
                    {
                        "metric_name": "Business Health Score",
                        "target_direction": TargetDirection.INCREASE,
                        "unit": "points",
                    },
                ],
            },
            {
                "title": "Operational Process Re-engineering",
                "description": "Execute workflow stabilization and metric control playbooks.",
                "objective": "Eliminate recurring bottlenecks and stabilize unit health above 70.0 points.",
                "priority": InitiativePriority.P2,
                "expected_health_gain": 12.0,
                "target_metrics": [
                    {
                        "metric_name": "Fulfillment Velocity",
                        "target_direction": TargetDirection.INCREASE,
                        "unit": "units/day",
                    },
                ],
            },
        ],
    },
    ProgramTemplateCode.CRITICAL_RISK_REMEDIATION: {
        "code": ProgramTemplateCode.CRITICAL_RISK_REMEDIATION,
        "name": "Critical Risk Remediation Program",
        "description": "Executive governance and rapid remediation program to eliminate critical findings, reduce portfolio risk concentration, and secure vulnerable business units.",
        "category": "RISK_REMEDIATION",
        "estimated_duration_days": 90,
        "default_initiatives": [
            {
                "title": "Severe Defect & Finding Elimination",
                "description": "Immediate operational sprint to remediate all active critical finding backlogs.",
                "objective": "Achieve 100% resolution on P1 findings within target lookback window.",
                "priority": InitiativePriority.P1,
                "expected_health_gain": 15.0,
                "target_metrics": [
                    {
                        "metric_name": "Critical Finding Count",
                        "target_direction": TargetDirection.DECREASE,
                        "unit": "count",
                    },
                ],
            },
            {
                "title": "Executive Oversight & Sponsorship Cadence",
                "description": "Establish weekly executive governance checkpoint reviews for at-risk units.",
                "objective": "Ensure sustained executive escalation and risk decompression below 10%.",
                "priority": InitiativePriority.P2,
                "expected_health_gain": 7.5,
                "target_metrics": [
                    {
                        "metric_name": "Risk Concentration Index",
                        "target_direction": TargetDirection.DECREASE,
                        "unit": "index",
                    },
                ],
            },
        ],
    },
    ProgramTemplateCode.GROWTH_EXPANSION: {
        "code": ProgramTemplateCode.GROWTH_EXPANSION,
        "name": "High-Performance Cohort Expansion",
        "description": "Strategic acceleration program providing enablement capital and best practices to promote cusp business units into elite peer cohorts.",
        "category": "CAPABILITY_EXPANSION",
        "estimated_duration_days": 270,
        "default_initiatives": [
            {
                "title": "Cusp Unit Enablement & Capital Injection",
                "description": "Target high-potential units within 5 points of top peer group thresholds.",
                "objective": "Promote at least 3 cusp business units into the Top Performer cohort.",
                "priority": InitiativePriority.P2,
                "expected_health_gain": 10.0,
                "target_metrics": [
                    {
                        "metric_name": "Revenue Growth Rate",
                        "target_direction": TargetDirection.INCREASE,
                        "unit": "%",
                    },
                    {
                        "metric_name": "Customer Lifetime Value",
                        "target_direction": TargetDirection.INCREASE,
                        "unit": "$",
                    },
                ],
            },
        ],
    },
    ProgramTemplateCode.COST_OPTIMIZATION: {
        "code": ProgramTemplateCode.COST_OPTIMIZATION,
        "name": "Portfolio Cost & Efficiency Optimization",
        "description": "Targeted margin expansion and expenditure rationalization across operational cost centers.",
        "category": "PORTFOLIO_BALANCING",
        "estimated_duration_days": 180,
        "default_initiatives": [
            {
                "title": "Unit Economics & CAC Rationalization",
                "description": "Audit channel acquisition efficiency and streamline operational spend.",
                "objective": "Improve gross margin by 400 basis points across mid-tier cohorts.",
                "priority": InitiativePriority.P2,
                "expected_health_gain": 8.0,
                "target_metrics": [
                    {
                        "metric_name": "Customer Acquisition Cost",
                        "target_direction": TargetDirection.DECREASE,
                        "unit": "$",
                    },
                    {
                        "metric_name": "Gross Margin",
                        "target_direction": TargetDirection.INCREASE,
                        "unit": "%",
                    },
                ],
            },
        ],
    },
    ProgramTemplateCode.PLAYBOOK_STANDARDIZATION: {
        "code": ProgramTemplateCode.PLAYBOOK_STANDARDIZATION,
        "name": "Flagship Operating Playbook Standardization",
        "description": "Codify operating models and governance frameworks from elite units for cross-portfolio replication.",
        "category": "CAPABILITY_EXPANSION",
        "estimated_duration_days": 180,
        "default_initiatives": [
            {
                "title": "Operating Playbook Codification",
                "description": "Extract operational KPIs and governance disciplines from top 10% workspaces.",
                "objective": "Publish standard operating playbooks for portfolio-wide adoption.",
                "priority": InitiativePriority.P3,
                "expected_health_gain": 6.0,
                "target_metrics": [
                    {
                        "metric_name": "Playbook Adoption Rate",
                        "target_direction": TargetDirection.INCREASE,
                        "unit": "%",
                    },
                ],
            },
        ],
    },
}


def get_template(code: ProgramTemplateCode) -> Optional[Dict[str, Any]]:
    """Retrieves system program template definition by code."""
    return SYSTEM_PROGRAM_TEMPLATES.get(code)


def list_templates() -> List[Dict[str, Any]]:
    """Returns list of all available system program templates."""
    return list(SYSTEM_PROGRAM_TEMPLATES.values())
