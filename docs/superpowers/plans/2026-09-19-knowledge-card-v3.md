# Knowledge Card v3 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 dictionary 站"生成知识卡片"下载的 PNG 从 v2（朱砂红国风）改造为 v3（杂志头条 / 纯白底 / 中文衬线 / 走读感）

**Architecture:** 单文件改造。`web/js/knowledge-card.js` 整个 buildCard() 重写：保留 v2 的 `collectCards()` / `wrapLines()` / `measureBlock()` 数据抓取与排版工具，重写整个 canvas 绘制循环（eyebrow / 主标题 / en-title / 橙分隔条 / 章节标题无序号 / 暖墨虚线分隔 / 引用条 / 底部 URL）。所有 438 个 terms 页共用同一份 JS，无需逐页改。

**Tech Stack:** 纯 canvas 2D（无外部库）

**Spec:** `D:\claudework\invest-dictionary\docs\specs\2026-09-19-knowledge-card-v3-design.md`

---

## Global Constraints

- 颜色必须用 v1.0 规范：`#F97316`（主橙）/ `#E05E0A`（深橙）/ `#241610`（深墨）/ `#3A332C`（暖墨）/ `#8A7D70`（暖灰）/ `rgba(36,22,16,.12)`（暖墨弱）
- **严禁** `#C43A31` 朱砂红（v1.0 第 3.3 节明令）
- **严禁** 楷体 `"KaiTi" / "STKaiti" / "FangSong"`（v1.0 不在字体链）
- 字体链必须含 `"Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji"`（避免 Windows emoji 异常，参考 CLAUDE.md 2026-09-17 错误记录）
- canvas 宽度 1242px，左右留白 90px，正文可用宽度 1062px
- 最小高度 1500px，高度自适应
- 不渲染章节序号（无 ① ②，纯标题层级）
- commit message 写明 `dictionary:` 前缀（按 AGENTS.md 提交前自查 4 问）

---

### Task 1: 重写 buildCard() 头部区（eyebrow + 主标题 + en-title + 80% 宽 2px 橙条）

**Files:**
- Modify: `web/js/knowledge-card.js:118-186`（buildCard 函数的前半段：H 测量 + 绘制头部）

**Interfaces:**
- Consumes: `getTermName()`, `getChapter()`, `cards`（来自 collectCards）
- Produces: canvas 顶部 ~280px 高度的 eyebrow / 主标题 / en-title / 2px 橙条

- [ ] **Step 1: 备份当前 knowledge-card.js 到 knowledge-card.js.bak-20260919**

```bash
cp "D:\claudework\invest-dictionary\web\js\knowledge-card.js" "D:\claudework\invest-dictionary\web\js\knowledge-card.js.bak-20260919"
```

- [ ] **Step 2: 改 W = 1242（从 750）**

```javascript
var W = 1242;            // 画布宽度（朋友圈封面标准）
var PAD = 90;            // 左右留白
var MAXW = W - PAD * 2; // 正文可用宽度 = 1062
```

- [ ] **Step 3: 改 H_HEAD = 280（从 330）**

```javascript
var H_HEAD = 280;              // 头部区域高度（eyebrow + 标题 + 橙条）
```

- [ ] **Step 4: 改字体大小常量**

```javascript
var EYEBROW_FONT = 'bold 32px "Inter","PingFang SC","Microsoft YaHei","Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif';
var TITLE_FONT_LG = 'bold 72px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
var TITLE_FONT_MD = 'bold 56px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
var ENTITLE_FONT = 'italic 36px "Fraunces","Noto Serif SC",serif';
```

- [ ] **Step 5: 改 measureTitle 用 Noto Serif SC**

```javascript
function measureTitle(ctx, title, font, lh) {
  ctx.font = font;
  return wrapLines(ctx, title, MAXW).length * lh;
}
```

（函数体不变，只把 font 参数传入 ctx.font）

- [ ] **Step 6: 改 ctx0 字体（测量循环）**

```javascript
ctx0.font = TITLE_FONT_LG;
var titleFont = ctx0.measureText(name).width > MAXW ? TITLE_FONT_MD : TITLE_FONT_LG;
```

- [ ] **Step 7: 改 measureBlock 用 Noto Serif SC + Inter 链**

```javascript
function measureBlock(ctx, block, lh) {
  ctx.font = '38px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
  if (block.type === 'ul') {
    var h = 0;
    block.items.forEach(function (it) {
      h += wrapLines(ctx, '· ' + it, MAXW - 16).length * lh;
      h += 12;
    });
    return h;
  }
  return wrapLines(ctx, block.text, MAXW).length * lh;
}
```

- [ ] **Step 8: 改卡片间距 / 章节标题行高 / 正文行高 / 引用行高**

```javascript
var TITLE_LH = 64;       // 章节标题 48px 64 行高（48 * 1.33）
var BLOCK_LH = 70;       // 正文 38px 70 行高（38 * 1.85）
var QUOTE_LH = 60;       // 引用 36px 60 行高
var CARD_GAP = 56;       // 章节间距
var HEADING_TO_BODY = 28; // 章节标题 → 正文
var DIVIDER_GAP = 32;    // 分隔虚线 → 下一章节标题
```

- [ ] **Step 9: 改 ctx0 测量循环（用新间距）**

```javascript
cards.forEach(function (card) {
  bodyH += CARD_GAP;
  if (card.title) bodyH += measureTitle(ctx0, card.title, 'bold 48px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif', TITLE_LH);
  bodyH += HEADING_TO_BODY;
  card.blocks.forEach(function (b) {
    if (b.type === 'quote') bodyH += measureBlock(ctx0, b, QUOTE_LH) + 24;
    else bodyH += measureBlock(ctx0, b, BLOCK_LH);
  });
  bodyH += DIVIDER_GAP; // 章节间分隔虚线 + 间距
});
var H = Math.max(1500, H_HEAD + bodyH + FOOT_H);
```

- [ ] **Step 10: 改绘制头部（eyebrow + 主标题 + en-title + 橙条）**

替换 buildCard() 中 "// 背景" 到 "// 分割线" 之间的代码：

```javascript
    // 背景（纯白）
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, W, H);

    var y = 0;

    // Eyebrow 眉题
    y += 70;
    ctx.font = EYEBROW_FONT;
    ctx.fillStyle = '#F97316';
    ctx.textAlign = 'left';
    ctx.fillText('MANGOFOLIO · 投资词典', PAD, y);

    // 主标题（Noto Serif SC 72px 900）
    y += 80;
    ctx.font = titleFont;
    ctx.fillStyle = '#241610';
    var titleLines = wrapLines(ctx, name, MAXW);
    titleLines.forEach(function (ln) {
      ctx.fillText(ln, PAD, y);
      y += 80;
    });

    // En-title（Fraunces italic 橙）
    y += 8;
    var enTitle = 'Invest Dictionary · ' + (chapter || '14-day reverse repo');
    ctx.font = ENTITLE_FONT;
    ctx.fillStyle = '#F97316';
    ctx.fillText(enTitle, PAD, y);

    // 2px 橙条 80% 宽
    y += 24;
    ctx.fillStyle = '#F97316';
    ctx.fillRect(PAD, y, MAXW * 0.8, 2);
```

- [ ] **Step 11: 验证头部代码语法**

```bash
node -e "new Function(require('fs').readFileSync('D:\\\\claudework\\\\invest-dictionary\\\\web\\\\js\\\\knowledge-card.js', 'utf8'))"
```

Expected: 无错（语法合法）

- [ ] **Step 12: Commit Task 1**

```bash
cd "D:\claudework\invest-dictionary"
git add web/js/knowledge-card.js
git commit -m "dictionary: knowledge-card v3 — eyebrow + 主标题 + en-title + 80% 橙条"
```

---

### Task 2: 重写章节绘制循环（无序号 + 暖墨虚线分隔 + 引用条）

**Files:**
- Modify: `web/js/knowledge-card.js` buildCard() 后续章节绘制段

**Interfaces:**
- Consumes: Task 1 输出的 ctx / canvas
- Produces: 完整章节渲染（标题无序号 / 正文衬线 / 列表 / 引用条 / 章节间虚线）

- [ ] **Step 1: 替换章节绘制循环**

替换 buildCard() 中 "// 正文卡片" 到 "// 底部" 之间的代码：

```javascript
    // 正文卡片
    y += 80;
    cards.forEach(function (card, idx) {
      if (idx > 0) {
        // 章节间分隔虚线（暖墨 12% 50% 宽）
        ctx.strokeStyle = 'rgba(36,22,16,0.12)';
        ctx.lineWidth = 1;
        ctx.setLineDash([6, 6]);
        ctx.beginPath();
        ctx.moveTo(PAD + MAXW * 0.25, y - DIVIDER_GAP / 2);
        ctx.lineTo(PAD + MAXW * 0.75, y - DIVIDER_GAP / 2);
        ctx.stroke();
        ctx.setLineDash([]);
      }
      y += CARD_GAP;
      if (card.title) {
        ctx.font = 'bold 48px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
        ctx.fillStyle = '#241610';
        var titleLines = wrapLines(ctx, card.title, MAXW);
        titleLines.forEach(function (ln) {
          ctx.fillText(ln, PAD, y);
          y += TITLE_LH;
        });
        y += HEADING_TO_BODY;
      }
      card.blocks.forEach(function (b) {
        if (b.type === 'quote') {
          // 引用条：2px 橙左边 + italic 13px 暖墨
          y += 10;
          ctx.strokeStyle = 'rgba(249,115,22,0.40)';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(PAD + 14, y - 8);
          ctx.lineTo(PAD + 14, y + 10);
          ctx.stroke();
          ctx.font = 'italic 36px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
          ctx.fillStyle = '#3A332C';
          var qLines = wrapLines(ctx, b.text, MAXW - 32);
          var qStart = y;
          qLines.forEach(function (ln) {
            ctx.fillText(ln, PAD + 36, y);
            y += QUOTE_LH;
          });
          // 引用条左边竖线拉长
          ctx.beginPath();
          ctx.moveTo(PAD + 14, qStart - 12);
          ctx.lineTo(PAD + 14, y - QUOTE_LH + 14);
          ctx.stroke();
          y += 20;
        } else if (b.type === 'ul') {
          ctx.font = '38px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
          ctx.fillStyle = '#3A332C';
          b.items.forEach(function (it) {
            var ls = wrapLines(ctx, '· ' + it, MAXW - 16);
            ls.forEach(function (ln) {
              ctx.fillText(ln, PAD + 16, y);
              y += BLOCK_LH;
            });
            y += 8;
          });
        } else {
          ctx.font = '38px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
          ctx.fillStyle = '#3A332C';
          var ps = wrapLines(ctx, b.text, MAXW);
          ps.forEach(function (ln) {
            ctx.fillText(ln, PAD, y);
            y += BLOCK_LH;
          });
        }
      });
    });
```

- [ ] **Step 2: 改 FOOT_H = 100（80 即可，给 URL + 副标留空间）**

```javascript
var FOOT_H = 100;
```

- [ ] **Step 3: 验证整个文件语法**

```bash
node -e "new Function(require('fs').readFileSync('D:\\\\claudework\\\\invest-dictionary\\\\web\\\\js\\\\knowledge-card.js', 'utf8'))"
```

Expected: 无错

- [ ] **Step 4: Commit Task 2**

```bash
cd "D:\claudework\invest-dictionary"
git add web/js/knowledge-card.js
git commit -m "dictionary: knowledge-card v3 — 章节标题无序号 + 暖墨虚线分隔 + 引用条"
```

---

### Task 3: 重写底部 URL 区（暖灰 URL + 副标）

**Files:**
- Modify: `web/js/knowledge-card.js` buildCard() 末尾 "// 底部" 段

**Interfaces:**
- Consumes: canvas / ctx / current y / W / PAD
- Produces: 底部 URL 行 + "内容仅供学习参考..." 副标

- [ ] **Step 1: 替换底部绘制**

替换 buildCard() 中 "// 底部" 段：

```javascript
    // 底部（暖灰 URL + 副标）
    y = H - FOOT_H + 50;
    ctx.font = '32px "Inter","PingFang SC","Microsoft YaHei","Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif';
    ctx.fillStyle = '#8A7D70';
    ctx.fillText('https://dictionary.mangofolio.com', PAD, y);
    ctx.fillText('内容仅供学习参考，不构成投资建议', PAD, y + 50);
    return canvas;
```

- [ ] **Step 2: 验证整个文件语法**

```bash
node -e "new Function(require('fs').readFileSync('D:\\\\claudework\\\\invest-dictionary\\\\web\\\\js\\\\knowledge-card.js', 'utf8'))"
```

Expected: 无错

- [ ] **Step 3: Commit Task 3**

```bash
cd "D:\claudework\invest-dictionary"
git add web/js/knowledge-card.js
git commit -m "dictionary: knowledge-card v3 — 底部 URL 暖灰 + 副标"
```

---

### Task 4: 验证 PNG 实际效果（4 个抽样词条）

**Files:**
- Test: 浏览器手工操作 4 个词条页（强刷 + 生成知识卡片 + 看 PNG）

**Interfaces:**
- Consumes: web/js/knowledge-card.js（Task 1-3 全部完成）
- Produces: 4 张 PNG 截图验证

- [ ] **Step 1: 强刷测试页 `14天期逆回购.html`**

浏览器地址：`http://localhost:8080/terms/14天期逆回购.html`

按 Ctrl+F5 强制刷新。

- [ ] **Step 2: 点 "生成知识卡片" 按钮（位于"← 返回投资词典"上方）**

下载 PNG 到 `~/Downloads/knowledge-XXXX.png`

- [ ] **Step 3: 检查 PNG 视觉清单（对照 spec 验收清单）**

| 检查项 | 期望 |
|---|---|
| Eyebrow "MANGOFOLIO · 投资词典" 橙 0.3em | ✅ |
| 主标题 Noto Serif SC 大字深墨 | ✅ |
| En-title Fraunces italic 橙 | ✅ |
| 标题下方 1 条 2px 橙线 80% 宽 | ✅ |
| 章节标题无序号（无 ① ② / 02 / 一 ·）| ✅ |
| 章节正文 Noto Serif SC 暖墨 | ✅ |
| 引用条 2px 橙左边 + italic | ✅ |
| 章节间暖墨虚线 50% 宽 dashed 6px | ✅ |
| 底部 URL + 副标暖灰 | ✅ |
| 无朱砂红 `#C43A31` | ✅ |
| 无楷体 KaiTi | ✅ |
| 1242 宽、高度自适应 | ✅ |

如果任一项不通过，回到 Task 1-3 对应代码修正。

- [ ] **Step 4: 重复测试 3 个不同长度词条**

- `4321法则.html`（中长）
- `可转债打新.html`（中等）
- `14天期逆回购.html`（已测）

每个都强刷 + 生成 PNG + 看视觉效果。

- [ ] **Step 5: Commit Task 4（如有调整）**

如果 Task 1-3 的代码经过修正：
```bash
cd "D:\claudework\invest-dictionary"
git add web/js/knowledge-card.js
git commit -m "dictionary: knowledge-card v3 — 视觉调整（基于 4 个词条页验证）"
```

如无调整，跳过此步。

---

### Task 5: 写 PROGRESS.md 更新（按 AGENTS.md 对话收尾流程）

**Files:**
- Modify: `D:\claudework\invest-dictionary\PROGRESS.md`

- [ ] **Step 1: 在 PROGRESS.md 顶部加 09-19 段**

```markdown
## 2026-09-19 · 知识卡片 v3

### 改动
- `web/js/knowledge-card.js` 整个 buildCard() 重写为 v3（杂志头条方向）
- 替代 v2 朱砂红国风版（2026-08 之前）
- 设计规范：`docs/specs/2026-09-19-knowledge-card-v3-design.md`

### 主要变化
- 主色 朱砂红 `#C43A31` → 芒果橙 `#F97316`（v1.0 严禁色移除）
- 底色 羊皮纸 `#f5efe0` → 纯白 `#FFFFFF`
- 字体链 "PingFang SC" → Noto Serif SC（中文衬线主导）
- 字号 1242 宽（朋友圈封面标准）
- 加 Eyebrow 眉题 + En-title + 80% 宽 2px 橙条（杂志头条标志）
- 章节序号移除（无 ① / 02 / 一 ·，纯标题层级）
- 章节间分隔：橙色 4px 短条 → 暖墨 12% 50% 虚线 dashed 6px

### 验证
- 4 个抽样词条页强刷 + 生成 PNG + 视觉清单逐项核对
- 全 438 个 terms 页共用同一份 JS，无后续逐页改
```

- [ ] **Step 2: Commit PROGRESS.md**

```bash
cd "D:\claudework\invest-dictionary"
git add PROGRESS.md
git commit -m "dictionary: PROGRESS.md 更新 — 知识卡片 v3 闭环"
```

---

## Self-Review

1. **Spec 覆盖**：
   - spec 第 3 节颜色 → Task 1-3 所有 fillStyle 都用 v1.0 值 ✅
   - spec 第 4 节字体 → Task 1-3 所有 ctx.font 都用 Inter / Noto Serif SC / Fraunces ✅
   - spec 第 5 节尺寸 → Task 1 Step 2-3 W=1242 PAD=90 ✅
   - spec 第 6 节字号阶梯 → Task 1 Step 4 ✅
   - spec 第 7 节数据来源 → Task 2 Step 1 用 collectCards() 输出（不变）
   - spec 第 8 节决策记录 → 已写进 spec，plan 任务落实
   - spec 第 9 节验收清单 → Task 4 Step 3 ✅

2. **占位扫描**：无 TBD / TODO。所有字号色值都给了具体值。

3. **类型一致性**：
   - `cards` / `card.title` / `card.blocks` / `block.type` 全程一致（v2 既有数据结构）
   - `ctx` / `canvas` / `W` / `PAD` / `MAXW` 全程一致
   - 常量 EYEBROW_FONT / TITLE_FONT_LG / TITLE_FONT_MD / ENTITLE_FONT / TITLE_LH / BLOCK_LH / QUOTE_LH / CARD_GAP / HEADING_TO_BODY / DIVIDER_GAP / H_HEAD / FOOT_H 命名无冲突

4. **范围**：单文件改动（knowledge-card.js）+ 1 个 PROGRESS.md，5 个任务足够，无子系统拆分。

---

*本计划基于 spec：`docs/specs/2026-09-19-knowledge-card-v3-design.md`*
*参考 mockup：`.superpowers/brainstorm/2582-1789781366/content/knowledge-card-directions.html`（A 杂志头条方案）*
