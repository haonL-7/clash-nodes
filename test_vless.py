import yaml, socket, ssl, struct, uuid

with open('latest.yaml', 'r', encoding='utf-8') as f:
    doc = yaml.safe_load(f)

# Find vless nodes
vless = [p for p in doc['proxies'] if p.get('type') == 'vless' and p.get('network', 'tcp') in ('tcp', None)]
if vless:
    p = vless[0]
    srv, prt = p['server'], p['port']
    uid = p['uuid']
    sni = p.get('servername', '') or srv

    print(f'Testing {srv}:{prt} sni={sni[:30]}')
    try:
        s = socket.socket()
        s.settimeout(8)
        s.connect((srv, prt))
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        t = ctx.wrap_socket(s, server_hostname=sni)

        # Vless header (correct spec format)
        ver = b'\x00'                          # version
        uid_bytes = uuid.UUID(uid).bytes       # 16 bytes
        addon = b'\x00'                        # no addons
        cmd = b'\x01'                          # TCP
        port_bytes = struct.pack('>H', 80)     # target port
        addr = b'\x03\x0bhttpbin.org'           # domain type + len + domain
        hdr = ver + uid_bytes + addon + cmd + port_bytes + addr

        http = b'GET /ip HTTP/1.1\r\nHost: httpbin.org\r\nConnection: close\r\n\r\n'
        t.send(hdr + http)

        r = b''
        try:
            while True:
                chunk = t.recv(4096)
                if not chunk: break
                r += chunk
        except:
            pass
        t.close()

        if r:
            print(f'RESPONSE ({len(r)} bytes):')
            print(r[:500].decode('utf-8', errors='replace'))
        else:
            print('No response - protocol likely broken')
    except Exception as e:
        print(f'FAIL: {e}')
else:
    print('No vless tcp nodes found')
