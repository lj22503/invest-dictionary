# Invest Dictionary · 项目目标记录

> 本文档用于防止长任务执行过程中遗漏目标，是本次发布任务的唯一权威目标清单。
> 创建日期：2026-08-01

## 项目定位

投资词典（Invest Dictionary）作为**独立项目**发布，**不并入 InvestBuddy**。
GitHub 仓库：https://github.com/lj22503/invest-dictionary

## 四大交付物

### 1. 字典网页版本（Vercel 部署）
- 部署域名：**dictionary.mangofolio.com**（Vercel）
- 内容：首页 index.html + 213 个词条详情页 + sitemap.xml + robots.txt + dictionary.json
- 要求：可链接到 Mangofolio 系列其他网站：
  - InvestBrain
  - InvestBuddy
  - MangoView
- 注意：所有 canonical / sitemap / robots 中的旧域名（investbuddy.com）必须替换为 dictionary.mangofolio.com

### 2. 金融词条生成 Skill
- 目标：将 213 个词条的生成方法论沉淀为可复用的 Agent Skill
- 定位：开放给其他人使用、贡献词条（开源协作）
- 内容：SKILL.md + 词条模板 + 示例

### 3. README 与 GitHub SEO 曝光优化
- 参考调研：`D:\ObsidianVault\03-Resources\IMA\research\`
  - `prod_19f9d95e5ff_2a054f0890fc_github-growth-hands-on.md.md`（GitHub 增长实操：搜索排名机制、README 前 200 字、Topics 打满 20 个、About 描述等）
  - `D-claudework爆款Skill选型与分发策略.md`（Skill 分发策略）
  - `Red Skill与SkillHub反向调研.md`（Skill 平台分发）
- 必须项：About 描述（150 字内，前 50 字含核心关键词）、Topics 标签打满、README 首屏 3 秒看懂、Demo 截图、结构化 README

### 4. 收尾整理（neat-freak skill）
- 使用卡兹克的 neat-freak skill 做知识收尾与文档一致性整理
- 坑点记录到项目（docs/PITFALLS.md）
- 同步到 Obsidian：`D:\ObsidianVault\02-Projects`

## 执行阶段

| 阶段 | 内容 | 状态 |
|------|------|------|
| A | 本地项目骨架 + 目标记录 | ✅ 本文档 |
| B | 网页版整理（域名替换、Mangofolio 导航、vercel.json、index SEO） | ✅ |
| C | 金融词条生成 Skill（SKILL.md + 模板 + 示例） | ✅ |
| D | README + CONTRIBUTING + 仓库 SEO（About/Topics 20 个/描述） | ✅ |
| E | git push 到 GitHub（commit a6d6f05，main 分支） | ✅ |
| F | Vercel 部署 + 域名绑定 dictionary.mangofolio.com | 🟡 部署成功（invest-dictionary.vercel.app，live verified）；域名待 Cloudflare DNS 配置 CNAME dictionary → 8f73e94d8020e067.vercel-dns-017.com |
| G | neat-freak 收尾 + 坑点记录 + Obsidian 同步 | ⏳ 进行中 |

## 已知坑点（登记处，详见 docs/PITFALLS.md）

已登记 10 条完整坑点（slug 特殊字符、%2F 断链、旧域名残留、条目数不一致、flex 布局塌陷、假二维码、git 分支名、staged 未提交、Vercel 未登录、market skill 未注册）。
