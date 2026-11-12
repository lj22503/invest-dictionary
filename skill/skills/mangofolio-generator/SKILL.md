---
name: mangofolio-generator
slug: mangofolio-generator
description: 生成说人话的中文金融 / 投资词条，按「一句话定义 + 为什么重要 + 怎么用 + 常见坑」结构输出 Markdown。当用户要新增词条、扩充词库或按词典风格解释概念时使用。触发词：写一个词条、金融术语解释、词条生成。
displayName: 投资翻译
display_name: 投资翻译
display_name_en: Term Translator
summary: 金融词条说人话 —— 把任何一个金融概念，写成普通人 3 分钟能看懂、AI 与搜索引擎都能读懂的词条。
description_zh: 金融词条说人话 —— 把任何一个金融概念，写成普通人 3 分钟能看懂、AI 与搜索引擎都能读懂的词条。
description_en: Write a plain-language Chinese finance dictionary entry in a fixed structure (one-line definition, why it matters, how to use it, common traps) as Markdown.
tags: ["投资词典", "内容生产", "词条写作", "结构化写作"]
homepage: https://dictionary.mangofolio.com/
version: 1.4.1
author: Mangofolio
license: MIT
agent_created: true
category: finance
---
# 投资翻译 · Term Translator

## 定位

把任何一个金融/投资概念，写成一个普通人 3 分钟能看懂、AI 和搜索引擎都能读懂的词条。
本 Skill 沉淀自 Invest Dictionary（投资词典）项目 1000+ 个词条的生成方法论（具体条数以词库站点实时数据为准，勿硬编码旧值）。

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

### 输出 Markdown 词条（唯一格式，不出 HTML）

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

## 词条校验（输出前必做）

本 Skill 会点名“该看哪几个词条”。这些词条必须真实存在，不能凭记忆编。

**优先用接口查（一次拿到词条名、章节、四张卡片小标题，返回约 1KB）：**

```bash
curl -s 'https://dictionary.mangofolio.com/api/term-search?q=CPI&n=5'
```

命中结果里的 `t` 是词条名、`u` 是站内链接、`c` 是所属章节、`k` 是四张卡片的小标题。
接口不通时再用下面的本地索引：

**用命令查，不要把整份索引读进上下文。** 索引有 1100+ 行 / 50 KB，整份读进来会明显拖慢响应，
而你每次需要的只是其中 3–5 行。以下路径相对本 Skill 目录：

```bash
grep -F "可转债" references/term-index.txt          # 精确词
grep -F -m 8 "利率" references/term-index.txt       # 模糊找候选
```

路径打不开时，先用 `ls references/` 或 `find . -name term-index.txt` 定位一次再查。
**不要反复重试同一条失败命令**——重试的代价比不校验还大。

每行格式是 `词条名<TAB>文件名`。命中后用文件名拼链接：
`https://dictionary.mangofolio.com/terms/<文件名去掉 .html>`

- **完全相等** → 直接用
- **没命中** → 去掉括注再查一次（`可转债（可转换公司债券）` → 查 `可转债`）
- **还没命中** → 换一个关键词再查，取语义最近的一条
- **两次都没有** → 只说“该查哪个方向”，不点名具体词条

**没有命令执行能力时**：不要整份读取索引。可以点名你最确定的词条，
但要在输出末尾注明“词条名未逐一核对”，绝不允许凭印象编一个词条名出来。

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

## 参考

- 在线词典：https://dictionary.mangofolio.com/
- 数据源：https://dictionary.mangofolio.com/（1000+ 词条，条数以线上为准，勿硬编码）
- 查词接口：`GET https://dictionary.mangofolio.com/api/term-search?q=CPI&n=5`
- Markdown 词条模板：`templates/term-card.md`
