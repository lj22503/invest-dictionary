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

## 待办（下一步）

- [x] **Wave 1 push gate**（2026-09-22 放行，随本 commit 入库）
- [x] docs/terms-md cron housekeeping commit（2026-09-22 单独 commit）
- [x] Wave 2 推进（字体 + 圆角 + footer）
- [x] **数据一致性修正**（2026-09-22）：manifest / llms 461 → 472；sitemap 补齐 33 页；断链 6 处；ALL_ENTRIES 同步 473；篇章笔误统一
- [ ] **待拍板**：`dictionary.json` 去重「信用卡」+ 修正 id 352/353 撞号（473 → 472）
- [ ] 清理候选（待批）：tracked `.bak` 5 个 / `docs/prod_*.md.md` 3 个 / `task6-*.ps1` 6 个 / 磁盘 `.bak*` 492 个
- [ ] Wave 3 推进（暗色 + 语义色）
- [x] neat-freak 6 面审计 + 终验（2026-09-22）