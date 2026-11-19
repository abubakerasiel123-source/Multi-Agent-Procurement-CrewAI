"""Visual identity for the Streamlit app: 'Crew Control Room'.
Each agent owns a colour; the same four colours run through the UI and the report."""
from __future__ import annotations

from html import escape as e

AGENTS = [
    ("Search", "Sourcing Scout", "#22D3EE", "⌕", "Tavily"),
    ("Scrape", "Data Collector", "#FBBF24", "⇩", "ScrapeGraph"),
    ("Analyse", "Procurement Analyst", "#A78BFA", "◈", "Scorer"),
    ("Report", "Report Writer", "#FB7185", "✎", "HTML"),
]
GOLD, SILVER, BRONZE = "#FFD166", "#CBD5E1", "#F59E6B"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700;900&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');
:root{--bg:#0B0D1E;--s1:#141836;--s2:#1B2048;--ln:#2A2F5E;--tx:#EDEBFF;--mut:#8D91C7;
--c1:#22D3EE;--c2:#FBBF24;--c3:#A78BFA;--c4:#FB7185}
html,body,.stApp,[class*="css"]{font-family:'Outfit',sans-serif!important;color:var(--tx)}
.stApp{background:radial-gradient(1200px 600px at 10% -10%,#22D3EE18,transparent 60%),
radial-gradient(900px 500px at 95% 0%,#FB718518,transparent 60%),radial-gradient(800px 600px at 50% 110%,#A78BFA18,transparent 60%),var(--bg)}
#MainMenu,footer,header{visibility:hidden}.block-container{padding-top:1.4rem;max-width:1180px}
[data-testid="stSidebar"]{background:var(--s1);border-right:1px solid var(--ln)}
/* masthead */
.mast{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:6px}
.mast h1{font:900 46px/1 'Unbounded',sans-serif;margin:0;letter-spacing:-.04em;
background:linear-gradient(90deg,var(--c1),var(--c3) 45%,var(--c4));-webkit-background-clip:text;background-clip:text;color:transparent}
.mast p{margin:8px 0 0;color:var(--mut);font-size:15px}
.legend{display:flex;gap:14px;font:600 11px 'JetBrains Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
.legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;box-shadow:0 0 10px currentColor}
.rule{height:3px;border-radius:3px;margin:16px 0 24px;background:linear-gradient(90deg,var(--c1),var(--c2),var(--c3),var(--c4))}
/* section label */
.sec{display:flex;align-items:center;gap:12px;margin:26px 0 12px;font:700 12px 'Unbounded',sans-serif;letter-spacing:.14em;text-transform:uppercase}
.sec b{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:9px;color:#0B0D1E;font:700 12px 'JetBrains Mono',monospace}
.sec:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--ln),transparent)}
/* pipeline */
.pipe{display:grid;grid-template-columns:1fr 28px 1fr 28px 1fr 28px 1fr;align-items:stretch;margin:4px 0 14px}
.agent{--c:#fff;position:relative;background:var(--s1);border:1px solid var(--ln);border-radius:18px;padding:16px 16px 14px;overflow:hidden;
transition:.3s;opacity:.55}
.agent:before{content:"";position:absolute;inset:0 0 auto 0;height:4px;background:var(--c)}
.agent .ic{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-size:22px;color:#0B0D1E;background:var(--c);margin-bottom:10px}
.agent small{display:block;font:600 10px 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--mut)}
.agent b{display:block;font:700 18px 'Unbounded',sans-serif;margin:2px 0 6px}
.agent .st{font:400 12.5px 'JetBrains Mono',monospace;color:var(--mut)}
.agent.run{opacity:1;border-color:var(--c);box-shadow:0 0 0 1px var(--c),0 0 36px -6px var(--c);animation:pulse 1.6s ease-in-out infinite}
.agent.run .st{color:var(--c)}.agent.run .st:before{content:"● ";animation:blink 1s infinite}
.agent.run:after{content:"";position:absolute;left:-60%;bottom:0;width:60%;height:3px;background:linear-gradient(90deg,transparent,var(--c),transparent);animation:sweep 1.4s linear infinite}
.agent.done{opacity:1;background:linear-gradient(180deg,color-mix(in srgb,var(--c) 14%,var(--s1)),var(--s1))}
.agent.done .st{color:var(--tx)}.agent.done .st:before{content:"✓ ";color:var(--c);font-weight:700}
.link{align-self:center;height:3px;background:var(--ln);border-radius:3px;position:relative;overflow:hidden}
.link.on:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent,#fff,transparent);animation:sweep2 1s linear infinite}
.link.full{background:linear-gradient(90deg,var(--a),var(--b))}
@keyframes sweep{to{left:100%}}@keyframes sweep2{from{transform:translateX(-100%)}to{transform:translateX(100%)}}
@keyframes blink{50%{opacity:.2}}@keyframes pulse{50%{transform:translateY(-2px)}}
/* live feed */
.feed{background:#080A18;border:1px solid var(--ln);border-radius:14px;padding:12px 16px;font:400 12.5px/1.7 'JetBrains Mono',monospace;min-height:64px;max-height:210px;overflow:auto}
.feed .ln{white-space:pre-wrap;word-break:break-word}.feed .tag{display:inline-block;min-width:96px;font-weight:600}
.feed .dim{color:var(--mut)}
/* podium */
.podium{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;align-items:end;margin:8px 0 8px}
.pod{--c:#fff;position:relative;border-radius:20px;padding:20px 18px 18px;background:linear-gradient(180deg,color-mix(in srgb,var(--c) 18%,var(--s1)),var(--s1) 70%);
border:1px solid color-mix(in srgb,var(--c) 55%,transparent)}
.pod.first{padding-top:30px;box-shadow:0 0 60px -14px var(--c)}
.pod .no{font:900 54px/1 'Unbounded',sans-serif;color:var(--c);opacity:.95}
.pod .crown{position:absolute;right:16px;top:14px;font:700 10px 'JetBrains Mono',monospace;letter-spacing:.14em;color:#0B0D1E;background:var(--c);padding:3px 9px;border-radius:99px}
.pod h4{font:600 16px/1.3 'Outfit',sans-serif;margin:10px 0 2px;min-height:42px}
.pod .sl{color:var(--mut);font-size:13px;margin-bottom:12px}
.pod .row{display:flex;justify-content:space-between;align-items:center;margin-top:8px}
.pod .px{font:600 20px 'JetBrains Mono',monospace}
.ring{--p:0;width:58px;height:58px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--c) calc(var(--p)*1%),#ffffff14 0)}
.ring span{width:46px;height:46px;border-radius:50%;background:var(--s1);display:grid;place-items:center;font:700 14px 'JetBrains Mono',monospace}
.flags{margin-top:10px;display:flex;gap:6px;flex-wrap:wrap}.flags em{font:600 10px 'JetBrains Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:#FB7185;border:1px solid #FB718588;border-radius:99px;padding:2px 8px;font-style:normal}
/* widgets */
.stTextInput input,.stTextArea textarea,.stNumberInput input,div[data-baseweb="select"]>div{background:var(--s1)!important;border:1px solid var(--ln)!important;border-radius:12px!important;color:var(--tx)!important}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:var(--c3)!important;box-shadow:0 0 0 3px #A78BFA33!important}
label,.stSlider label{color:var(--mut)!important;font-size:13px!important}
.stButton>button,.stDownloadButton>button{border:0;border-radius:14px;color:#0B0D1E;font:700 13px 'Unbounded',sans-serif;letter-spacing:.06em;padding:.85rem 1.8rem;
background:linear-gradient(90deg,var(--c1),var(--c3),var(--c4));background-size:200% 100%;transition:.4s}
.stButton>button:hover,.stDownloadButton>button:hover{background-position:100% 0;transform:translateY(-2px);box-shadow:0 12px 30px -10px var(--c3);color:#0B0D1E}
[data-testid="stMetric"]{background:var(--s1);border:1px solid var(--ln);border-radius:14px;padding:12px 16px}
@media(max-width:820px){.pipe{grid-template-columns:1fr}.link{display:none}.podium{grid-template-columns:1fr}.mast{flex-direction:column;align-items:flex-start}.mast h1{font-size:32px}}
</style>
"""


def masthead() -> str:
    legend = "".join(f'<span><i style="color:{c};background:{c}"></i>{a}</span>' for _, a, c, _, _ in AGENTS[:4])
    return (f'<div class="mast"><div><h1>AXIOM PROCURE</h1><p>Four AI agents search, scrape, compare and rank '
            f'what you need to buy, then hand you a report.</p></div><div class="legend">{legend}</div></div>'
            '<div class="rule"></div>')


def section(n: str, title: str, color: str) -> str:
    return f'<div class="sec"><b style="background:{color}">{n}</b>{e(title)}</div>'


def pipeline(states: list[str], notes: list[str] | None = None) -> str:
    notes = notes or [""] * 4
    word = {"wait": "standing by", "run": "working", "done": "done"}
    out = '<div class="pipe">'
    for i, ((stage, agent, col, icon, tool), s, n) in enumerate(zip(AGENTS, states, notes)):
        out += (f'<div class="agent {s}" style="--c:{col}"><div class="ic">{icon}</div><small>{e(tool)}</small>'
                f'<b>{e(stage)}</b><div class="st">{e(n or word[s])}</div></div>')
        if i < 3:
            nxt = AGENTS[i + 1][2]
            cls = "full" if s == "done" else ("on" if s == "run" else "")
            out += f'<div class="link {cls}" style="--a:{col};--b:{nxt}"></div>'
    return out + "</div>"


def feed(lines: list[tuple[int, str]]) -> str:
    if not lines:
        return '<div class="feed"><span class="dim">Agent activity will stream here once the crew starts.</span></div>'
    rows = ""
    for idx, text in lines[-40:]:
        _, agent, col, _, _ = AGENTS[idx]
        rows += f'<div class="ln"><span class="tag" style="color:{col}">{e(agent)}</span>{e(text)}</div>'
    return f'<div class="feed">{rows}</div>'


def podium(ranking, currency: str) -> str:
    top = ranking[:3]
    if not top:
        return ""
    colors = [GOLD, SILVER, BRONZE]
    order = [1, 0, 2] if len(top) == 3 else ([1, 0] if len(top) == 2 else [0])
    cards = ""
    for i in order:
        p, c = top[i], colors[i]
        price = f"{p.price:,.0f} {e(p.currency or currency)}" if p.price else "price n/a"
        flags = "".join(f"<em>{e(f)}</em>" for f in p.flags)
        cards += (f'<div class="pod {"first" if i == 0 else ""}" style="--c:{c}">'
                  f'{"<span class=crown>TOP PICK</span>" if i == 0 else ""}<div class="no">{p.rank}</div>'
                  f'<h4>{e(p.name[:70])}</h4><div class="sl">{e(p.seller or p.brand or "—")}</div>'
                  f'<div class="row"><span class="px">{price}</span>'
                  f'<div class="ring" style="--p:{p.final_score * 10:.0f}"><span>{p.final_score:.1f}</span></div></div>'
                  f'<div class="flags">{flags}</div></div>')
    return f'<div class="podium">{cards}</div>'
