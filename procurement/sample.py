"""Offline demo data so the UI and report can be previewed without API keys."""
from .context import CompanyContext
from .models import Analysis, RankedProduct, ReportNarrative
from .scoring import rerank


def demo(ctx: CompanyContext):
    raw = [
        RankedProduct(rank=1, name="Dell Latitude 5450 (i5-1345U, 16GB, 512GB)", seller="Dell Business", url="https://example.com/dell-5450",
            price=1080, currency=ctx.currency, spec_score=8.5,
            specs={"CPU": "Core i5-1345U", "RAM": "16 GB", "Storage": "512 GB SSD", "Warranty": "3 years onsite", "Weight": "1.5 kg"},
            pros=["3-year onsite warranty included", "Business invoice available", "Strong battery life"],
            cons=["Priced above the cheapest option"]),
        RankedProduct(rank=2, name="Lenovo ThinkPad E14 Gen 6", seller="Lenovo Egypt", url="https://example.com/e14",
            price=940, currency=ctx.currency, spec_score=6.0,
            specs={"CPU": "Core i5-1335U", "RAM": "16 GB", "Storage": "512 GB SSD", "Warranty": "1 year", "Weight": "1.4 kg"},
            pros=["Lowest verified price", "Good keyboard"], cons=["Only 1-year warranty by default"]),
        RankedProduct(rank=3, name="HP ProBook 450 G10", seller="Local reseller", url="https://example.com/hp450",
            price=None, currency="", spec_score=7.0,
            specs={"CPU": "Core i5-1335U", "RAM": "8 GB", "Storage": "512 GB SSD", "Warranty": "3 years"},
            pros=["3-year warranty"], cons=["Price not listed", "8 GB RAM only"]),
    ]
    ranking = rerank(raw, ctx.weights(), ctx.budget_per_unit)
    analysis = Analysis(ranking=ranking, assumptions=["All prices already in USD; no conversion applied.", "Prices exclude VAT, shipping and import duty."])
    narrative = ReportNarrative(
        title="Business laptops for the Cairo warehouse team",
        executive_summary="Three business-class laptops were compared on price, specification fit and value. The Dell Latitude 5450 gives the best balance and meets the 3-year warranty requirement without extra cost.",
        recommendation=f"Order {ctx.quantity} units of the {ranking[0].name} from {ranking[0].seller}. It ranks first on overall score and is the only verified option that includes a 3-year onsite warranty.",
        why_not_others=["Lenovo E14: cheapest verified price but a 1-year warranty fails a must-have.", "HP ProBook: no verified price and only 8 GB RAM."],
        risks=["Prices are from product pages on the day of the run and may change.", "Stock for 25 units is not confirmed.", "Import duty to Egypt is not included."],
        next_steps=["Request a formal quote for 25 units including delivery to Cairo.", "Confirm warranty terms in writing.", "Ask for a sample unit before the full order."])
    return analysis, narrative
