"""Deterministic ranking maths, so the numbers in the report can be audited."""
from __future__ import annotations

from .models import RankedProduct


def score_products(items: list[dict], weights: tuple[float, float, float],
                   budget: float | None = None) -> list[dict]:
    """items: dicts with name, price (float|None), spec_score (0-10).

    price_score  = 10 * cheapest / price           (cheapest = 10)
    value_score  = 10 * (spec/price) / best(spec/price)
    final_score  = w_price*price_score + w_specs*spec_score + w_value*value_score
    Products with no verified price get price_score = value_score = 0 and a flag.
    """
    wp, ws, wv = weights
    prices = [i["price"] for i in items if i.get("price")]
    cheapest = min(prices) if prices else None
    ratios = [i["spec_score"] / i["price"] for i in items if i.get("price")]
    best_ratio = max(ratios) if ratios else None

    out = []
    for i in items:
        price, spec = i.get("price"), float(i.get("spec_score", 0))
        flags = list(i.get("flags", []))
        if price and cheapest and best_ratio:
            ps = 10 * cheapest / price
            vs = 10 * (spec / price) / best_ratio if best_ratio else 0
        else:
            ps = vs = 0.0
            if "price not verified" not in flags:
                flags.append("price not verified")
        if price and budget and price > budget and "over budget" not in flags:
            flags.append("over budget")
        final = wp * ps + ws * spec + wv * vs
        out.append({**i, "price_score": round(ps, 2), "value_score": round(vs, 2),
                    "final_score": round(final, 2), "flags": flags})
    out.sort(key=lambda d: d["final_score"], reverse=True)
    for n, d in enumerate(out, 1):
        d["rank"] = n
    return out


def rerank(products: list[RankedProduct], weights, budget=None) -> list[RankedProduct]:
    """Recompute scores from the analyst's raw inputs so the displayed ranking is authoritative."""
    scored = score_products([p.model_dump() for p in products], weights, budget)
    return [RankedProduct(**d) for d in scored]
