"""CrewAI workflow: Search -> Scrape -> Analyse -> Report, run sequentially."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from crewai import LLM, Agent, Crew, Process, Task

from .context import CompanyContext
from .models import Analysis, CandidateList, ReportNarrative, ScrapedProducts
from .scoring import rerank
from .tools import ScoreProductsTool, ScrapeGraphTool, TavilySearchTool

STAGES = [
    ("Search", "Sourcing Scout"),
    ("Scrape", "Data Collector"),
    ("Analyse", "Procurement Analyst"),
    ("Report", "Report Writer"),
]


@dataclass
class Keys:
    llm: str
    tavily: str
    scrapegraph: str


def _has(attr: str, msg: str):
    """Guardrail: the task must return at least one item, otherwise retry once with feedback."""
    def check(out):
        data = getattr(out, "pydantic", None)
        return (True, out) if data is not None and getattr(data, attr, None) else (False, msg)
    return check


def _clean(text: str) -> str:
    # CrewAI treats {braces} as template variables, so strip them from free text.
    return (text or "").replace("{", "(").replace("}", ")")


def build_crew(ctx: CompanyContext, request: str, keys: Keys, model: str,
               max_products: int = 5, on_task_done: Callable[[int, object], None] | None = None,
               on_step: Callable[[object], None] | None = None,
               on_event: Callable[[str], None] | None = None,
               verbose: bool = False) -> Crew:
    llm = LLM(model=model, api_key=keys.llm)
    company = _clean(ctx.as_prompt())
    request = _clean(request)

    search_tool = TavilySearchTool(api_key=keys.tavily, on_event=on_event)
    scrape_tool = ScrapeGraphTool(api_key=keys.scrapegraph, on_event=on_event)
    score_tool = ScoreProductsTool(weights=ctx.weights(), budget=ctx.budget_per_unit, on_event=on_event)

    common = dict(llm=llm, allow_delegation=False, verbose=verbose)

    scout = Agent(
        role="Sourcing Scout",
        goal="Find the most relevant product pages from reputable sellers for the procurement request.",
        backstory="A veteran B2B buyer who knows which retailers and manufacturers are trustworthy "
                  "and never shortlists a product without a direct product page.",
        tools=[search_tool], max_iter=8, **common)
    collector = Agent(
        role="Data Collector",
        goal="Extract accurate price, availability, warranty and specifications from each product page.",
        backstory="A meticulous data analyst. Missing data stays empty: it never invents a price.",
        tools=[scrape_tool], max_iter=12, **common)
    analyst = Agent(
        role="Procurement Analyst",
        goal="Compare the products against the company needs and rank them on price, specs and value.",
        backstory="A category manager who rates specification fit honestly and always uses the "
                  "scoring tool for the final numbers.",
        tools=[score_tool], max_iter=6, **common)
    writer = Agent(
        role="Report Writer",
        goal="Turn the ranked analysis into a clear recommendation a purchasing manager can act on.",
        backstory="A procurement consultant who writes short, direct reports and states risks plainly.",
        max_iter=4, **common)

    def cb(i):
        return (lambda out: on_task_done(i, out)) if on_task_done else None

    t_search = Task(
        description=(
            f"{company}\n\nREQUEST: {request}\n\n"
            f"Search the web and shortlist up to {max_products + 3} candidate product pages. "
            "Run several different queries (model names, 'price', the company's region). "
            "Prefer direct product pages from reputable sellers; skip blogs and forums."),
        expected_output="A list of candidates with title, direct product URL, seller and a short snippet.",
        agent=scout, output_pydantic=CandidateList, callback=cb(0),
        guardrail=_has("candidates", "No candidates were returned. Run more searches with different queries. "
                       "If the search tool returned SEARCH_ERROR, say so; never invent URLs."),
        guardrail_max_retries=1)

    t_scrape = Task(
        description=(
            f"For the candidates found by the scout, extract data from each product URL (at most "
            f"{max_products + 2}). Keep only products you actually got data for. If a price is "
            "missing leave it empty. Keep specs as short key/value strings."),
        expected_output="Structured product records with price, currency, availability, warranty and specs.",
        agent=collector, context=[t_search], output_pydantic=ScrapedProducts, callback=cb(1),
        guardrail=_has("products", "No product data was extracted. Try the remaining candidate URLs. "
                       "If the scraper returned SCRAPE_ERROR, say so; never invent data."),
        guardrail_max_retries=1)

    t_analyse = Task(
        description=(
            f"{company}\n\nCompare the collected products for this request: {request}\n"
            f"1. Convert prices to {ctx.currency} if needed and note the rate in assumptions.\n"
            "2. Give each product a spec_score from 0 to 10 for how well its specs and warranty "
            "fit the company's must-haves. Be critical.\n"
            "3. Call the score_products tool ONCE with every product (name, price, spec_score).\n"
            f"4. Return the best {max_products} in the order the tool returned, copying its "
            "price_score, value_score, final_score and flags. Add 2-3 pros and cons each."),
        expected_output="A ranked list with scores, pros, cons and flags, plus assumptions.",
        agent=analyst, context=[t_scrape], output_pydantic=Analysis, callback=cb(2))

    t_report = Task(
        description=(
            f"{company}\n\nWrite the narrative for the procurement report on: {request}\n"
            "Use only the ranked analysis. Give the top pick as the recommendation with the "
            "reasons, one line on why each other product ranked lower, the real risks "
            "(unverified prices, stock, warranty, import) and concrete next steps. "
            "Plain text, no markdown."),
        expected_output="Title, executive summary, recommendation, why-not-others, risks and next steps.",
        agent=writer, context=[t_analyse], output_pydantic=ReportNarrative, callback=cb(3))

    return Crew(agents=[scout, collector, analyst, writer],
                tasks=[t_search, t_scrape, t_analyse, t_report],
                process=Process.sequential, verbose=verbose,
                step_callback=on_step)


def run(ctx: CompanyContext, request: str, keys: Keys, model: str, **kw):
    crew = build_crew(ctx, request, keys, model, **kw)
    crew.kickoff()
    t = crew.tasks
    analysis: Analysis = t[2].output.pydantic
    if not analysis.ranking:
        raise RuntimeError("No products could be ranked. Check the Tavily / ScrapeGraph keys and credits, "
                           "or make the request less specific.")
    narrative: ReportNarrative = t[3].output.pydantic
    analysis.ranking = rerank(analysis.ranking, ctx.weights(), ctx.budget_per_unit)
    return analysis, narrative
