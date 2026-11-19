"""Axiom Procure: Streamlit front end for the CrewAI procurement crew."""
from __future__ import annotations

import os
import threading
import time
import traceback

import streamlit as st
import streamlit.components.v1 as components
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

from procurement import theme
from procurement.context import CompanyContext
from procurement.crew import Keys, run
from procurement.report import render_html
from procurement.sample import demo

st.set_page_config(page_title="Axiom Procure", page_icon="🧭", layout="wide")
st.markdown(theme.CSS, unsafe_allow_html=True)
st.markdown(theme.masthead(), unsafe_allow_html=True)


def secret(name: str) -> str:
    try:
        return st.secrets.get(name, "") or os.environ.get(name, "")
    except Exception:  # no secrets file present
        return os.environ.get(name, "")


C1, C2, C3, C4 = (a[2] for a in theme.AGENTS)

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown(theme.section("⚙", "Engine", C3), unsafe_allow_html=True)
    demo_mode = st.toggle("Demo mode (no API calls)", value=False)
    provider = st.selectbox("LLM provider", ["Anthropic", "OpenAI", "Gemini", "Groq"])
    models = {"Anthropic": ["anthropic/claude-sonnet-5-5", "anthropic/claude-haiku-5-5"],
              "OpenAI": ["openai/gpt-4o-mini"], "Gemini": ["gemini/gemini-2.5-flash"],
              "Groq": ["groq/llama-3.3-70b-versatile"]}[provider]
    try:
        model = st.selectbox("Model", models, accept_new_options=True)
    except TypeError:  # older Streamlit
        model = st.selectbox("Model", models)
    st.markdown(theme.section("🔑", "Keys", C2), unsafe_allow_html=True)
    k_llm = st.text_input("LLM API key", type="password", value=secret("LLM_API_KEY"))
    k_tav = st.text_input("Tavily API key", type="password", value=secret("TAVILY_API_KEY"))
    k_sg = st.text_input("ScrapeGraph API key", type="password", value=secret("SGAI_API_KEY"))
    st.caption("Loaded from .streamlit/secrets.toml when present. Never committed to Git.")

# ------------------------------------------------------------------ company context
st.markdown(theme.section("01", "Company context", C1), unsafe_allow_html=True)
a1, a2, a3, a4 = st.columns([2, 2, 1, 1])
name = a1.text_input("Company", "Nile Logistics Co.")
industry = a2.text_input("Industry", "Logistics & warehousing")
location = a3.text_input("Location", "Cairo, Egypt")
currency = a4.text_input("Currency", "USD")
b1, b2, b3 = st.columns([1, 1, 3])
qty = b1.number_input("Quantity", 1, 100000, 25)
budget = b2.number_input("Budget / unit (0 = none)", 0, 10_000_000, 1200)
must = b3.text_input("Must have", "3-year warranty, ships to Egypt, business invoice available")
d1, d2 = st.columns([3, 2])
avoid = d1.text_input("Avoid", "unknown brands with no reviews, refurbished units")
max_products = d2.slider("Products in final ranking", 3, 8, 5)
w1, w2, w3 = st.columns(3)
wp = w1.slider("Weight · price", 0, 10, 4)
ws = w2.slider("Weight · specs", 0, 10, 4)
wv = w3.slider("Weight · value", 0, 10, 3)

st.markdown(theme.section("02", "What do you need to buy?", C2), unsafe_allow_html=True)
request = st.text_area("Request", height=90, label_visibility="collapsed",
                       value="25 business laptops for warehouse supervisors: 14-inch, 16 GB RAM, 512 GB SSD, light enough to carry all day.")

ctx = CompanyContext(name=name, industry=industry, location=location, currency=currency,
                     budget_per_unit=float(budget) or None, quantity=int(qty), must_have=must,
                     avoid=avoid, w_price=wp or 0.1, w_specs=ws or 0.1, w_value=wv or 0.1)

# ------------------------------------------------------------------ live crew view
st.markdown(theme.section("03", "The crew", C3), unsafe_allow_html=True)
pipe_box, feed_box = st.empty(), st.empty()
states, notes, log, cur = ["wait"] * 4, [""] * 4, [], [0]


def paint():
    pipe_box.markdown(theme.pipeline(states, notes), unsafe_allow_html=True)
    feed_box.markdown(theme.feed(log), unsafe_allow_html=True)


paint()
go = st.button("RUN THE CREW")


def short(x, n=110):
    x = str(x).replace("\n", " ")
    return x if len(x) <= n else x[:n] + "…"


if go:
    missing = [] if demo_mode else [n for n, v in (("LLM", k_llm), ("Tavily", k_tav), ("ScrapeGraph", k_sg)) if not v]
    if missing:
        st.error("Add your " + ", ".join(missing) + " API key(s) in the sidebar, or switch on demo mode.")
    elif not request.strip():
        st.error("Describe what you need to buy.")
    else:
        t0 = time.time()
        states[0] = "run"
        paint()

        def finish(i, note):
            states[i], notes[i] = "done", note
            if i < 3:
                states[i + 1], cur[0] = "run", i + 1
            log.append((i, f"finished in {time.time() - t0:.0f}s total"))
            paint()

        ctx_st = get_script_run_ctx()

        def on_event(msg):  # tools may run on a worker thread: give it the Streamlit context first
            add_script_run_ctx(threading.current_thread(), ctx_st)
            log.append((cur[0], short(msg, 140)))
            paint()

        def on_step(step):
            if not getattr(step, "tool", None):
                on_event("✓ answer ready")

        try:
            if demo_mode:
                script = [("→ tavily_search  25 business laptops 16GB price Egypt", "found 8 candidate pages"),
                          ("→ scrapegraph_extract  https://example.com/dell-5450", "extracted 3 products"),
                          ("→ score_products  3 items, weights 36/36/27", "ranked 3 products"),
                          ("✓ report narrative drafted", "report ready")]
                for i, (line, note) in enumerate(script):
                    log.append((i, line)); paint(); time.sleep(0.7)
                    finish(i, note)
                analysis, narrative = demo(ctx)
            else:
                analysis, narrative = run(ctx, request, Keys(k_llm, k_tav, k_sg), model, max_products=max_products,
                                          on_task_done=lambda i, _o: finish(i, f"{time.time() - t0:.0f}s elapsed"),
                                          on_step=on_step, on_event=on_event)
            st.session_state.update(html=render_html(ctx, request, analysis, narrative), ranking=analysis.ranking,
                                    cur=ctx.currency)
        except Exception as exc:
            st.error(f"The crew stopped: {exc}")
            with st.expander("Details"):
                st.code(traceback.format_exc())

# ------------------------------------------------------------------ results
if "html" in st.session_state:
    ranking = st.session_state["ranking"]
    st.markdown(theme.section("04", "Ranking", C4), unsafe_allow_html=True)
    st.markdown(theme.podium(ranking, st.session_state["cur"]), unsafe_allow_html=True)
    st.markdown(theme.section("05", "Full report", C1), unsafe_allow_html=True)
    st.download_button("DOWNLOAD HTML REPORT", st.session_state["html"], "procurement_report.html", "text/html")
    if hasattr(st, "iframe"):
        st.iframe(st.session_state["html"], height=1600)
    else:
        components.html(st.session_state["html"], height=1600, scrolling=True)
