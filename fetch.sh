#!/bin/bash
set -euo pipefail

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

echo "=== $(date -u +'%Y-%m-%d %H:%M UTC') ==="
echo "Clash Nodes — Multi-Source Aggregation"
echo ""

mkdir -p sources

# ── Source 1: yoyapai.com ──
echo "[1/5] yoyapai.com"
CATEGORY_URL="https://yoyapai.com/category/mianfeijiedian"
POST_PATH=$(curl -sL --connect-timeout 15 -H "User-Agent: $UA" "$CATEGORY_URL" 2>&1 \
  | grep -oP 'href="https://yoyapai\.com/\d+"' \
  | head -1 \
  | grep -oP '/\d+')

if [ -n "$POST_PATH" ]; then
  POST_URL="https://yoyapai.com${POST_PATH}"
  RAW=$(curl -sL --connect-timeout 15 -H "User-Agent: $UA" "$POST_URL" 2>&1)
  YAML_URL=$(echo "$RAW" | sed 's/&#47;/\//g' | grep -oP 'https?://[^"<> ]*\.yaml[^"<> ]*' | head -1)
  if [ -n "$YAML_URL" ]; then
    curl -sL --connect-timeout 15 -H "User-Agent: $UA" "$YAML_URL" -o sources/yoyapai.yaml
    echo "  OK: $(grep -c 'name:' sources/yoyapai.yaml 2>/dev/null || echo 0) proxies"
  else
    echo "  SKIP: no YAML URL found"
  fi
else
  echo "  SKIP: no post found"
fi

# ── Source 2: Ruk1ng001/freeSub ──
echo "[2/5] Ruk1ng001/freeSub"
URLS=(
  "https://gh-proxy.com/raw.githubusercontent.com/Ruk1ng001/freeSub/main/clash.yaml"
  "https://raw.githubusercontent.com/Ruk1ng001/freeSub/main/clash.yaml"
)
for url in "${URLS[@]}"; do
  if curl -sL --connect-timeout 15 -H "User-Agent: $UA" "$url" -o sources/freeSub.yaml 2>/dev/null; then
    if grep -q 'proxies:\|name:' sources/freeSub.yaml 2>/dev/null; then
      echo "  OK: $(grep -c 'name:' sources/freeSub.yaml 2>/dev/null || echo 0) proxies"
      break
    fi
  fi
  echo "  Retry with next URL..."
done

# ── Source 3: Au1rxx/free-vpn-subscriptions ──
echo "[3/5] Au1rxx/free-vpn-subscriptions"
curl -sL --connect-timeout 15 -H "User-Agent: $UA" \
  "https://raw.githubusercontent.com/Au1rxx/free-vpn-subscriptions/main/output/clash.yaml" \
  -o sources/free-vpn.yaml 2>/dev/null || echo "  SKIP: download failed"
echo "  OK: $(grep -c 'name:' sources/free-vpn.yaml 2>/dev/null || echo 0) proxies"

# ── Source 4: awesome-vpn/awesome-vpn ──
echo "[4/5] awesome-vpn/awesome-vpn"
curl -sL --connect-timeout 15 -H "User-Agent: $UA" \
  "https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/clash.yaml" \
  -o sources/awesome-vpn.yaml 2>/dev/null || echo "  SKIP: download failed"
echo "  OK: $(grep -c 'name:' sources/awesome-vpn.yaml 2>/dev/null || echo 0) proxies"

# ── Source 5: Jsnzkpg/Jsnzkpg ──
echo "[5/5] Jsnzkpg/Jsnzkpg"
curl -sL --connect-timeout 15 -H "User-Agent: $UA" \
  "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/main/clash.yaml" \
  -o sources/Jsnzkpg.yaml 2>/dev/null || echo "  SKIP: download failed"
echo "  OK: $(grep -c 'name:' sources/Jsnzkpg.yaml 2>/dev/null || echo 0) proxies"

# ── Merge all sources ──
echo ""
echo "[merge] Combining all sources..."
python3 merge_yaml.py

# ── Health check ──
echo ""
echo "[health] Testing node connectivity..."
python3 health_check.py

# ── Check result ──
if ! grep -q 'proxies:' latest.yaml 2>/dev/null; then
  echo "FATAL: merge failed, latest.yaml is invalid"
  exit 1
fi

TOTAL=$(grep -c 'name:' latest.yaml 2>/dev/null || echo 0)
echo ""
echo "Done: latest.yaml ($TOTAL unique proxies)"
