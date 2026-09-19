# PROGRESS — invest-dictionary（投资词典）

> mangofolio 生态第 3 块 · 术语平权（听得懂）。213+ 中文投资术语，"说人话不装逼"。
> 进度记录：每次对话收尾更新（项目线规范②）。

## 2026-09-19 · 知识卡片 v3

### 背景
"生成知识卡片"下载的 PNG 是 dictionary 站最核心的"分享出去"素材。
v2 版（2026-08 之前）用朱砂红 + 羊皮纸 + 楷体国风体系，与 mangofolio v1.0 品牌库脱节；
mangofolio v1.0 第 3.3 节明令严禁朱砂红 `#C43A31`。
按规范重构为杂志头条风格。

### 改动
- `web/js/knowledge-card.js` — 整个 `buildCard()` 重写为 v3
  - 主色朱砂红 `#C43A31` → 芒果橙 `#F97316`（v1.0 严禁色移除）
  - 底色羊皮纸 `#f5efe0` → 纯白 `#FFFFFF`
  - 字体链 `"PingFang SC","Microsoft YaHei"` → Noto Serif SC 主导（中文衬线）
  - 字号 1242px 宽（朋友圈封面标准），高度自适应（最小 1500）
  - 加 Eyebrow 眉题 "MANGOFOLIO · 投资词典" + En-title Fraunces italic + 80% 宽 2px 橙条（杂志头条标志）
  - 章节序号移除（无 ① ② / 02 / 一 ·，纯标题层级）
  - 章节间分隔：橙色 4px 短条 → 暖墨 12% 50% 虚线 dashed 6px
  - 字体链补 `"Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji"`（避免 Windows emoji 异常，参考 CLAUDE.md 2026-09-17 错误）
  - 底部距底 40px 留白 + URL 右对齐（杂志风）

### 备份与回滚
- `web/js/knowledge-card.js.bak-20260919` 保留（10135 bytes，原始 v2）
- 回滚：`mv web/js/knowledge-card.js.bak-20260919 web/js/knowledge-card.js`

### 验证
- 4 个抽样词条页强刷 + 生成 PNG + 视觉清单逐项核对
- 全部通过；唯一微调是底部距底 40px（Task 4 视觉验证触发）

### 全 438 个 terms 页
- 共用同一份 `web/js/knowledge-card.js`，无需逐页改
- 自动生效于所有 terms 页（`<script src="../js/knowledge-card.js">`）

### 设计文档
- spec: `docs/specs/2026-09-19-knowledge-card-v3-design.md`
- plan: `docs/superpowers/plans/2026-09-19-knowledge-card-v3.md`
- 模拟方案: `.superpowers/brainstorm/2582-1789781366/content/knowledge-card-directions.html`

### 下一步
- **首页 v1.0 品牌对齐**（开新对话）
- iAsk 已对齐（09-18），fintools / brain 已 v08，dictionary 是生态里唯一未做主页对齐的站
- 待办：读 index.html (259KB) → 对照 v1.0 规范逐项审计 → 出首页改造方案

---

## 2026-09-10 · 埋点 SDK 引入

### 背景
按 OPC OS 事实标准核对，invest-dictionary **此前 0 埋点**（Vercel Insights 只有自动 pageview，无自定义事件）。

### 改动
- `web/js/tracker.js`（新增）— 与 invest-tools 同源的零依赖 SDK
  - 公共属性：page_referrer（同源）+ utm_5 透传
  - 自动 page_view / landing_view / 滚动深度（首页）
  - 公开 API：`window.track(name, params)` / `recordDuration` / `endDuration`
  - 声明式 `[data-track]` + `[data-track-params]` 绑定
- `web/index.html`：引入 `/js/tracker.js`（与 Vercel Insights 并存）

### 不做（避免过度设计）
- 业务元素具体 `[data-track]` 标记：留给后续按页面迭代（首页词条卡 / 搜索框 / 订阅按钮 / 跳转 / footer / 分享 / 热词轮播）
- 词条详情页事件：terms/ 目录下文件多，按需逐个补

### 验证
- commit `625c430` push `lj22503/invest-dictionary` main 成功
- 与 iAsk / invest-tools / invest-brain SDK 接口形态对齐

## 2026-08-12

### 每日热词持续产出
- 每日热词词条页新增（commit `287d2fb`：霍尔木兹海峡/美国CPI/日元/恒生科技指数 + dictionary.json/sitemap 更新）
- 8-13 热词预览（commit `6b64d53`：隔夜逆回购/打新/公积金装修提取/资本开支）
- 一鱼多吃落地：222 词条 title 批量场景化 + robots 放行 AI 爬虫 + llms.txt + 知识卡片脚本 + PWA + 两站互导（T2/T5/T6/T7，一鱼多吃代码改动-20260815）

### 当前状态
- 线上：dictionary.mangofolio.com（213+ 词条，SEO/GEO 底子好）
- 下一步：内容挖掘跑账号矩阵（词条 → 小红书/公众号素材）

## 历史

### 2026-08-01 ~ 08-11
- 222 词条完成（DefinedTerm schema 教科书级）
- 邮箱订阅 E8 落地（投资词典-邮箱订阅后端落地经验-20260809）

---

## 待办（下一步）

- [ ] E8 邮箱订阅 5 条待办（见 00-Inbox/投资词典-邮箱订阅后端落地经验-20260809.md）
- [ ] 词条内容挖掘 → 账号矩阵素材（小红书/知乎）
- [ ] 词条 × 工具两站互导持续
