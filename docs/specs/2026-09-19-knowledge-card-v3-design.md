# 知识卡片 v3 设计规范 — 杂志头条方向

**版本**：v3（2026-09-19 重新设计）
**取代**：v2（朱砂红国风版，2026-08 之前）
**位置**：`web/js/knowledge-card.js`
**适用**：所有 dictionary 词条页的"生成知识卡片"按钮（注入在 `.term-back` 之前）

---

## 1. 设计目标

让生成的 PNG 分享卡片**像一页正式的杂志 / 出版物内容页**——"读得下去"，有内容站的气质而不是 SaaS 截图。

**核心原则**：
- 中文衬线为主（Noto Serif SC）—— 出版物感
- 颜色克制但有温度（主橙 + 深墨 + 暖灰，**不**用朱砂）
- 内容紧凑但不挤（行高 1.85，留白呼吸）
- 装饰元素少而精（eyebrow 眉题、en-title、橙分隔条、章节标题左竖线）

---

## 2. 风格定义（杂志头条）

### 2.1 整体结构

```
┌─ Eyebrow ──────────────────────────────┐
│ MANGOFOLIO · 投资词典                  │ ← Inter 11px 橙 0.3em
├─ 主标题 ─────────────────────────────────┤
│ 14天期逆回购                           │ ← Noto Serif SC 36px 900 深墨
├─ En-title ──────────────────────────────┤
│ A 14-day reverse repo · holiday window  │ ← Fraunces 14px italic 橙 0.15em
━━━━━ 2px 橙短条（80% 宽）━━━━━━━━━━━━━

▌ 央行的跨节红包                       │ ← Noto Serif SC 18px 700 深墨
14 天期逆回购 = 央行把钱借给银行 14 天，│ ← Noto Serif SC 14px 暖墨 line-height 1.85
到期收回本金和利息。央行公开市场操作…
   ┃ 一句话：14 天期逆回购不是"放水"…  │ ← 引用条 2px 橙左边 + italic

━━━━━ 暖墨 12% 弱线 50% 宽 ━━━━━━━━━━━━
▌ 为什么重要                           │
长假前现金需求集中爆发…

[页底]
https://dictionary.mangofolio.com       │ ← Inter 12px 暖灰
内容仅供学习参考，不构成投资建议        │ ← Inter 12px 暖灰
```

### 2.2 章节序号

**决策**：无序号，纯走标题层级。
- 章节标题 Noto Serif SC 18px 700 深墨
- 与正文区分靠字重 + 字号（不要 ② / 02 / 一 ·）

### 2.3 章节分隔线

章节之间用 `rgba(36,22,16,.12)` 暖墨 12% 50% 宽 1px 虚线（dashed 6px 间隔），**不是**橙条（橙条只在标题下方一次性出现）。

---

## 3. 颜色（mangofolio v1.0）

| 角色 | 值 | 用途 |
|---|---|---|
| 背景 | `#FFFFFF` | 纯白底 |
| Eyebrow 橙 | `#F97316` | "MANGOFOLIO · 投资词典" |
| 主标题 | `#241610` | 词条名 |
| En-title 橙 | `#F97316` | 英文副标 italic |
| 顶部橙条 | `#F97316` | 80% 宽 2px 实线（标题下方一次） |
| 章节分隔虚线 | `rgba(36,22,16,.12)` | 暖墨弱 50% 宽 dashed 6px |
| 章节标题 | `#241610` | Noto Serif SC 18px 700 |
| 章节正文 | `#3A332C` | Noto Serif SC 14px 暖墨 |
| 引用竖线 | `rgba(249,115,22,.40)` | 40% 透明橙 2px |
| 引用文字 | `#3A332C` | Noto Serif SC italic 13px |
| URL | `#8A7D70` | 暖灰 |
| 副标 | `#8A7D70` | "内容仅供学习参考..." |

---

## 4. 字体

| 角色 | 字体栈 |
|---|---|
| Eyebrow / URL / 副标 / 数字 | `"Inter","PingFang SC","Microsoft YaHei","Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif` |
| 主标题 / 章节标题 / 章节正文 / 引用 | `"Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif` |
| En-title | `"Fraunces","Noto Serif SC",serif` |

**字体顺序原则**：Inter 优先（v1.0 规范）→ PingFang SC（macOS 默认）→ 微软雅黑（Windows 默认）→ emoji 字体兜底（避免 Windows emoji 渲染异常，参考 CLAUDE.md 2026-09-17 错误记录）。

---

## 5. 尺寸（canvas）

| 参数 | 值 | 备注 |
|---|---|---|
| 宽度 | 1242px | 朋友圈封面标准 |
| 左右留白 | 90px | PAD |
| 正文可用宽度 | 1062px | MAXW |
| 顶部 eyebrow + 标题区高度 | 自适应 | 约 280px |
| 章节间距 | 56px | 章节间呼吸 |
| 章节标题 → 正文间距 | 24px | |
| 章节正文行高 | 1.85 | 14px 字号下约 26px |
| 章节分隔虚线 → 下一章节标题 | 32px | |
| 底部 URL 区高度 | 80px | 包含 URL + 副标 |
| **最小高度** | **1500px** | 短词条也保证视觉重量 |
| **高度策略** | **自适应** | 内容多则高，不裁切 |

---

## 6. 字体大小阶梯

| 角色 | px | 备注 |
|---|---|---|
| Eyebrow | 32px（缩放后）| canvas 上 32px = 网页 11px |
| 主标题 | 72px | canvas 72px = 网页 36px |
| En-title | 36px | canvas 36px = 网页 14px |
| 章节标题 | 48px | canvas 48px = 网页 18px |
| 章节正文 | 38px | canvas 38px = 网页 14px |
| 引用文字 | 36px italic | canvas 36px = 网页 13px |
| URL / 副标 | 32px | canvas 32px = 网页 12px |

> canvas 与网页对应按 2x 缩放（canvas 宽 1242 渲染后网页看 621）。

---

## 7. 数据来源（从 DOM 抓取）

`collectCards()` 函数（保留 v2 已有）从 `article.card` 抓：

| 字段 | DOM 选择器 | 用途 |
|---|---|---|
| 词条名 | `h1.main-title` | 主标题 |
| 章节（breadcrumb 第二项）| `.term-breadcrumb span` 第 N-2 | Eyebrow 副标（如"投资词典 · 第一篇"）|
| 章节标题 | `.card-title` | 每节标题 |
| 章节正文 | `.card-body p` | 每节段落 |
| 章节列表 | `.card-body ul li` | 每节列表 |
| 引用 | `.card-body .card-quote` | 一句话引用条 |

**章节序号（card-number）**：v3 不使用（纯标题层级），DOM 仍抓但不渲染。

---

## 8. 决策记录

| 日期 | 决策 | 原因 |
|---|---|---|
| 2026-09-19 | 用 A 杂志头条方向 | 用户选择；走读感 + 中文出版物气质 |
| 2026-09-19 | 底色纯白 `#FFFFFF` | 用户拍板；与主站卡片一致 |
| 2026-09-19 | 无章节序号 | 用户选择；纯标题层级更极简 |
| 2026-09-19 | 高度自适应 | 用户选择；灵活 + 不裁切 |
| 2026-09-19 | 中文衬线为主 | 出版物感核心 |
| 2026-09-19 | 不用朱砂红 | v1.0 严禁色（v1.0 第 3.3 节）|
| 2026-09-19 | 章节间暖墨虚线（非橙条）| 橙条只 1 次在标题下方；重复橙条会破坏层次 |

---

## 9. 验收清单

- [ ] Eyebrow "MANGOFOLIO · 投资词典" 橙 0.3em tracking
- [ ] 主标题 Noto Serif SC 36px 900 深墨
- [ ] En-title Fraunces 14px italic 橙
- [ ] 标题下方 1 条 2px 橙线 80% 宽
- [ ] 章节标题 Noto Serif SC 18px 700 深墨（无序号）
- [ ] 章节正文 Noto Serif SC 14px line-height 1.85 暖墨
- [ ] 引用条 2px 橙左边 + italic 13px
- [ ] 章节间暖墨虚线 50% 宽 dashed 6px
- [ ] 底部 URL + 副标暖灰
- [ ] canvas 宽度 1242px，高度自适应（最小 1500）
- [ ] 字体链含 emoji 字体（避免 Windows emoji 异常）
- [ ] 无 `#C43A31` 朱砂红（v1.0 严禁）
- [ ] 无楷体 / 仿宋 / "KaiTi"（v1.0 不在字体链）
- [ ] 生成 PNG 后可在微信朋友圈 / 微博长图位正常展示

---

## 10. 迁移计划

**Step 1**：在 `web/js/knowledge-card.js` 替换 buildCard() 函数：
- 删除所有 `ctx.fillStyle = '#c43a31'` 朱砂红
- 改字体栈为 Inter / Noto Serif SC / Fraunces
- 调整字号阶梯（v2 是 56/44/34/30/26，v3 是 72/48/38/36/32）
- 加 Eyebrow + En-title + 80% 宽 2px 橙条（一次性）
- 章节间用暖墨虚线（非橙条）
- 不渲染 card-number 序号

**Step 2**：验证（用一个词条页强刷 + 生成 PNG + 看效果）

**Step 3**：4 个抽样词条页验证（短 / 中 / 长 / 含引用）

**Step 4**：所有 438 个 terms 页共用同一份 JS（无需逐页改）

---

*本规范是 iAsk 09-18 品牌对齐 + dictionary 09-19 知识卡片优化的延续*
*上游品牌库：mangofolio-tokens-v09.css + Mangofolio-设计规范-v1.0.md*
*参考方案 mockup：`.superpowers/brainstorm/2582-1789781366/content/knowledge-card-directions.html`*
