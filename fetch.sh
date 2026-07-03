#!/bin/bash
set -euo pipefail

echo "=== $(date) ==="

# ── 第一步：从分类页抓取最新文章链接 ──
CATEGORY_URL="https://yoyapai.com/category/mianfeijiedian"
echo "[1/4] 抓取分类页: $CATEGORY_URL"

POST_PATH=$(curl -sL --connect-timeout 15 "$CATEGORY_URL" 2>&1 \
  | grep -oP 'href="https://yoyapai\.com/\d+"' \
  | head -1 \
  | grep -oP '/\d+')

if [ -z "$POST_PATH" ]; then
  echo "❌ 未找到文章链接，退出"
  exit 1
fi

POST_URL="https://yoyapai.com${POST_PATH}"
echo "[2/4] 最新文章: $POST_URL"

# ── 第二步：从文章页抓取 Clash YAML 链接 ──
echo "[3/4] 提取订阅链接..."

# WordPress 会把 URL 中的 / 编码为 &#47;，先抓原始文本再解码
RAW=$(curl -sL --connect-timeout 15 "$POST_URL" 2>&1)

# 解码 HTML 实体：&#47; → /
YAML_URL=$(echo "$RAW" \
  | sed 's/&#47;/\//g' \
  | grep -oP 'https?://[^"<> ]*\.yaml[^"<> ]*' \
  | head -1)

if [ -z "$YAML_URL" ]; then
  echo "❌ 未找到 YAML 链接，退出"
  exit 1
fi

echo "    找到: $YAML_URL"

# ── 第三步：下载 YAML ──
echo "[4/4] 下载配置..."
curl -sL --connect-timeout 15 "$YAML_URL" -o latest.yaml

NODE_COUNT=$(grep -c 'name:' latest.yaml 2>/dev/null || echo 0)
echo "✅ 完成！节点数量: ~$NODE_COUNT"
echo "    文件: latest.yaml"
