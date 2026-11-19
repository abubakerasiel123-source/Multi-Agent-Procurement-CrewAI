"""Renders the final procurement report as a single self-contained HTML file."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from html import escape as e

from .context import CompanyContext
from .models import Analysis, ReportNarrative

CYAN, AMBER, VIOLET, ROSE = "#22D3EE", "#FBBF24", "#A78BFA", "#FB7185"
CHIPS = [CYAN, AMBER, VIOLET, ROSE]

CSS = """
:root{--ink:#14163A;--mut:#6A6E9C;--ln:#E3E5F6;--c1:#22D3EE;--c2:#FBBF24;--c3:#A78BFA;--c4:#FB7185;--bg:#EEF0FB}
*{box-sizing:border-box}body{margin:0;color:var(--ink);font:16px/1.6 'Outfit',system-ui,sans-serif;
background:radial-gradient(900px 500px at 0 0,#22D3EE22,transparent 60%),radial-gradient(900px 500px at 100% 0,#FB718522,transparent 60%),var(--bg)}
.sheet{max-width:1060px;margin:28px auto;background:#fff;border-radius:26px;padding:0 54px 44px;box-shadow:0 30px 70px -30px #14163A55;overflow:hidden}
.band{height:10px;margin:0 -54px;background:linear-gradient(90deg,var(--c1),var(--c2),var(--c3),var(--c4))}
.top{display:flex;justify-content:space-between;padding:20px 0 0;font:600 11px 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--mut)}
h1{font:900 42px/1.08 'Unbounded',sans-serif;letter-spacing:-.04em;margin:22px 0 10px;max-width:820px;
background:linear-gradient(90deg,#14163A 40%,#6D4AE8);-webkit-background-clip:text;background-clip:text;color:transparent}
.req{color:var(--mut);margin:0 0 20px}
h2{display:flex;align-items:center;gap:12px;font:700 13px 'Unbounded',sans-serif;letter-spacing:.12em;text-transform:uppercase;margin:44px 0 16px}
h2 b{display:inline-grid;place-items:center;width:32px;height:32px;border-radius:10px;color:#14163A;font:700 12px 'JetBrains Mono',monospace}
h2:after{content:"";flex:1;height:1px;background:var(--ln)}
.meta{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.meta div{background:#F6F7FE;border-radius:14px;padding:12px 14px;font-weight:600}
.meta small{display:block;font:600 10px 'JetBrains Mono',monospace;color:var(--mut);letter-spacing:.14em;text-transform:uppercase;margin-bottom:2px}
p{margin:0 0 12px;max-width:80ch}
.podium{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;align-items:end}
.pod{--c:#999;border-radius:20px;padding:18px;background:linear-gradient(180deg,color-mix(in srgb,var(--c) 22%,#fff),#fff 75%);border:2px solid var(--c)}
.pod.first{padding-top:28px;box-shadow:0 18px 40px -18px var(--c)}
.pod .no{font:900 46px/1 'Unbounded',sans-serif;color:var(--c)}.pod h3{font:600 16px/1.3 'Outfit';margin:8px 0 2px}
.pod .sl{color:var(--mut);font-size:13px}.pod .px{font:600 20px 'JetBrains Mono',monospace;margin-top:10px}
.pod .sc{display:inline-block;margin-top:6px;font:700 12px 'JetBrains Mono',monospace;background:var(--ink);color:#fff;border-radius:99px;padding:3px 10px}
.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:left;font:600 10px 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);padding:8px;border-bottom:2px solid var(--ln)}
td{padding:11px 8px;border-bottom:1px solid var(--ln);vertical-align:middle}td.n{text-align:right;font:500 13px 'JetBrains Mono',monospace}
.rk{font:900 20px 'Unbounded',sans-serif}tr.top1 td{background:#FBBF2412}
.bar{height:9px;border-radius:9px;background:#EEF0FB;min-width:100px;overflow:hidden}.bar i{display:block;height:100%;border-radius:9px;background:linear-gradient(90deg,var(--c1),var(--c3),var(--c4))}
a{color:#5B3FD6;text-underline-offset:3px}small{color:var(--mut)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:14px}
.card{border:1px solid var(--ln);border-radius:18px;padding:16px 18px;border-top:5px solid var(--k)}
.card h3{font:600 17px/1.3 'Outfit';margin:0 0 8px}.card ul{margin:4px 0 10px;padding-left:20px}
.pro li::marker{content:"+ ";color:#10B981;font-weight:700}.con li::marker{content:"– ";color:var(--c4);font-weight:700}
.flag{display:inline-block;border:1px solid var(--c4);color:var(--c4);border-radius:99px;font:600 10px 'JetBrains Mono',monospace;letter-spacing:.08em;text-transform:uppercase;padding:2px 9px;margin:0 6px 6px 0}
.rec{border-radius:20px;padding:22px 26px;background:linear-gradient(#fff,#fff) padding-box,linear-gradient(120deg,var(--c1),var(--c3),var(--c4)) border-box;border:3px solid transparent}
ol.steps{counter-reset:s;list-style:none;padding:0}ol.steps li{counter-increment:s;padding-left:44px;position:relative;margin:10px 0}
ol.steps li:before{content:counter(s);position:absolute;left:0;top:0;width:30px;height:30px;border-radius:10px;background:var(--c3);color:#14163A;display:grid;place-items:center;font:700 13px 'JetBrains Mono',monospace}
ul.risk li::marker{color:var(--c4)}
footer{margin-top:44px;padding-top:14px;border-top:1px solid var(--ln);font:500 11px 'JetBrains Mono',monospace;color:var(--mut);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
@media(max-width:760px){.sheet{padding:0 20px 30px;margin:0;border-radius:0}.band{margin:0 -20px}.meta,.podium{grid-template-columns:1fr 1fr}.podium{grid-template-columns:1fr}h1{font-size:28px}}
@media print{body{background:#fff}.sheet{box-shadow:none;margin:0;max-width:none}}
"""


def _url(u: str) -> str:
    """Only http(s) links are allowed; anything else (javascript:, data:) is neutralised."""
    u = (u or "").strip()
    return e(u) if u.lower().startswith(("http://", "https://")) else "#"


def _money(v, cur):
    return f"{v:,.0f} {e(cur)}".strip() if v else "n/a"


def _list(items):
    return "".join(f"<li>{e(x)}</li>" for x in items)


def _h2(n, title, i):
    return f'<h2><b style="background:{CHIPS[i % 4]}">{n}</b>{e(title)}</h2>'


def render_html(ctx: CompanyContext, request: str, analysis: Analysis,
                narrative: ReportNarrative, generated: datetime | None = None) -> str:
    now = generated or datetime.now()
    rank = analysis.ranking
    top = rank[0] if rank else None
    wp, ws, wv = ctx.weights()
    cur = ctx.currency

    medal = ["#FFD166", "#B8C2D3", "#F59E6B"]
    order = [1, 0, 2] if len(rank) >= 3 else ([1, 0] if len(rank) == 2 else [0])
    pods = ""
    for i in order[: len(rank)]:
        p = rank[i]
        pods += (f'<div class="pod {"first" if i == 0 else ""}" style="--c:{medal[i]}"><div class="no">{p.rank}</div>'
                 f'<h3>{e(p.name[:80])}</h3><div class="sl">{e(p.seller or p.brand)}</div>'
                 f'<div class="px">{_money(p.price, p.currency or cur)}</div><span class="sc">{p.final_score:.2f} / 10</span></div>')

    rows = ""
    for p in rank:
        pct = max(0, min(100, p.final_score * 10))
        rows += (f'<tr class="{"top1" if p.rank == 1 else ""}"><td class="rk">{p.rank}</td>'
                 f'<td><a href="{_url(p.url)}" target="_blank" rel="noopener">{e(p.name)}</a><br><small>{e(p.seller or p.brand)}</small></td>'
                 f'<td class="n">{_money(p.price, p.currency or cur)}</td><td class="n">{p.spec_score:.1f}</td>'
                 f'<td class="n">{p.price_score:.1f}</td><td class="n">{p.value_score:.1f}</td>'
                 f'<td><b>{p.final_score:.2f}</b><div class="bar"><i style="width:{pct:.0f}%"></i></div></td></tr>')

    counts = Counter(k for p in rank for k in p.specs)
    keys = [k for k, _ in counts.most_common(8)]
    matrix = ""
    if keys:
        head = "".join(f"<th>{e(p.name[:26])}</th>" for p in rank)
        body = "".join(f"<tr><td><b>{e(k)}</b></td>" + "".join(f"<td>{e(p.specs.get(k, '—'))}</td>" for p in rank) + "</tr>" for k in keys)
        matrix = f'{_h2("03", "Specification matrix", 2)}<div class="scroll"><table><tr><th>Spec</th>{head}</tr>{body}</table></div>'

    cards = "".join(
        f'<div class="card" style="--k:{CHIPS[(p.rank - 1) % 4]}"><h3>#{p.rank} {e(p.name)}</h3>'
        + "".join(f'<span class="flag">{e(f)}</span>' for f in p.flags)
        + f'<ul class="pro">{_list(p.pros)}</ul><ul class="con">{_list(p.cons)}</ul></div>' for p in rank)

    total = ""
    if top and top.price:
        total = (f"<p><b>Estimated order value:</b> {ctx.quantity} × {_money(top.price, top.currency or cur)} = "
                 f"{_money(top.price * ctx.quantity, top.currency or cur)} <small>(excl. shipping, tax, import duty)</small></p>")

    sources = "".join(f'<li><a href="{_url(p.url)}" target="_blank" rel="noopener">{e(p.url)}</a></li>' for p in rank)
    assume = f'{_h2("08", "Assumptions", 3)}<ul>{_list(analysis.assumptions)}</ul>' if analysis.assumptions else ""
    why = f'{_h2("06", "Why the others ranked lower", 0)}<ul>{_list(narrative.why_not_others)}</ul>' if narrative.why_not_others else ""
    ref = now.strftime("AX-%Y%m%d-%H%M")

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(narrative.title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@600;900&family=Outfit:wght@400;500;600&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="sheet"><div class="band"></div>
<div class="top"><span>Axiom Procure · {ref}</span><span>{now:%d %b %Y}</span></div>
<h1>{e(narrative.title)}</h1><p class="req">{e(request)}</p>
<div class="meta"><div><small>Company</small>{e(ctx.name)}</div><div><small>Quantity</small>{ctx.quantity} units</div>
<div><small>Budget / unit</small>{_money(ctx.budget_per_unit, cur)}</div><div><small>Weights P / S / V</small>{wp:.0%} / {ws:.0%} / {wv:.0%}</div></div>
{_h2("01", "Executive summary", 0)}<p>{e(narrative.executive_summary)}</p>
{_h2("02", "Ranking", 1)}<div class="podium">{pods}</div><br>
<div class="scroll"><table><tr><th>#</th><th>Product</th><th>Unit price</th><th>Specs</th><th>Price</th><th>Value</th><th>Final /10</th></tr>{rows}</table></div>
{matrix}
{_h2("04", "Product notes", 3)}<div class="cards">{cards}</div>
{_h2("05", "Recommendation", 0)}<div class="rec"><p>{e(narrative.recommendation)}</p>{total}</div>
{why}
{_h2("06", "Risks", 3)}<ul class="risk">{_list(narrative.risks)}</ul>
{_h2("07", "Next steps", 2)}<ol class="steps">{_list(narrative.next_steps)}</ol>
{assume}
{_h2("09", "Sources", 1)}<ol>{sources}</ol>
<footer><span>CrewAI · Search → Scrape → Analyse → Report</span><span>Verify prices before ordering</span></footer>
</div></body></html>"""
