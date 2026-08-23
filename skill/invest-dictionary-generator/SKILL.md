---
name: invest-dictionary-generator
description: 生成"说人话"的中文金融/投资词条，输出可直接发布为投资词典（Invest Dictionary）网页的词条内容与 HTML 页面。当用户想新增投资术语词条、扩充投资词典、按"说人话不装逼"风格解释金融概念时使用。触发词：投资词条、金融术语、说人话、Invest Dictionary、投资词典词条生成。
version: 1.0.0
license: MIT
---

# 金融词条生成器 · Invest Dictionary Generator

## 定位

把任何一个金融/投资概念，写成一个普通人 3 分钟能看懂、AI 和搜索引擎都能读懂的词条。
本 Skill 沉淀自 Invest Dictionary（投资词典）项目 238 个词条的生成方法论。

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

- 复用仓库 `skill/invest-dictionary-generator/templates/term-page.html` 模板（已按线上生产页 article.card 结构重建，勿再用旧 story-card 结构）
- 头部元数据必填：`title`、`description`（一句话定义）、`canonical`（正式域名）、OG/Twitter Card、Schema.org `DefinedTerm` JSON-LD
- 正文用故事卡结构（`article.card`，含 `.card-title`/`.card-body`/`.card-quote`/`.card-number`/`.step-list`），样式复用模板内置纸感手账风格
- 页尾加"上下篇导航"（term-pager）与"相关词条"（term-related，链接用归一化编码 URL）

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

- [ ] 第一句是大白话定义（外行能懂）
- [ ] 正文 ≥2 张故事卡，且覆盖"这是什么 / 为什么重要"
- [ ] 含至少 1 个真实场景或数字例子
- [ ] 含"常见坑 / 误区"（除非概念确无坑）
- [ ] 相关词条链接全部可跳转（用归一化文件名）
- [ ] canonical / og:url 域名正确（正式站 https://dictionary.mangofolio.com）
- [ ] 无假二维码、无 HTML 残留（如 `<div>`、CSS 碎片混入正文）
- [ ] 页面条目数与数据源一致

## 参考

- 在线词典：https://dictionary.mangofolio.com/
- 数据源：`web/dictionary.json`（238 词条、22 篇章）
- 模板：`templates/term-page.html`、`templates/term-card.md`
