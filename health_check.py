#!/usr/bin/env python3
"""Health check: TLS handshake with correct SNI for encrypted proxies."""
import yaml, socket, ssl, time
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 5
WORKERS = 30

def test_node(proxy):
    server = proxy.get('server', '')
    port = proxy.get('port', 443)
    sni = proxy.get('sni', '') or proxy.get('servername', '') or server

    if not server:
        return (proxy, False)

    try:
        sock = socket.socket()
        sock.settimeout(TIMEOUT)
        sock.connect((server, port))
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        tls = ctx.wrap_socket(sock, server_hostname=sni)
        tls.close()
        return (proxy, True)
    except:
        return (proxy, False)

def filter_alive(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        doc = yaml.safe_load(f)

    proxies = doc.get('proxies', [])
    total = len(proxies)
    print(f"Testing {total} nodes (TLS handshake, {WORKERS} concurrent)...")

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
                print(f"  {tested}/{total} ({len(alive)} alive)", end='\r')

    print(f"\n  {len(alive)}/{total} alive ({len(alive)*100//total}%)")

    doc['proxies'] = alive
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Health-checked: {len(alive)}/{total} TLS alive\n")
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)

if __name__ == '__main__':
    filter_alive('latest.yaml', 'latest.yaml')
