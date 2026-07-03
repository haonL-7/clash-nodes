#!/usr/bin/env python3
"""从 latest.yaml 生成 index.html"""
import json, datetime, re
from datetime import timezone, timedelta

# 移除节点名中的 emoji（只匹配 emoji Unicode 块，不误伤 CJK 文字）
def strip_emoji(s):
    emoji_pat = re.compile("["
        "\U0001F600-\U0001F64F"   # Emoticons
        "\U0001F300-\U0001F5FF"   # Misc Symbols & Pictographs
        "\U0001F680-\U0001F6FF"   # Transport & Map
        "\U0001F1E0-\U0001F1FF"   # Flags (regional indicators)
        "\U00002600-\U000027BF"   # Misc Symbols + Dingbats
        "\U0001F900-\U0001F9FF"   # Supplemental Symbols
        "\U0001FA00-\U0001FA6F"   # Chess Symbols
        "\U0001FA70-\U0001FAFF"   # Symbols Extended-A
        "\U0000FE00-\U0000FE0F"   # Variation Selectors
        "\U0000200D"              # Zero Width Joiner
        "\U00002B50\U00002B55"   # Stars
        "\U0000231A\U0000231B"   # Watch, Hourglass
        "\U00002328\U000023CF"   # Keyboard, Eject
        "\U000023E9-\U000023F3"   # Double triangles
        "\U000023F8-\U000023FA"   # Controls
        "\U000025AA\U000025AB"   # Squares
        "\U000025B6\U000025C0"   # Triangles
        "\U000025FB-\U000025FE"   # Medium squares
        "\U000000A9\U000000AE"   # Copyright, Registered
        "\U00002122\U00002139"   # TM, Information
        "\U00003030\U0000303D"   # Japanese-style punctuation (〰〽 etc)
        "]+", flags=re.UNICODE)
    return emoji_pat.sub('', s).strip()

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
:root {{
  --bg: #080c12; --surface: #10161e; --elevated: #161e2a;
  --border: #1e2a3a; --border-light: #263348;
  --text: #e2e8f0; --muted: #7388a5; --faint: #3d516d;
  --primary: #6c8cff; --primary-dim: rgba(108,140,255,.12);
  --green: #34d399; --green-dim: rgba(52,211,153,.12);
  --amber: #f59e0b; --amber-dim: rgba(245,158,11,.12);
  --rose: #f87171; --rose-dim: rgba(248,113,113,.12);
  --radius: 10px; --radius-sm: 6px;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', system-ui, sans-serif;
  min-height: 100vh;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}}

/* Background glow */
body::before {{
  content: ''; position: fixed; top: -30vh; left: 50%; transform: translateX(-50%);
  width: 80vw; height: 60vh; border-radius: 50%;
  background: radial-gradient(ellipse, rgba(108,140,255,.06) 0%, transparent 70%);
  pointer-events: none; z-index: 0;
}}

.container {{ max-width: 960px; margin: 0 auto; padding: 2.5rem 1.25rem; position: relative; z-index: 1; }}

/* Header */
header {{ text-align: center; margin-bottom: 2.5rem; }}
header h1 {{ font-size: 1.6rem; font-weight: 700; letter-spacing: -.02em; margin-bottom: .35rem; }}
header h1 span {{ color: var(--primary); }}
header .live {{ display: inline-flex; align-items: center; gap: .4rem; font-size: .8rem; color: var(--green); margin-top: .3rem; }}
header .live::before {{
  content: ''; width: 7px; height: 7px; border-radius: 50%; background: var(--green);
  animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{ 0%,100%{{opacity:1;box-shadow:0 0 0 0 rgba(52,211,153,.4)}} 50%{{opacity:.6;box-shadow:0 0 0 6px rgba(52,211,153,0)}} }}
header p {{ color: var(--muted); font-size: .84rem; margin-top: .4rem; }}
header a {{ color: var(--primary); text-decoration: none; }}
header a:hover {{ text-decoration: underline; }}

/* Stats grid */
.stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin-bottom: 1.5rem; }}
@media (max-width: 600px) {{ .stats {{ grid-template-columns: repeat(2, 1fr); }} }}
.stat {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.15rem 1rem;
  text-align: center; transition: all .25s ease; cursor: default;
  position: relative; overflow: hidden;
}}
.stat:hover {{ border-color: var(--border-light); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,.3); }}
.stat::after {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  opacity: 0; transition: opacity .3s;
}}
.stat:hover::after {{ opacity: 1; }}
.stat.total::after {{ background: var(--green); }}
.stat.jp::after {{ background: var(--rose); }}
.stat.us::after {{ background: var(--primary); }}
.stat.fr::after {{ background: var(--amber); }}
.stat .num {{ font-size: 2.2rem; font-weight: 800; letter-spacing: -.03em; line-height: 1; }}
.stat .num.total {{ color: var(--green); }}
.stat .num.jp {{ color: var(--rose); }}
.stat .num.us {{ color: var(--primary); }}
.stat .num.fr {{ color: var(--amber); }}
.stat .label {{ color: var(--muted); font-size: .76rem; margin-top: .4rem; font-weight: 500; text-transform: uppercase; letter-spacing: .05em; }}

/* Cards */
.card {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.4rem; margin-bottom: 1rem;
  transition: border-color .2s;
}}
.card:hover {{ border-color: var(--border-light); }}
.card h2 {{ font-size: .95rem; font-weight: 600; margin-bottom: .9rem; color: var(--text); }}

/* Subscribe rows */
.sub-list {{ display: flex; flex-direction: column; gap: .6rem; }}
.sub-item {{ display: flex; gap: .5rem; align-items: center; }}
.sub-item label {{ font-size: .76rem; color: var(--muted); min-width: 70px; font-weight: 500; }}
.sub-item input {{
  flex: 1; background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: .55rem .75rem;
  font-size: .8rem; color: var(--text); font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
  transition: border-color .2s; min-width: 200px;
}}
.sub-item input:focus {{ outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-dim); }}
.sub-item button {{
  background: var(--elevated); color: var(--text); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: .55rem 1rem;
  cursor: pointer; font-size: .78rem; font-weight: 500; white-space: nowrap;
  transition: all .2s; letter-spacing: .01em;
}}
.sub-item button:hover {{ background: var(--primary); border-color: var(--primary); color: #fff; }}
.sub-item button.copied {{ background: var(--green); border-color: var(--green); color: #fff; }}

/* Filter bar */
.toolbar {{ display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; margin-bottom: 1rem; }}
.search-box {{
  margin-left: auto; background: var(--bg); border: 1px solid var(--border);
  border-radius: 20px; padding: .4rem .85rem; font-size: .8rem; color: var(--text);
  outline: none; transition: all .2s; width: 180px;
}}
.search-box:focus {{ border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-dim); width: 220px; }}
.search-box::placeholder {{ color: var(--faint); }}
@media (max-width: 500px) {{ .search-box {{ width: 120px; }} .search-box:focus {{ width: 150px; }} }}

.filter-btn {{
  background: transparent; border: 1px solid var(--border); color: var(--muted);
  padding: .35rem .9rem; border-radius: 20px; cursor: pointer;
  font-size: .78rem; font-weight: 500; transition: all .2s;
}}
.filter-btn:hover {{ color: var(--text); border-color: var(--border-light); }}
.filter-btn.active {{ background: var(--primary); border-color: var(--primary); color: #fff; }}
.filter-btn .count {{ font-size: .68rem; opacity: .7; margin-left: 2px; }}

/* Table */
.table-wrap {{ max-height: 460px; overflow-y: auto; border-radius: var(--radius-sm); }}
.table-wrap::-webkit-scrollbar {{ width: 5px; }}
.table-wrap::-webkit-scrollbar-track {{ background: transparent; }}
.table-wrap::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 10px; }}
table {{ width: 100%; border-collapse: collapse; font-size: .82rem; }}
th, td {{ padding: .5rem .8rem; text-align: left; border-bottom: 1px solid var(--border); }}
th {{ color: var(--muted); font-weight: 500; font-size: .74rem; text-transform: uppercase; letter-spacing: .04em; position: sticky; top: 0; background: var(--surface); z-index: 1; }}
tr {{ transition: background .15s; }}
tr:hover td {{ background: rgba(108,140,255,.03); }}
tr.fade-out {{ opacity: .25; transition: opacity .2s; }}

.badge {{ display: inline-flex; align-items: center; gap: 5px; padding: 3px 10px; border-radius: 12px; font-size: .7rem; font-weight: 600; letter-spacing: .01em; }}
.badge::before {{ content: ''; width: 6px; height: 6px; border-radius: 50%; }}
.badge.jp {{ background: var(--rose-dim); color: var(--rose); }}
.badge.jp::before {{ background: var(--rose); }}
.badge.us {{ background: var(--primary-dim); color: var(--primary); }}
.badge.us::before {{ background: var(--primary); }}
.badge.fr {{ background: var(--amber-dim); color: var(--amber); }}
.badge.fr::before {{ background: var(--amber); }}
.badge.other {{ background: rgba(115,136,165,.08); color: var(--muted); }}
.badge.other::before {{ background: var(--muted); }}

/* Footer */
footer {{ text-align: center; color: var(--faint); font-size: .72rem; margin-top: 2.5rem; padding-bottom: 1rem; }}
footer a {{ color: var(--muted); text-decoration: none; }}
footer a:hover {{ color: var(--primary); }}

/* Toast */
#toast {{
  position: fixed; top: 1.25rem; left: 50%; transform: translateX(-50%) translateY(-120%);
  background: var(--elevated); color: var(--text); border: 1px solid var(--border-light);
  padding: .6rem 1.4rem; border-radius: 20px; font-size: .82rem; font-weight: 500;
  z-index: 99; transition: transform .35s cubic-bezier(.16,1,.3,1);
  box-shadow: 0 8px 30px rgba(0,0,0,.4);
}}
#toast.show {{ transform: translateX(-50%) translateY(0); }}

/* Empty state */
.empty-state {{ text-align: center; padding: 2rem; color: var(--muted); font-size: .85rem; }}
</style>
</head>
<body>
<div id="toast">Copied to clipboard</div>

<div class="container">
<header>
  <h1>Clash <span>Nodes</span></h1>
  <div class="live">Live &middot; auto-updated daily</div>
  <p>Data via <a href="https://yoyapai.com" target="_blank">yoyapai.com</a></p>
</header>

<div class="stats">
  <div class="stat total"><div class="num total" data-target="{total}">0</div><div class="label">Total</div></div>
  <div class="stat jp"><div class="num jp" data-target="{jp_cnt}">0</div><div class="label">Japan</div></div>
  <div class="stat us"><div class="num us" data-target="{us_cnt}">0</div><div class="label">United States</div></div>
  <div class="stat fr"><div class="num fr" data-target="{fr_cnt}">0</div><div class="label">France</div></div>
</div>

<div class="card">
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

<div class="card">
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
      <thead><tr><th style="width:65%">Name</th><th>Region</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="empty-state" id="empty" style="display:none">No matching nodes.</div>
  </div>
</div>

<footer>
  Last update: {now} &middot; Powered by <a href="https://github.com/haonL-7/clash-nodes">GitHub Actions</a>
</footer>
</div>

<script>
var NODES = {nodes_json};
var BADGES = {{
  jp: '<span class="badge jp">Japan</span>',
  us: '<span class="badge us">United States</span>',
  fr: '<span class="badge fr">France</span>',
  other: '<span class="badge other">Other</span>'
}};
var curFilter = 'all', curSearch = '';

function esc(s) {{ var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

function render() {{
  var h = '', c = 0;
  var q = curSearch.toLowerCase();
  NODES.forEach(function(n) {{
    if (curFilter !== 'all' && n.r !== curFilter) return;
    if (q && n.n.toLowerCase().indexOf(q) === -1) return;
    h += '<tr><td>' + esc(n.n) + '</td><td>' + (BADGES[n.r] || BADGES.other) + '</td></tr>';
    c++;
  }});
  document.getElementById('tbody').innerHTML = h;
  document.getElementById('empty').style.display = c ? 'none' : 'block';
}}

function setFilter(f, btn) {{
  curFilter = f;
  document.querySelectorAll('.filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
  btn.classList.add('active');
  render();
}}

function setSearch(q) {{ curSearch = q; render(); }}

function doCopy(id, btn) {{
  var inp = document.getElementById(id);
  inp.select(); inp.setSelectionRange(0, 99999);
  navigator.clipboard.writeText(inp.value).then(function() {{
    var orig = btn.textContent;
    btn.textContent = 'Copied'; btn.classList.add('copied');
    var toast = document.getElementById('toast');
    toast.classList.add('show');
    setTimeout(function() {{
      toast.classList.remove('show');
      btn.textContent = orig; btn.classList.remove('copied');
    }}, 1800);
  }});
}}

/* Animate counters on load */
function animateCounters() {{
  document.querySelectorAll('.stat .num[data-target]').forEach(function(el) {{
    var target = parseInt(el.getAttribute('data-target'));
    var dur = 800, start = performance.now();
    function tick(now) {{
      var p = Math.min((now - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.floor(eased * target);
      if (p < 1) requestAnimationFrame(tick);
      else el.textContent = target;
    }}
    requestAnimationFrame(tick);
  }});
}}

render();
animateCounters();
</script>
</body>
</html>'''

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK: index.html ({len(html)} bytes), total={total}, JP={jp_cnt}, US={us_cnt}, FR={fr_cnt})")
