#!/usr/bin/env python3
"""Health check: real proxy test (vless/trojan protocol), TLS fallback for others."""
import yaml, socket, ssl, struct, uuid, time
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 8
WORKERS = 10
TEST_HOST = b'httpbin.org'
TEST_PORT = 80
TEST_REQ = b'GET /ip HTTP/1.1\r\nHost: httpbin.org\r\nUser-Agent: clash-nodes\r\nConnection: close\r\n\r\n'

def test_node(proxy):
    ptype = proxy.get('type', '')
    server = proxy.get('server', '')
    port = proxy.get('port', 443)
    sni = proxy.get('servername', '') or proxy.get('sni', '') or server

    if not server:
        return (proxy, False)

    # ── vless: full protocol test ──
    if ptype == 'vless':
        try:
            s = socket.socket(); s.settimeout(TIMEOUT)
            s.connect((server, port))
            ctx = ssl.create_default_context()
            ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
            t = ctx.wrap_socket(s, server_hostname=sni)
            u = uuid.UUID(proxy.get('uuid', '')).bytes
            hdr = b'\x00' + u + b'\x00\x01' + struct.pack('>H', TEST_PORT)
            hdr += bytes([3, len(TEST_HOST)]) + TEST_HOST
            t.send(hdr + TEST_REQ)
            resp = t.recv(2048); t.close()
            return (proxy, b'HTTP/' in resp)
        except:
            return (proxy, False)

    # ── trojan: full protocol test ──
    if ptype == 'trojan':
        try:
            s = socket.socket(); s.settimeout(TIMEOUT)
            s.connect((server, port))
            ctx = ssl.create_default_context()
            ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
            t = ctx.wrap_socket(s, server_hostname=sni)
            pw = proxy.get('password', '').encode()
            hdr = pw + b'\r\n\x01' + struct.pack('>H', TEST_PORT)
            hdr += bytes([3, len(TEST_HOST)]) + TEST_HOST + b'\r\n'
            t.send(hdr + TEST_REQ)
            resp = t.recv(2048); t.close()
            return (proxy, b'HTTP/' in resp)
        except:
            return (proxy, False)

    # ── vmess/others: TLS check only (protocol too complex) ──
    try:
        s = socket.socket(); s.settimeout(TIMEOUT)
        s.connect((server, port))
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        t = ctx.wrap_socket(s, server_hostname=sni)
        t.close()
        return (proxy, True)
    except:
        return (proxy, False)

def filter_alive(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        doc = yaml.safe_load(f)

    proxies = doc.get('proxies', [])
    total = len(proxies)
    vless_count = sum(1 for p in proxies if p.get('type') == 'vless')
    trojan_count = sum(1 for p in proxies if p.get('type') == 'trojan')

    print(f"Testing {total} nodes (vless:{vless_count} trojan:{trojan_count})...")

    alive = []
    tested = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(test_node, p): p for p in proxies}
        for f in as_completed(futures):
            proxy, ok = f.result()
            tested += 1
            if ok:
                alive.append(proxy)
            if tested % 30 == 0:
                t = proxy.get('type', '?')
                status = 'OK' if ok else 'DEAD'
                print(f"  {tested}/{total} [{len(alive)} alive]")

    pct = len(alive) * 100 // max(total, 1)
    print(f"  => {len(alive)}/{total} alive ({pct}%)")

    doc['proxies'] = alive
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Real proxy test: {len(alive)}/{total} alive\n")
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)

if __name__ == '__main__':
    filter_alive('latest.yaml', 'latest.yaml')
