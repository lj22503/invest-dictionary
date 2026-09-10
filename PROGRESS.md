# PROGRESS — invest-dictionary（投资词典）

> mangofolio 生态第 3 块 · 术语平权（听得懂）。213+ 中文投资术语，"说人话不装逼"。
> 进度记录：每次对话收尾更新（项目线规范②）。

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
