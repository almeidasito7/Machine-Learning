from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AnalyzeResponse(BaseModel):
    structures: List[Dict[str, Any]] = Field(default_factory=list)
    total_structures: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    kpis: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    insight: Optional[str] = None