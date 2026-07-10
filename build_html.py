#!/usr/bin/env python3
"""Source directory + per-source node list with URI links."""
import datetime, urllib.request, ssl, re, json, yaml, os
from datetime import timezone, timedelta

ctx = ssl.create_default_context()
ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131'
def fetch(url, timeout=15):
    r = urllib.request.Request(url, headers={'User-Agent': UA})
    return urllib.request.urlopen(r, context=ctx, timeout=timeout).read()

# ── yoyapai URL ──
def get_yoyapai_url():
    try:
        html = fetch('https://yoyapai.com/category/mianfeijiedian').decode('utf-8', errors='ignore')
        posts = re.findall(r'href="https://yoyapai\.com/(\d+)"', html)
        if not posts: return None
        html2 = fetch(f'https://yoyapai.com/{posts[0]}').decode('utf-8', errors='ignore')
        html2 = html2.replace('&#47;', '/')
        yamls = re.findall(r'https?://[^"<>\s]+\.yaml[^"<>\s]*', html2)
        return yamls[0] if yamls else None
    except: return None

def to_uri(p):
    """Convert proxy dict to shareable URI (vless:// trojan:// ss://)"""
    name = p.get('name', 'node')
    server = p.get('server', '') or ''
    port = p.get('port', 443)
    ptype = (p.get('type', '') or '').lower()
    params = []

    if ptype == 'vless':
        uid = p.get('uuid', '') or ''
        if p.get('tls'): params.append('security=tls')
        sni = p.get('servername', '') or p.get('sni', '') or ''
        if sni: params.append('sni=' + sni)
        if p.get('network') == 'ws':
            params.append('type=ws')
            ws = p.get('ws-opts', {}) or {}
            if isinstance(ws, dict) and ws.get('path'):
                params.append('path=' + ws['path'])
            if isinstance(ws, dict) and isinstance(ws.get('headers'), dict) and ws['headers'].get('Host'):
                params.append('host=' + ws['headers']['Host'])
        if p.get('skip-cert-verify'): params.append('allowInsecure=1')
        qs = '?' + '&'.join(params) if params else ''
        return f"vless://{uid}@{server}:{port}{qs}#{name}" if uid else None

    if ptype == 'trojan':
        pw = p.get('password', '') or ''
        sni = p.get('sni', '') or p.get('servername', '') or ''
        if sni: params.append('sni=' + sni)
        if p.get('skip-cert-verify'): params.append('allowInsecure=1')
        qs = '?' + '&'.join(params) if params else ''
        return f"trojan://{pw}@{server}:{port}{qs}#{name}" if pw else None

    if ptype == 'ss':
        method = p.get('cipher', '') or 'aes-256-gcm'
        pw = p.get('password', '') or ''
        import base64
        b64 = base64.b64encode(f"{method}:{pw}".encode()).decode()
        return f"ss://{b64}@{server}:{port}#{name}" if pw else None

    if ptype == 'vmess':
        return None  # too complex for URI

    return None

def load_proxies(label):
    """Load proxies from source file. Returns list of (uri, name, type)"""
    path = f'sources/{label}.yaml'
    if not os.path.exists(path): return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            doc = yaml.safe_load(f)
        proxies = doc.get('proxies', []) if isinstance(doc, dict) else []
        result = []
        for p in proxies:
            if not isinstance(p, dict): continue
            if (p.get('type') or '').lower() in ('http', 'socks5'): continue
            uri = to_uri(p)
            if uri:
                result.append({'uri': uri, 'name': p.get('name', '?'), 'type': p.get('type', '?')})
        return result
    except Exception as e:
        print(f"  [{label}] parse error: {e}")
        return []

# ── Build ──
yoyapai_url = get_yoyapai_url()

sources = [
    ('yoyapai', yoyapai_url or 'https://freenode.yoyapai.com/latest.yaml', 'daily'),
    ('freeSub', 'https://raw.githubusercontent.com/Ruk1ng001/freeSub/main/clash.yaml', 'stable'),
    ('free-vpn', 'https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/clash.yaml', 'stable'),
    ('awesome-vpn', 'https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/clash.yaml', 'stable'),
]

node_lists = {}
for label, url, tag in sources:
    node_lists[label] = load_proxies(label)

now = datetime.datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M CST")

# ── CSS (same as before) ──
html = f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Free proxy nodes — clean, ad-free directory with per-node links.">
<meta name="robots" content="index,follow">
<meta property="og:title" content="Clash Nodes">
<title>Clash Nodes — Free Proxy Nodes</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {{
  --bg-deep: #060b14; --bg: #0a0f1e;
  --surface-glass: rgba(18,24,42,0.55);
  --border-glass: rgba(255,255,255,0.06); --border-strong: rgba(255,255,255,0.1);
  --text: #e8edf5; --text-dim: #8899b4; --text-muted: #556680;
  --primary: #6b8cff; --green: #34d399; --rose: #f87171;
  --radius: 14px; --radius-sm: 8px;
  --nav-height: 56px;
}}

[data-theme="light"] {{
  --bg-deep: #f0f4f8; --bg: #f6f9fc;
  --surface-glass: rgba(255,255,255,0.65);
  --border-glass: rgba(0,0,0,0.06); --border-strong: rgba(0,0,0,0.12);
  --text: #1a2332; --text-dim: #556680; --text-muted: #8899b4;
  --primary: #4b6eec; --green: #10b981;
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
.nav-brand {{ font-weight: 800; font-size: 1rem; color: var(--text); text-decoration: none; display: flex; align-items: center; gap: .45rem; }}
.dot {{ width:8px; height:8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px rgba(52,211,153,0.5); }}
.nav-actions {{ display: flex; gap: .4rem; }}
.nav-btn {{
  background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass); color: var(--text-dim);
  padding: .35rem .65rem; border-radius: var(--radius-sm); cursor: pointer;
  font-size: .75rem; font-weight: 600; font-family: inherit; transition: all .25s;
  display: flex; align-items: center; gap: .3rem;
}}
.nav-btn:hover {{ color: var(--text); border-color: var(--border-strong); }}
.nav-btn svg {{ fill: none; stroke: currentColor; stroke-width: 1.8; }}
.sun-icon {{ display: none; }}
[data-theme="light"] .moon-icon {{ display: none; }}
[data-theme="light"] .sun-icon {{ display: inline; }}

.container {{ max-width: 800px; margin: 0 auto; padding: 1.5rem 1.2rem; }}

header {{ text-align: center; margin-bottom: 2rem; }}
header h1 {{ font-size: 2rem; font-weight: 900; letter-spacing: -.03em; }}
.subtitle {{ color: var(--text-dim); font-size: .82rem; margin-top: .3rem; }}

.card {{
  background: var(--surface-glass); border: 1px solid var(--border-glass);
  border-radius: var(--radius); padding: 1.3rem; margin-bottom: 1rem;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
}}
.card h2 {{ font-size: .85rem; font-weight: 700; color: var(--text-dim); margin-bottom: .8rem; text-transform: uppercase; letter-spacing: .06em; }}

/* ── Subscription box ── */
.sub-list {{ display: flex; flex-direction: column; gap: .6rem; }}
.sub-item {{ display: flex; gap: .5rem; align-items: center; }}
.sub-item label {{
  font-size: .72rem; color: var(--text-muted); min-width: 80px; font-weight: 600;
  text-transform: uppercase; letter-spacing: .05em; white-space: nowrap;
}}
.sub-item input {{
  flex: 1; background: rgba(0,0,0,0.3); border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm); padding: .5rem .7rem;
  font-size: .72rem; color: var(--text); font-family: 'SF Mono','Fira Code',monospace;
  transition: all .25s; min-width: 0;
}}
.sub-item input:focus {{ outline: none; border-color: var(--primary); }}
.sub-item button {{
  background: rgba(107,140,255,0.1); color: var(--primary);
  border: 1px solid rgba(107,140,255,0.25); border-radius: var(--radius-sm);
  padding: .45rem .85rem; cursor: pointer; font-size: .72rem; font-weight: 600;
  white-space: nowrap; font-family: inherit; transition: all .25s;
}}
.sub-item button:hover {{ background: var(--primary); border-color: var(--primary); color: #fff; }}
.sub-item button.copied {{ background: var(--green); border-color: var(--green); color: #fff; }}

.tag {{
  display: inline-block; font-size: .6rem; font-weight: 700; padding: 1px 6px;
  border-radius: 3px; text-transform: uppercase; letter-spacing: .04em; vertical-align: middle;
}}
.tag-daily {{ background: rgba(52,211,153,0.12); color: var(--green); }}
.tag-stable {{ background: rgba(136,153,184,0.1); color: var(--text-dim); }}

.toggle-btn {{
  background: none; border: 1px solid var(--border-glass); color: var(--text-dim);
  padding: .3rem .7rem; border-radius: var(--radius-sm); cursor: pointer;
  font-size: .7rem; font-family: inherit; margin-top: .6rem; transition: all .2s;
}}
.toggle-btn:hover {{ color: var(--text); border-color: var(--border-strong); }}

.node-list {{
  display: none; margin-top: .6rem; max-height: 360px; overflow-y: auto;
  background: rgba(0,0,0,0.2); border-radius: var(--radius-sm); padding: .4rem;
}}
.node-list.open {{ display: block; }}
.node-row {{
  display: flex; align-items: center; gap: .5rem;
  padding: .3rem .5rem; border-radius: 3px; cursor: pointer; transition: background .15s;
  border-bottom: 1px solid rgba(255,255,255,0.02);
}}
.node-row:hover {{ background: rgba(107,140,255,0.06); }}
.node-row.copied {{ background: rgba(52,211,153,0.1); }}
.node-name {{
  flex:1; font-size: .68rem; color: var(--text-dim); white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; min-width: 0;
}}
.node-type {{
  font-size: .6rem; color: var(--text-muted); font-family: 'SF Mono',monospace;
  padding: 1px 5px; border-radius: 2px; background: rgba(255,255,255,0.04);
}}
.node-count {{ font-size: .65rem; color: var(--text-muted); margin-left: .3rem; }}

.warning-box {{
  background: rgba(107,140,255,0.06); border-left: 3px solid var(--primary);
  padding: .6rem .8rem; margin-bottom: .8rem; border-radius: 4px;
  font-size: .72rem; color: var(--text-dim); line-height: 1.5;
}}

footer {{ text-align: center; color: var(--text-muted); font-size: .7rem; margin-top: 2rem; padding-bottom: 1.5rem; }}
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

@media (max-width: 600px) {{
  .container {{ padding: 1rem .6rem; }}
  .sub-item {{ flex-wrap: wrap; }}
  .sub-item label {{ min-width: 60px; font-size: .66rem; }}
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
  <p class="subtitle">Free proxy nodes — clean, ad&#8209;free. Click any node to copy.</p>
</header>

<div class="card entrance entrance-d1">
  <h2>Tutorial</h2>
  <div class="warning-box">
    <strong>Do NOT open YAML links in your browser</strong> — they're raw config files, not web pages.
    Click any <em style="color:var(--primary)">node row below</em> to copy its link, or copy the full subscription URL.<br>
    Paste into FlClash / Clash Verge / cmfa → <em style="color:var(--primary)">Profiles → + → URL → Download</em>.
  </div>

  <p style="color:var(--text-dim);font-size:.72rem">
    1. Install <a href="https://github.com/chen08209/FlClash/releases/latest" target="_blank" style="color:var(--primary)">FlClash</a> (Windows) or <a href="https://github.com/clash-verge-rev/clash-verge-rev/releases/latest" target="_blank" style="color:var(--primary)">Clash Verge Rev</a><br>
    2. Click any node below → copy → paste into client → connect<br>
    3. Not working? Try another node or another source.
  </p>
</div>

<!-- Subscription sources with per-node lists -->
'''

for idx, (label, url, tag) in enumerate(sources):
    nodes = node_lists.get(label, [])
    tag_class = 'tag-daily' if tag == 'daily' else 'tag-stable'
    html += f'''<div class="card entrance entrance-d1">
  <h2>{label} <span class="tag {tag_class}">{tag}</span> <span class="node-count">({len(nodes)} nodes)</span></h2>
  <div class="sub-list">
    <div class="sub-item">
      <label>Full URL</label>
      <input id="sub{idx}" value="{url}" readonly onclick="this.select()">
      <button onclick="doCopy('sub{idx}', this)">Copy</button>
    </div>
  </div>
  <button class="toggle-btn" onclick="document.getElementById('nodes{idx}').classList.toggle('open');this.textContent=document.getElementById('nodes{idx}').classList.contains('open')?'Hide nodes':'Show {len(nodes)} individual nodes'">Show {len(nodes)} individual nodes</button>
  <div class="node-list" id="nodes{idx}">
'''

    for ni, node in enumerate(nodes):
        html += f'    <div class="node-row" onclick="copyURI(\'{node["uri"].replace(chr(39), chr(92)+chr(39))}\', this)" title="Click to copy"><span class="node-type">{node["type"]}</span><span class="node-name">{node["name"][:60]}</span></div>\n'

    html += '  </div>\n</div>\n'

html += f'''
<footer>
  <a href="https://haonl-7.github.io">haonl-7.github.io</a> &middot; Updated: {now} &middot;
  <span>No ads. No tracking. Just links.</span>
</footer>
</div>

<script>
(function() {{
  var saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
}})();
function toggleTheme() {{
  var el = document.documentElement;
  el.setAttribute('data-theme', el.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
  localStorage.setItem('theme', el.getAttribute('data-theme'));
}}
function doCopy(id, btn) {{
  var inp = document.getElementById(id);
  inp.select(); inp.setSelectionRange(0, 99999);
  navigator.clipboard.writeText(inp.value).then(function() {{
    var orig = btn.textContent;
    btn.textContent = 'Copied'; btn.classList.add('copied');
    document.getElementById('toast').textContent = 'Link copied!';
    document.getElementById('toast').classList.add('show');
    setTimeout(function() {{
      document.getElementById('toast').classList.remove('show');
      btn.textContent = orig; btn.classList.remove('copied');
    }}, 1800);
  }});
}}
function copyURI(uri, row) {{
  navigator.clipboard.writeText(uri).then(function() {{
    row.classList.add('copied');
    setTimeout(function() {{ row.classList.remove('copied'); }}, 600);
    document.getElementById('toast').textContent = 'Copied! Paste into client';
    document.getElementById('toast').classList.add('show');
    setTimeout(function() {{ document.getElementById('toast').classList.remove('show'); }}, 1500);
  }});
}}
</script>
</body>
</html>'''

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK: {len(html)} bytes")
