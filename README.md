---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 1c835e55ba3b06878e6538b2edadf703_35651056d20911f1992e525400638852
    ReservedCode1: xHT9+rjA0XdjGKHe/2/ebhI53K3f/SMVM/co+lmkt8O3pQxe8hAPfp74UF0oUCEX61uxXsz96mb2smC+4bPbs9GOSjYMz4UFcfmK/axUM812y1+lGyYPIomOjBeEv80lsASqQ0JoTsPtnKefbNeWdFkmaS582e2Y2+ARYC3XPiBjZmw4V1yzNpLCmPo=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 1c835e55ba3b06878e6538b2edadf703_35651056d20911f1992e525400638852
    ReservedCode2: xHT9+rjA0XdjGKHe/2/ebhI53K3f/SMVM/co+lmkt8O3pQxe8hAPfp74UF0oUCEX61uxXsz96mb2smC+4bPbs9GOSjYMz4UFcfmK/axUM812y1+lGyYPIomOjBeEv80lsASqQ0JoTsPtnKefbNeWdFkmaS582e2Y2+ARYC3XPiBjZmw4V1yzNpLCmPo=
---

<div align="center">

# 投资词典 · Invest Dictionary

**472 个投资术语，说人话，不装逼。**

一个面向普通人的**中文投资术语词典**（Chinese investment dictionary / financial glossary）。
每一个词条都用"3 分钟能看懂"的方式解释：一句话定义 → 为什么重要 → 怎么用 → 常见坑。

[![在线词典](https://img.shields.io/badge/在线体验-dictionary.mangofolio.com-c43a31?style=for-the-badge)](https://dictionary.mangofolio.com)
[![GitHub Stars](https://img.shields.io/github/stars/lj22503/invest-dictionary?style=for-the-badge&color=gold)](https://github.com/lj22503/invest-dictionary/stargazers)
[![License](https://img.shields.io/badge/License-Apache--2.0-yellow?style=for-the-badge)](LICENSE)
[![Skill](https://img.shields.io/badge/Agent_Skill-可复用-8b5040?style=for-the-badge)](skill/invest-dictionary-generator)

**中文金融扫盲 · 说人话的投资科普 · 472 个理财必备术语 · 覆盖股票/基金/债券/保险/房产/宏观**

</div>

---

## 为什么做这个

市面上的金融术语解释要么太学术（"货币是充当一般等价物的特殊商品"），要么太营销（"带你抓住财富风口"）。
投资词典只做一件事：**把每一个投资术语，讲成人话**。

- 货币 = **你手里攥着的 100 块**
- 市盈率 = **回本需要多少年**
- 通货膨胀 = **你兜里的钱偷偷变薄**

## 在线体验

| 入口 | 地址 | 说明 |
|------|------|------|
| 🏠 投资词典（本项目） | https://dictionary.mangofolio.com | 472 个词条 · 22 个篇章 · 全文搜索 |
| 🧠 投资大脑 InvestBrain | https://brain.mangofolio.com | 投资决策与行为分析 |
| 🐻 投资伙伴 InvestBuddy | https://investbuddy.mangofolio.com | 投资人格测试与守护兽 |
| 📊 市场观察 MangoView | https://view.mangofolio.com | 市场行情可视化 |

> 本项目是 **Mangofolio 系列**的一员，专注"投资术语科普"。

## 特性

- 📚 **472 个词条**，覆盖货币、股票、基金、债券、保险、房产、宏观、AI 金融等 22 个篇章
- 🗣️ **说人话**：每个词条 = 一句话定义 + 真实场景 + 实操步骤 + 常见坑
- 🔍 **全文搜索**：输入关键词即时过滤，章节联动
- 🌐 **SEO 就绪**：每个词条独立页面，含 Schema.org `DefinedTerm` 结构化数据、OG/Twitter Card、canonical、面包屑、上下篇导航
- 🤖 **AI 友好**：robots.txt 放行 GPTBot / ClaudeBot，AI 与搜索引擎均可抓取
- 🧩 **可复用 Skill**：金融词条生成方法论已沉淀为 Agent Skill，欢迎贡献词条

## 快速开始

### 直接浏览

打开 https://dictionary.mangofolio.com 即可，无需安装。

### 本地运行

```bash
# 静态站点，任意静态服务器即可
cd web
python -m http.server 8080
# 打开 http://localhost:8080
```

### 使用词条生成 Skill（AI 用户）

本仓库附带 `skill/invest-dictionary-generator`，让 Claude / 各类 Agent 按同一方法论生成新词条：

```bash
# 复制到你的 Agent 技能目录（以 Claude Code 为例）
cp -r skill/invest-dictionary-generator ~/.claude/skills/
```

之后对 Agent 说："用投资词典的方法写一个词条：**可转债**"，即可得到符合本词典风格的词条 Markdown 与 HTML 页面。

### 场景使用说明（AI 用户）

投资词典二期沉淀了 8 个 Skill，覆盖普通人最常见的 8 个理财场景。把场景提示词直接发给 AI（已加载对应 Skill 的 Claude / Agent），即可触发对应 Skill：

| 场景 | 提示词示例（照着发） | 配套 Skill |
|------|------|------|
| **查词学词** | "用投资词典的方法写一个词条：**可转债**" | `invest-dictionary-generator`（单词条生成） |
| **看新闻** | "帮我翻译这段新闻：**央行降准0.5个百分点，释放长期资金约1万亿**，说人话" | `combo-narrative`（新闻翻译机） |
| **持仓亏了** | "**我买的理财亏了，要不要赶紧卖掉？**" | `symptom-lookup`（理财急诊 / 症状倒查） |
| **产品对比** | "手里有 10 万，**存定期还是买银行理财？**" | `duel-compare`（二选一擂台） |
| **重大决定** | "**我要不要提前还房贷？**" | `decision-mosaic`（决策拆解桌 / 决策拼图） |
| **防坑提问** | "**增额终身寿险**，我该问销售什么问题？" | `question-probe`（防坑提问器 / 该问什么） |
| **复杂事件** | "把这段做成网页：**央行降准后市场怎么看**，讲给客户听" | `invest-dictionary-concept-combinator`（概念串联） |
| **今日热词** | "**今日热词**，今天市场都在聊什么？" | `daily-hotword`（每日热词） |

> 💡 五个核心 Skill 的分工口诀：**看新闻找 combo-narrative，亏了找 symptom-lookup，纠结二选一找 duel-compare，纠结该不该找 decision-mosaic，面对产品找 question-probe**。
> 所有 Skill 输出均为"概念梳理与提问参考"，不构成投资建议。

## 目录结构

```
invest-dictionary/
├── web/                          # 字典网页版（Vercel 静态部署）
│   ├── index.html                # 首页：搜索 + 22 篇章词条卡片
│   ├── terms/                    # 472 个词条独立页面
│   ├── dictionary.json           # 词条数据源（id/slug/title/related）
│   ├── sitemap.xml / robots.txt  # SEO
│   └── vercel.json               # 部署配置
├── skill/
│   ├── invest-dictionary-generator/   # 金融词条生成 Skill
│   │   ├── SKILL.md              # 方法论 + 质量三原则 + 命名规范
│   │   ├── templates/            # 词条 Markdown / HTML 模板
│   │   └── examples/             # 示例词条
│   ├── invest-dictionary-concept-combinator/   # 概念串联（原有 Skill，保留原名）
│   │   ├── SKILL.md              # 6 屏叙事方法论（S1-S6 模板）
│   │   ├── templates/            # 叙事大纲 / 页面模板
│   │   └── examples/             # 示例叙事
│   ├── symptom-lookup/           # 理财急诊（症状倒查）
│   ├── combo-narrative/          # 新闻翻译机（概念串联轻量版）
│   ├── duel-compare/             # 二选一擂台（二选一对打）
│   ├── decision-mosaic/          # 决策拆解桌（决策拼图）
│   ├── question-probe/           # 防坑提问器（该问什么）
│   └── daily-hotword/            # 每日热词
└── docs/
    ├── PROJECT_GOALS.md          # 项目目标记录
    ├── PITFALLS.md               # 已知坑点（开发排雷手册）
    └── specs/
        └── 投资词典知识库使用指南.md  # 场景式使用指南（含 ima 链接）
```

## 贡献词条

欢迎所有人贡献词条！三种方式任选：

1. **Issue 提词条**：发 Issue 告诉我们你想加的词条，维护者会按方法论生成。
2. **PR 提交词条**：按 [CONTRIBUTING.md](CONTRIBUTING.md) 的规范提交 Markdown 词条 + dictionary.json 登记。
3. **Skill 推荐**：用本仓库 Skill 生成词条后，以 PR 形式回传。

词条标准只有 4 条：**说人话 · 有场景 · 讲坑点 · 能搜索**。

## 技术栈

- 纯静态 HTML/CSS/JS（零依赖，零构建）
- Vercel 部署（`cleanUrls` + 安全响应头）
- Schema.org 结构化数据（DefinedTerm / DefinedTermSet）
- Agent Skill 方法论沉淀（Markdown 驱动）

## 路线图

- [ ] 词条 i18n（英文版）
- [ ] 词条关联图谱可视化
- [ ] 社区贡献词条自动审核流程（CI）
- [ ] 移动端 App 封装

## License

[Apache-2.0](LICENSE)

---

**免责声明**：内容由 AI 生成，仅供学习参考，不构成投资建议。
*（内容由AI生成，仅供参考）*
