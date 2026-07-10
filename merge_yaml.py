#!/usr/bin/env python3
"""Merge multiple Clash YAML subscription files, deduplicate by name, output unified YAML."""
import sys, yaml, os
from collections import OrderedDict

SOURCES = {
    "yoyapai": "https://yoyapai.com",
    "freeSub": "https://github.com/Ruk1ng001/freeSub",
    "free-vpn": "https://github.com/Au1rxx/free-vpn-subscriptions",
    "awesome-vpn": "https://github.com/awesome-vpn/awesome-vpn",
    "Jsnzkpg": "https://github.com/Jsnzkpg/Jsnzkpg",
}

def load_proxies(path, label):
    """Load proxies from a YAML file. Returns list of proxy dicts."""
    if not os.path.exists(path):
        print(f"  [{label}] SKIP: file not found ({path})")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Handle both YAML and non-standard formats
        # Some sources may not be valid YAML — try parsing anyway
        try:
            doc = yaml.safe_load(content)
        except yaml.YAMLError:
            # Fallback: try to extract proxy entries manually
            print(f"  [{label}] WARN: invalid YAML, trying manual parse")
            doc = manual_parse(content)

        if doc is None:
            print(f"  [{label}] WARN: empty document")
            return []
        if isinstance(doc, dict) and "proxies" in doc:
            proxies = doc["proxies"]
        elif isinstance(doc, list):
            proxies = doc
        else:
            print(f"  [{label}] WARN: unexpected format (keys={list(doc.keys()) if isinstance(doc, dict) else type(doc)})")
            return []

        count = len(proxies) if proxies else 0
        print(f"  [{label}] {count} proxies")
        return proxies if proxies else []
    except Exception as e:
        print(f"  [{label}] ERROR: {e}")
        return []

def manual_parse(content):
    """Fallback: extract proxy entries from non-standard YAML-like content."""
    proxies = []
    current = {}
    in_proxies = False
    for line in content.split("\n"):
        s = line.strip()
        if s.startswith("proxies:") or s == "proxies:":
            in_proxies = True
            continue
        if in_proxies:
            if s.startswith("- name:"):
                if current and "name" in current:
                    proxies.append(dict(current))
                current = {"name": s.replace("- name:", "").strip().strip('"').strip("'")}
            elif s.startswith("name:") and not line.startswith("  -"):
                if current and "name" in current:
                    proxies.append(dict(current))
                current = {"name": s.replace("name:", "").strip().strip('"').strip("'")}
            elif s.startswith("server:"):
                current["server"] = s.replace("server:", "").strip().strip('"').strip("'")
            elif s.startswith("port:"):
                try: current["port"] = int(s.replace("port:", "").strip())
                except: pass
            elif s.startswith("type:"):
                current["type"] = s.replace("type:", "").strip().strip('"').strip("'")
            elif s.startswith("  ") and ":" in s:
                key, _, val = s.partition(":")
                key = key.strip(); val = val.strip().strip('"').strip("'")
                if key not in current:
                    current[key] = val
            elif not s.startswith(" ") and s != "" and ":" in s and not s.startswith("-"):
                # New top-level key — end of proxies
                break
    if current and "name" in current:
        proxies.append(dict(current))
    return {"proxies": proxies}

def dedup_key(p):
    """Generate dedup key: prefer UUID > server:port > servername > name"""
    uuid = p.get("uuid", "") or ""
    server = p.get("server", "") or ""
    port = str(p.get("port", "")) if p.get("port") else ""
    sni = p.get("servername", "") or ""
    name = p.get("name", "") or ""
    # Best: UUID (unique service identity)
    if uuid and len(uuid) > 4:
        return "uuid:" + uuid.strip().lower()
    # Good: server:port (network endpoint)
    if server and port:
        return f"srv:{server.strip().lower()}:{port}"
    # OK: server alone
    if server:
        return "srv:" + server.strip().lower()
    # Fallback: servername (SNI)
    if sni and len(sni) > 4:
        return "sni:" + sni.strip().lower()
    # Last resort: name
    return "name:" + name.strip().lower()

def merge_all(files_and_labels):
    """Merge proxies from multiple sources, smart dedup by UUID/server/SNI."""
    seen = set()
    merged = []
    stats = {}

    for path, label in files_and_labels:
        proxies = load_proxies(path, label)
        added = 0
        for p in proxies:
            if not isinstance(p, dict):
                continue
            name = p.get("name", "")
            if not name:
                continue
            key = dedup_key(p)
            if key not in seen:
                seen.add(key)
                merged.append(p)
                added += 1
        stats[label] = {"total": len(proxies), "added": added}
        if proxies:
            print(f"  [{label}] {added} new (from {len(proxies)} total, {len(proxies)-added} dupes)")

    return merged, stats

def output_yaml(merged_proxies, template_path, output_path, stats):
    """Write merged YAML using template structure from primary source."""
    # Try to keep the original structure from the first source
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except:
        doc = {}

    if doc is None:
        doc = {}
    if not isinstance(doc, dict):
        doc = {"proxies": merged_proxies}

    doc["proxies"] = merged_proxies

    # Add merge stats as comment
    header = []
    header.append("# ============================================")
    header.append("# Clash Nodes — Multi-Source Aggregation")
    header.append("# ============================================")
    header.append("# Sources:")
    for label, url in SOURCES.items():
        if label in stats:
            s = stats[label]
            header.append(f"#   {label}: {s['added']} nodes — {url}")
    header.append(f"# Total unique proxies: {len(merged_proxies)}")
    header.append("# ============================================")
    header.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(header))
        yaml.dump(doc, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)

    print(f"\n  => {len(merged_proxies)} unique proxies written to {output_path}\n")

if __name__ == "__main__":
    files_and_labels = [
        ("sources/yoyapai.yaml", "yoyapai"),
        ("sources/freeSub.yaml", "freeSub"),
        ("sources/free-vpn.yaml", "free-vpn"),
        ("sources/awesome-vpn.yaml", "awesome-vpn"),
        ("sources/Jsnzkpg.yaml", "Jsnzkpg"),
    ]

    merged, stats = merge_all(files_and_labels)
    if not merged:
        print("ERROR: No proxies found from any source!")
        sys.exit(1)

    output_yaml(merged, files_and_labels[0][0], "latest.yaml", stats)
