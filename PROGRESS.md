# PROGRESS — invest-dictionary（投资词典）

> mangofolio 生态第 3 块 · 术语平权（听得懂）。213+ 中文投资术语，"说人话不装逼"。
> 进度记录：每次对话收尾更新（项目线规范②）。

## 2026-09-19 → 2026-09-20 · 首页品牌对齐 v1.0（**进行中，5/17 tasks**）

### 背景
dictionary 是 mangofolio 生态里**唯一未对齐** v1.0 的站——iAsk / fintools / brain 都已 v1.0，dictionary 还停留在朱砂红 + 宣纸 + 楷体国风老体系。BRAND_AUDIT 完成（35 分符合度）。开始三波对齐改造。

### 文档
- spec: `docs/superpowers/specs/2026-09-19-homepage-v1-design.md`
- plan: `docs/superpowers/plans/2026-09-19-homepage-v1.md`
- BRAND_AUDIT: `docs/BRAND_AUDIT_2026-09-19.md`
- HANDOFF: `docs/HANDOFF.md`

### 已完成（5/17）
| Task | 改动 | Commits |
|---|---|---|
| 1. 引入 v09.css | web/css/mangofolio-tokens-v09.css（从 OPC OS 拷贝） | fd42597 |
| 3. index.html :root 改 v1.0 | `--paper` / `--cinnabar` / `--ink` 等 6 个变量映射到 var(--mf-colors-*)；line 478 inline hover 也修复 | cf00075 + 0b22932 |
| 4. term-page-regular.html v1.0 | 7 :root vars + 11 font-family + 10 borders + 6 cinnabar + 4 card-bg + 30+ legacy hex 全清；grep = 0 | e307f1c + c2659c3 |
| 5. term-page.html v1.0（**真 cron 模板**）| 同 Task 5 sweep | 243a667 |

### Partially done
| Task | 状态 | 说明 |
|---|---|---|
| 6. sed 446 terms | sed 应用 + grep 0；**未 commit** | R8 — 新窗口 commit |

### 未做
- Task 7: manifest.json + meta theme-color
- Task 8: cron 验证（file mode 跑 2 条）
- Task 9: PROGRESS + HANDOFF 同步 + Wave 1 push gate
- Wave 2（Tasks 10-14）：Google Fonts + emoji 字体链 + 卡面圆角 + footer 重做
- Wave 3（Tasks 15-17）：暗色模式 + 涨红跌绿 + 终验

### 关键 cron 路径修正
之前以为 `batch_fill_1000.py` 是 cron，实际 cron 是 **Marvis 11_1_0.yaml**，直接读 `templates/term-page.html`（hot-word 模板）。Task 5 已改 v1.0，下次 cron 产出就是新体系。

### 工作区状态
- Wip commit `b226be1`（cron in-progress 改动 housekeeping）
- 446 terms sed 已应用未 commit（Task 6 partial）
- 所有 commits 本地，未 push（Wave 1 push 是 gate，等用户批）

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

- [ ] **Task 6 commit**（新窗口第一件事）
- [ ] Tasks 7-9 完成 Wave 1 → push gate
- [ ] Wave 2 推进（字体 + 圆角 + footer）
- [ ] Wave 3 推进（暗色 + 语义色）
- [ ] neat-freak 6 面审计 + 终验