"""DecisionOS Root Entrypoint Proxy.

Forwards to app.main for backward compatibility.
Usage: uvicorn app.main:app --reload
"""

from app.main import app

__all__ = ["app"]
