"""Brute-force test: try every node with a real request. Output working config."""
import yaml, socket, ssl, struct, uuid, time
from concurrent.futures import ThreadPoolExecutor, as_completed

TIMEOUT = 5
WORKERS = 15
TEST_HOST = b'httpbin.org'
TEST_PORT = 80
TEST_REQ = b'GET /ip HTTP/1.1\r\nHost: httpbin.org\r\nUser-Agent: clash-nodes\r\nConnection: close\r\n\r\n'

def test_node(proxy):
    ptype = proxy.get('type', '')
    server = proxy.get('server', '')
    port = proxy.get('port', 443)
    sni = proxy.get('servername', '') or proxy.get('sni', '') or server

    if not server: return (proxy, False, 'no server')

    if ptype in ('vless', 'vmess', 'trojan'):
        try:
            s = socket.socket(); s.settimeout(TIMEOUT)
            s.connect((server, port))
            ctx = ssl.create_default_context()
            ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
            t = ctx.wrap_socket(s, server_hostname=sni)

            # Build appropriate header
            if ptype == 'vless':
                u = uuid.UUID(proxy.get('uuid', '')).bytes
                hdr = b'\x00' + u + b'\x00\x01' + struct.pack('>H', TEST_PORT)
                hdr += bytes([3, len(TEST_HOST)]) + TEST_HOST
                t.send(hdr + TEST_REQ)
            elif ptype == 'trojan':
                pw = proxy.get('password', '').encode()
                hdr = pw + b'\r\n\x01' + struct.pack('>H', TEST_PORT)
                hdr += bytes([3, len(TEST_HOST)]) + TEST_HOST + b'\r\n'
                t.send(hdr + TEST_REQ)
            else:  # vmess or other — just try raw HTTP after TLS
                t.send(TEST_REQ)

            resp = t.recv(2048)
            t.close()
            if b'HTTP/' in resp:
                return (proxy, True, len(resp))
            return (proxy, False, f'Bad response: {resp[:60]}')
        except Exception as e:
            return (proxy, False, str(e)[:80])

    # Other types just TCP check
    if ptype in ('ss', 'hysteria2', 'anytls', 'socks5'):
        try:
            s = socket.socket(); s.settimeout(3)
            s.connect((server, port)); s.close()
            return (proxy, True, 'tcp ok')
        except:
            return (proxy, False, 'tcp dead')

    return (proxy, False, f'unknown type: {ptype}')

print("Loading yoyapai raw config...")
with open('sources/yoyapai.yaml', 'r', encoding='utf-8') as f:
    doc = yaml.safe_load(f)

proxies = doc.get('proxies', [])
total = len(proxies)
print(f"Testing {total} nodes...\n")

alive = []
tested = 0
with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = {pool.submit(test_node, p): p for p in proxies}
    for f in as_completed(futures):
        proxy, ok, info = f.result()
        tested += 1
        if ok:
            alive.append(proxy)
            print(f"[{tested:3d}/{total}] ALIVE {proxy.get('type','?'):8s} {proxy.get('name','')[:40]}")
        if tested % 20 == 0:
            print(f"  ... {tested}/{total} tested, {len(alive)} alive", end='\r')

print(f"\n{'='*60}")
print(f"RESULT: {len(alive)}/{total} working ({len(alive)*100//total}%)")

if alive:
    doc['proxies'] = alive
    with open('yoyapai-working.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)
    print(f"Written: yoyapai-working.yaml")
else:
    print("No working nodes found!")
