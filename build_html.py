#!/usr/bin/env python3
"""从 latest.yaml 生成 index.html"""
import json, datetime, re
from datetime import timezone, timedelta

# ── 移除节点名中的 emoji ──
def strip_emoji(s):
    emoji_pat = re.compile("["
        "\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF\U00002600-\U000027BF"
        "\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF"
        "\U0000FE00-\U0000FE0F\U0000200D\U00002B50\U00002B55"
        "\U0000231A\U0000231B\U00002328\U000023CF"
        "\U000023E9-\U000023F3\U000023F8-\U000023FA"
        "\U000025AA\U000025AB\U000025B6\U000025C0\U000025FB-\U000025FE"
        "\U000000A9\U000000AE\U00002122\U00002139\U00003030\U0000303D"
        "]+", flags=re.UNICODE)
    return emoji_pat.sub('', s).strip()

# ── 读取 YAML ──
with open("latest.yaml", "r", encoding="utf-8") as f:
    lines = f.readlines()

nodes = []
for line in lines:
    if line.startswith("  - name:"):
        name = strip_emoji(line.replace("  - name: ", "").strip())
        r = "other"
        nl = name.lower()
        if any(k in nl for k in ["日本","jp","japan","tokyo","osaka"]):
            r = "jp"
        elif any(k in nl for k in ["美国","美國","usa","united states"]):
            r = "us"
        elif any(k in nl for k in ["法国","法國","france"]):
            r = "fr"
        nodes.append({"n": name, "r": r})

total, jp_cnt = len(nodes), sum(1 for n in nodes if n["r"] == "jp")
us_cnt = sum(1 for n in nodes if n["r"] == "us")
fr_cnt = sum(1 for n in nodes if n["r"] == "fr")
other_cnt = total - jp_cnt - us_cnt - fr_cnt
nodes_json = json.dumps(nodes, ensure_ascii=False)
now = datetime.datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M CST")

html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Clash Nodes &mdash; Free Proxy Subscription</title>
<style>
/* ── Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Variables ── */
:root {{
  --bg-deep: #060b14;
  --bg: #0a0f1e;
  --surface-glass: rgba(18,24,42,0.55);
  --surface-solid: rgba(16,22,38,0.8);
  --border-glass: rgba(255,255,255,0.06);
  --border-strong: rgba(255,255,255,0.1);
  --text: #e8edf5;
  --text-dim: #8899b4;
  --text-muted: #556680;
  --primary: #6b8cff;
  --primary-soft: rgba(107,140,255,0.15);
  --green: #34d399;
  --green-soft: rgba(52,211,153,0.12);
  --amber: #f59e0b;
  --amber-soft: rgba(245,158,11,0.12);
  --rose: #f87171;
  --rose-soft: rgba(248,113,113,0.12);
  --radius-sm: 8px; --radius: 14px; --radius-lg: 20px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  --shadow: 0 2px 8px rgba(0,0,0,0.25), 0 1px 2px rgba(0,0,0,0.2);
  --shadow-md: 0 8px 32px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.3);
  --shadow-lg: 0 16px 48px rgba(0,0,0,0.5);
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}}

/* ── Light theme ── */
[data-theme="light"] {{
  --bg-deep: #f0f4f8;
  --bg: #f6f9fc;
  --surface-glass: rgba(255,255,255,0.65);
  --surface-solid: rgba(255,255,255,0.85);
  --border-glass: rgba(0,0,0,0.06);
  --border-strong: rgba(0,0,0,0.12);
  --text: #1a2332;
  --text-dim: #556680;
  --text-muted: #8899b4;
  --primary: #4b6eec;
  --primary-soft: rgba(75,110,236,0.1);
  --green: #10b981;
  --green-soft: rgba(16,185,129,0.1);
  --amber: #d97706;
  --amber-soft: rgba(217,119,6,0.08);
  --rose: #ef4444;
  --rose-soft: rgba(239,68,68,0.08);
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow: 0 2px 8px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
  --shadow-md: 0 8px 32px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
  --shadow-lg: 0 16px 48px rgba(0,0,0,0.1);
}}
[data-theme="light"] body::before {{
  background:
    radial-gradient(ellipse 80% 50% at 20% -10%, rgba(75,110,236,0.04) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 60%, rgba(16,185,129,0.03) 0%, transparent 50%),
    radial-gradient(ellipse 50% 50% at 50% 100%, rgba(239,68,68,0.02) 0%, transparent 50%);
}}
[data-theme="light"] body::after {{ border-color: rgba(0,0,0,0.03); }}
[data-theme="light"] header h1 {{
  background: linear-gradient(135deg, #1a2332 0%, #4b6eec 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
[data-theme="light"] .search-box,
[data-theme="light"] .filter-btn,
[data-theme="light"] .client-item,
[data-theme="light"] .table-wrap {{ background: rgba(0,0,0,0.03); }}
[data-theme="light"] th {{ background: rgba(240,244,248,0.95); }}
[data-theme="light"] .sub-item input {{ background: rgba(0,0,0,0.03); }}
[data-theme="light"] .sub-item button {{ background: rgba(75,110,236,0.06); color: var(--primary); border-color: rgba(75,110,236,0.15); }}
[data-theme="light"] .sub-item button:hover {{ background: var(--primary); color: #fff; }}

/* ── Theme toggle ── */
.theme-toggle {{
  position: fixed; top: 1.25rem; right: 1.25rem; z-index: 50;
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--surface-glass); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-glass); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .35s var(--ease); box-shadow: var(--shadow);
  color: var(--text-dim); font-size: 1.1rem;
}}
.theme-toggle:hover {{ border-color: var(--border-strong); box-shadow: var(--shadow-md); transform: scale(1.08); }}
.theme-toggle svg {{ width: 18px; height: 18px; stroke: currentColor; fill: none; stroke-width: 1.8; }}
.sun-icon {{ display: none; }}
[data-theme="light"] .moon-icon {{ display: none; }}
[data-theme="light"] .sun-icon {{ display: inline; }}

* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}

body {{
  background: var(--bg-deep);
  color: var(--text);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  min-height: 100vh; line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
  position: relative;
}}

/* ── Ambient background ── */
body::before {{
  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background:
    radial-gradient(ellipse 80% 50% at 20% -10%, rgba(107,140,255,0.08) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 60%, rgba(52,211,153,0.05) 0%, transparent 50%),
    radial-gradient(ellipse 50% 50% at 50% 100%, rgba(248,113,113,0.04) 0%, transparent 50%);
  animation: bgBreath 16s ease-in-out infinite;
}}
@keyframes bgBreath {{
  0%,100% {{ opacity:0.7; }}
  33% {{ opacity:1; }}
  66% {{ opacity:0.8; }}
}}

/* Geometric accents */
body::after {{
  content: ''; position: fixed; top: -200px; right: -200px;
  width: 500px; height: 500px; border-radius: 50%;
  border: 1px solid rgba(107,140,255,0.05);
  pointer-events: none; z-index: 0;
}}

.container {{ max-width: 980px; margin: 0 auto; padding: 2.5rem 1.25rem; position: relative; z-index: 1; }}

/* ── Header ── */
header {{ text-align: center; margin-bottom: 2.5rem; }}
header h1 {{
  font-size: 1.75rem; font-weight: 800; letter-spacing: -0.03em;
  background: linear-gradient(135deg, #e8edf5 0%, #8899b4 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: .25rem;
}}
header .live {{
  display: inline-flex; align-items: center; gap: .45rem;
  font-size: .78rem; color: var(--green); font-weight: 500; margin-top: .2rem;
}}
header .live::before {{
  content: ''; width: 7px; height: 7px; border-radius: 50%; background: var(--green);
  box-shadow: 0 0 8px rgba(52,211,153,0.5);
  animation: pulse 2.2s ease-in-out infinite;
}}
@keyframes pulse {{
  0%,100% {{ opacity:1; box-shadow:0 0 0 0 rgba(52,211,153,0.4); }}
  50% {{ opacity:.5; box-shadow:0 0 0 10px rgba(52,211,153,0); }}
}}
header p {{ color: var(--text-dim); font-size: .82rem; margin-top: .35rem; }}
header a {{ color: var(--primary); text-decoration: none; font-weight: 500; }}
header a:hover {{ text-decoration: underline; }}

/* ── Stats ── */
.stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin-bottom: 1.5rem; }}
@media (max-width: 600px) {{ .stats {{ grid-template-columns: repeat(2, 1fr); }} }}

.stat {{
  background: var(--surface-glass);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius); padding: 1.25rem 1rem;
  text-align: center; cursor: default;
  transition: all .35s var(--ease);
  position: relative; overflow: hidden;
  box-shadow: var(--shadow-sm);
}}
.stat:hover {{
  border-color: var(--border-strong);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}}
.stat::before {{
  content: ''; position: absolute; inset: 0;
  opacity: 0; transition: opacity .4s;
  border-radius: inherit; pointer-events: none;
}}
.stat.total::before {{ background: radial-gradient(circle at 50% 0%, rgba(52,211,153,0.08), transparent 70%); }}
.stat.jp::before {{ background: radial-gradient(circle at 50% 0%, rgba(248,113,113,0.08), transparent 70%); }}
.stat.us::before {{ background: radial-gradient(circle at 50% 0%, rgba(107,140,255,0.08), transparent 70%); }}
.stat.fr::before {{ background: radial-gradient(circle at 50% 0%, rgba(245,158,11,0.08), transparent 70%); }}
.stat:hover::before {{ opacity:1; }}
.stat .num {{
  font-size: 2.4rem; font-weight: 900; letter-spacing: -0.04em; line-height: 1;
  position: relative; z-index: 1;
}}
.stat .num.total {{ color: var(--green); }}
.stat .num.jp {{ color: var(--rose); }}
.stat .num.us {{ color: var(--primary); }}
.stat .num.fr {{ color: var(--amber); }}
.stat .label {{
  color: var(--text-muted); font-size: .73rem; margin-top: .35rem;
  font-weight: 600; text-transform: uppercase; letter-spacing: .08em;
  position: relative; z-index: 1;
}}

/* ── Glass card ── */
.card {{
  background: var(--surface-glass);
  backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg); padding: 1.5rem; margin-bottom: 1rem;
  box-shadow: var(--shadow);
  transition: border-color .3s, box-shadow .3s;
}}
.card:hover {{ border-color: var(--border-strong); box-shadow: var(--shadow-md); }}
.card h2 {{ font-size: .9rem; font-weight: 700; margin-bottom: .85rem; color: var(--text); letter-spacing: -0.01em; }}

/* ── Subscribe ── */
.sub-list {{ display: flex; flex-direction: column; gap: .55rem; }}
.sub-item {{ display: flex; gap: .5rem; align-items: center; }}
.sub-item label {{
  font-size: .74rem; color: var(--text-muted); min-width: 56px;
  font-weight: 600; text-transform: uppercase; letter-spacing: .06em;
}}
.sub-item input {{
  flex: 1; background: rgba(0,0,0,0.3); border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm); padding: .55rem .75rem;
  font-size: .78rem; color: var(--text);
  font-family: 'SF Mono','Fira Code','Cascadia Code',monospace;
  transition: all .25s; min-width: 200px;
}}
.sub-item input:focus {{ outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-soft); }}
.sub-item button {{
  background: rgba(107,140,255,0.1); color: var(--primary); border: 1px solid rgba(107,140,255,0.2);
  border-radius: var(--radius-sm); padding: .55rem 1rem;
  cursor: pointer; font-size: .76rem; font-weight: 600; white-space: nowrap;
  transition: all .25s; letter-spacing: .01em;
}}
.sub-item button:hover {{ background: var(--primary); border-color: var(--primary); color: #fff; box-shadow: 0 4px 16px rgba(107,140,255,0.3); }}
.sub-item button.copied {{ background: var(--green); border-color: var(--green); color: #fff; box-shadow: 0 4px 16px rgba(52,211,153,0.3); }}

/* ── Client grid ── */
.client-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: .55rem; }}
.client-item {{
  display: block; background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm); padding: .85rem 1rem;
  text-decoration: none; transition: all .3s var(--ease);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}}
.client-item:hover {{
  border-color: var(--primary); background: var(--primary-soft);
  transform: translateY(-2px); box-shadow: var(--shadow-md);
}}
.client-name {{ color: var(--text); font-size: .84rem; font-weight: 700; }}
.client-meta {{ color: var(--text-muted); font-size: .7rem; margin-top: .2rem; }}

/* ── Toolbar ── */
.toolbar {{ display: flex; gap: .4rem; flex-wrap: wrap; align-items: center; margin-bottom: 1rem; }}
.search-box {{
  margin-left: auto; background: rgba(0,0,0,0.3); border: 1px solid var(--border-glass);
  border-radius: 20px; padding: .4rem .9rem; font-size: .78rem; color: var(--text);
  outline: none; transition: all .3s var(--ease); width: 180px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}}
.search-box:focus {{ border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-soft); width: 220px; }}
.search-box::placeholder {{ color: var(--text-muted); }}
@media (max-width: 500px) {{ .search-box {{ width: 120px; }} .search-box:focus {{ width: 150px; }} }}

.filter-btn {{
  background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass); color: var(--text-dim);
  padding: .35rem .85rem; border-radius: 20px; cursor: pointer;
  font-size: .76rem; font-weight: 600; transition: all .25s var(--ease);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}}
.filter-btn:hover {{ color: var(--text); border-color: var(--border-strong); }}
.filter-btn.active {{ background: var(--primary); border-color: var(--primary); color: #fff; box-shadow: 0 4px 16px rgba(107,140,255,0.25); }}
.filter-btn .count {{ font-size: .66rem; opacity: .6; margin-left: 2px; }}

/* ── Table ── */
.table-wrap {{
  max-height: 460px; overflow-y: auto; border-radius: var(--radius-sm);
  background: rgba(0,0,0,0.2);
}}
.table-wrap::-webkit-scrollbar {{ width: 5px; }}
.table-wrap::-webkit-scrollbar-track {{ background: transparent; }}
.table-wrap::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 10px; }}
table {{ width: 100%; border-collapse: collapse; font-size: .8rem; }}
th, td {{ padding: .5rem .8rem; text-align: left; border-bottom: 1px solid var(--border-glass); }}
th {{
  color: var(--text-muted); font-weight: 600; font-size: .7rem;
  text-transform: uppercase; letter-spacing: .06em;
  position: sticky; top: 0; background: rgba(10,15,30,0.95);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  z-index: 1;
}}
tr {{ transition: background .2s; }}
tr:hover td {{ background: rgba(107,140,255,0.04); }}

.badge {{ display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 12px; font-size: .68rem; font-weight: 600; }}
.badge::before {{ content: ''; width: 6px; height: 6px; border-radius: 50%; }}
.badge.jp {{ background: var(--rose-soft); color: var(--rose); }}
.badge.jp::before {{ background: var(--rose); box-shadow: 0 0 6px rgba(248,113,113,0.5); }}
.badge.us {{ background: var(--primary-soft); color: var(--primary); }}
.badge.us::before {{ background: var(--primary); box-shadow: 0 0 6px rgba(107,140,255,0.5); }}
.badge.fr {{ background: var(--amber-soft); color: var(--amber); }}
.badge.fr::before {{ background: var(--amber); box-shadow: 0 0 6px rgba(245,158,11,0.5); }}
.badge.other {{ background: rgba(136,153,180,.08); color: var(--text-dim); }}
.badge.other::before {{ background: var(--text-muted); }}

.empty-state {{ text-align: center; padding: 2rem; color: var(--text-muted); font-size: .82rem; }}

/* ── Footer ── */
footer {{
  text-align: center; color: var(--text-muted); font-size: .7rem;
  margin-top: 2.5rem; padding-bottom: 1.5rem;
}}
footer a {{ color: var(--text-dim); text-decoration: none; font-weight: 500; }}
footer a:hover {{ color: var(--primary); }}

/* ── Toast ── */
#toast {{
  position: fixed; top: 1.5rem; left: 50%; transform: translateX(-50%) translateY(-150%);
  background: var(--surface-glass); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  color: var(--text); border: 1px solid var(--border-strong);
  padding: .6rem 1.5rem; border-radius: 24px; font-size: .8rem; font-weight: 600;
  z-index: 99; transition: transform .4s var(--ease-spring);
  box-shadow: var(--shadow-lg);
}}
#toast.show {{ transform: translateX(-50%) translateY(0); }}

/* ── Entrance animation ── */
@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(16px); }}
  to {{ opacity:1; transform:translateY(0); }}
}}
.entrance {{ animation: fadeUp .6s var(--ease) both; }}
.entrance-d1 {{ animation-delay: .05s; }}
.entrance-d2 {{ animation-delay: .12s; }}
.entrance-d3 {{ animation-delay: .19s; }}
.entrance-d4 {{ animation-delay: .26s; }}
</style>
</head>
<body>

<!-- Theme toggle -->
<button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme" id="themeBtn">
  <svg class="moon-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
  <svg class="sun-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
</button>

<div id="toast">Copied to clipboard</div>

<div class="container">
<header class="entrance">
  <h1>Clash Nodes</h1>
  <div class="live">Live &middot; auto-updated daily</div>
  <p>Data via <a href="https://yoyapai.com" target="_blank">yoyapai.com</a></p>
</header>

<div class="stats">
  <div class="stat total entrance entrance-d1"><div class="num total" data-target="{total}">0</div><div class="label">Total</div></div>
  <div class="stat jp entrance entrance-d2"><div class="num jp" data-target="{jp_cnt}">0</div><div class="label">Japan</div></div>
  <div class="stat us entrance entrance-d3"><div class="num us" data-target="{us_cnt}">0</div><div class="label">US</div></div>
  <div class="stat fr entrance entrance-d4"><div class="num fr" data-target="{fr_cnt}">0</div><div class="label">France</div></div>
</div>

<div class="card entrance entrance-d1">
  <h2>Subscription URLs</h2>
  <div class="sub-list">
    <div class="sub-item">
      <label>GitHub</label>
      <input id="sub-raw" value="https://raw.githubusercontent.com/haonL-7/clash-nodes/main/latest.yaml" readonly onclick="this.select()">
      <button onclick="doCopy('sub-raw', this)">Copy</button>
    </div>
    <div class="sub-item">
      <label>CDN</label>
      <input id="sub-cdn" value="https://cdn.jsdelivr.net/gh/haonL-7/clash-nodes@main/latest.yaml" readonly onclick="this.select()">
      <button onclick="doCopy('sub-cdn', this)">Copy</button>
    </div>
  </div>
</div>

<div class="card entrance entrance-d2">
  <h2>Desktop Clients</h2>
  <div class="client-grid">
    <a class="client-item" href="https://github.com/clash-verge-rev/clash-verge-rev/releases/latest" target="_blank">
      <div class="client-name">Clash Verge Rev</div>
      <div class="client-meta">Windows / macOS / Linux</div>
    </a>
    <a class="client-item" href="https://github.com/chen08209/FlClash/releases/latest" target="_blank">
      <div class="client-name">FlClash</div>
      <div class="client-meta">Windows / macOS / Linux / Android</div>
    </a>
    <a class="client-item" href="https://github.com/LibNyanpasu/clash-nyanpasu/releases/latest" target="_blank">
      <div class="client-name">Clash Nyanpasu</div>
      <div class="client-meta">Windows / macOS / Linux</div>
    </a>
  </div>
  <p style="color:var(--text-muted);font-size:.72rem;margin-top:.75rem;font-weight:500;">Install any client above, then import the subscription URL.</p>
</div>

<div class="card entrance entrance-d3">
  <h2>Node Directory</h2>
  <div class="toolbar">
    <button class="filter-btn active" onclick="setFilter('all', this)">All<span class="count">{total}</span></button>
    <button class="filter-btn" onclick="setFilter('jp', this)">Japan<span class="count">{jp_cnt}</span></button>
    <button class="filter-btn" onclick="setFilter('us', this)">US<span class="count">{us_cnt}</span></button>
    <button class="filter-btn" onclick="setFilter('fr', this)">France<span class="count">{fr_cnt}</span></button>
    <button class="filter-btn" onclick="setFilter('other', this)">Other<span class="count">{other_cnt}</span></button>
    <input class="search-box" type="text" placeholder="Search nodes..." oninput="setSearch(this.value)">
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr><th style="width:68%">Name</th><th>Region</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="empty-state" id="empty" style="display:none">No matching nodes.</div>
  </div>
</div>

<footer>
  <a href="https://haonl-7.github.io">haonl-7.github.io</a> &middot;
  Last update: {now} &middot;
  Powered by <a href="https://github.com/haonL-7/clash-nodes">GitHub Actions</a>
</footer>
</div>

<script>
var NODES={nodes_json};
var BADGES={{
  jp:'<span class="badge jp">Japan</span>',
  us:'<span class="badge us">United States</span>',
  fr:'<span class="badge fr">France</span>',
  other:'<span class="badge other">Other</span>'
}};
var curFilter='all',curSearch='';

function esc(s){{var d=document.createElement('div');d.textContent=s;return d.innerHTML;}}

function render(){{
  var h='',c=0,q=curSearch.toLowerCase();
  NODES.forEach(function(n){{
    if(curFilter!=='all'&&n.r!==curFilter)return;
    if(q&&n.n.toLowerCase().indexOf(q)===-1)return;
    h+='<tr><td>'+esc(n.n)+'</td><td>'+(BADGES[n.r]||BADGES.other)+'</td></tr>';
    c++;
  }});
  document.getElementById('tbody').innerHTML=h;
  document.getElementById('empty').style.display=c?'none':'block';
}}

function setFilter(f,btn){{
  curFilter=f;
  document.querySelectorAll('.filter-btn').forEach(function(b){{b.classList.remove('active')}});
  btn.classList.add('active');
  render();
}}

function setSearch(q){{curSearch=q;render();}}

function doCopy(id,btn){{
  var inp=document.getElementById(id);
  inp.select();inp.setSelectionRange(0,99999);
  navigator.clipboard.writeText(inp.value).then(function(){{
    var orig=btn.textContent;
    btn.textContent='Copied';btn.classList.add('copied');
    var toast=document.getElementById('toast');
    toast.classList.add('show');
    setTimeout(function(){{
      toast.classList.remove('show');
      btn.textContent=orig;btn.classList.remove('copied');
    }},1800);
  }});
}}

function animateCounters(){{
  document.querySelectorAll('.stat .num[data-target]').forEach(function(el){{
    var target=parseInt(el.getAttribute('data-target'));
    var dur=1000,start=performance.now();
    function tick(now){{
      var p=Math.min((now-start)/dur,1);
      var eased=1-Math.pow(1-p,3);
      el.textContent=Math.floor(eased*target);
      if(p<1)requestAnimationFrame(tick);
      else el.textContent=target;
    }}
    requestAnimationFrame(tick);
  }});
}}

/* ── Theme ── */
(function(){{
  var saved=localStorage.getItem('theme')||'dark';
  document.documentElement.setAttribute('data-theme',saved);
}})();
function toggleTheme(){{
  var el=document.documentElement;
  var cur=el.getAttribute('data-theme')==='light'?'dark':'light';
  el.setAttribute('data-theme',cur);
  localStorage.setItem('theme',cur);
}}

render();
animateCounters();
</script>
</body>
</html>'''

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK: index.html ({len(html)} bytes), total={total}, JP={jp_cnt}, US={us_cnt}, FR={fr_cnt})")
