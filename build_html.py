#!/usr/bin/env python3
"""从 latest.yaml 生成 index.html"""
import json, sys

# 读取节点
with open("latest.yaml", "r", encoding="utf-8") as f:
    lines = f.readlines()

nodes = []
for line in lines:
    if line.startswith("  - name:"):
        name = line.replace("  - name: ", "").strip()
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
nodes_json = json.dumps(nodes, ensure_ascii=False)

import datetime
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CST")

# CSS 内联，JS 内联，纯静态 HTML
html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Clash 免费节点 - 每日更新</title>
<style>
:root{{--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#c9d1d9;--muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--red:#f85149;--purple:#a371f7}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh}}
.container{{max-width:960px;margin:0 auto;padding:2rem 1rem}}
header{{text-align:center;margin-bottom:2rem}}
header h1{{font-size:1.75rem;margin-bottom:.25rem}}
header p{{color:var(--muted);font-size:.9rem}}
a{{color:var(--accent);text-decoration:none}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:.75rem;margin-bottom:1.5rem}}
.stat{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:1.2rem;text-align:center;transition:transform .15s}}
.stat:hover{{transform:translateY(-2px)}}
.stat .num{{font-size:2rem;font-weight:700}}
.stat .label{{color:var(--muted);font-size:.8rem;margin-top:.25rem}}
.c-total{{color:var(--green)}}.c-jp{{color:var(--red)}}.c-us{{color:var(--accent)}}.c-fr{{color:var(--purple)}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:1.25rem;margin-bottom:1rem}}
.card h2{{font-size:1.05rem;margin-bottom:.75rem}}
.sub-row{{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap}}
.sub-row input{{flex:1;background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:.6rem .8rem;font-size:.82rem;color:var(--accent);font-family:monospace;min-width:240px}}
.sub-row button{{background:var(--accent);color:#fff;border:none;border-radius:6px;padding:.6rem 1.2rem;cursor:pointer;font-size:.85rem;white-space:nowrap;font-weight:500}}
.sub-row button:hover{{opacity:.85}}
.sub-row button.copied{{background:var(--green)}}
.filter-bar{{display:flex;gap:.4rem;flex-wrap:wrap;margin-bottom:1rem}}
.filter-bar button{{background:var(--card);border:1px solid var(--border);color:var(--text);padding:.35rem .9rem;border-radius:20px;cursor:pointer;font-size:.8rem;transition:all .15s}}
.filter-bar button:hover{{border-color:var(--muted)}}
.filter-bar button.active{{background:var(--accent);border-color:var(--accent);color:#fff}}
.table-wrap{{max-height:520px;overflow-y:auto;border-radius:6px}}
table{{width:100%;border-collapse:collapse;font-size:.84rem}}
th,td{{padding:.45rem .75rem;text-align:left;border-bottom:1px solid var(--border)}}
th{{color:var(--muted);font-weight:500;position:sticky;top:0;background:var(--card);z-index:1}}
tr:hover td{{background:rgba(255,255,255,.02)}}
.badge{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.7rem;font-weight:600}}
.badge.jp{{background:rgba(248,81,73,.15);color:var(--red)}}
.badge.us{{background:rgba(88,166,255,.15);color:var(--accent)}}
.badge.fr{{background:rgba(163,113,247,.15);color:var(--purple)}}
.badge.other{{background:rgba(139,148,158,.15);color:var(--muted)}}
footer{{text-align:center;color:var(--muted);font-size:.75rem;margin-top:2rem;padding-bottom:1rem}}
#toast{{position:fixed;top:1rem;right:1rem;background:var(--green);color:#fff;padding:.6rem 1.2rem;border-radius:8px;font-size:.85rem;opacity:0;transition:opacity .3s;pointer-events:none;z-index:99}}
#toast.show{{opacity:1}}
</style>
</head>
<body>
<div id="toast">✅ 已复制订阅地址</div>
<div class="container">
<header><h1>🛰️ Clash 免费节点</h1><p>每日自动更新 &middot; 数据来源 <a href="https://yoyapai.com">yoyapai.com</a></p></header>

<div class="stats">
<div class="stat"><div class="num c-total">{total}</div><div class="label">📡 总节点</div></div>
<div class="stat"><div class="num c-jp">{jp_cnt}</div><div class="label">🇯🇵 日本</div></div>
<div class="stat"><div class="num c-us">{us_cnt}</div><div class="label">🇺🇸 美国</div></div>
<div class="stat"><div class="num c-fr">{fr_cnt}</div><div class="label">🇫🇷 法国</div></div>
</div>

<div class="card">
<h2>📋 订阅地址</h2>
<div class="sub-row">
<input id="subUrl" value="https://raw.githubusercontent.com/haonL-7/clash-nodes/main/latest.yaml" readonly onclick="this.select()">
<button id="copyBtn" onclick="doCopy()">📋 复制</button>
</div>
<p style="color:var(--muted);font-size:.78rem;margin-top:.6rem">💡 填入 Clash / Shadowrocket 订阅即可每日自动更新</p>
</div>

<div class="card">
<h2>🌐 节点列表 <span id="shownCount" style="color:var(--muted);font-weight:400;font-size:.85rem"></span></h2>
<div class="filter-bar">
<button class="active" onclick="filter('all')">全部</button>
<button onclick="filter('jp')">🇯🇵 日本</button>
<button onclick="filter('us')">🇺🇸 美国</button>
<button onclick="filter('fr')">🇫🇷 法国</button>
<button onclick="filter('other')">🌍 其他</button>
</div>
<div class="table-wrap">
<table><thead><tr><th style="width:70%">节点名称</th><th>地区</th></tr></thead>
<tbody id="tbody"></tbody></table>
</div>
</div>

<footer>最后更新: {now} &middot; Powered by <a href="https://github.com/haonL-7/clash-nodes">GitHub Actions</a></footer>
</div>

<script>
var NODES={nodes_json};
var BADGES={{jp:'<span class="badge jp">🇯🇵 日本</span>',us:'<span class="badge us">🇺🇸 美国</span>',fr:'<span class="badge fr">🇫🇷 法国</span>',other:'<span class="badge other">🌍 其他</span>'}};
function render(f){{var h='',c=0;NODES.forEach(function(n){{if(f!=='all'&&n.r!==f)return;h+='<tr><td>'+esc(n.n)+'</td><td>'+(BADGES[n.r]||BADGES.other)+'</td></tr>';c++}});document.getElementById('tbody').innerHTML=h;document.getElementById('shownCount').textContent='('+c+' 个节点)'}}
function esc(s){{var d=document.createElement('div');d.textContent=s;return d.innerHTML}}
function filter(f){{document.querySelectorAll('.filter-bar button').forEach(function(b){{b.classList.remove('active')}});event.target.classList.add('active');render(f)}}
function doCopy(){{var i=document.getElementById('subUrl');i.select();i.setSelectionRange(0,99999);navigator.clipboard.writeText(i.value).then(function(){{var t=document.getElementById('toast');t.classList.add('show');var b=document.getElementById('copyBtn');b.textContent='✅ 已复制';b.classList.add('copied');setTimeout(function(){{t.classList.remove('show');b.textContent='📋 复制';b.classList.remove('copied')}},2000)}})}}
render('all');
</script>
</body>
</html>'''

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK: index.html ({len(html)} bytes), total={total}, JP={jp_cnt}, US={us_cnt}, FR={fr_cnt}")
