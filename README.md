# Clash 订阅每日更新

每天自动从 [yoyapai.com](https://yoyapai.com) 抓取最新免费节点，输出固定链接。

## 订阅地址

```
https://raw.githubusercontent.com/<你的用户名>/<仓库名>/main/latest.yaml
```

如果 raw.githubusercontent.com 访问不了，用 jsDelivr CDN：

```
https://cdn.jsdelivr.net/gh/<你的用户名>/<仓库名>@main/latest.yaml
```

## 原理

- GitHub Actions 每天北京时间 11:07 自动运行
- 从 yoyapai.com 分类页抓取最新文章
- 提取文章中的 Clash YAML 订阅链接
- 下载并提交到仓库
- 你只需在 Clash / Shadowrocket 中订阅固定 URL 即可

## 手动运行

在 GitHub 仓库页面 → Actions → Daily Node Update → Run workflow
