"""Company context shared with every agent (slide requirement: 'create a company context')."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CompanyContext:
    name: str = "Nile Logistics Co."
    industry: str = "Logistics & warehousing"
    location: str = "Cairo, Egypt"
    currency: str = "USD"
    budget_per_unit: float | None = 1200.0
    quantity: int = 25
    must_have: str = "3-year warranty, ships to Egypt, business invoice available"
    avoid: str = "unknown brands with no reviews, refurbished units"
    # relative importance of the three ranking criteria (normalised on use)
    w_price: float = 0.35
    w_specs: float = 0.40
    w_value: float = 0.25
    extra_notes: str = ""

    def weights(self) -> tuple[float, float, float]:
        total = (self.w_price + self.w_specs + self.w_value) or 1.0
        return self.w_price / total, self.w_specs / total, self.w_value / total

    def as_prompt(self) -> str:
        wp, ws, wv = self.weights()
        budget = (
            f"{self.budget_per_unit:,.0f} {self.currency} per unit"
            if self.budget_per_unit
            else "not specified"
        )
        return (
            f"COMPANY CONTEXT\n"
            f"- Company: {self.name} ({self.industry}), based in {self.location}\n"
            f"- Buying: {self.quantity} units | Budget: {budget} | Reporting currency: {self.currency}\n"
            f"- Must have: {self.must_have}\n"
            f"- Avoid: {self.avoid}\n"
            f"- Ranking weights: price {wp:.0%}, specifications {ws:.0%}, value-for-money {wv:.0%}\n"
            f"- Notes: {self.extra_notes or 'none'}"
        )
