---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 1c835e55ba3b06878e6538b2edadf703_597daf73b65211f1bcef52540024e231
    ReservedCode1: hehuwTFhHcXg8Ymm4Sp9mV7MGAfl2mEPKtjSLYHi0/ecWvOAG5q6TXKHgJLc9IgUDInDccpD83fPhDB7Uf64JcN5HuM2R5wLrHvLDs+7G1GNY+meTjWyI2/jV7lEkF8NpoyerZ3NQz0Sz/7SImqWv8oMW+Fq/bEN2y3jO1uBRIOGGQ7I+ELUFfQ8vNI=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 1c835e55ba3b06878e6538b2edadf703_597daf73b65211f1bcef52540024e231
    ReservedCode2: hehuwTFhHcXg8Ymm4Sp9mV7MGAfl2mEPKtjSLYHi0/ecWvOAG5q6TXKHgJLc9IgUDInDccpD83fPhDB7Uf64JcN5HuM2R5wLrHvLDs+7G1GNY+meTjWyI2/jV7lEkF8NpoyerZ3NQz0Sz/7SImqWv8oMW+Fq/bEN2y3jO1uBRIOGGQ7I+ELUFfQ8vNI=
---

# Mangofolio 设计令牌速查（invest-dictionary）

> **权威源**：`web/css/mangofolio-tokens-v09.css`（文件名 v09，内部版本注释为 v0.6 系列，实测值以该 CSS 为准）
> 本文是**速查 + 使用规范**，任何数值冲突以 CSS 源文件为准。
> 最后整理：2026-09-22

---

## 1. 品牌基调（先记这 5 条）

| 项 | 取值 | 说明 |
|---|---|---|
| 品牌主色（电压色） | `#F97316` 芒果橙 | **只用于 CTA / 链接 / 图标 / 焦点 / Logo，整页占比 ≤5%**，不铺底 |
| 深档 | `#E05E0A` | 按压 / hover / 深铺底 / 强调文字 |
| 页面主底 | `#FFFFFF` 纯白 | v1.0 起取代旧宣纸底 `#F7F5F2` |
| 正文墨 | `#3A332C`，强强调 `#241610` | 对比度 ≥7:1 |
| 禁用色 | `#C43A31` 朱砂红 | **一票否决，任何页面/图文不得出现** |

涨跌语义色与品牌色严格区分：涨红 `#B8221E`、跌绿 `#11693D`，仅用于行情涨跌语义。

---

## 2. 色彩

### 2.1 背景组（Background）

| 令牌 | 值 | 用途 |
|---|---|---|
| `--mf-colors-background` | `#FFFFFF` | 页面主底（v1.0 改纯白） |
| `--mf-colors-background-surface` | `#FFFFFF` | 卡片面 |
| `--mf-colors-background-surface-hover` | `#FFF3EA` | 卡片 hover 浅橙 |
| `--mf-colors-background-neutral` | `#F7F5F2` | **中性弱底，仅局部分区，不作页面默认底** |
| `--mf-colors-background-primary` | `#F97316` | 主 CTA |
| `--mf-colors-background-primary-hover` | `#E05E0A` | 主 CTA hover |
| `--mf-colors-background-overlay` | `rgba(36,22,16,.72)` | 遮罩 |
| `--mf-colors-background-success` | `rgba(17,105,61,.10)` | 成功/跌浅底 |
| `--mf-colors-background-critical` | `rgba(184,34,30,.08)` | 危险/涨浅底 |
| `--mf-colors-background-warning` | `rgba(249,115,22,.10)` | 警示浅底 |

### 2.2 文字组（Text）

| 令牌 | 值 | 用途 |
|---|---|---|
| `--mf-colors-text` | `#3A332C` | 正文 |
| `--mf-colors-text-strong` | `#241610` | 标题 / 强强调 |
| `--mf-colors-text-weak` | `#8A7D70` | 次级文字、占位、禁用 |
| `--mf-colors-text-inverse` | `#FFFFFF` | 深底浅字 |
| `--mf-colors-text-on-primary` | `#FFFFFF` | 主色上的文字 |
| `--mf-colors-text-link` | `#F97316` | 链接（← 首页 `--accent` 即取此值） |
| `--mf-colors-text-link-hover` | `#E05E0A` | 链接 hover |
| `--mf-colors-text-accent-mango` | `#E05E0A` | eyebrow / 眉题橙 |
| `--mf-colors-text-accent-caramel` | `#241610` | 眉题 / 标签 |
| `--mf-colors-text-accent-indigo` | `#8A7D70` | 冷锚点（hero en-title） |
| `--mf-colors-text-critical` | `#B8221E` | 涨 / 错误 |
| `--mf-colors-text-success` | `#11693D` | 跌 / 成功 |

### 2.3 描边组（Border）

| 令牌 | 值 | 用途 |
|---|---|---|
| `--mf-colors-border` | `rgba(36,22,16,.10)` | 默认描边 |
| `--mf-colors-border-weak` | `rgba(36,22,16,.10)` | 弱描边（页脚分隔线等） |
| `--mf-colors-border-strong` | `#8A7D70` | 强描边（次按钮） |
| `--mf-colors-border-focused` | `#F97316` | 聚焦态 |
| `--mf-colors-border-critical` | `#B8221E` | 危险态 |

### 2.4 图表组（dataviz，节选）

`--mf-colors-dataviz-dict-1/2/3` = `#3A332C` / `#F97316` / `#FFF3EA`；涨 `#B8221E`、跌 `#11693D` 各 3 档；网格 `rgba(36,22,16,.08)`。

### 2.5 橙阶速记

`050 #FFF3EA`（最浅橙底）→ `600 #F97316`（PRIMARY）→ `700/800 #E05E0A`（按压/深档）。浅档用于底/标签/分区，中档 CTA，深档 hover 与强调文字。

---

## 3. 排版（Typography）

| 令牌 | 值 |
|---|---|
| `--mf-fonts-sans` | `"Inter", "Noto Serif SC", "Source Han Serif SC", "PingFang SC", "Microsoft YaHei", … , "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif`（**必须含 emoji 段**） |
| `--mf-fonts-ui` | `"Inter", "PingFang SC", "Microsoft YaHei", …`（导航 / 面包屑 / 按钮小栈） |
| `--mf-fonts-display` | `"Noto Serif SC", "Source Han Serif SC", "Songti SC", "SimSun", serif`（衬线标题） |
| `--mf-fonts-display-extended` | `"Fraunces", "Noto Serif SC", serif`（英文标题） |
| `--mf-fonts-mono` | `"Inter", "SF Mono", "Cascadia Mono", Consolas, monospace` |

字号：`25 12px / 30 13px(眉题) / 50 14px / 100 16px(正文) / 200 18px / 300 24px / 400 32px / 500 48px / title1 72px(首页 hero)`；`h1 clamp(2.5rem,6vw,4.5rem)`、`lead clamp(1rem,2vw,1.15rem)`、`eyebrow 0.78rem`。

字重：`light 300 / regular 400 / medium 500 / semibold 600 / bold 700 / black 900`（标题用 black 900）。
字距：`normal 0 / wide 0.08em / loose 0.28em / eyebrow 0.3em`；正文行高 `1.6`，lead `1.9`。

---

## 4. 间距 / 尺寸 / 圆角 / 阴影

- **间距**（4px 基）：`25 2 / 50 4 / 100 8 / 150 12 / 200 16 / 300 24 / 400 32 / 500 40 / 600 48 / 800 64`；容器内边距 `container-padding 28.8px`（移动端 16px）。
- **断点**：`sm 500 / md 700 / lg 964 / xl 1224`；容器最大宽 `1200px`，页面最大宽 `1440px`。
- **圆角**：`small 4 / medium 6 / large 8 / card 16（纸感卡）/ round 9999（胶囊）`。按钮一律胶囊，卡片 16px。
- **阴影**（墨色系）：`sm 1px 2px 4px rgba(36,22,16,.08)`；`default 0 1px 3px + 0 4px 12px`；`card 0 4px 8px + 0 12px 32px`；主按钮 `0 8px 20px rgba(249,115,22,.22)`。
- **z-index**：`nav 99 / overlay 100 / modal 200 / select 500`。
- **动效**：`fast 150ms ease-out / normal 250ms ease-out / duration 0.2s`。
- **渐变**：`mango linear-gradient(180deg,#F97316,#E05E0A 50%)`；hero 光晕 `radial-gradient(ellipse at center, rgba(249,115,22,.07), transparent 70%)`。

---

## 5. 组件令牌（Component Tokens）

| 组件 | 令牌 → 引用 |
|---|---|
| 主按钮 | `--mf-component-button-primary-bg` → `#F97316`；文字 `#FFFFFF`；圆角 round；投影 `--mf-shadows-button-primary` |
| 次按钮 | `--mf-component-button-secondary-bg` → `#FFFFFF`；文字 `--mf-colors-text`；描边 `--mf-colors-border-strong` |
| 输入框 | bg `#FFFFFF`；border `--mf-colors-border-input`；聚焦 `#F97316`；圆角 round |
| 卡片 | bg `#FFFFFF`；border `rgba(36,22,16,.10)`；radius `16px`；shadow `--mf-shadows-card` |
| 徽标（涨/跌） | 涨：底 `rgba(184,34,30,.08)` + 字 `#B8221E`；跌：底 `rgba(17,105,61,.10)` + 字 `#11693D` |
| 导航 | bg 纯白；毛玻璃 `rgba(255,255,255,.9)` + blur `12px`；描边 `1px solid rgba(36,22,16,.10)`；激活文字 `#241610`；指示条 `#F97316` |
| 模态遮罩 | `rgba(36,22,16,.72)` |
| Tooltip | 底 `#3A332C`；字 `#FFFFFF` |

---

## 6. Hero 区块令牌

`--mf-hero-eyebrow-color → #E05E0A`（电压橙）｜`--mf-hero-h1-font → --mf-fonts-display`，weight `900`｜`--mf-hero-en-title-color → #8A7D70`（冷锚点）｜`--mf-hero-lead-color → #8A7D70`｜`--mf-hero-cta-gap 16px`｜`--mf-hero-padding-block clamp(72px,14vh,120px)`｜光晕 `--mf-hero-glow`。

---

## 7. 暗色模式

`<html data-color-mode="dark">` 触发 `[data-color-mode="dark"]` 覆盖：底 `#171310`、卡面 `#1C1814`、正文 `#F2EDE7`、次级 `#B3A596`、主色仍 `#F97316`（其上文字改深墨 `#241610`）、描边改 `rgba(255,255,255,.10)`、毛玻璃 `rgba(23,19,16,.85)`。

---

## 8. 落地对象与例外

| 对象 | 状态 |
|---|---|
| `skill/invest-dictionary-generator/templates/term-page.html`、`term-page-regular.html` | 已按本规范重做（Wave2） |
| `web/index.html` + `web/terms/*.html`（存量 453 页） | 已刷 token（2026-09-21 全量） |
| cron 入口（`11_1_0.yaml` / `12_1_0.yaml` 的 prompt + `SKILL.md`） | 已写【品牌视觉基准】+【产出前自检清单】，新产出自动对齐 |
| **抖音图文线** `D:\ANT\agents\marvis\08-每日热词图文\main.py` | **例外（2026-09-22 决策）**：保留暖灰宣纸渐变底 `#F7F5F2→#EFEAE2`，不随本规范变更 |

---

## 9. 落地自检清单（含踩坑）

1. 新页面必须 `<link>` 引入 `mangofolio-tokens-v09.css`，且**不在页内重复定义**令牌值。
2. 引用任何 `var(--xxx)` 前，确认该变量在本页 `:root` 或 token CSS 中**确有定义**——首页曾因 `:root` 缺 `--accent` 导致 hero 主按钮白字落白底、彻底隐形（2026-09-21 修复）。
3. 禁止裸写 hex 色值、禁止 `font-family: Georgia/serif` 之类硬编码字体栈，一律走令牌。
4. 虚线分隔改实线；圆角一律用 `--mf-radii-*`（卡片 16px、按钮胶囊）。
5. 字体链必须保留 emoji 段（`"Segoe UI Emoji"` 等），否则表情与符号降级。
6. 橙色的量：整页占比 ≤5%，宁可少不可多；深档 `#E05E0A` 用于文字与按压。
7. 朱砂红 `#C43A31` 出现即判不合格。
*（内容由AI生成，仅供参考）*
