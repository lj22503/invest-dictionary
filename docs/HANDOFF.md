# invest-dictionary 接手说明（2026-09-18 新窗口用）

> 这份说明是给**新开窗口接手 invest-dictionary 的 agent** 看的。读完这份文件 + PROGRESS.md + AGENTS.md 即可开始工作。

---

## 1. 项目一句话

`D:\claudework\invest-dictionary` — **投资词典**（Invest Dictionary）

- 213+ 中文投资术语，"说人话不装逼"
- 线上站：https://dictionary.mangofolio.com
- mangofolio 生态第 3 块（术语平权，听得懂）
- 静态站，零依赖零构建，Vercel 托管

## 2. 关键文件 / 目录

| 路径 | 作用 |
|---|---|
| `web/` | 线上站点（index.html、terms/ 词条页、dictionary.json） |
| `web/dictionary.json` | 词条唯一数据源（id/slug/chapter/description/related） |
| `web/index.html` | 首页（hero + 热词轮播 + 订阅 + footer） |
| `web/terms/` | 213 个词条静态页 |
| `web/js/tracker.js` | 零依赖埋点 SDK（2026-09-10 引入，对齐 invest-tools 形态） |
| `web/api/events.js` | 埋点 Edge function 走 `@vercel/kv`（key 前缀 `evt:dictionary:`） |
| `skill/invest-dictionary-generator/` | 金融词条生成 Skill |
| `docs/PROJECT_GOALS.md` | 目标清单 |
| `docs/PITFALLS.md` | 坑点 |
| `AGENTS.md` | 接手规则 + 对话收尾流程 |
| `PROGRESS.md` | 进度记录 |

## 3. 怎么跑起来

```bash
cd web && python -m http.server 8080
# 打开 http://localhost:8080
```

或者 `npx serve web -p 8080`（如果本地有 Node）。

## 4. 上游品牌规范（mangofolio v1.0）

**项目视觉设计必须对齐**：`D:\claudework\OPC OS\10-about-me\brand-standards\`

- `Mangofolio-设计规范-v1.0.md`（权威规范，v1.0 = 2026-09-18 修订）
- `mangofolio-tokens-v09.css`（523 变量，light/dark 双模式）
- `collectui-mangofolio-mapping.html`（落地参考）

**v1.0 关键决策**（容易踩坑）：
- **页面底色 = 纯白 `#FFFFFF`**（v0.6/0.8 曾用 `#F7F5F2` 宣纸，v1.0 纠正）
- **主橙 `#F97316`**（电压色，仅 CTA/链接/图标/焦点/Logo，占页面 ≤5%）
- **H1 走 Noto Serif SC 衬线**（body 仍 Inter）
- **en-title 装饰行**（Fraunces italic 橙，H1 下方）：dictionary 站落地，其他站按需
- **完整暗色模式**（`[data-color-mode="dark"]` 双值覆盖）

**iAsk 2026-09-18 已落地对齐**（5 项必修 + 决策记录）：见 `D:\claudework\invest-iAskbetter\docs\DESIGN.md`（**reference 文档**，对 dictionary 同样适用，可直接套用）。iAsk 的差异（en-title 不做 / eyebrow 不做）**只针对工具型 hero**，dictionary 是品牌站，**应该保留 eyebrow + en-title**。

## 5. 当前状态（2026-09-18 接手时）

PROGRESS.md 记录到 2026-09-19，最后状态：
- 词条数 ~428（HTML 文件数，dictionary.json 解析失败待修）
- 埋点 SDK 已引入
- 一鱼多吃（T2-T7）部分落地
- **知识卡片 v3 已闭环（2026-09-19）**：从朱砂红国风 → 芒果橙杂志头条，5 个 commit

**知识卡片 v3 改动**（2026-09-19）：
- 文件：`web/js/knowledge-card.js`（整个 `buildCard()` 重写）
- 主色 `#C43A31` → `#F97316`（v1.0 严禁色移除）
- 字体链 "KaiTi/STKaiti" → Noto Serif SC 主导
- 底部距底 40px + URL 右对齐
- 备份：`web/js/knowledge-card.js.bak-20260919`
- spec: `docs/specs/2026-09-19-knowledge-card-v3-design.md`
- plan: `docs/superpowers/plans/2026-09-19-knowledge-card-v3.md`
- 全 438 个 terms 页共用同一份 JS，自动生效

**未做（PROGRESS.md 待办区）**：
- **首页 v1.0 品牌对齐**（2026-09-19 用户提出，下一窗口首要任务）—— index.html 是国风老体系（朱砂红/宣纸/楷体），需要重做
- dictionary.json 解析失败待修（line 29 `\"` 未转义）
- E8 邮箱订阅 5 条待办（见 `00-Inbox/投资词典-邮箱订阅后端落地经验-20260809.md`）
- 词条内容挖掘 → 账号矩阵素材（小红书/知乎）
- 词条 × 工具两站互导持续

**用户最新意图**（2026-09-19 晚上）："我们要开新对话继续搞首页" —— **接手第一件事：index.html v1.0 品牌对齐改造**。

## 6. 项目线规范（必读）

来自 `AGENTS.md`：

### 提交前自查 4 问
1. 我改的是哪个项目？（commit message 写明项目名 `dictionary`）
2. 这个功能是不是已经存在？（查一遍再写）
3. 我有没有绕过统一入口？
4. 我改的是不是这个项目该改的？

### 对话收尾流程（每次工作完必走）
1. 更新 `PROGRESS.md`（今日进度：做了什么/下一步/卡点）+ `docs/PITFALLS.md`（今日坑点）
2. neat-freak 六面审计（代码/运行态/文档/规则/记忆/工作区一致性）
3. commit（conventional commits）+ push
4. 更新 Obsidian 02-Projects

### slug 归一化
- 词条名 `/`、`*`、`>` 一律替换为 `_`
- 所有链接（相关词条、首页卡片）必须用归一化文件名

### 域名
- 正式 `dictionary.mangofolio.com`
- 禁止 `investbuddy.com` 残留（canonical/og/sitemap/robots）

## 7. 跟其它站的关系（生态视角）

mangofolio 生态下各站项目：
- `invest-iAskbetter/` — 提问私教（iAsk，M2 阶段）
- `invest-dictionary/` — **本项目**，投资词典
- 投资大脑（Brain）
- 财务工具箱（FinTools）
- 投资 Buddy
- `mangoview` 分析引擎
- `mangofolio forge` — 投资平权终端（MangoForge，10 模块）

规范都在 `D:\claudework\OPC OS\10-about-me\brand-standards\`。改 dictionary 视觉前先核对上游版本（v1.0 = 当前最新）。

## 8. 用户操作习惯（CLAUDE.md 全局行为规范）

- 中文回复，简洁（每次 ≤ 300 字），列表展示
- 不报时间估算、不 narrate tool 选择
- 给路径用相对/可读形式
- Bash 操作（git/npm/python）直接执行
- PowerShell 执行 git（Bash PATH 找不到 Git）
- GitHub 推送 SSH 443（22 端口被 LJG 网络挡，配置在 `~/.ssh/config`）

## 9. 接手 checklist（新窗口第一件事）

1. 读 `AGENTS.md`（项目规则）
2. 读 `PROGRESS.md`（当前进度）
3. 读 `docs/PROJECT_GOALS.md`（目标）
4. 读 `docs/PITFALLS.md`（历史坑点）
5. 跑 `cd web && python -m http.server 8080` 看站能不能起来
6. **问用户**这次要做什么（"相关整理"具体是什么）

---

*这份说明写于 2026-09-18，从 iAsk 品牌对齐工作收尾后切换。*
*参考文档：`D:\claudework\invest-iAskbetter\docs\DESIGN.md`（iAsk 品牌规范实施层，可套用 framework）*
