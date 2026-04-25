from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class AnonymizeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    method: Literal["intelligent", "label", "random"] = "intelligent"
    role: Literal["admin", "auditor", "operator", "researcher", "api_client"] = "researcher"
    irreversible: bool = True
    responsible_user: str = "demo_user"
    dataset_name: Optional[str] = None


class SpanModel(BaseModel):
    start: int
    end: int
    label: str
    rank: int = 0


class JobReport(BaseModel):
    job_id: str
    status: str
    original_hash: str
    anonymized_hash: str
    method: str
    role: str
    compliance_standards: List[str]
    span_count: int
    risk_summary: dict
    output_preview: str
