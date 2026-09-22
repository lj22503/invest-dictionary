---
name: invest-dictionary-generator
description: 生成"说人话"的中文金融/投资词条，输出可直接发布为投资词典（Invest Dictionary）网页的词条内容与 HTML 页面。当用户想新增投资术语词条、扩充投资词典、按"说人话不装逼"风格解释金融概念时使用。触发词：投资词条、金融术语、说人话、Invest Dictionary、投资词典词条生成。
version: 1.1.0
license: MIT
---

# 金融词条生成器 · Invest Dictionary Generator

## 定位

把任何一个金融/投资概念，写成一个普通人 3 分钟能看懂、AI 和搜索引擎都能读懂的词条。
本 Skill 沉淀自 Invest Dictionary（投资词典）项目 448 个词条的生成方法论（词条数须与 `web/dictionary.json` 实际条目数一致）。

仓库：https://github.com/lj22503/invest-dictionary
在线词典：https://dictionary.mangofolio.com/

## 词条质量三原则

1. **一句话定义**：词条第一句必须让外行听懂，禁止"术语套术语"。例：货币 = "你手里攥着的 100 块"，而不是"一般等价物"。
2. **真实场景**：每个概念必须放进真实生活/投资场景，讲"关我什么事"。
3. **避开装逼**：禁止堆砌行话；必须用到行话时，紧跟大白话解释（如"贴现率（未来钱打折成现在值多少的比率）"）。

## 词条内容结构（5 部分）

每篇词条正文由 2~4 张"故事卡"组成，每张卡对应一个读者会问的问题：

| 卡片 | 要回答的问题 | 写法要点 |
|------|-------------|---------|
| 这是什么 | 一句话定义 + 核心机制 | 先用大白话定义，再用比喻/生活例子展开 |
| 为什么重要 | 关我什么事 | 结合赚钱/亏钱/避坑场景，给出具体数字或对比 |
| 怎么用 / 怎么看 | 实操怎么用 | 步骤化（step-list），给判断标准、阈值、操作口诀 |
| 常见坑 / 误区 | 哪里容易翻车 | 反常识点、新手误区、容易被骗的地方 |

每张卡的标题用"口语化提问"或"结论式短语"，例如：
- ✅ 「钱为什么能买东西？」「为什么说 CPI 会咬人？」「定投的坑：跌了不敢买」
- ❌ 「货币的起源与发展」「CPI 概述」「定投策略分析」

## 输出格式

### 方式 A：Markdown 词条（推荐，便于他人 Review 与贡献）

```markdown
# 词条名（别名）

> 一句话定义，≤30 字，必须大白话

## 1. 这是什么
...

## 2. 为什么重要
...

## 3. 怎么用 / 怎么看
- 步骤 1
- 步骤 2

## 4. 常见坑 / 误区
- 坑 1

---

**相关词条**：词条A、词条B（用归一化 slug 命名，见"命名规范"）
```

### 方式 B：HTML 词条页（用于直接发布到投资词典）

- 视觉与结构的**唯一基准页**：`web/terms/14天期逆回购.html`。生成任何 HTML 词条页之前，必须先 read_text 该基准页，逐项对齐其色板、字体链、圆角、版式与页脚；仓库模板 `templates/term-page.html` 尚未完成品牌视觉同步（后续步骤处理），模板与基准页冲突时一律**以基准页为准**
- 头部元数据必填：`title`、`description`（一句话定义）、`canonical`（正式域名）、OG/Twitter Card、Schema.org `DefinedTerm` JSON-LD
- 正文用故事卡结构（`article.card`，含 `.card-title`/`.card-body`/`.card-quote`/`.card-number`/`.step-list`）；样式一律对齐基准页，**禁止复用任何"纸感手账"类旧样式**
- 页尾加"上下篇导航"（term-pager）与"相关词条"（term-related，链接用归一化编码 URL）

### 方式 B 的品牌视觉硬约束（强制，与基准页逐项对齐）

- **色板（只允许这些颜色，全部写成页内 `:root` 变量）**
  - 纯白 `#FFFFFF`（`--bg-paper` / `--card-bg`）、主橙 `#F97316`（`--accent`）、深橙 `#E05E0A`（`--accent-hover`）
  - 正文墨 `#3A332C`（`--ink`）、暖灰 `#8A7D70`（`--ink-light`）、标题深墨 `#241610`、描边 `rgba(36,22,16,.10)`（`--border-dashed`）
  - 允许的透明色仅限 `#241610` 系（.02/.04/.05/.06/.08/.10/.18/.30）、`#F97316` 系（.04/.06/.08/.10/.15/.18/.30/.40）与 `rgba(255,255,255,.92)`
  - 禁止品牌外色值、命名色（red/blue/gray 等）、纸纹/宣纸纹理与噪点背景；渐变只允许基准页的品牌虚线装饰（`repeating-linear-gradient` 的 `#F97316`、`#E05E0A` 或 `rgba(36,22,16,.18)` 短划）
- **字体链（每条 `font-family` 末尾必须带 emoji 段 `"Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji"`；禁止裸 `serif` / Times）**
  - body（页面级）：`"Inter", "Noto Serif SC", "Source Han Serif SC", "PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, "Segoe UI", <emoji 段>, sans-serif`
  - 组件 / UI（面包屑、分享条、正文段落、导航、页脚等）：`"Inter", "PingFang SC", "Microsoft YaHei", -apple-system, "Segoe UI", sans-serif, <emoji 段>`
  - 标题衬线：`"Noto Serif SC", "Source Han Serif SC", "Songti SC", serif, <emoji 段>`（次级标题可省 `"Songti SC"`）
  - 数字与装饰：`"Fraunces", "Noto Serif SC", serif, <emoji 段>`
  - 等宽：`"JetBrains Mono", "Fraunces", ui-monospace, Consolas, monospace, <emoji 段>`（可省 `"Fraunces"`）
  - 除以上字族外不得引入其他字族；字体文件引入（Google Fonts 等）由模板层统一处理，词条生成任务不得自行添加外部字体请求
- **圆角**：只允许 `16px`（卡片/面板）、`9999px`（按钮/标签/胶囊）、`2~12px`（小元素）、`50%`（圆点）
- **版式基线**：html 字号 17px；body `line-height:1.9`、`letter-spacing:.01em`；`.paper` 固定 `max-width:720px`、白底、`1px solid rgba(36,22,16,.10)` 边框、16px 圆角、阴影 `0 4px 8px rgba(36,22,16,.08), 0 12px 32px rgba(36,22,16,.10)`；`h1.main-title` 为 3.2rem / 900 字重 / `#241610`，下方品牌橙虚线装饰
- **结构顺序（固定，类名与位置不得增删改名）**：copy-toast → `nav.term-breadcrumb` → `.share-bar` → `.paper`（header：`h1.main-title` + `p.subtitle`「—— 投资词典 · Invest Dictionary」；正文 2~4 张 `article.card`，卡间 `.card-divider`）→ `nav.term-pager` → `.term-related` → `.term-back` → `.term-footer-spacer` → `footer.mangofolio-nav`
- **页脚**：全站统一 `footer.mangofolio-nav`，「Mangofolio 系列」标签 + 5 个系列链接（投资词典 Dictionary / 投资大脑 Brain / 投资伙伴 Buddy / 市场观察 View / 财务工具箱 FinTools，链接色 `#F97316`）+ 免责声明「内容由 AI 生成，仅供学习参考，不构成投资建议」；每页只出现一次，页脚样式不得重复注入

## 命名规范（重要，易踩坑）

- **slug 规则**：词条名中含 `/`、`*`、`>` 等文件名非法/危险字符时，一律替换为 `_`（下划线）。
  - 例：`M0 / M1 / M2（货币供应量）` → 文件名 `M0 _ M1 _ M2（货币供应量）.html`
  - 例：`新股（IPO / 打新）` → `新股（IPO _ 打新）.html`
- **相关词条链接必须用归一化文件名**，禁止直接 `href=词条名.html`，否则含特殊字符的词条会断链。
- 页面声称的条目数必须与数据源实际条目数一致（曾出现副标题写"217 个"而实际 213 条的脏数据）。

## 贡献新词条（欢迎 PR）

1. 先查 `dictionary.json` 是否已存在同义词条（避免重复）。
2. 在对应篇章下新建 Markdown 词条（方式 A），通过 Review 后再生成 HTML。
3. 提交 PR 时：同时提供词条 Markdown、HTML 页、并在 `dictionary.json` 中登记（id 递增、slug 用归一化命名、related 填相关词条 id）。
4. 命名与风格不符会被维护者打回：说人话、有场景、有坑点。

## 质量检查清单（生成后必查）

**内容项**

- [ ] 第一句是大白话定义（外行能懂）
- [ ] 正文 ≥2 张故事卡，且覆盖"这是什么 / 为什么重要"
- [ ] 含至少 1 个真实场景或数字例子
- [ ] 含"常见坑 / 误区"（除非概念确无坑）
- [ ] 相关词条链接全部可跳转（用归一化文件名）
- [ ] canonical / og:url 域名正确（正式站 https://dictionary.mangofolio.com）
- [ ] 无假二维码、无 HTML 残留（如 `<div>`、CSS 碎片混入正文）
- [ ] 页面条目数与数据源一致

**视觉项（任一项不通过必须先修正，未通过不得写入仓库）**

- [ ] 页内存在 `:root` 变量块，色值全部来自品牌色板
- [ ] 无品牌外色值、无纸纹/宣纸/噪点背景、无非品牌渐变（全量核对 `#` 与 `rgba` 取值）
- [ ] 字体链与基准页一致且含 emoji 段，无裸 `serif`
- [ ] 圆角只出现 `16px` / `9999px` / `2~12px` / `50%`
- [ ] `footer.mangofolio-nav` 仅 1 处，5 个系列链接与免责声明齐全，页脚样式未重复注入
- [ ] `subtitle` 为固定文案「—— 投资词典 · Invest Dictionary」，未混入其它词条名
- [ ] 无占位符残留（`{{ }}`、TODO、lorem、xx%）
- [ ] 结构完整：面包屑 → 分享条 → `.paper`（h1 + subtitle + 2~4 张 `article.card`）→ term-pager → term-related → term-back
- [ ] 元数据齐备：`title` / `description` / `canonical` / OG / Twitter Card / Schema.org `DefinedTerm` JSON-LD
- [ ] 无 `googleapis` 等外部字体请求（字体引入由模板层统一处理）

## 参考

- 在线词典：https://dictionary.mangofolio.com/
- 数据源：`web/dictionary.json`（当前 448 词条；写法上任一处声称的条目数必须与该文件实际条目数一致，勿硬编码旧值）
- 视觉基准页：`web/terms/14天期逆回购.html`（品牌视觉与结构的唯一基准，冲突时以此页为准）
- 模板：`templates/term-page.html`、`templates/term-card.md`（模板层品牌视觉同步进行中，尚未完成前不得作为视觉依据）
