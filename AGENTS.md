# AGENTS.md

> 给接手本仓库的人类开发者与 AI Agent 的现役规则。最后更新：2026-08-01

## 项目一句话定位

投资词典（Invest Dictionary）：213 个中文投资术语，说人话不装逼。独立项目，不并入 InvestBuddy。线上站：https://dictionary.mangofolio.com

## 怎么跑起来

```bash
# 静态站点，零依赖零构建
cd web && python -m http.server 8080
# 打开 http://localhost:8080
```

Vercel 部署（web/ 为根目录，vercel.json 已配置 cleanUrls + 安全响应头）。

## 技术栈

纯静态 HTML/CSS/JS（无框架）；Schema.org DefinedTerm 结构化数据；Vercel 托管；Agent Skill（Markdown 方法论）。

## 目录与约定

- `web/` — 线上站点（index.html、terms/ 213 词条页、dictionary.json、sitemap.xml、robots.txt、vercel.json）
- `web/dictionary.json` — 词条唯一数据源（id/slug/chapter/description/related）
- `skill/invest-dictionary-generator/` — 金融词条生成 Skill（SKILL.md + templates + examples）
- `docs/` — PROJECT_GOALS.md（目标清单）、PITFALLS.md（坑点）
- **slug 归一化**：词条名中 `/`、`*`、`>` 一律替换为 `_`（文件名）；所有链接（相关词条、首页卡片）必须用归一化文件名
- **域名**：正式域名 dictionary.mangofolio.com；禁止 investbuddy.com 残留（canonical/og/sitemap/robots）
- 词条质量标准：说人话（一句话定义）、有场景、讲坑点、能搜索

## 当前状态与下一步

- 已推送 GitHub（main, a6d6f05），仓库 SEO 已配置（About + 20 Topics）
- **待办**：Vercel 登录授权 → 部署 web/ → 绑定 dictionary.mangofolio.com → live 验证
- 词条数据：213 条（页面声称条目数必须与 dictionary.json 一致）
