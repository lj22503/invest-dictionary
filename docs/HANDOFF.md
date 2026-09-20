# invest-dictionary 接手说明（**2026-09-20 新窗口用**）

> 这份说明是给**新开窗口接手 invest-dictionary 的 agent** 看的。读完这份文件 + PROGRESS.md + AGENTS.md 即可开始工作。

---

## 1. 项目一句话

`D:\claudework\invest-dictionary` — **投资词典**（Invest Dictionary）

- 213+ 中文投资术语，"说人话不装逼"
- 线上站：https://dictionary.mangofolio.com
- mangofolio 生态第 3 块（术语平权，听得懂）
- 静态站，零依赖零构建，Vercel 托管

---

## 2. 当前首要任务 — 首页对齐 mangofolio v1.0（**in progress**）

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

## 3. 新窗口接手 checklist

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

**Task 5 已改 term-page.html v1.0**——下次 cron 跑出来的就是 v1.0 体系。

热词 cron（12_1_0.yaml）走 KV 推送路径，与本次改造无关。

---

## 5. Rulings（已做的决策）

| ID | 内容 | 影响 |
|---|---|---|
| R1 | Cron 脏树先 commit 成 housekeeping | 不阻塞 plan |
| R2 | 真 cron 模板是 term-page.html（hot-word） | Task 5 是关键 |
| R3 | Wave 1 push 是 gate | 需用户批 push |
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
- 字体链必含 `"Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji"`（CLAUDE.md 2026-09-17 错误避坑）
- emoji 显示需要 Windows 11 Segoe UI Emoji（CLAUDE.md 2026-09-17 错误避坑）

---

*这份说明写于 2026-09-20，从 2026-09-19 首页 v1.0 对齐工作中途断点（用户主动要求整理上下文）。*
*后续：Task 6 commit → Task 7-9 → Wave 1 push gate → Wave 2/3 推进。*