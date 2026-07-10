#!/usr/bin/env python3
"""Health check: TCP + TLS handshake, HTTP proxy real test."""
import yaml, socket, ssl, time, struct
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 5  # seconds
WORKERS = 20

def test_node(proxy):
    """Returns (proxy, alive, latency_ms, error_reason)"""
    server = proxy.get('server', '')
    port = proxy.get('port', 443)
    ptype = proxy.get('type', '').lower()
    tls_enabled = proxy.get('tls', False)
    if not server:
        return (proxy, False, 0, 'no server')

    # Step 1: TCP connect
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        t0 = time.time()
        sock.connect((server, port))
        tcp_ms = (time.time() - t0) * 1000
    except Exception as e:
        return (proxy, False, 0, f'TCP: {e}')

    # Step 2: TLS handshake if tls=True
    if tls_enabled or ptype in ('vless', 'vmess', 'trojan', 'anytls', 'hysteria2'):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            tls_sock = ctx.wrap_socket(sock, server_hostname=server)
            latency = (time.time() - t0) * 1000
            tls_sock.close()
            return (proxy, True, latency, '')
        except Exception as e:
            try: sock.close()
            except: pass
            return (proxy, False, 0, f'TLS: {e}')

    # Step 3: HTTP proxy real test
    if ptype == 'http':
        try:
            sock.settimeout(5)
            # Send CONNECT or direct GET depending on proxy type
            sock.sendall(
                b'GET http://httpbin.org/ip HTTP/1.1\r\n'
                b'Host: httpbin.org\r\n'
                b'User-Agent: clash-nodes/1.0\r\n'
                b'Connection: close\r\n\r\n'
            )
            data = sock.recv(1024)
            sock.close()
            # Check for valid HTTP response
            if b'HTTP/' in data and len(data) > 10:
                return (proxy, True, tcp_ms, '')
            return (proxy, False, 0, 'HTTP: no valid response')
        except Exception as e:
            try: sock.close()
            except: pass
            return (proxy, False, 0, f'HTTP: {e}')

    # SS/SOCKS: just TCP connect is enough
    if ptype in ('ss', 'socks5'):
        sock.close()
        return (proxy, True, tcp_ms, '')

    # Unknown: TCP connect only
    sock.close()
    return (proxy, True, tcp_ms, '(TCP only)')

def filter_alive(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        doc = yaml.safe_load(f)

    proxies = doc.get('proxies', [])
    total = len(proxies)
    if total == 0:
        print("No proxies to test")
        return

    print(f"Testing {total} nodes ({WORKERS} concurrent, {TIMEOUT}s)...")
    alive, dead = [], []
    errors = {}
    tested = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(test_node, p): p for p in proxies}
        for f in as_completed(futures):
            proxy, ok, ms, err = f.result()
            tested += 1
            if ok:
                alive.append((proxy, ms))
            else:
                dead.append(proxy)
                if err:
                    key = err.split(':')[0]
                    errors[key] = errors.get(key, 0) + 1
            if tested % 50 == 0:
                print(f"  {tested}/{total} ({len(alive)} ok, {len(dead)} dead)", end='\r')

    print(f"\n  Done: {len(alive)} alive, {len(dead)} dead ({len(alive)*100//total}%)")
    if errors:
        print(f"  Fail reasons: {dict(errors)}")

    doc['proxies'] = [p for p, _ in alive]
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Health-checked: {len(alive)}/{total} alive\n")
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)

if __name__ == '__main__':
    filter_alive('latest.yaml', 'latest.yaml')
