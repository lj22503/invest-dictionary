---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 1c835e55ba3b06878e6538b2edadf703_3fdeb632b66a11f190f9525400638852
    ReservedCode1: bpRGsANTxD1bp3zXmn7RN558xOsfH9cbpjo3lIpvyR488ltBwuyoNWsqcg/UPhl4Lqlx0bVS67XibBb6AwvtQnQu0y/nrIElmKwm8wEF14dMCjYVm01wzDGb1JwNZVtP0jzAHZqYJB51avOhkaiVSFmdCKAFT9k6E3XzQoYpulFV6QEYlt403+KItEc=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 1c835e55ba3b06878e6538b2edadf703_3fdeb632b66a11f190f9525400638852
    ReservedCode2: bpRGsANTxD1bp3zXmn7RN558xOsfH9cbpjo3lIpvyR488ltBwuyoNWsqcg/UPhl4Lqlx0bVS67XibBb6AwvtQnQu0y/nrIElmKwm8wEF14dMCjYVm01wzDGb1JwNZVtP0jzAHZqYJB51avOhkaiVSFmdCKAFT9k6E3XzQoYpulFV6QEYlt403+KItEc=
---

# PROGRESS — invest-dictionary（投资词典）

> mangofolio 生态第 3 块 · 术语平权（听得懂）。472 个中文投资术语，"说人话不装逼"。
> 进度记录：每次对话收尾更新（项目线规范②）。

## 2026-09-22 · neat-freak 审计 + 一致性收尾（品牌 v1.0 push 后）

### 修复（本轮）
| # | 问题 | 修复 |
|---|---|---|
| 1 | 214 个词条页的微博分享链接仍指向旧域名 `investbuddy.com` | 全量替换为 `dictionary.mangofolio.com` + 写盘回读校验（残留 0） |
| 2 | `manifest.json` / `llms.txt` 计数 `461` ≠ 实际 472 页 | 统一为 **472** |
| 3 | `sitemap.xml` 仅 439 个词条 URL，缺 33 页 | `scripts/generate-sitemap.py` 同源重建 → 472 + 首页，双向差集 0 |
| 4 | 页内断链 6 处（链接用了斜杠版文件名） | 改为下划线归一化文件名；复验断链 = 0 |
| 5 | 首页内嵌 `ALL_ENTRIES` 461 ≠ dictionary 473（11 条搜不到） | `scripts/sync_all_entries.py` 同步 → 473，缺/多 = 0 |
| 6 | 篇章名「第九篇…市场情绪与风险」与「…风险篇」并存（篇章数 23 ≠ 首页声称 22） | `dictionary.json` 统一为「…风险篇」→ 22 篇 |
| 7 | 文档数字漂移（AGENTS / README / PROJECT_GOALS / HANDOFF / PROGRESS 写 213 · 461 · 旧 commit） | 统一为 472；HANDOFF 现役化、旧结论标注作废 |

### 新增
- `scripts/check-consistency.py` — 提交前门禁：计数一致性 / id·slug·filename 唯一性 / 页内断链 / sitemap 覆盖 / 旧域名残留 / ALL_ENTRIES 同步
- `scripts/generate-sitemap.py` — sitemap 由 `dictionary.json` 同源生成（禁止手改）
- `docs/PITFALLS.md` 新增 #20-#25（分享链接旧域名、批量空转、计数漂移、sitemap 脱节、ALL_ENTRIES 不同步、`.bak` 被跟踪）

### 未修（待拍板）
- `dictionary.json` 去重「信用卡」+ id 352/353 撞号（473 → 472）
- 清理候选：tracked `.bak` 5 个、`docs/prod_*.md.md` 3 个、根目录 `task6-*.ps1` 6 个、磁盘 `.bak*` 492 个

---

## 2026-09-21 → 2026-09-22 · 品牌视觉 v1.0 全量落地（Wave 2 + 存量页 + 数据层 + 令牌集中化）

### 背景
Wave 1 只覆盖首页与模板；本阶段把 v1.0 推到入口层（Skill）、模板层、存量词条页、数据层，并补一份令牌速查文档收口"令牌散落多处、无唯一速查"的问题。

### 各层落地
| 层 | 改动 | 文件 |
|---|---|---|
| 入口层 | SKILL.md 写入品牌视觉硬约束 + 产出前自检清单；HANDOFF 修正会误导后续 agent 的旧结论 | `skill/invest-dictionary-generator/SKILL.md`、`docs/HANDOFF.md` |
| 模板层 | 两个词条模板切 Token 体系：字体链补 emoji 段、圆角走 `--mf-radii-*`、页脚单次注入、内联硬编码色改 `:root` 变量 | `skill/.../templates/term-page.html`、`term-page-regular.html` |
| 存量页 | `web/terms` 459 个词条页品牌 sweep（朱砂红 / 米色 rgba / 老国风橙 / 楷体字面清零）；删除 1 个重复页 `资产 _  负债.html` | `web/terms/*.html` |
| 数据层 | 词条同步脚本修正；manifest 的 theme_color / background_color 切 v1.0 值 | `scripts/sync_all_entries.py`、`web/manifest.json`、`web/llms.txt` |
| 首页 | 补 `:root --accent`，修复 hero 主按钮隐形 | `web/index.html` |
| 令牌文档 | 新增集中速查 `docs/design-tokens.md` | `docs/design-tokens.md` |
| 图文线 | 08-每日热词图文曾改品牌暖白底，**2026-09-22 按偏好回滚**为原暖灰宣纸底（`#F7F5F2→#EFEAE2`） | 仓库外 `D:\ANT\...\08-每日热词图文\main.py` |

### 令牌文档（新增）
`docs/design-tokens.md` 汇总：品牌基调 5 条、色彩（背景 / 文字 / 描边 / 图表 / 橙阶）、排版（字体栈 / 字号 / 字重）、间距尺寸圆角阴影、组件令牌、hero 令牌、暗色模式、落地对象与例外、落地自检清单。权威源仍为 `web/css/mangofolio-tokens-v09.css`。

### 数据一致性（2026-09-22 neat-freak 收尾后）
- ✅ 计数：`manifest.json`（1 处）、`llms.txt`（2 处）461 → **472**；首页内嵌 `ALL_ENTRIES` 461 → **473**（`scripts/sync_all_entries.py`）
- ✅ `sitemap.xml` 重建：439 → **472** 词条 URL + 首页（补齐 33 页缺口）
- ✅ 页内断链 6 处修复（斜杠版 → 下划线版）
- ✅ 篇章笔误统一：「第九篇：读懂指标 · 市场情绪与风险」→「…风险篇」，篇章数 23 → **22**（与首页一致）
- ⏳ **待批**：`dictionary.json` **473 条**含重复「信用卡」（同 slug 同 filename）+ **id 352/353 撞号**；去重后应为 **472** 条（删哪条需你拍板）

---

## 2026-09-19 → 2026-09-20 · 首页品牌对齐 v1.0 · **Wave 1 ✅ 完成（9/9 tasks）**

### 背景
dictionary 是 mangofolio 生态里**唯一未对齐** v1.0 的站——iAsk / fintools / brain 都已 v1.0，dictionary 还停留在朱砂红 + 宣纸 + 楷体国风老体系。BRAND_AUDIT 完成（35 分符合度）。开始三波对齐改造。

### 文档
- spec: `docs/superpowers/specs/2026-09-19-homepage-v1-design.md`
- plan: `docs/superpowers/plans/2026-09-19-homepage-v1.md`
- cron 验证: `docs/superpowers/specs/2026-09-20-wave1-cron-verify.md`
- BRAND_AUDIT: `docs/BRAND_AUDIT_2026-09-19.md`
- HANDOFF: `docs/HANDOFF.md`

### 已完成（9/9 · Wave 1 闭环）
| Task | 改动 | Commits |
|---|---|---|
| 1. 引入 v09.css | web/css/mangofolio-tokens-v09.css（从 OPC OS 拷贝） | fd42597 |
| 3. index.html :root 改 v1.0 | `--paper` / `--cinnabar` / `--ink` 等 6 个变量映射到 var(--mf-colors-*)；line 478 inline hover 也修复 | cf00075 + 0b22932 |
| 4. term-page-regular.html v1.0 | 7 :root vars + 11 font-family + 10 borders + 6 cinnabar + 4 card-bg + 30+ legacy hex 全清；grep = 0 | e307f1c + c2659c3 |
| 5. term-page.html v1.0（**真 cron 模板**）| 同 Task 5 sweep | 243a667 |
| 6. **redo** sed 446 terms（扩范围）| plan 14 模式太窄；扩到 ~40 模式覆盖米色 rgba（5 类）/ 老国风橙（#e8784a #d4745c）/ 楷体字面（含 unicode codepoint + HTML-encoded inline style 残段）/ 朱砂红 rgba（#C43A31 rgba）/ 米色卡面 (#fdfaf4) / 米色文字 (#4a4035 等)；脚本 scripts/brand-sweep.pl 沉淀 | d87a66e |
| 7. **redo** manifest + index.html sweep（同扩范围）| manifest.json `theme_color`→#F97316、`background_color`→#FFFFFF；index.html 全文件 + 446 terms 一次性扩 sweep；grep 全 4 类残留 = 0；amend 后 `0122524` | 0122524（amend from 07bcd62）|
| 8. cron 模板验证 | one-shot 渲染 `term-page-regular.html` × 2 个 placeholder，验证产物 grep = 0 残留；模板 v1.0 化干净，下次 cron 自动合规 | 5ba03ed |
| 9. Wave 1 收尾 | 本表 + HANDOFF + PITFALLS 同步；commit 待 push | (本 commit) |

### Wave 1 终验（grep = 0）
- 朱砂红 hex + rgba（#C43A31 / rgba(196,58,49,*) / rgba(184,34,30,*)）：0
- 米色 rgba（rgba(180,160,130,*) / rgba(180,155,120,*) / rgba(230,215,190,*) / rgba(220,205,175,*) / rgba(160,140,110,*)）：0
- 老国风橙（#e8784a / #d4745c / rgba(232,120,74,*)）：0
- 楷体 / 仿宋 / KaiTi / FangSong / STFangsong / STKaiti（含 HTML-encoded inline 残段）：0
- theme-color：全站 ~451 处均为 `#F97316`

### 关键 cron 路径修正
之前以为 `batch_fill_1000.py` 是 cron，实际 cron 是 **Marvis 11_1_0.yaml**，直接读 `templates/term-page.html`（hot-word 模板）。Task 5 已改 v1.0，下次 cron 产出就是新体系（Task 8 验证确认）。

### 沉淀工具
- `scripts/brand-sweep.pl`（永久）— v1.0 brand sweep，支持单目录 / 递归（`web` 或 `web/terms`），覆盖米色/楷体/老国风/朱砂红 rgba/HTML-encoded inline 残段，加 emoji 字体。
- `scripts/task6-extended-sweep.pl`（已删除，被 brand-sweep.pl 取代）

### 工作区状态
- 本地 ahead origin/main by 5 commits（Task 6 redo + Task 7 redo + Task 8 + 之前 3）
- 待 push（Wave 1 push 是 gate R3，等用户批）
- docs/terms-md/ 10 文件 pending（cron AIGC 元数据 housekeeping，**不在 wave 1 scope**，下次单独 commit）
- *.bak-* 备份按 plan Task 6 Step 6 建议保留 7 天后清理
- index.html line 163 `.entry-grid` 折叠动画（max-height + padding）：impeccable layout-transition hook 报 layout thrash；**false positive**（accordion 折叠合理需要 max-height），defer 到 Wave 2 Task 12 按 grid-template-rows 0fr/1fr 重构

### 下一步（Wave 2/3）
- Wave 2（Tasks 10-14）：Google Fonts + emoji 字体链 + 卡面圆角 + footer 重做
- Wave 3（Tasks 15-17）：暗色模式 + 涨红跌绿 + 终验

---

## 2026-09-19 · 知识卡片 v3

### 改动
- `web/js/knowledge-card.js` — 整个 `buildCard()` 重写为 v3
  - 主色朱砂红 `#C43A31` → 芒果橙 `#F97316`（v1.0 严禁色移除）
  - 底色羊皮纸 `#f5efe0` → 纯白 `#FFFFFF`
  - 字体链 `"PingFang SC","Microsoft YaHei"` → Noto Serif SC 主导（中文衬线）
  - 字号 1242px 宽（朋友圈封面标准），高度自适应（最小 1500）
  - 加 Eyebrow 眉题 + En-title Fraunces italic + 80% 宽 2px 橙条
  - 章节序号移除；章节间分隔：橙色 4px 短条 → 暖墨 12% 50% 虚线 dashed 6px
  - 字体链补 emoji 3 段
  - 底部距底 40px 留白 + URL 右对齐

### 验证
- 4 个抽样词条页强刷 + 生成 PNG + 视觉清单逐项核对
- 全 438 个 terms 页共用同一份 JS

## 2026-09-10 · 埋点 SDK 引入

按 OPC OS 事实标准核对，invest-dictionary **此前 0 埋点**。

### 改动
- `web/js/tracker.js`（新增）— 与 invest-tools 同源的零依赖 SDK
- `web/index.html`：引入 `/js/tracker.js`

## 2026-08-12
每日热词持续产出；一鱼多吃（T2-T7）落地；222 词条完成；邮箱订阅 E8。

## 2026-10-19 · 二期：概念串联 Skill 上线（投顾工作台）

### 背景

一期解决了"有 472 个词条，能逐个查"。但用户拿到一段复杂内容（央行数据、政策、事件、异动、财报、个人决策）时，仍然不知道怎么把多个词条**串成一条线**给客户 / 朋友讲清楚。

二期把这个"组合应用"沉淀为可复用方法论——`invest-dictionary-concept-combinator` skill，让 AI 把一段复杂内容自动拆成 3-5 个核心词条，沿着因果链串成 6 屏叙事，输出客户能看懂的网页。

### 定位

不是 generator 的"另一个 skill"，而是 generator 的**姐妹 skill**：

| Skill | 输入 | 输出 |
|---|---|---|
| `invest-dictionary-generator`（一期）| 一个词条名（"M1""剪刀差"）| 单个词条 markdown + HTML |
| `invest-dictionary-concept-combinator`（二期）| 一段复杂内容（数据/事件/政策/异动/财报/决策）| 3-5 个词条串成的 6 屏叙事网页 |

### 交付（这次）

| 项 | 路径 |
|---|---|
| SKILL 方法论 | `skill/invest-dictionary-concept-combinator/SKILL.md` |
| HTML 模板 | `skill/invest-dictionary-concept-combinator/templates/narrative-page.html` |
| Markdown 草稿骨架 | `skill/invest-dictionary-concept-combinator/templates/narrative-outline.md` |
| Q3 worked example | `skill/invest-dictionary-concept-combinator/examples/q3-2026.html` |
| Q3 方法论回放 | `skill/invest-dictionary-concept-combinator/examples/q3-2026.md` |

### 6 模板系统（S1-S6）

| 模板 | 起点 | 核心动作 | 状态 |
|---|---|---|---|
| S1 宏观数据 | 数字 | 概念提取 3-5 | **完整 + Q3 worked example** |
| S2 事件解读 | 反直觉事实 | 传导链 ≤4 步 | 骨架 |
| S3 政策解读 | 政策与钱包连接点 | 逐条翻译 | 骨架 |
| S4 市场异动 | 情绪降温 | 短因/长逻 + 历史对照 | 骨架 |
| S5 公司财报 | 数字 vs 股价反差 | 预期差 + 利润质量 | 骨架 |
| S6 个人决策 | 你妈说…你朋友说… | 变量拆解 3-4 个 | 骨架 |

骨架内容已写齐（角色 / 输入 / 处理流程 / 六屏结构 / 质量标准 / 输出格式），worked example 待续。后续按用户需求逐模板补 worked example。

### Spec 来源

- 第一版（方法论雏形）：`docs/specs/概念组合应用.txt`（5000+ 行 LLM 对话残留里提炼）
- 第二版（投顾定位）：`docs/specs/投顾写文工作台.txt`（3400+ 行 6 模板骨架）

### 品牌视觉一致性

Q3 HTML 示例 已 grep 验证（本地）：
- 0 处 #C43A31 老朱砂红
- 0 处老米色 rgba
- 0 处老国风橙 #e8784a/#d4745c
- 0 处楷体/仿宋/KaiTi/FangSong
- 4 处 emoji 字体段（CSS variables 中）
- border-radius 全用 var(--mf-radius-*) 引用，0 处硬编码
- footer.mangofolio-nav 仅 1 处 <footer> 注入
- UTF-8 round-trip clean

### 下一步

- 公众号续篇（基于 Q3 example 改写）—— 任务列表另列
- 投顾工作台 HTML 工具（2000+ 行 form+iframe 生成器）—— 当前**不在范围**，按用户决定未来是否集成到 skill
- S2-S6 各补 worked example —— 按用户决定逐个补
- Wave 3（暗色 + 语义色）/ dictionary.json 去重 —— 一期遗留，与本期独立

### 待批

- 二期内容是否推 origin/master？push 会触发 Vercel 重新部署（注意：本次仅 skill/ 改动不部署 web/，但仍要确认是否推送）
- Q3 worked example 是否直接 publish 到 `dictionary.mangofolio.com/narratives/q3-2026.html`？（需另开一个 web/ 提交流程，先不入库）

---

## 待办（一期遗留 + 二期新增）

### 一期遗留（仍 pending）

- [x] **Wave 1 push gate**（2026-09-22 放行，随本 commit 入库）
- [x] docs/terms-md cron housekeeping commit（2026-09-22 单独 commit）
- [x] Wave 2 推进（字体 + 圆角 + footer）
- [x] **数据一致性修正**（2026-09-22）：manifest / llms 461 → 472；sitemap 补齐 33 页；断链 6 处；ALL_ENTRIES 同步 473；篇章笔误统一
- [ ] **待拍板**：`dictionary.json` 去重「信用卡」+ 修正 id 352/353 撞号（473 → 472）
- [ ] 清理候选（待批）：tracked `.bak` 5 个 / `docs/prod_*.md.md` 3 个 / `task6-*.ps1` 6 个 / 磁盘 `.bak*` 492 个
- [ ] Wave 3 推进（暗色 + 语义色）
- [x] neat-freak 6 面审计 + 终验（2026-09-22）

### 二期新增（Concept Combinator 上线）

- [x] SKILL.md 初稿（11 节，~860 行，6 模板架构）
- [x] templates/narrative-page.html（v1.0 brand-token 兼容）
- [x] templates/narrative-outline.md（Markdown 草稿骨架）
- [x] examples/q3-2026.html（5 概念 + 6 屏 + ASCII 流程图 + 行动清单）
- [x] examples/q3-2026.md（方法论三阶段回放）
- [x] 本地验证（HTML 标签平衡 / UTF-8 round-trip / 品牌色 grep 全 OK）
- [x] PROGRESS.md + HANDOFF.md 同步
- [ ] git commit + push（等用户批）
- [ ] 公众号续篇（基于 Q3 example）

*（内容由AI生成，仅供参考）*
