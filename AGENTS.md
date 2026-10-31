---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 1c835e55ba3b06878e6538b2edadf703_3e37d843b66a11f18e4752540024e231
    ReservedCode1: ZHvROtgCNoi1cPg8aR9pE4tjhY3Qz9jLqU1rE2UEp+Bi+n3LU0EoARVJ1yUcWB9BQZn3CPf8CKuMU5o8OxHOhpGDAOVNGwUsM/vo5SJujkQZRxW2PHC4ikkJJmlltcW0Gm6EyqcWURAJIzlp1Uj/oBnNABAz0NByWcL2jR5uwxwtgzqj0LJe58tSVWo=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 1c835e55ba3b06878e6538b2edadf703_3e37d843b66a11f18e4752540024e231
    ReservedCode2: ZHvROtgCNoi1cPg8aR9pE4tjhY3Qz9jLqU1rE2UEp+Bi+n3LU0EoARVJ1yUcWB9BQZn3CPf8CKuMU5o8OxHOhpGDAOVNGwUsM/vo5SJujkQZRxW2PHC4ikkJJmlltcW0Gm6EyqcWURAJIzlp1Uj/oBnNABAz0NByWcL2jR5uwxwtgzqj0LJe58tSVWo=
---



# AGENTS.md

> 给接手本仓库的人类开发者与 AI Agent 的现役规则。最后更新：2026-10-31

## 项目一句话定位

投资词典（Invest Dictionary）：995 个中文投资术语，说人话不装逼。独立项目，不并入 InvestBuddy。线上站：https://dictionary.mangofolio.com

## 怎么跑起来

```bash
# 静态站点，零依赖零构建
cd web && python -m http.server 8080
# 打开 http://localhost:8080
```

Vercel 部署（web/ 为根目录，vercel.json 已配置 cleanUrls + 安全响应头）。

## 技术栈

纯静态 HTML/CSS/JS（无框架）；Schema.org DefinedTerm 结构化数据；Vercel 托管；Agent Skill（Markdown 方法论）。

**埋点链路**：`web/js/tracker.js` 零依赖 SDK + `web/api/events.js` Edge function 走 `@vercel/kv`（与 5 站共享 `invest-dictionary-kv`，key 前缀 `evt:dictionary:`）；公共属性 page_referrer（同源）+ utm_5 透传；KV 还承担邮件订阅（subscribers set + subscriber:meta hash）与每日热词缓存（daily_hot）。

## 目录与约定

- `web/` — 线上站点（`index.html` 首页、`dictionary.html` 全部词条、`guide.html` 使用指南、`privacy.html` 隐私政策、`terms-of-service.html` 用户协议、`terms/` 995 词条页、`dictionary.json`、`sitemap.xml`、`llms.txt`、`robots.txt`、`vercel.json`）
- `web/css/mangofolio-tokens-v09.css` — 颜色/字体/间距/圆角**唯一令牌源**；`web/css/site.css` — 三页共用外壳（色带 `.band--*` / 页头 / 页脚 / 区块头 / 按钮 / 卡片 / 目录 / 代码块）。页面专属样式才写进各自 `<style>`，禁止三页各抄一份 header/footer
- 三页设计口径见 `docs/specs/三页改版设计规格.md`（色带表 / 信息架构 / 硬规则 / 验收标准）；外来参考包只放 `docs/reference/`，**不进 web/**
- `web/dictionary.json` — 词条唯一数据源（id/slug/chapter/description/related）
- `skill/invest-dictionary-generator/` — 金融词条生成 Skill（SKILL.md + templates + examples）
- `docs/` — PROJECT_GOALS.md（目标清单）、PITFALLS.md（坑点）、design-tokens.md（令牌速查）、HANDOFF.md（接手说明）、BRAND_AUDIT_2026-09-19.md、superpowers/（spec 与 plan）
- **slug 归一化**：词条名中 `/`、`*`、`>` 一律替换为 `_`（文件名）；所有链接（相关词条、首页卡片）必须用归一化文件名
- **域名**：正式域名 dictionary.mangofolio.com；禁止旧域名 `investbuddy.com` 残留。扫描范围含 canonical / og:url / sitemap / robots **及页内所有绝对 URL（社交分享、复制链接等）**；匹配模式用 `//investbuddy.com`，避免误伤合法子站 `investbuddy.mangofolio.com`
- 词条质量标准：说人话（一句话定义）、有场景、讲坑点、能搜索

## 历史回填闸门（2026-10-31 新增，硬规则）

> 由来：9-14 诊断出的 4 个硬伤，到 10-30 复查**一个都没修**，期间词条从 380 涨到 995。
> 根因是**调研结论没有强制回填通道** —— 调研停在 md 里，没变成检查项。这条规则就是补那个通道。

**规则 1 —— 调研结论必须落地成检查项。**
任何审计/调研产出结论后，先问：「这条结论能不能变成一条可执行的检查？」
能 → **当天**写进 `scripts/site-audit.py` 的 `backfill` 维度；不能 → 写进 issue 排期。
**不允许只躺在 md 里等人记起。**

**规则 2 —— backfill 维度 5 项必须全绿**（当前实测均 ✅）：

| 检查项 | 判什么 |
|---|---|
| P0-1 URL 残留 `.html` | 本站域名 + 相对路径的 URL 后缀，**含分享链接 query 里二次编码的**（`%2F` 分隔） |
| P0-2 首页静态词条内链 | 剥掉 `<script>` 后数真锚点，覆盖率下限 95% |
| sitemap 覆盖率 | 词条页 + 主页面双向零缺口 |
| llms.txt 覆盖率 | **解码后**比对（不解码会假性全通过） |
| 隐私政策 / 用户协议页 | 文件存在 + footer 挂入口 |

**规则 3 —— URL 一律 clean URL（不带 `.html`）。**
覆盖范围：canonical / og:url / JSON-LD / sitemap / 相关词链接 / **分享链接的 query 参数**。
> 踩过的坑：微博分享链接里嵌的是二次编码 URL，`url=...%2Fterms%2Fxxx.html`，
> 当年的规范化脚本没扫 query 参数，20 个页面漏网，分享出去多一跳 308。

**规则 4 —— 写检查项时的三条经验（别再踩）：**

1. **口径对齐实际形态**：首页静态链接是相对路径 `terms/xxx`，正则只认 `/terms/` 会误报「0 条」。
2. **别扫全文找关键词**：CSS 注释里的基准页路径、JSON 字段 `"filename": "货币.html"`、
   外站本来就带 `.html` 的（`invest-tools.mangofolio.app/tools/xirr.html`）全是误报源 → 只判本站。
3. **先解码再比对**：llms.txt 用百分号编码，不解码会得到「全通过」的假象
   （当年「758/985」的错判就是这么来的）。

## 当前状态与下一步

- 已推送 GitHub（main），仓库 SEO 已配置（About + 20 Topics）；线上站 https://dictionary.mangofolio.com 已上线并验证
- 品牌视觉：mangofolio v1.0 全量落地（2026-09-22）；令牌权威源 `web/css/mangofolio-tokens-v09.css`，速查 `docs/design-tokens.md`
- 词条数据：`web/terms` **995 页**；唯一数据源 `web/dictionary.json`；首页内嵌 `ALL_ENTRIES` 由 `scripts/sync_all_entries.py` 同步；`web/sitemap.xml` 由 `scripts/generate-sitemap.py` 生成 —— 三者条数必须一致（页面声称条目数同理）
- **提交前必跑（两条命令，缺一不可）**：
  1. `python scripts/check-consistency.py` —— 一致性门禁 10 项（计数一致性 / id·slug·filename 唯一性 / 页内断链 / sitemap 双向覆盖 / 旧域名残留 / ALL_ENTRIES 同步）
  2. `python scripts/site-audit.py` —— 站点体检 26 项，其中 **backfill 维度 5 项必须全绿**（见下）
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
*（内容由AI生成，仅供参考）*
