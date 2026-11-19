"""Structured outputs passed between agents."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    title: str
    url: str
    seller: str = ""
    snippet: str = ""


class CandidateList(BaseModel):
    candidates: list[Candidate]


class ScrapedProduct(BaseModel):
    name: str
    brand: str = ""
    seller: str = ""
    url: str
    price: float | None = Field(None, description="Unit price as a number, no symbols")
    currency: str = ""
    availability: str = ""
    warranty: str = ""
    specs: dict[str, str] = Field(default_factory=dict)
    notes: str = ""


class ScrapedProducts(BaseModel):
    products: list[ScrapedProduct]


class RankedProduct(BaseModel):
    rank: int
    name: str
    brand: str = ""
    seller: str = ""
    url: str
    price: float | None = None
    currency: str = ""
    specs: dict[str, str] = Field(default_factory=dict)
    spec_score: float = Field(..., description="0-10 judgement of how well specs fit the company need")
    price_score: float = 0.0
    value_score: float = 0.0
    final_score: float = 0.0
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)


class Analysis(BaseModel):
    ranking: list[RankedProduct]
    assumptions: list[str] = Field(default_factory=list)


class ReportNarrative(BaseModel):
    title: str
    executive_summary: str
    recommendation: str
    why_not_others: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
