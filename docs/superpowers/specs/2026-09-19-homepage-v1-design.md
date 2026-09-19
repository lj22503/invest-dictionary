# 投资词典首页对齐 mangofolio v1.0 设计规范

**版本**：v1.0（首页首次品牌对齐）
**日期**：2026-09-19
**取代**：朱砂红 + 宣纸 + 楷体 国风老体系（v2 知识卡片已 09-19 同步完成）
**适用范围**：`web/index.html`（首页）+ `web/terms/*.html`（446 个详情页）+ `skill/.../templates/*.html`（cron 渲染源）+ `web/manifest.json`（PWA）
**权威规范**：`D:\claudework\OPC OS\10-about-me\brand-standards\Mangofolio-设计规范-v1.0.md`（v1.0 = 2026-09-18 修订）
**设计参考**：`iAsk` 站 09-18 已对齐（`D:\claudework\invest-iAskbetter\docs\DESIGN.md` 框架可套用，但 dictionary 是品牌站，应保留 eyebrow + en-title）

---

## 1. 背景与目标

dictionary 是 mangofolio 生态里**唯一未对齐** v1.0 的站——iAsk（09-18）、fintools（v08）、brain（v08）都已走 v1.0 体系，dictionary 仍停留在 **"羊皮纸 + 朱砂红 + 楷体仿宋"** 国风老体系。BRAND_AUDIT_2026-09-19 已完成全站审计（439 文件 / 12064 处硬编码 / Top 7 严重问题），符合度约 **35 分 / 100 分**。

**最严重**：主色 `#C43A31` 朱砂红在 v1.0 第 3.3 节"使用场景与禁忌"被明令**严禁使用**——全 446 个 terms 页 + index.html 命中。

**好消息**：全站 446 个 terms 页 + cron 模板共用**同一份模板**，修复只需改 1 份源 + 1 个 index.html + sed 批量分发。

**改造目标**：
- 全站对齐 mangofolio v1.0（颜色 / 字体 / 圆角 / 阴影 / 组件态）
- 引入 `mangofolio-tokens-v09.css` 外部令牌（暗色模式零成本继承）
- 批量 cron 生成的新词条自动套用 v1.0（修 `term-page-regular.html`）
- 不破坏知识卡片 v3（已 09-19 完成）

---

## 2. 改造范围（451 个文件）

| 类别 | 文件 | 数量 | 改动 |
|---|---|---|---|
| 外部令牌 | `web/css/mangofolio-tokens-v09.css`（新建） | 1 | 从 OPC OS 拷贝 523 变量 light/dark |
| 首页 | `web/index.html`（8159 行 / 259KB） | 1 | `:root` 改 `var(--mf-*)`；head 加 token link；hero / nav / hot-section / footer 重做 |
| cron 模板（regular） | `skill/invest-dictionary-generator/templates/term-page-regular.html` | 1 | 同上；同步 `theme-color` |
| cron 模板（hot-word） | `skill/invest-dictionary-generator/templates/term-page.html` | 1 | 同上（cron 当前不引用，但保持模板体系一致） |
| 详情页 | `web/terms/*.html` | 446 | sed 批量：去朱砂红 / 宣纸 / 米黄 / 楷体；改 `theme-color` |
| PWA | `web/manifest.json` | 1 | `theme_color: #c43a31` → `#F97316` |
| 字体源 | Google Fonts `<link>` 加 Fraunces + Inter | 1 | 引入英文装饰 + 正文无衬线 |

**不动的文件**：
- `web/api/*.js`（无样式）
- `web/js/knowledge-card.js`（已 v3 完成，自带 CSS）
- `web/dictionary.json`（数据源）
- `web/sitemap.xml` / `web/robots.txt`（无样式）
- `web/sw.js`（service worker）

---

## 3. 色彩映射（v1.0 语义令牌）

页面只允许引用语义层（`--mf-colors-*`），禁止硬编码色值。

### 3.1 核心 10 项映射

| 老值（出现处） | v1.0 令牌 | 新值 | 备注 |
|---|---|---|---|
| `#C43A31` 朱砂红（严禁色） | `--mf-colors-text-link` | `#F97316` | 主色（移除严禁色） |
| `#A33028` / `#a92e26` 朱砂深 | `--mf-colors-text-link-hover` | `#E05E0A` | hover 深档 |
| `#F5F2EC` 宣纸 / `#f5efe0` 米色羊皮纸 | `--mf-colors-background` | `#FFFFFF` | 页面底（**默认纯白**） |
| `#faf6ee` 米白卡面 | `--mf-colors-background-surface` | `#FFFFFF` | 卡面 |
| `#2C2C2C` / `#3a3a3a` 冷墨 | `--mf-colors-text` | `#3A332C` | 正文（暖墨，对比度 ≥7:1） |
| `#5A5A5A` 冷灰 | `--mf-colors-text-weak` | `#8A7D70` | 弱字 |
| `#D9D4CC` 冷灰边 | `--mf-colors-border-weak` | `rgba(36,22,16,.10)` | 默认描边 |
| `rgba(196,58,49,.25)` 朱砂投影 | `--mf-shadows-button-primary` | `0 8px 20px rgba(249,115,22,.22)` | 主按钮橙投影 |
| `#c4b5a0` 米黄 dashed | `--mf-colors-border-weak` | `rgba(36,22,16,.10)` | 分隔虚线（去除米黄自配色） |
| `#c43a31`（manifest meta） | — | `#F97316` | `theme_color` + `<meta name="theme-color">` |

### 3.2 旧自定义色系移除（v1.0 体系外色相）

dictionary 自带的"国风米色系"需全部移除（出现频次括号内为 grep 数）：
- `#e8784a` × 6（朱砂橙，已被主橙取代）
- `#d4745c` × 5（同）
- `#b8a58e` × 2（米黄边，已被暖墨边取代）
- `#c4b5a0` × 12（米黄 dashed）
- `#faf6ee` × 4（米白卡面 → 纯白）
- `#fff` / `#FFFFFF` → 走 `--mf-colors-background-surface`

### 3.3 浅米黄 radial-gradient 光斑移除

- `body { background-image: radial-gradient(ellipse at 20% 10%, rgba(180,160,130,0.08)...) }`
- → 改为 `body { background: var(--mf-colors-background); }` 单值纯白

### 3.4 hero 光晕（v1.0 极浅橙光晕）

- 顶部加 `radial-gradient(ellipse at center top, rgba(249,115,22,.025) 0%, transparent 70%)`
- 浏览器实测首屏仍是纯白（v1.0 第 6.2 节三站验证通过）

---

## 4. 字体链改造

### 4.1 楷体/仿宋移除（CLAUDE.md 09-17 错误避坑）

**移除**：`"KaiTi", "楷体", "STKaiti", "FangSong", "仿宋", "STFangsong"` 共 6 段。

理由：
- `"KaiTi", "STKaiti"` 是 iOS/macOS 默认字体，**Windows 上没有 KaiTi 字体会回退**——两端体验不一致
- v1.0 第 4.1 节"字体族"未列楷体/仿宋（仅 Noto Serif SC + Inter）

### 4.2 字体链规范化（v1.0 第 4.1 节）

| 角色 | 字体栈 |
|---|---|
| **body（var(--mf-fonts-sans)）** | `"Inter", "Source Han Sans SC", "PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif` |
| **H1 / 标题（var(--mf-fonts-display)）** | `"Noto Serif SC", "Source Han Serif SC", "Songti SC", "SimSun", serif` |
| **en-title / 装饰（var(--mf-fonts-display-extended)）** | `"Fraunces", "Noto Serif SC", serif` |

**emoji 字体必加**（CLAUDE.md 09-17 错误避坑）：`"Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji"` 三段缺一不可。

### 4.3 Google Fonts link 改造

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Serif+SC:wght@400;700;900&family=Fraunces:ital,wght@1,400;1,500&display=swap" rel="stylesheet">
```

---

## 5. 圆角 / 阴影 / 组件态

### 5.1 圆角（v1.0 第 5.2 节）

| 类别 | 老值 | 新值（var） |
|---|---|---|
| 卡面（`.entry-card` / `.hot-section` / `.card`） | 8/12/6px | `var(--mf-radii-card)` = **16px** |
| 按钮（`.btn-primary` / `.hero-btn` / `.subscribe-btn`） | 24/8px | `var(--mf-radii-round)` = **9999px** |
| 搜索框（`.search-wrap input`） | 24px | `var(--mf-radii-round)` = **9999px** |
| 角标 / 序号 | 4px | `var(--mf-radii-small)` = 4px |

### 5.2 主按钮橙投影

- 老：`box-shadow: 0 4px 14px rgba(196,58,49,.25)`
- 新：`box-shadow: var(--mf-shadows-button-primary)` = `0 8px 20px rgba(249,115,22,.22)`
- hover 上移 1px：`transform: translateY(-1px)`

### 5.3 搜索框 focus 态（v1.0 第 7.6 节）

```css
.search-wrap input:focus {
  border-color: var(--mf-colors-border-selected);  /* 橙 */
  box-shadow: 0 0 0 3px rgba(249,115,22,.15);  /* 橙光环 */
}
```

### 5.4 卡片 hover 态（v1.0 第 7.3 节）

```css
.entry-card:hover, .hot-section:hover {
  border-color: var(--mf-colors-border-focused);
  transform: translateY(-2px);
  box-shadow: var(--mf-shadows-float);
}
```

---

## 6. 组件形态（按 v1.0 第 7 章）

### 6.1 Nav（v1.0 第 7.1 节）

```css
.site-header {
  position: sticky; top: 0; z-index: 1000;
  background: rgba(255,255,255,.9);  /* 跟纯白底 */
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--mf-colors-border-weak);
}
.brand {
  font-family: var(--mf-fonts-display);  /* Noto Serif SC */
  font-size: 1.25rem; font-weight: 700;
  color: var(--mf-colors-text-strong);
}
.brand .en {
  font-family: var(--mf-fonts-display-extended);  /* Fraunces */
  font-size: 0.8rem; font-style: italic;
  color: var(--mf-colors-text-accent-mango);  /* 橙 */
}
nav a:hover { color: var(--mf-colors-text-link); }  /* hover 变橙 */
```

### 6.2 Hero（v1.0 第 6.2 节 dictionary 形态）

四段式居中单栏：**eyebrow → h1 → en-title → lead → 搜索框 → CTA**

```css
.hero-eyebrow {  /* MANGOFOLIO · 投资词典 */
  font-size: 0.78rem; font-weight: 500; letter-spacing: 0.3em;
  color: var(--mf-colors-text-link);  /* 橙 */
  text-transform: uppercase;
}
.hero h1 {
  font-family: var(--mf-fonts-display);
  font-size: var(--mf-font-sizes-h1);  /* clamp(2.5rem,6vw,4.5rem) */
  font-weight: 900; line-height: 1.3; letter-spacing: 0.02em;
  color: var(--mf-colors-text-strong);  /* 深墨 */
}
.en-title {  /* Invest Dictionary */
  font-family: var(--mf-fonts-display-extended);  /* Fraunces */
  font-size: 1.1rem; font-style: italic; letter-spacing: 0.15em;
  color: var(--mf-colors-text-accent-mango);  /* 橙 */
}
```

### 6.3 Hot-section（v1.0 第 7.5 节）

```css
.hot-section {  /* 白卡 16px 圆角 + dashed 左分栏 */
  background: var(--mf-colors-background-surface);
  border: 1px solid var(--mf-colors-border-weak);
  border-radius: var(--mf-radii-card);
  box-shadow: var(--mf-shadows-card);
}
.hot-item {  /* 高 74px 自动轮播 + dashed 分隔 */
  border-bottom: 1px dashed var(--mf-colors-border-weak);
}
.hot-badge {  /* 橙底白字小胶囊 */
  background: var(--mf-colors-background-primary);
  color: var(--mf-colors-text-on-primary);
  border-radius: var(--mf-radii-round);
  font-size: 0.7rem; padding: 2px 8px;
}
```

### 6.4 Footer（v1.0 第 7.7 节 dictionary 专属）

深墨底 + 暖灰字 + 生态三卡 + 色板 swatches：

```css
.site-footer {
  background: var(--mf-colors-background-abyss);  /* #241610 深墨 */
  color: var(--mf-colors-text-inverse);  /* 暖灰 #B3A596 */
  padding: clamp(40px,8vh,72px) 0;
}
.eco-eyebrow {
  font-size: 0.75rem; letter-spacing: 0.3em;
  color: var(--mf-colors-text-accent-mango);
  text-transform: uppercase;
}
.eco-card {
  background: rgba(255,255,255,.06);  /* 半透白卡 */
  border: 1px solid rgba(255,255,255,.10);
  border-radius: var(--mf-radii-card);
}
.eco-card .eco-icon {
  background: var(--mf-colors-background-primary);
  color: var(--mf-colors-text-on-primary);
  border-radius: var(--mf-radii-round);
}
.brand-swatches span[data-color] { /* 5 色板：mango #F97316 / abyss #241610 / white #FFFFFF / up #B8221E / down #11693D */ }
```

---

## 7. cron 同步策略（防老模板回流）

### 7.1 改造 `term-page-regular.html`（cron 主引用）

- `batch_fill_1000.py:31` 引用 `templates/term-page-regular.html`
- 模板 head 加 token link + Google Fonts link
- `:root` 改 `var(--mf-*)`
- `<style>` 块整套清理老色系（朱砂红/宣纸/米黄/楷体）
- `<meta name="theme-color">` 改 `#F97316`

### 7.2 改造 `term-page.html`（hot-word 历史模板）

虽然 cron 当前不引用，但保留作为热词词条派生模板（生态贡献者可能复用）。同步改造。

### 7.3 sed 批量替换 446 个 terms 页

**关键原则**（BRAND_AUDIT 第七节）：**先抽样 1 个**确认无副作用再全量。

```powershell
# 抽样（先验证）
$samples = Get-ChildItem web/terms/ | Select-Object -First 1
foreach ($f in $samples) {
  $content = Get-Content $f.FullName -Raw
  # 干替换预览（先 echo diff 再 -inplace）
}

# 全量替换（PowerShell，多模式替换）
$patterns = @{
  '#C43A31' = '#F97316'
  '#c43a31' = '#F97316'
  '#A33028' = '#E05E0A'
  '#a92e26' = '#E05E0A'
  '#F5F2EC' = '#FFFFFF'
  '#f5efe0' = '#FFFFFF'
  '#faf6ee' = '#FFFFFF'
  '#2C2C2C' = '#3A332C'
  '#3a3a3a' = '#3A332C'
  '#5A5A5A' = '#8A7D70'
  '#5a4a3a' = '#8A7D70'
  '#D9D4CC' = '#24161014'  # 占位，实际改为 var 引用更复杂
  '#c4b5a0' = ''  # 删 dashed 米黄边
  '"KaiTi"' = ''  # 删楷体
  '"STKaiti"' = ''
  '"FangSong"' = ''
  '"STFangsong"' = ''
  '"楷体"' = ''
  '"仿宋"' = ''
}
# 注意：仅替换 CSS / font-family 中的色值；正文 / og:url / canonical / "朱砂红"字面词保留
```

### 7.4 验证 cron 产物

```bash
# 用 --batch-size 2 生成 2 条验证
python scripts/batch_fill_1000.py --batch-size 2 --skip-sync

# 检查生成的 HTML
grep -l "#C43A31\|#f5efe0\|KaiTi" web/terms/新词条*.html
# 期望：0 处命中
```

---

## 8. 暗色模式（第三波）

`mangofolio-tokens-v09.css` 已自带 `[data-color-mode="dark"]` 双值覆盖，引入后**零成本继承**。

可选增强（按需）：
- 顶部 nav 加切换按钮（参考 iAsk 形态）
- 写入 localStorage 持久化

---

## 9. 验收清单（v1.0 第 10 章 + 自定义项）

### 9.1 品牌红线（必过）

- [ ] 主色芒果橙 `#F97316` 未变
- [ ] 朱砂红 `#C43A31` **全站 0 处**（`grep -r '#C43A31\|#c43a31' web/` = 0）
- [ ] 橙色占比 ≤5%（视觉验证）
- [ ] hero 首屏背景 `#FFFFFF` 纯白，不发橙（浏览器像素采样）

### 9.2 链接令牌化

- [ ] `var(--mf-colors-*)` 引用，无硬编码色值（除必要的字体链 raw 值）
- [ ] 已 link `mangofolio-tokens-v09.css`，无内联令牌子集

### 9.3 对比度达标

- [ ] 正文 `#3A332C` on `#FFFFFF` ≥ 7:1（达标）
- [ ] 主按钮白字 on 橙 `#F97316` ≥ 3:1（达标）
- [ ] 弱文字 `#8A7D70` 仅用于辅助信息，不做正文

### 9.4 字体链

- [ ] 含 `"Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji"` 三段（避 CLAUDE.md 09-17 错误）
- [ ] 不含 `"KaiTi", "STKaiti", "FangSong", "STFangsong"` 四段楷体仿宋
- [ ] en-title 走 Fraunces italic 橙（v1.0 第 7.1 节）

### 9.5 组件态

- [ ] 卡面 16px 圆角 + 暖墨边
- [ ] 主按钮 9999px 胶囊 + 橙投影
- [ ] 搜索框 9999px 胶囊 + focus 橙边 + 3px 橙光环

### 9.6 批量改造 + cron 验证

- [ ] 446 个 terms sed 替换 0 残留
- [ ] cron 生成 1-2 条新词条验证无朱砂红
- [ ] `manifest.json` `theme_color: #F97316`
- [ ] `<meta name="theme-color">` 全站 `#F97316`

### 9.7 提交前自查 4 问（AGENTS.md）

- [ ] commit message 写明 `dictionary: brand align v1.0 wave 1/2/3`
- [ ] PROGRESS.md 追加 2026-09-19 段
- [ ] docs/HANDOFF.md 同步"首页对齐完成 + 下一窗口首要任务"
- [ ] docs/PITFALLS.md 追加 sed 替换 / cron 验证坑点

---

## 10. 风险与注意

1. **sed 替换前必抽 1 页验证**——避免把 og:url / canonical / "朱砂红"字面词误改
2. **词条正文保留**——正文出现"朱砂红""宣纸"字面词不替换（只换 CSS 色值）
3. **`/terms/` 详情页 `theme-color`** 也必须改
4. **knowledge-card.js 已 v3**——不动（自带 CSS 不受页面 token 影响）
5. **Google Fonts 链接**——首次访问会慢，可加 `preconnect` 优化
6. **第一波 vs 第二波节奏**——若第二波工作量过大（footer 重做 ~2h），可拆为第二波 a（圆角+字体）和第二波 b（footer）

---

## 11. 不做（避免过度设计）

- 词条页 .card 区块结构重做（保留故事卡结构 + 章节序号，仅替换色/字体）
- 涨红 `#B8221E` / 跌绿 `#11693D` 立即沉淀（第三波按需）
- 间距 4px 刻度变量化（em/rem 混用影响小，留待 token 完整迁移时统一）
- 引入 JS 暗色模式切换按钮（v1.0 第 8 节只是规范，落地可后续）

---

## 12. 参考

- `D:\claudework\OPC OS\10-about-me\brand-standards\Mangofolio-设计规范-v1.0.md`（权威）
- `D:\claudework\OPC OS\10-about-me\brand-standards\mangofolio-tokens-v09.css`（523 变量源）
- `D:\claudework\invest-dictionary\docs\BRAND_AUDIT_2026-09-19.md`（现状审计）
- `D:\claudework\invest-dictionary\docs\specs\2026-09-19-knowledge-card-v3-design.md`（v3 改造参考）
- `D:\claudework\invest-iAskbetter\docs\DESIGN.md`（iAsk 实施层框架）
- `D:\claudework\invest-dictionary\docs\superpowers\plans\2026-09-19-knowledge-card-v3.md`（plan 模板）