# Axiom Procure — Multi-Agent Procurement Assistant (CrewAI)

Four CrewAI agents run in sequence and turn a plain-language purchase request into a ranked, HTML procurement report.

| # | Agent | Tool | Output |
|---|-------|------|--------|
| 1 | Sourcing Scout | Tavily Search | candidate product pages |
| 2 | Data Collector | ScrapeGraph (extract) | price, specs, warranty, availability |
| 3 | Procurement Analyst | score_products | ranking on price / specs / value |
| 4 | Report Writer | — | summary, recommendation, risks, next steps |

The company context (budget, quantity, must-haves, ranking weights) is injected into every task.
Scores come from `procurement/scoring.py`, so the numbers are auditable:
`price = 10·cheapest/price`, `value = specs-per-price normalised to the best`, `final = weighted sum`.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```
Keys: an LLM key (any LiteLLM provider), `TAVILY_API_KEY`, `SGAI_API_KEY`. Enter them in the sidebar or put
`LLM_API_KEY`, `TAVILY_API_KEY`, `SGAI_API_KEY` in `.streamlit/secrets.toml`. Demo mode runs with no keys.

## Deploy
Push to GitHub, create an app on Streamlit Community Cloud pointing at `app.py`, and add the three keys under Secrets.
