<div align="center">

# 投资词典 · Invest Dictionary

**213 个投资术语，说人话，不装逼。**

一个面向普通人的**中文投资术语词典**（Chinese investment dictionary / financial glossary）。
每一个词条都用"3 分钟能看懂"的方式解释：一句话定义 → 为什么重要 → 怎么用 → 常见坑。

[![在线词典](https://img.shields.io/badge/在线体验-dictionary.mangofolio.com-c43a31?style=for-the-badge)](https://dictionary.mangofolio.com)
[![GitHub Stars](https://img.shields.io/github/stars/lj22503/invest-dictionary?style=for-the-badge&color=gold)](https://github.com/lj22503/invest-dictionary/stargazers)
[![License](https://img.shields.io/badge/License-Apache--2.0-yellow?style=for-the-badge)](LICENSE)
[![Skill](https://img.shields.io/badge/Agent_Skill-可复用-8b5040?style=for-the-badge)](skill/invest-dictionary-generator)

**中文金融扫盲 · 说人话的投资科普 · 213 个理财必备术语 · 覆盖股票/基金/债券/保险/房产/宏观**

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
| 🏠 投资词典（本项目） | https://dictionary.mangofolio.com | 213 个词条 · 22 个篇章 · 全文搜索 |
| 🧠 投资大脑 InvestBrain | https://brain.mangofolio.com | 投资决策与行为分析 |
| 🐻 投资伙伴 InvestBuddy | https://investbuddy.mangofolio.com | 投资人格测试与守护兽 |
| 📊 市场观察 MangoView | https://view.mangofolio.com | 市场行情可视化 |

> 本项目是 **Mangofolio 系列**的一员，专注"投资术语科普"。

## 特性

- 📚 **213 个词条**，覆盖货币、股票、基金、债券、保险、房产、宏观、AI 金融等 22 个篇章
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

## 目录结构

```
invest-dictionary/
├── web/                          # 字典网页版（Vercel 静态部署）
│   ├── index.html                # 首页：搜索 + 22 篇章词条卡片
│   ├── terms/                    # 213 个词条独立页面
│   ├── dictionary.json           # 词条数据源（id/slug/title/related）
│   ├── sitemap.xml / robots.txt  # SEO
│   └── vercel.json               # 部署配置
├── skill/
│   └── invest-dictionary-generator/   # 金融词条生成 Skill
│       ├── SKILL.md              # 方法论 + 质量三原则 + 命名规范
│       ├── templates/            # 词条 Markdown / HTML 模板
│       └── examples/             # 示例词条
└── docs/
    ├── PROJECT_GOALS.md          # 项目目标记录
    └── PITFALLS.md               # 已知坑点（开发排雷手册）
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
