"""Executive Ownership Resolver for Phase 7.1 Boardroom Intelligence."""

from typing import Optional


class ExecutiveOwnershipResolver:
    """
    Dynamically maps recommendations and initiatives to C-suite executive roles
    based on functional domain, risk category, and strategic pillar.
    """

    @staticmethod
    def resolve_owner(domain_or_category: Optional[str] = None, title: Optional[str] = None) -> str:
        """
        Determines the responsible C-suite owner dynamically.
        """
        text = f"{domain_or_category or ''} {title or ''}".lower()

        if any(w in text for w in ["delivery", "courier", "sla", "logistics", "fulfillment", "shipping", "transit", "operational", "dispatch"]):
            return "Chief Operating Officer (COO)"
        elif any(w in text for w in ["retention", "churn", "loyalty", "customer", "csat", "win-back", "marketing", "nps", "satisfaction"]):
            return "Chief Marketing Officer (CMO)"
        elif any(w in text for w in ["revenue", "pricing", "margin", "discount", "finance", "billing", "budget", "arr", "cost"]):
            return "Chief Financial Officer (CFO)"
        elif any(w in text for w in ["algorithm", "data", "twin", "monte carlo", "ai", "model", "analytics"]):
            return "Head of Data & AI"
        elif any(w in text for w in ["expansion", "governance", "board", "merger", "strategic", "policy"]):
            return "Chief Executive Officer (CEO)"
        else:
            return "Executive Transformation Lead"
