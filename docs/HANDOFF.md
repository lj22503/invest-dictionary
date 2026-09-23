---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 1c835e55ba3b06878e6538b2edadf703_3f037635b66a11f190f9525400638852
    ReservedCode1: XEx1/wvJAHED06BY0Yrua5ROVa4jLnzM4FvjIUogqLKt3UolCENmdQVIXjTBjgiM75eJhafAVxmuYMwurhaHc9Zqqqxs7vJbVxfOz2k/4UwPZkzwzPYs2Ga2jFJS+LwWYb3JD9f+8hZJVKsJh0omE026z3Y8Q50ekk1dRVmIhMmGTaEwrysX1r0DbHc=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 1c835e55ba3b06878e6538b2edadf703_3f037635b66a11f190f9525400638852
    ReservedCode2: XEx1/wvJAHED06BY0Yrua5ROVa4jLnzM4FvjIUogqLKt3UolCENmdQVIXjTBjgiM75eJhafAVxmuYMwurhaHc9Zqqqxs7vJbVxfOz2k/4UwPZkzwzPYs2Ga2jFJS+LwWYb3JD9f+8hZJVKsJh0omE026z3Y8Q50ekk1dRVmIhMmGTaEwrysX1r0DbHc=
---

# invest-dictionary 接手说明（**2026-09-22 更新 · 品牌视觉 v1.0 全量落地后**）

> 这份说明是给**新开窗口接手 invest-dictionary 的 agent** 看的。读完这份文件 + PROGRESS.md + AGENTS.md 即可开始工作。

---

## 0. 现役状态（2026-09-22，先读这段）

- **品牌视觉 v1.0**：全量落地并已 push（入口层 / 模板层 / 存量 472 页 / 数据层 / 首页）。
- **线上**：https://dictionary.mangofolio.com 已上线（Vercel，web/ 为根目录）。
- **数据面**：`web/terms` 472 页；`dictionary.json` 唯一数据源；`sitemap.xml` 由 `scripts/generate-sitemap.py` 同源生成；首页 `ALL_ENTRIES` 由 `scripts/sync_all_entries.py` 同步。
- **提交前必跑**：`python scripts/check-consistency.py`（见 AGENTS.md）。
- **待你拍板**：① `dictionary.json` 去重「信用卡」+ id 352/353 撞号（473 → 472）；② 清理候选：tracked `.bak` 5 个、`docs/prod_*.md.md` 3 个、根目录 `task6-*.ps1` 6 个、磁盘 `.bak*` 492 个。
- **下一步**：Wave 3（暗色模式 + 语义色）。

---

## 1. 项目一句话

`D:\claudework\invest-dictionary` — **投资词典**（Invest Dictionary）

- 213+ 中文投资术语，"说人话不装逼"
- 线上站：https://dictionary.mangofolio.com
- mangofolio 生态第 3 块（术语平权，听得懂）
- 静态站，零依赖零构建，Vercel 托管

---

## 2. 历史任务（✅ 已完成）：首页对齐 mangofolio v1.0

> **2026-09-22 结论**：本任务已全部完成并 push（Wave 1 `d87a66e` / `0122524` / `5ba03ed`，品牌全量 `2d75288`，docs `af28980`）。
> 本节以下内容为**历史过程记录**，其中「in progress / Task 6 partial / 未 commit」等表述**均已作废，不可再引用**。

**2026-09-19 开新窗口**：投资词典是 mangofolio 生态里**唯一未对齐 v1.0** 的站——iAsk / fintools / brain 都已 v1.0，dictionary 还停留在朱砂红 + 宣纸 + 楷体国风老体系。BRAND_AUDIT 完成，符合度约 35 分。

**已写完**：
- Spec: `docs/superpowers/specs/2026-09-19-homepage-v1-design.md`（commit `3cb827b`）
- Plan: `docs/superpowers/plans/2026-09-19-homepage-v1.md`（commit `91a589f`，17 tasks / 3 waves）
- Wip housekeeping: `b226be1`（cron in-progress 改动）

**已完成 tasks（5/17）**：
| Task | 状态 | Commits |
|---|---|---|
| 1. 引入 v09.css | ✅ complete | fd42597 |
| 2. index.html head 加 link | ✅ complete | （合并到 Task 3） |
| 3. index.html :root 改 v1.0 | ✅ complete | cf00075 + 0b22932 (fix hover) |
| 4. term-page-regular.html v1.0 | ✅ complete | e307f1c + c2659c3 (fix hardcoded 27 处) |
| 5. term-page.html v1.0（**真 cron 模板**） | ✅ complete | 243a667 |

**Partially done**：
| Task | 状态 | 说明 |
|---|---|---|
| 6. sed 446 terms | ⚠️ PARTIAL | sed 已应用，grep 验证 = 0；**未 commit**。R8 |

**未完成**：
- Task 7: manifest.json + meta theme-color 全站
- Task 8: cron 验证（用 file mode 跑 2 条新词条）
- Task 9: PROGRESS + HANDOFF 同步 + Wave 1 push gate
- Wave 2（Tasks 10-14）：Google Fonts + emoji 字体链 + 卡面圆角 + footer 重做
- Wave 3（Tasks 15-17）：暗色模式 + 涨红跌绿工具类 + 终验

---

## 3. 新窗口接手 checklist（历史阶段存档；现役接手请先读顶部第 0 节 + PROGRESS.md 最新段）

1. 读 `AGENTS.md`（项目规则）
2. 读 `PROGRESS.md`（看 2026-09-19 段）
3. 读 `docs/superpowers/specs/2026-09-19-homepage-v1-design.md`（spec）
4. 读 `docs/superpowers/plans/2026-09-19-homepage-v1.md`（plan）
5. 读 `.superpowers/sdd/2026-09-19-homepage-v1/progress.md`（SDD ledger + Rulings）
6. 跑 `git status` 确认 Task 6 partial 状态
7. **继续 Task 6 commit** → Task 7 → ... → Wave 1 push gate

---

## 4. 关键 cron 路径修正（**重要**）

之前认为 `batch_fill_1000.py` 是 cron，但实际 cron 是 **Marvis `C:\Users\lj225\.marvis\schedules\11_1_0.yaml`**，直接按 `skill/invest-dictionary-generator/templates/term-page.html`（hot-word 模板）生成新词条。

**模板现状（2026-09-22）**：两个模板均已完成 Wave 2（字体链 + emoji 段、圆角走 `--mf-radii-*`、footer 单次注入、内联硬编码色改 `:root` 变量）；**暗色模式（Wave 3）未做**。

> **2026-09-20 更新（入口层修复后）**：两个 cron（`11_1_0.yaml` 词条线、`12_1_0.yaml` 热词线）的 prompt 均已写入【品牌视觉基准】+【产出前自检清单】，统一以 `web/terms/14天期逆回购.html` 为唯一基准页；`skill/invest-dictionary-generator/SKILL.md` 已升级 v1.1.0，同步品牌视觉硬约束与视觉自检清单（含删除"纸感手账风格"表述）。
> **热词 cron 同样产出 HTML 页面，属于本次品牌视觉改造范围——本节此前"与改造无关"的判断已作废、不可再引用。** 模板层尚未同步，模板与基准页冲突时一律以基准页为准。

---

## 5. Rulings（已做的决策）

| ID | 内容 | 影响 |
|---|---|---|
| R1 | Cron 脏树先 commit 成 housekeeping | 不阻塞 plan |
| R2 | 真 cron 模板是 term-page.html（hot-word） | Task 5 是关键 |
| R3 | Wave 1 push 是 gate | **2026-09-22 已放行**（Wave 1/2 均 push） |
| R4 | Wave 2/3 push 同 R3 | 同上 |
| R5 | Task 2 不单独 commit，合并 Task 3 | 一个 commit 包含 link + :root |
| R6 | index.html 部分 hex 残留 deferred | Tasks 4-7 覆盖 |
| R7 | Task 4 brief 范围不全（27 处硬编码）| 后续 brief 预含全 sweep |
| R8 | Task 6 partial — sed 应用未 commit | 新窗口 commit |

---

## 6. 项目线规范（同上一份）

来自 `AGENTS.md`：
- 提交前自查 4 问
- 对话收尾流程（PROGRESS + PITFALLS + neat-freak + commit + Obsidian）
- slug 归一化（`/` `*` `>` → `_`）
- 域名 `dictionary.mangofolio.com`

---

## 7. 工作流程约束

- Git 操作 PowerShell（CLAUDE.md 2026-06-11 错误避坑）
- Git push 用 SSH 443（CLAUDE.md `ssh-22-blocked-use-443`）

---

## 8. Wave 1 · 色系主线 ✅（2026-09-19 → 2026-09-20 完成）

### 范围
全站 449 个 terms + index.html + manifest + 2 份 cron 模板 → mangofolio v1.0 色系（纯白底 / 芒果橙电压色 / 暖墨正文 / 0 楷体 / 0 老国风 / 0 朱砂红）。

### Commits（5 个 wave 1 commits + 3 个 housekeeping，已全部 push）
- `d87a66e` Task 6 redo：扩 sed ~40 模式覆盖米色 rgba / 楷体 / 老国风橙 / 朱砂红 rgba / 米色卡面 / 米色文字；`scripts/brand-sweep.pl` 沉淀
- `0122524` Task 7 redo：manifest + index.html 全站扩 sweep（amend 自 `07bcd62`）
- `5ba03ed` Task 8 cron verify：one-shot 渲染 term-page-regular.html × 2 placeholder，验证产物 grep = 0 残留
- (待) Task 9 Wave 1 收尾：PROGRESS + HANDOFF + PITFALLS

之前已有 commits（不算 wave 1 新增）：
- `0e07e95` Task 6 first cut：plan 14 模式（范围不全，已被 d87a66e 扩展覆盖）
- `07bcd62` Task 7 first cut：manifest + index.html sweep（已被 0122524 扩展覆盖）

### 验证（终验 grep = 0）
- 朱砂红 hex + rgba
- 米色 rgba（5 类）
- 老国风橙 hex + rgba
- 楷体 / 仿宋 / KaiTi / FangSong（含 HTML-encoded inline style 残段）
- theme-color 全站 `#F97316`

### 沉淀
- `scripts/brand-sweep.pl`（永久）— v1.0 brand sweep 工具，支持单/递归扫

### 下一步（Wave 2/3 · Tasks 10-17）
- Wave 2：Google Fonts + emoji 字体链 + 卡面 16px 圆角 + footer 重做
- Wave 3：暗色模式 + 涨红跌绿工具类 + 终验

### 教训（详见 PITFALLS.md #17-19）
- plan 14 sed 模式漏米色 rgba + 楷体字面 + 老国风橙；agent 不能信 plan 拍板的"grep = 0"，必须实际浏览器验证
- Windows perl 中文 regex 要用 `\x{}` unicode codepoint + `<:encoding(UTF-8)`
- inline `style="..."` 里 CSS 引号用 `&quot;` HTML encode，sweep 要双层处理
- 字体链必含 `"Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji"`（CLAUDE.md 2026-09-17 错误避坑）
- emoji 显示需要 Windows 11 Segoe UI Emoji（CLAUDE.md 2026-09-17 错误避坑）

---

*这份说明初写于 2026-09-20（源自 2026-09-19 首页 v1.0 对齐的中途断点）；2026-09-22 更新为 v1.0 全量落地后的现役状态。*
*后续：Wave 3（暗色模式 + 语义色）→ `dictionary.json` 去重（待批）→ 终验。*
*（内容由AI生成，仅供参考）*
