#!/bin/bash
set -euo pipefail

echo "=== $(date -u +'%Y-%m-%d %H:%M UTC') ==="

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
echo "    最新文章: $POST_URL"

# ── 第二步：从文章页抓取 Clash YAML 链接 ──
echo "[2/4] 提取订阅链接..."
RAW=$(curl -sL --connect-timeout 15 "$POST_URL" 2>&1)
YAML_URL=$(echo "$RAW" | sed 's/&#47;/\//g' | grep -oP 'https?://[^"<> ]*\.yaml[^"<> ]*' | head -1)

if [ -z "$YAML_URL" ]; then
  echo "❌ 未找到 YAML 链接，退出"
  exit 1
fi
echo "    找到: $YAML_URL"

# ── 第三步：下载 YAML ──
echo "[3/4] 下载配置..."
curl -sL --connect-timeout 15 "$YAML_URL" -o latest.yaml

# 校验：确保下载的是有效的 Clash 配置文件
if ! grep -q 'mixed-port\|proxies:' latest.yaml 2>/dev/null; then
  echo "❌ 下载内容无效（非 Clash 配置），退出"
  exit 1
fi

# ── 第四步：生成网页（解析 YAML + 渲染 HTML） ──
echo "[4/4] 生成网页..."
python3 build_html.py

echo "✅ 完成！latest.yaml + index.html 已更新"
