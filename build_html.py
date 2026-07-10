#!/usr/bin/env python3
"""Build index.html — each verified node is individually copyable."""
import json, datetime, re, os, yaml, urllib.request, ssl
from datetime import timezone, timedelta

def strip_emoji(s):
    emoji_pat = re.compile("["
        "\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF\U00002600-\U000027BF"
        "\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF"
        "\U0000FE00-\U0000FE0F\U0000200D\U00002B50\U00002B55"
        "]+", flags=re.UNICODE)
    return emoji_pat.sub('', s).strip()

# Parse merged YAML for full proxy data
with open("latest.yaml", "r", encoding="utf-8") as f:
    doc = yaml.safe_load(f)

proxies = doc.get("proxies", []) if isinstance(doc, dict) else []
nodes = []
for p in proxies:
    if not isinstance(p, dict): continue
    name = strip_emoji(p.get("name", ""))
    if not name: continue
    r = "other"
    nl = name.lower()
    if any(k in nl for k in ["日本","jp","japan","tokyo","osaka","東京","大阪"]): r = "jp"
    elif any(k in nl for k in ["美国","美國","usa","united states"]): r = "us"
    elif any(k in nl for k in ["法国","法國","france"]): r = "fr"

    # Build a clean proxy entry for copy
    entry = {}
    for k in ("name","server","port","type","uuid","password","cipher","network",
              "servername","sni","tls","ws-opts","skip-cert-verify","udp","client-fingerprint"):
        if k in p and p[k] is not None:
            entry[k] = p[k]
    nodes.append({"name": name, "region": r, "data": entry})

total = len(nodes)
jp_cnt = sum(1 for n in nodes if n["region"] == "jp")
us_cnt = sum(1 for n in nodes if n["region"] == "us")
fr_cnt = sum(1 for n in nodes if n["region"] == "fr")

# Serialize the full proxy data for each node into JS
nodes_js = json.dumps([{"n": n["name"], "r": n["region"], "d": n["data"]} for n in nodes], ensure_ascii=False)

now = datetime.datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M CST")

html = f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Free proxy nodes — individually verified, one-click copy to client.">
<meta name="robots" content="index,follow">
<meta property="og:title" content="Clash Nodes — Free Proxy">
<title>Clash Nodes</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {{
  --bg-deep: #060b14; --bg: #0a0f1e;
  --surface-glass: rgba(18,24,42,0.55); --surface-solid: rgba(16,22,38,0.8);
  --border-glass: rgba(255,255,255,0.06); --border-strong: rgba(255,255,255,0.1);
  --text: #e8edf5; --text-dim: #8899b4; --text-muted: #556680;
  --primary: #6b8cff; --primary-soft: rgba(107,140,255,0.15);
  --green: #34d399; --green-soft: rgba(52,211,153,0.12);
  --amber: #f59e0b; --amber-soft: rgba(245,158,11,0.12);
  --rose: #f87171; --rose-soft: rgba(248,113,113,0.12);
  --radius-sm: 8px; --radius: 14px; --radius-lg: 20px;
  --nav-height: 56px;
}}

[data-theme="light"] {{
  --bg-deep: #f0f4f8; --bg: #f6f9fc;
  --surface-glass: rgba(255,255,255,0.65); --surface-solid: rgba(255,255,255,0.85);
  --border-glass: rgba(0,0,0,0.06); --border-strong: rgba(0,0,0,0.12);
  --text: #1a2332; --text-dim: #556680; --text-muted: #8899b4;
  --primary: #4b6eec; --primary-soft: rgba(75,110,236,0.1);
  --green: #10b981; --green-soft: rgba(16,185,129,0.1);
  --amber: #d97706; --amber-soft: rgba(217,119,6,0.08);
  --rose: #ef4444; --rose-soft: rgba(239,68,68,0.08);
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}

body {{
  background: radial-gradient(ellipse at 50% 0%, var(--bg) 0%, var(--bg-deep) 70%);
  color: var(--text); font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  font-size: 15px; line-height: 1.6; min-height: 100vh; padding-top: var(--nav-height);
  -webkit-font-smoothing: antialiased;
}}

.nav {{
  height: var(--nav-height); display: flex; align-items: center; justify-content: space-between;
  padding: 0 1.5rem; background: rgba(10,15,30,0.7); border-bottom: 1px solid var(--border-glass);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  position: fixed; top:0; left:0; right:0; z-index: 100;
}}
[data-theme="light"] .nav {{ background: rgba(240,244,248,0.7); }}
.nav-brand {{ font-weight: 800; font-size: 1rem; color: var(--text); text-decoration: none; display: flex; align-items: center; gap: .45rem; }}
.dot {{ width:8px; height:8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px rgba(52,211,153,0.5); }}
.nav-actions {{ display: flex; gap: .4rem; align-items: center; }}
.nav-btn {{
  background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass); color: var(--text-dim);
  padding: .35rem .65rem; border-radius: var(--radius-sm); cursor: pointer;
  font-size: .75rem; font-weight: 600; transition: all .25s;
  display: flex; align-items: center; gap: .3rem; font-family: inherit;
}}
[data-theme="light"] .nav-btn {{ background: rgba(0,0,0,0.03); }}
.nav-btn:hover {{ color: var(--text); border-color: var(--border-strong); }}
.nav-btn svg {{ fill: none; stroke: currentColor; stroke-width: 1.8; }}
.sun-icon {{ display: none; }}
[data-theme="light"] .moon-icon {{ display: none; }}
[data-theme="light"] .sun-icon {{ display: inline; }}

.container {{ max-width: 800px; margin: 0 auto; padding: 1.5rem 1.2rem; }}

header {{ text-align: center; margin-bottom: 2rem; }}
header h1 {{ font-size: 2rem; font-weight: 900; letter-spacing: -.03em; }}
.subtitle {{ color: var(--text-dim); font-size: .82rem; margin-top: .3rem; }}

.stats {{ display: flex; flex-wrap: wrap; gap: .6rem; margin-bottom: 1.5rem; justify-content: center; }}
.stat {{
  background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass);
  border-radius: var(--radius); padding: .85rem .9rem; text-align: center;
  min-width: 80px; flex: 1; max-width: 140px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}}
[data-theme="light"] .stat {{ background: rgba(0,0,0,0.03); }}
.stat .num {{ font-size: 1.8rem; font-weight: 900; line-height: 1.1; }}
.stat .label {{ font-size: .7rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: .05em; margin-top: .2rem; }}
.num.total {{ color: var(--text); }}
.num.jp {{ color: var(--rose); }}
.num.us {{ color: var(--primary); }}
.num.fr {{ color: var(--amber); }}

.card {{
  background: var(--surface-glass); border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg); padding: 1.3rem; margin-bottom: 1.2rem;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
}}
.card h2 {{ font-size: .85rem; font-weight: 700; color: var(--text-dim); margin-bottom: .8rem; text-transform: uppercase; letter-spacing: .06em; }}

.toolbar {{ display: flex; gap: .4rem; flex-wrap: wrap; align-items: center; margin-bottom: 1rem; }}
.search-box {{
  margin-left: auto; background: rgba(0,0,0,0.3); border: 1px solid var(--border-glass);
  border-radius: 20px; padding: .4rem .9rem; font-size: .78rem; color: var(--text);
  outline: none; transition: all .3s; width: 180px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}}
.search-box:focus {{ border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-soft); width: 220px; }}
.search-box::placeholder {{ color: var(--text-muted); }}

.filter-btn {{
  background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass); color: var(--text-dim);
  padding: .35rem .85rem; border-radius: 20px; cursor: pointer;
  font-size: .76rem; font-weight: 600; transition: all .25s; font-family: inherit;
}}
.filter-btn:hover {{ color: var(--text); border-color: var(--border-strong); }}
.filter-btn.active {{ background: var(--primary); border-color: var(--primary); color: #fff; box-shadow: 0 4px 16px rgba(107,140,255,0.25); }}

.table-wrap {{ max-height: 460px; overflow-y: auto; border-radius: var(--radius-sm); background: rgba(0,0,0,0.2); }}
.table-wrap::-webkit-scrollbar {{ width: 5px; }}
.table-wrap::-webkit-scrollbar-track {{ background: transparent; }}
.table-wrap::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 10px; }}
table {{ width: 100%; border-collapse: collapse; font-size: .8rem; }}
th, td {{ padding: .5rem .8rem; text-align: left; border-bottom: 1px solid var(--border-glass); }}
th {{
  color: var(--text-muted); font-weight: 600; font-size: .7rem;
  text-transform: uppercase; letter-spacing: .06em;
  position: sticky; top: 0; background: rgba(10,15,30,0.95);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); z-index: 1;
}}
tr {{ transition: background .2s; cursor: pointer; }}
tr:hover td {{ background: rgba(107,140,255,0.06); }}
tr.copied td {{ background: rgba(52,211,153,0.1); transition: background .3s; }}

.badge {{ display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 12px; font-size: .68rem; font-weight: 600; }}
.badge::before {{ content: ''; width: 6px; height: 6px; border-radius: 50%; }}
.badge.jp {{ background: var(--rose-soft); color: var(--rose); }}
.badge.jp::before {{ background: var(--rose); }}
.badge.us {{ background: var(--primary-soft); color: var(--primary); }}
.badge.us::before {{ background: var(--primary); }}
.badge.fr {{ background: var(--amber-soft); color: var(--amber); }}
.badge.fr::before {{ background: var(--amber); }}
.badge.other {{ background: rgba(136,153,180,.08); color: var(--text-dim); }}
.badge.other::before {{ background: var(--text-muted); }}

.empty-state {{ text-align: center; padding: 2rem; color: var(--text-muted); font-size: .82rem; }}

.tip {{ font-size: .72rem; color: var(--text-muted); margin-bottom: .8rem; line-height: 1.5; }}

footer {{ text-align: center; color: var(--text-muted); font-size: .7rem; margin-top: 2.5rem; padding-bottom: 1.5rem; }}
footer a {{ color: var(--text-dim); text-decoration: none; font-weight: 500; }}
footer a:hover {{ color: var(--primary); }}

#toast {{
  position: fixed; top: calc(var(--nav-height) + 1rem); left: 50%; transform: translateX(-50%) translateY(-200%);
  background: var(--surface-glass); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  color: var(--text); border: 1px solid var(--border-strong);
  padding: .55rem 1.4rem; border-radius: 24px; font-size: .8rem; font-weight: 600;
  z-index: 200; transition: transform .4s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 16px 48px rgba(0,0,0,0.5); white-space: nowrap;
}}
#toast.show {{ transform: translateX(-50%) translateY(0); }}

@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(16px); }} to {{ opacity:1; transform:translateY(0); }} }}
.entrance {{ animation: fadeUp .6s ease both; }}
.entrance-d1 {{ animation-delay: .05s; }}
.entrance-d2 {{ animation-delay: .12s; }}
.entrance-d3 {{ animation-delay: .19s; }}
.entrance-d4 {{ animation-delay: .26s; }}

@media (max-width: 600px) {{
  .container {{ padding: 1rem .6rem; }}
  .stat {{ min-width: 60px; padding: .6rem .5rem; }}
  .stat .num {{ font-size: 1.3rem; }}
  .filter-btn {{ padding: .3rem .6rem; font-size: .7rem; }}
  th, td {{ padding: .35rem .5rem; }}
  header h1 {{ font-size: 1.5rem; }}
}}
</style>
</head>
<body>

<nav class="nav">
  <a href="#" class="nav-brand"><span class="dot"></span> Clash Nodes</a>
  <div class="nav-actions">
    <button class="nav-btn" id="themeBtn" onclick="toggleTheme()" aria-label="Toggle theme">
      <svg class="moon-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      <svg class="sun-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
    </button>
  </div>
</nav>

<div id="toast"></div>

<div class="container">
<header class="entrance">
  <h1>Clash Nodes</h1>
  <p class="subtitle">Free verified proxy nodes &mdash; click to copy, paste into your client.</p>
</header>

<div class="stats">
  <div class="stat total entrance entrance-d1"><div class="num total">{total}</div><div class="label">Verified</div></div>
  <div class="stat jp entrance entrance-d2"><div class="num jp">{jp_cnt}</div><div class="label">Japan</div></div>
  <div class="stat us entrance entrance-d3"><div class="num us">{us_cnt}</div><div class="label">US</div></div>
  <div class="stat fr entrance entrance-d4"><div class="num fr">{fr_cnt}</div><div class="label">France</div></div>
</div>

<div class="card entrance entrance-d1">
  <h2>Verified Nodes</h2>
  <p class="tip">Each row is one verified node. <strong>Click any row</strong> to copy its config. Then paste into FlClash / Clash Verge / cmfa.</p>
  <div class="toolbar">
    <button class="filter-btn active" onclick="setFilter('all', this)">All<span class="count" style="font-size:.66rem;opacity:.6;margin-left:2px">{total}</span></button>
    <button class="filter-btn" onclick="setFilter('jp', this)">Japan<span class="count" style="font-size:.66rem;opacity:.6;margin-left:2px">{jp_cnt}</span></button>
    <button class="filter-btn" onclick="setFilter('us', this)">US<span class="count" style="font-size:.66rem;opacity:.6;margin-left:2px">{us_cnt}</span></button>
    <button class="filter-btn" onclick="setFilter('fr', this)">France<span class="count" style="font-size:.66rem;opacity:.6;margin-left:2px">{fr_cnt}</span></button>
    <input class="search-box" type="text" placeholder="Search nodes..." oninput="setSearch(this.value)">
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr><th style="width:60%">Name</th><th>Region</th><th style="width:80px">Type</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="empty-state" id="empty" style="display:none">No matching nodes.</div>
  </div>
</div>

<div class="card entrance entrance-d2">
  <h2>How to Use</h2>
  <p class="tip">
    1. Install <a href="https://github.com/chen08209/FlClash/releases/latest" target="_blank" style="color:var(--primary)">FlClash</a> (Windows) or <a href="https://github.com/clash-verge-rev/clash-verge-rev/releases/latest" target="_blank" style="color:var(--primary)">Clash Verge Rev</a>.<br>
    2. Click any node above to copy its config.<br>
    3. In your client: <strong>New Profile → Paste → Save</strong>.<br>
    4. Turn on System Proxy, select the node, done.
  </p>
</div>

<footer>
  <a href="https://haonl-7.github.io">haonl-7.github.io</a> &middot;
  Last update: {now} &middot;
  <span>Nodes individually verified via protocol test</span>
</footer>
</div>

<script>
/* ── Theme ── */
(function() {{
  var saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
}})();
function toggleTheme() {{
  var el = document.documentElement;
  var cur = el.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  el.setAttribute('data-theme', cur);
  localStorage.setItem('theme', cur);
}}

/* ── Node data ── */
var NODES = {nodes_js};
var BADGES = {{
  jp: '<span class="badge jp">Japan</span>',
  us: '<span class="badge us">US</span>',
  fr: '<span class="badge fr">France</span>',
  other: '<span class="badge other">Other</span>'
}};
var curFilter = 'all', curSearch = '';
var ALL_NODES = NODES;

function render() {{
  var h = '', c = 0, q = curSearch.toLowerCase();
  NODES.forEach(function(n, idx) {{
    if (curFilter !== 'all' && n.r !== curFilter) return;
    if (q && n.n.toLowerCase().indexOf(q) === -1) return;
    var ptype = (n.d && n.d.type) || '?';
    h += '<tr onclick="copyNode(' + idx + ', this)" title="Click to copy config">';
    h += '<td>' + esc(n.n) + '</td>';
    h += '<td>' + (BADGES[n.r] || BADGES.other) + '</td>';
    h += '<td style="color:var(--text-muted);font-size:.7rem">' + ptype + '</td>';
    h += '</tr>';
    c++;
  }});
  document.getElementById('tbody').innerHTML = h;
  document.getElementById('empty').style.display = c ? 'none' : 'block';
}}

function esc(s) {{ var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

function setFilter(f, btn) {{
  curFilter = f;
  document.querySelectorAll('.filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
  if (btn) btn.classList.add('active');
  render();
}}

function setSearch(q) {{ curSearch = q; render(); }}

function toURI(data) {{
  var name = encodeURIComponent(data.name || 'node');
  var type = data.type || '';
  var server = data.server || '';
  var port = data.port || 443;
  var params = [];

  if (type === 'vless') {{
    var uuid = data.uuid || '';
    // Build params
    if (data.tls) {{ params.push('security=tls'); }}
    if (data.servername || data.sni) {{ params.push('sni=' + encodeURIComponent(data.servername || data.sni)); }}
    if (data.network === 'ws') {{
      params.push('type=ws');
      var ws = data['ws-opts'] || {{}};
      if (typeof ws === 'object' && ws.path) params.push('path=' + encodeURIComponent(ws.path));
      if (typeof ws === 'object' && ws.headers && ws.headers.Host) params.push('host=' + encodeURIComponent(ws.headers.Host));
    }}
    if (data['skip-cert-verify']) params.push('allowInsecure=1');
    return 'vless://' + uuid + '@' + server + ':' + port + '?' + params.join('&') + '#' + name;
  }}

  if (type === 'trojan') {{
    var pw = data.password || '';
    if (data.sni || data.servername) params.push('sni=' + encodeURIComponent(data.sni || data.servername));
    if (data['skip-cert-verify']) params.push('allowInsecure=1');
    return 'trojan://' + encodeURIComponent(pw) + '@' + server + ':' + port + '?' + params.join('&') + '#' + name;
  }}

  if (type === 'ss') {{
    // shadowsocks: ss://base64(method:password@server:port)#name
    var method = data.cipher || 'aes-256-gcm';
    var pw2 = data.password || '';
    var b64 = btoa(method + ':' + pw2);
    return 'ss://' + b64 + '@' + server + ':' + port + '#' + name;
  }}

  // Fallback: raw YAML snippet
  var lines = [];
  for (var k in data) {{ if (k !== 'name') {{ var v = data[k]; if (typeof v === 'object') v = JSON.stringify(v); lines.push('  ' + k + ': ' + v); }} }}
  return '- name: ' + (data.name || '') + '\\n' + lines.join('\\n');
}}

function copyNode(idx, row) {{
  var node = ALL_NODES[idx];
  var uri = toURI(node.d);
  navigator.clipboard.writeText(uri).then(function() {{
    row.classList.add('copied');
    setTimeout(function() {{ row.classList.remove('copied'); }}, 600);
    var toast = document.getElementById('toast');
    toast.textContent = 'Copied! Paste into client';
    toast.classList.add('show');
    setTimeout(function() {{ toast.classList.remove('show'); }}, 1500);
  }});
}}

render();
</script>
</body>
</html>'''

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK: index.html ({len(html)} bytes), total={total}, JP={jp_cnt}, US={us_cnt}, FR={fr_cnt})")
