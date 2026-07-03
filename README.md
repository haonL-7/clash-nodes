# Clash Nodes — Free Proxy Subscription

Daily auto-updated free proxy nodes from [yoyapai.com](https://yoyapai.com).

## Usage

Add this URL to Clash / Shadowrocket / Stash:

```
https://cdn.jsdelivr.net/gh/haonL-7/clash-nodes@main/latest.yaml
```

Alternative (GitHub raw):

```
https://raw.githubusercontent.com/haonL-7/clash-nodes/main/latest.yaml
```

## Web Dashboard

Browse the node directory: **[haonl-7.github.io/clash-nodes](https://haonl-7.github.io/clash-nodes/)**

## How it works

- GitHub Actions runs daily at ~11:07 CST
- Scrapes the latest post from yoyapai.com
- Downloads the Clash YAML subscription
- Generates a static web dashboard
- Commits & pushes back to this repo

## Manual trigger

Repo page → Actions → Daily Node Update → Run workflow
