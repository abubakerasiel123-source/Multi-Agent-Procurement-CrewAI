"""Tools the agents can call: Tavily Search, ScrapeGraph (v2 API) and a deterministic scorer."""
from __future__ import annotations

import json
from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .scoring import score_products

def _emit(tool, msg: str) -> None:
    """Send a progress line to the UI, never letting a UI problem break the tool."""
    try:
        if tool.on_event:
            tool.on_event(msg)
    except Exception:
        pass


# ---------------------------------------------------------------- Tavily search


class SearchInput(BaseModel):
    query: str = Field(..., description="Web search query, e.g. 'Dell Latitude 5450 price Egypt'")


class TavilySearchTool(BaseTool):
    name: str = "tavily_search"
    description: str = (
        "Search the web for products, prices and retailers. Returns titles, URLs and short "
        "snippets. Use specific queries (model names, region, 'buy', 'price')."
    )
    args_schema: Type[BaseModel] = SearchInput
    api_key: str = ""
    max_results: int = 6
    on_event: Any = None  # optional callable(str) used by the UI's live feed

    def _run(self, query: str) -> str:
        from tavily import TavilyClient

        _emit(self, f"→ tavily_search  {query}")

        try:
            res = TavilyClient(api_key=self.api_key).search(
                query=query, max_results=self.max_results, search_depth="basic"
            )
        except Exception as exc:  # surface the error to the agent instead of crashing the crew
            _emit(self, f"✗ search failed: {str(exc)[:120]}")
            return f"SEARCH_ERROR: {exc}"
        rows = [
            {"title": r.get("title"), "url": r.get("url"), "snippet": (r.get("content") or "")[:300]}
            for r in res.get("results", [])
        ]
        _emit(self, f"  {len(rows)} results")
        return json.dumps(rows, ensure_ascii=False)


# ---------------------------------------------------------------- ScrapeGraph

PRODUCT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "brand": {"type": "string"},
        "price": {"type": "number", "description": "unit price, number only"},
        "currency": {"type": "string"},
        "availability": {"type": "string"},
        "warranty": {"type": "string"},
        "seller": {"type": "string"},
        "specs": {"type": "object", "additionalProperties": {"type": "string"}},
    },
}


class ScrapeInput(BaseModel):
    url: str = Field(..., description="Product page URL to extract data from")


class ScrapeGraphTool(BaseTool):
    name: str = "scrapegraph_extract"
    description: str = (
        "Open a product page and extract structured data: name, brand, price, currency, "
        "availability, warranty, seller and key specifications. Input is one URL."
    )
    args_schema: Type[BaseModel] = ScrapeInput
    api_key: str = ""
    on_event: Any = None

    def _run(self, url: str) -> str:
        from scrapegraph_py import ScrapeGraphAI

        _emit(self, f"→ scrapegraph_extract  {url}")

        prompt = (
            "Extract the main product on this page: name, brand, unit price as a number, "
            "currency, availability, warranty, seller and the key technical specifications "
            "as a flat key/value object."
        )
        try:
            with ScrapeGraphAI(api_key=self.api_key) as client:
                res = client.extract(prompt, url=url, schema=PRODUCT_SCHEMA)
        except Exception as exc:
            _emit(self, f"✗ scrape failed: {str(exc)[:120]}")
            return f"SCRAPE_ERROR for {url}: {exc}"
        if res.status != "success" or res.data is None:
            _emit(self, f"✗ scrape failed: {res.error or 'no data'}")
            return f"SCRAPE_ERROR for {url}: {res.error or 'no data'}"
        _emit(self, "  page extracted")
        payload = res.data.json_data or {"raw": (res.data.raw or "")[:1500]}
        return json.dumps({"url": url, **payload}, ensure_ascii=False)[:3500]


# ---------------------------------------------------------------- scorer


class ScoreItem(BaseModel):
    name: str
    price: float | None = Field(None, description="Unit price in the reporting currency, or null")
    spec_score: float = Field(..., ge=0, le=10, description="0-10 fit of the specs to the company need")


class ScoreInput(BaseModel):
    items: list[ScoreItem]


class ScoreProductsTool(BaseTool):
    name: str = "score_products"
    description: str = (
        "Compute price, value and final scores using the company's ranking weights. "
        "Pass ALL products at once. Returns them sorted best-first. Use these numbers as-is."
    )
    args_schema: Type[BaseModel] = ScoreInput
    weights: tuple[float, float, float] = (0.34, 0.33, 0.33)
    budget: float | None = None
    on_event: Any = None

    def _run(self, items: list) -> str:
        rows = [i.model_dump() if hasattr(i, "model_dump") else dict(i) for i in items]
        _emit(self, f"→ score_products  {len(rows)} items")
        return json.dumps(score_products(rows, self.weights, self.budget))
