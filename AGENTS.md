---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 1c835e55ba3b06878e6538b2edadf703_25385af48d8611f1bfea525400e6dd8f
    ReservedCode1: nrmtUC2eeoX4phKV9EyPVKWX2I5vtWP4ambbBNQzJUsfEL8TIsorg8w0lGOuL8f0PulBtuBmEtwEvAUs1weKXp1R2YU21g5w2KKol3vPmeprKLJLgGSVQbpGDNidpT+eXVHjcEnBTRqoNjahD7WBNtkCBnhc0kyYCHsVF1kvSvBaiRZDMe7TlZ5Y7cg=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 1c835e55ba3b06878e6538b2edadf703_25385af48d8611f1bfea525400e6dd8f
    ReservedCode2: nrmtUC2eeoX4phKV9EyPVKWX2I5vtWP4ambbBNQzJUsfEL8TIsorg8w0lGOuL8f0PulBtuBmEtwEvAUs1weKXp1R2YU21g5w2KKol3vPmeprKLJLgGSVQbpGDNidpT+eXVHjcEnBTRqoNjahD7WBNtkCBnhc0kyYCHsVF1kvSvBaiRZDMe7TlZ5Y7cg=
---

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
*（内容由AI生成，仅供参考）*


---

## 提交前自查 4 问（2026-08-12 项目线规范，谁提交谁查）

> 任何 agent 在本仓库提交代码前，先过这 4 问（30 秒）：
1. **我改的是哪个项目？**（commit message 写明项目名）
2. **这个功能是不是已经存在？**（有没有重复实现——查一遍再写）
3. **我有没有绕过统一入口？**（有统一路由/工具就走统一入口，不另开独立通道）
4. **我改的是不是这个项目该改的？**（没串线——只动本项目文件）

**违反任一 → 停下修正后再提交。**


---

## 对话收尾流程（2026-08-12 项目线规范②，每次对话工作完成后必走）

> 完整规范：`D:\ObsidianVault\00-Meta\项目线-对话收尾流程.md`

1. **更新项目文档**：PROGRESS.md（今日进度：做了什么/下一步/卡点）+ docs/PITFALLS.md（今日坑点：现象→根因→修复→预防）
2. **neat-freak 六面审计**：代码/运行态/文档/规则/记忆/工作区一致性（五态：verified-current/changed-and-verified/pending/out-of-scope/not-applicable），消除多真相并存
3. **同步 GitHub**：commit（conventional commits + 提交前自查 4 问）+ push
4. **更新 Obsidian 02-Projects**：项目上下文.md / 项目经验.md（衔接③）
