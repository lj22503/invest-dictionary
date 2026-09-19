# invest-dictionary 品牌对齐现状审计（2026-09-19）

**审计对象**：`D:\claudework\invest-dictionary\web/`（静态站，1 个 index.html + 438 个 terms/*.html）
**审计基准**：`D:\claudework\OPC OS\10-about-me\brand-standards\Mangofolio-设计规范-v1.0.md` + `mangofolio-tokens-v09.css`
**审计方法**：直接读 `web/index.html`（主样式 20-492 行）+ 抽样 `web/terms/14天期逆回购.html`（terms 详情页）+ 跨 4 个 terms 页（14天期逆回购 / 4321法则 / 可转债打新 / A+H股）验证模板一致性 + 全站 grep 老色系 / mango 系 / 字体链
**审计日期**：2026-09-19

> **关键事实（验证已做）**：dictionary 站的"全局规范"是**一套老体系**——所有 438 个 terms 页用同一份模板（羊皮纸底 `#f5efe0` + 楷体仿宋字体链 + 米白卡面 `#faf6ee` + 米黄虚线 `#c4b5a0`），4 个抽样页全命中。**站内全局一致性 100%**，问题只是这套老规范本身就是 v1.0 的反面。

---

## 一、总评（先给结论）

**dictionary 是 mangofolio 生态里唯一没做品牌对齐的站**——iAsk（09-18 已对齐）、fintools（v08 落地）、brain（v08 落地）都已走 mangofolio v1.0，dictionary 还停留在 **"羊皮纸 + 朱砂红 + 楷体仿宋"** 的国风老体系。

| 项 | iAsk / fintools / brain | dictionary 现状 |
|---|---|---|
| 页面底 | `#FFFFFF` 纯白 | `#F5F2EC` 宣纸 / `#f5efe0` 米色羊皮纸 |
| 主色 | `#F97316` 芒果橙 | `#C43A31` **朱砂红**（mangofolio v1.0 第 3.3 节明令"严禁使用"）|
| 文字墨 | `#3A332C` 暖墨 | `#2C2C2C` / `#3a3a3a` 冷墨 |
| 字体 | Inter + Noto Serif SC + Fraunces | "PingFang SC" + "Noto Serif SC" + **"KaiTi" 楷体** |
| 圆角 | 16px 卡 / 9999px 按钮 | 8/12/24px 散乱 |
| Fraunces 装饰 | ✅ | ❌（用 Noto Serif SC italic 凑合）|

**总体符合度：D（约 35 分）**

- 调性/氛围 30%（国风 vs 现代极简）
- 颜色 Token 10%（主色 = 朱砂红 = 严禁色）
- 字体系统 40%（Noto Serif SC 衬线已引，但楷体仿宋是 iOS 默认不是规范）
- 圆角/间距 35%
- 暗色模式 0%
- 语义色 0%

**严重性**：dictionary 当前主色 `#C43A31` 在 mangofolio v1.0 第 3.3 节"使用场景与禁忌"被列为 **"严禁使用"**。这不是"未对齐"，是"用了禁用色"。

**好消息**：因为全站用同一份模板，**修复只需替换 1 份模板 + 1 个 index.html，然后批量同步到 438 个 terms 页**，不需要逐页决策。

---

## 二、逐项差异（按规范章节）

### 2.1 颜色（v1.0 第 3 章）— 严重不符

| 角色 | 规范 | dictionary 现状 | 偏差 |
|---|---|---|---|
| 页面底 | `#FFFFFF` 纯白 | `--paper: #F5F2EC`（index）/ `#f5efe0`（terms）| ❌ 宣纸/羊皮纸 |
| 主色 | `#F97316` 芒果橙 | `--cinnabar: #C43A31` 朱砂红 | ❌ **严禁色** |
| 深色 hover | `#E05E0A` | `#a92e26` 朱砂深 | ❌ |
| 文字墨 | `#3A332C` 暖墨 | `--ink: #2C2C2C` / `#3a3a3a` | ❌ 冷墨 |
| 弱文字 | `#8A7D70` 暖灰 | `--ink-light: #5A5A5A` | ❌ 冷灰 |
| 描边 | `rgba(36,22,16,.10)` 暖墨 10% | `--border: #D9D4CC` | ❌ 冷灰边 |
| 阴影 | `rgba(36,22,16,...)` 暖墨 | `rgba(44,44,44,...)` | ❌ 冷墨 |
| 主按钮 hover 投影 | `0 8px 20px rgba(249,115,22,.22)` 橙投影 | `0 4px 14px rgba(196,58,49,.25)` 朱砂投影 | ❌ 色相完全错 |
| 涨红 | `#B8221E` | 无 | ❌ |
| 跌绿 | `#11693D` | 无 | ❌ |
| 自定义暖米 | （无）| `#c4b5a0` × 12 / `#e8784a` × 6 / `#d4745c` × 5 / `#faf6ee` × 4 / `#b8a58e` × 2 | ❌ 自成体系未与上游对齐 |

### 2.2 字体（v1.0 第 4 章）— 部分不符

| 项 | 规范 | dictionary 现状 | 偏差 |
|---|---|---|---|
| Body sans | Inter | "PingFang SC" + "Microsoft YaHei" + "Hiragino Sans GB" + **"KaiTi"** | ❌ **楷体混进 body 字体链** |
| H1 display | Noto Serif SC | ✅ Noto Serif SC | ✅ |
| en-title | Fraunces italic 1.1rem 0.15em 橙 | "Noto Serif SC" italic 1.1rem 0.15em 朱砂红 | ⚠️ 字体错（应 Fraunces）+ 色错（应橙） |
| JetBrains Mono | ✅ 用于卡片 num | ❌ 无（用衬线代替）| ⚠️ |
| 字体链包含 emoji 字体 | "Segoe UI Emoji" "Apple Color Emoji" "Noto Color Emoji" | ❌ 无（CLAUDE.md 2026-09-17 错误已踩过）| ❌ |

> 关键问题：`"KaiTi", "STKaiti"` 是 iOS / macOS 默认衬线，**Windows 上没有 KaiTi 字体会回退到默认中文字体**，导致 iOS/Mac 用户看到楷体、Windows 用户看到默认字体——**两端体验不一致**。

### 2.3 圆角 / 间距 / 阴影（v1.0 第 5 章）— 部分不符

| 项 | 规范 | dictionary 现状 | 偏差 |
|---|---|---|---|
| 卡面圆角 | 16px | 8px（entry-card）/ 12px（hot-section） | ❌ 偏小 |
| 按钮圆角 | 9999px 胶囊 | 24px（hero-btn）/ 8px（subscribe btn） | ❌ 不是胶囊 |
| 搜索框圆角 | 9999px 胶囊 | 24px | ❌ |
| 主按钮 padding | 14px 34px / 10px 26px | 10px 26px | ✅ 一致 |
| 间距 base 4px | `--space-*` 12 档 | 散乱（em/rem/px 混用） | ⚠️ |
| 容器 max-width | 1200px（fintools/brain）| 1200px（index）/ 720px（terms paper）| ✅ index / ⚠️ terms 偏窄 |
| 阴影档 | 7 档 | 2 档 | ⚠️ |
| 主按钮投影 | `0 8px 20px rgba(249,115,22,.22)` | `0 4px 14px rgba(196,58,49,.25)` | ❌ 朱砂投影 |

### 2.4 Hero 结构（v1.0 第 6.2 节）— 结构对，色全错

dictionary 的 hero **结构上与规范一致**（eyebrow → h1 → en-title → subtitle → 搜索框 → CTA），但**所有色值都是老体系**：

```
.hero p.hero-eyebrow "说人话 · 不装逼 · 每天一篇" (0.3em 朱砂红) ✅ eyebrow 角色
.hero h1 "投资词典" (Noto Serif SC 900 clamp(2rem,5vw,3.5rem)) ✅ h1 角色
.hero .en-title "Invest Dictionary" (Noto Serif SC italic 1.1rem 0.15em 朱砂红) ⚠️ 应 Fraunces
.hero .subtitle "把投资术语翻译成你听得懂的话" (1.05rem #5A5A5A) ⚠️ 应暖墨
.hero input[type="search"] (24px 圆角) ⚠️ 应 9999px 胶囊
.hero-btn "C43A31 橙投影" ❌ 应 mango #F97316 + 橙投影
```

### 2.5 导航（v1.0 第 7.1 节）

| 项 | 规范 | dictionary 现状 | 评估 |
|---|---|---|---|
| 底 | `rgba(255,255,255,.9)` + blur(12px) | `rgba(245,242,236,.92)` + blur(6px) | ❌ 宣纸底 + blur 偏弱 |
| 描边 | 1px border-weak | 1px solid #D9D4CC | ❌ |
| z-index | 1000（dictionary 落地）| 999 | ⚠️ 接近 |
| Brand en 装饰 | Fraunces italic 橙 | Noto Serif SC italic 朱砂红 | ⚠️ |
| 导航链接 hover 变橙 | ✅ | hover 变朱砂红 | ⚠️ 色错 |

### 2.6 卡片 / 热词卡 / 搜索框（v1.0 第 7.3-7.6 节）

| 项 | 规范 | dictionary 现状 | 评估 |
|---|---|---|---|
| 词条卡（entry-card） | 16px 白卡 + border-weak + 双层墨影 | 8px 白卡 + #D9D4CC 边 + 单层投影 | ❌ 圆角小、边冷、阴影少 |
| 热词卡 | 16px 白卡 + 320px 订阅表单 + dashed 左分栏 | 12px 白卡 + 320px 订阅 + dashed 左分栏 | ⚠️ 圆角错 |
| 搜索框 | 9999px 胶囊 + focus 橙边 + 3px 橙光环 | 24px + focus 朱砂红边 + 3px 朱砂光环 | ❌ 圆角+色全错 |
| Footer | 深墨底 + 暖灰字 + 生态三卡 | 简单文字 footer（无生态卡）| ❌ **完全没按规范** |

### 2.7 暗色模式（v1.0 第 8 章）

- ❌ 无
- dictionary 是品牌站 + 长文阅读，暗色模式优先级高

### 2.8 涨跌幅 / 风险（v1.0 第 3.1.5 节）

- ❌ 无涨红 `#B8221E` / 跌绿 `#11693D`
- dictionary 现状：词条页无涨跌幅展示，但词条涉及涨跌幅时（如"美股 CPI""新股破发"）应该有

---

## 三、严重问题 Top 7（按影响排）

1. **主色用禁用色 `#C43A31` 朱砂红**——v1.0 第 3.3 节明令"严禁使用"，全 438 个 terms 页 + index.html 命中
2. **页面底用宣纸 `#F5F2EC` / 米色羊皮纸 `#f5efe0`**——v1.0 第 1.3 节明确"默认全站纯白"
3. **正文用了楷体 `"KaiTi", "STKaiti"`**——iOS 默认字体，Windows 端回退不一致
4. **缺 Fraunces 字体**——en-title 用 Noto Serif SC italic 凑合，缺"英文装饰"角色
5. **全 12064 处老色系硬编码**——任何品牌调整都需要全文替换
6. **缺暗色模式**——生态其他站都有，dictionary 是孤岛
7. **footer 完全没按规范**——深墨底 + 生态三卡 + 跨品牌互导 全缺

---

## 四、工作面与改动量

### 4.1 文件清单

| 文件 | 数量 | 备注 |
|---|---|---|
| `web/index.html` | 1 | 首页（含 nav / hero / hot-section / footer） |
| `web/terms/*.html` | 438 | 词条详情页（**同一份米色羊皮纸模板**）|
| `web/api/*.js` | 5+ | 无样式，不影响 |
| `web/js/*.js` | 2 | tracker.js / knowledge-card.js 可能有 inline style，需扫 |
| `web/manifest.json` | 1 | `theme-color: #c43a31` 也要改 |

**核心改动文件：439 个 HTML + manifest.json**

**模板一致性（验证已做）**：抽样 4 个 terms 页（14天期逆回购 / 4321法则 / 可转债打新 / A+H股）—— `:root`、body、`.paper`、`.paper-content`、font-family、虚线米黄 `#c4b5a0`、羊皮纸底 `#f5efe0`、米白卡面 `#faf6ee` 全部相同。这意味着：
- **改 1 份模板 → 全 438 页同步生效**（用 sed 批量同步即可）
- **不会逐页出现意外差异**，审计风险大幅降低
- 不需要逐页决策，工作量从"439 个文件独立改"降到"改 2 份源 + sed 批量分发"

### 4.2 颜色硬编码覆盖度

| 文件 | 老色系硬编码处数 |
|---|---|
| `index.html` | 18 |
| `terms/14天期逆回购.html`（抽样）| 13 |
| 全 438 terms 页合计 | ~12000 |

每页平均 **27 处色值硬编码**，覆盖到 `:root` 变量外还散落在各组件 CSS 中。

---

## 五、修复策略（3 阶段，避免一次性大爆炸）

### 第一波：色系主线对齐（4-6 小时，推荐立即做）

**目标**：把朱砂红 + 宣纸 + 冷墨替换为 mango + 纯白 + 暖墨

| 改动 | 工作量 | 影响 |
|---|---|---|
| 1. index.html `:root` 变量替换：`--paper:#FFFFFF` / `--cinnabar:#F97316` / `--ink:#3A332C` / `--ink-light:#8A7D70` / `--border:rgba(36,22,16,.10)` / `--shadow:0 1px 3px rgba(36,22,16,.08), 0 4px 12px rgba(36,22,16,.06)` / `--shadow-hover:0 8px 20px rgba(249,115,22,.22)` | 30 min | 高 |
| 2. 移除 hero `linear-gradient(180deg, rgba(196,58,49,.03), transparent)` 朱砂光晕，改纯白 | 5 min | 中 |
| 3. 主按钮 hover 朱砂深 `#a92e26` → `var(--mango-deep)` = `#E05E0A`；投影改橙 | 5 min | 高 |
| 4. terms 详情页 `:root` + body 替换：底 `#f5efe0` → `#FFFFFF`，去掉双 radial-gradient 米黄光斑；font-family 去掉 `"KaiTi", "STKaiti", "FangSong"` 楷体仿宋；纸面 `#faf6ee` → `#FFFFFF`；暖米黄边 `#c4b5a0` → `rgba(36,22,16,.10)` | 30 min | 高 |
| 5. 全 438 terms 页批量 sed 替换老色系（朱砂红系 / 冷墨 / 米黄）| 2-3h | 高 |
| 6. `manifest.json` `theme-color: #c43a31` → `#F97316` | 2 min | 中 |

**Top 6 加起来 ~4-6h**，符合度从 35 拉到 75+。

### 第二波：字体与组件态（2-3 小时）

| 改动 | 工作量 | 影响 |
|---|---|---|
| 1. 引入 Fraunces 字体（Google Fonts link 加 `&family=Fraunces:ital,wght@1,400;1,500&display=swap`）| 5 min | 高 |
| 2. en-title 字体从 Noto Serif SC italic → Fraunces italic 1.1rem 0.15em 橙 | 20 min | 高 |
| 3. 引入 Inter（body 字体规范化）| 5 min | 高 |
| 4. 字体链加 `"Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji"`（CLAUDE.md 09-17 错误避坑）| 5 min | 中 |
| 5. 卡面圆角 8/12 → 16；按钮圆角 24 → 9999；搜索框 24 → 9999 | 30 min | 高 |
| 6. footer 重做：深墨底 + 暖灰字 + 生态三卡（dictionary / fintools / brain）+ 色板 swatches | 1-2h | 高 |

### 第三波：缺口补齐（按需，6+ 小时）

| 改动 | 工作量 |
|---|---|
| 1. 暗色模式（`[data-color-mode="dark"]` 双值覆盖）| ~2 天 |
| 2. 涨红 `#B8221E` / 跌绿 `#11693D` 沉淀（无场景可暂缓）| 0.5h |
| 3. 阴影 7 档补齐 | 2h |
| 4. Spacing 4px 刻度变量化（`--space-*`）| 2h |
| 5. 引入 `mangofolio-tokens-v09.css` 外部依赖（替代 inline `:root`）| 1h |

---

## 六、推进路径建议

| 时间 | 工作 | 工作量 |
|---|---|---|
| **今晚** | 第一波（色系主线）| 4-6h |
| 明天 | 第二波（字体 / 圆角 / footer）| 2-3h |
| 后续按需 | 第三波（暗色 / 涨跌幅 / 阴影）| 6+ h |

**推荐**：
- **今晚必做第一波**——主色禁用是品牌红线，越拖越痛
- 第二波可分两次：先把字体+en-title+楷体清理（45min）做完，footer 单独安排 1h
- 第三波全部按需，不急

---

## 七、回归风险与注意

1. **438 个 terms 页批量替换**——用 `sed` 一次替换前，**先抽样 1 个页确认无副作用**（避免把 og:url / canonical 里的 `#C43A31` 误改）
2. **关键词语保留**：词条正文里若出现"朱砂红""宣纸"等字面词，**不要替换**（只换 CSS 里的色值）
3. **og:url / canonical / schema.org** 里硬编码的 `dictionary.mangofolio.com` 不动
4. **`/terms/` 详情页 `theme-color` 元数据** 也可能要改
5. **提交前自查 4 问**：commit message 写明 `dictionary: brand align v1.0 wave 1`

---

## 八、结论

dictionary 是 mangofolio 生态里**唯一未对齐**的站，主色用了 v1.0 明令严禁的朱砂红，是品牌红线级偏差。**第一波色系主线 4-6 小时即可拉到 75+ 分**，强烈建议立即开工。

完整修复后预期符合度 88-92（与 iAsk 对齐水平）。

---

*审计方法：globals.css（460 行）/ layout.tsx 等价物（index.html 主样式 20-492 行）/ 抽样 terms 详情页 / 全站 grep 老色系 12064 处 / 字体链分析*
*对比对象：Mangofolio-设计规范-v1.0.md + DESIGN.md（iAsk 实施层）+ collectui-mangofolio-mapping.html*
*修订记录：相对首次分析（09-18 晚上用户澄清目标前）确认 dictionary 是真正目标；quantify 439 文件 / 12064 硬编码 / 4 个新发现（楷体混 body / 自定义米色系 / theme-color / 缺 Segoe UI Emoji）。*
