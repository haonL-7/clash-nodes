#!/usr/bin/env python3
"""TCP health check: test each proxy node, keep only reachable ones."""
import yaml, socket, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 3  # seconds
WORKERS = 30  # concurrent connections

def test_node(proxy):
    """Return (proxy, alive, latency_ms)"""
    server = proxy.get('server', '')
    port = proxy.get('port', 443)
    if not server:
        return (proxy, False, 0)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        t0 = time.time()
        sock.connect((server, port))
        ms = (time.time() - t0) * 1000
        sock.close()
        return (proxy, True, ms)
    except:
        return (proxy, False, 0)

def filter_alive(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        doc = yaml.safe_load(f)

    proxies = doc.get('proxies', [])
    total = len(proxies)
    if total == 0:
        print("No proxies to test")
        return

    print(f"Testing {total} nodes ({WORKERS} concurrent, {TIMEOUT}s timeout)...")
    alive, dead = [], []
    tested = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(test_node, p): p for p in proxies}
        for f in as_completed(futures):
            proxy, ok, ms = f.result()
            tested += 1
            if ok:
                alive.append((proxy, ms))
            else:
                dead.append(proxy)
            if tested % 50 == 0 or tested == total:
                print(f"  {tested}/{total} ({len(alive)} ok, {len(dead)} dead)", end='\r')

    print(f"\n  Done: {len(alive)} alive, {len(dead)} dead ({len(alive)*100//total}%)")

    # Write filtered output
    alive_proxies = [p for p, _ in alive]
    doc['proxies'] = alive_proxies

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Health-checked: {len(alive)}/{total} nodes alive\n")
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)

    print(f"  Written: {output_file}")

if __name__ == '__main__':
    filter_alive('latest.yaml', 'latest.yaml')
