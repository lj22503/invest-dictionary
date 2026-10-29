# 投资词典 · 网站优化审计报告

> 审计日期：2026-10-29
> 审计对象：`D:\claudework\invest-dictionary\web`
> 品牌基线：`D:\claudework\OPC OS\22-content\0913-品牌模板规范-v0.1.md` + `css/mangofolio-tokens-v09.css`

---

## 0. 一句话结论

**内容资产（934 个词条页、Schema 结构化数据、SEO meta）做得相当扎实，但"承载层"塌了**：首页 627KB 里塞了 378KB 的内联数据，同一份数据又通过 `dictionary.json` 二次下载 507KB；品牌令牌里写着"对比度 ≥7:1"的橙色，实测只有 **2.80:1**——主 CTA 按钮达不到 WCAG 最低标准。

**先修性能与对比度，再谈视觉美化。** 前者决定有没有人看到，后者决定看的人信不信。

---

## 1. 问题总览（按优先级）

| 级别 | 问题 | 影响 | 修复成本 |
|---|---|---|---|
| **P0** | 首页内联 378KB 词条数据 + 再 fetch 507KB JSON，双重下载 | 首屏 ~1.1MB，LCP 灾难 | 低 |
| **P0** | `xhr.open(..., false)` 同步 XHR 兜底 | 主线程硬阻塞 | 极低 |
| **P0** | Google Fonts 直连（Inter+Noto Serif SC+Fraunces） | 国内不可达/超时，字体兜底失效，CLS 抖动 | 中 |
| **P0** | 橙色 `#F97316` 对比度 2.80:1 | 主 CTA、全部链接不达标 | 低 |
| **P1** | 486 个 `.bak` 备份文件（14MB）随站部署 | 可被抓取、污染 sitemap、泄露迭代痕迹 | 极低 |
| **P1** | 卡片网格高度不齐，CTA 不对齐 | 视觉粗糙感的主因 | 中 |
| **P1** | 场景卡内嵌预览图文字过小不可读 | 缩略图变噪点，反效果 | 中 |
| **P2** | 弱灰 `#8A7D70` 正文 4.00:1 | 正文/描述可读性不足 | 低 |
| **P2** | 移动端导航、标签点击区 <44px | 触控误点 | 中 |
| **P2** | 副标题 en-title 用灰色，违反品牌规范（应为橙） | 品牌一致性 | 极低 |
| **P3** | `site.css` 存在 6 处硬编码色值 | 违反品牌一票否决 | 低 |

---

## 2. P0 致命问题：性能

### 2.1 首页双重数据下载

实测 `web/index.html` 结构：

| 组成 | 体积 |
|---|---|
| 可见 HTML 标记 | 13.8 KB |
| 内联 `<style>` | 17.2 KB |
| **内联 `<script>`（含 `var ALL_ENTRIES`）** | **378.4 KB** |
| 文件总计 | **627 KB** |

而页面运行时**又去 fetch 了 `dictionary.json`（507 KB）**：

```js
fetch('dictionary.json')
  .then(r => r.json())
  .then(d => __entriesDone(d))
```

也就是说：**同一份 934 条词条数据，先以 378KB 内联进 HTML 阻塞解析，再以 507KB 异步下载一遍，合计 ~885KB**。内联的那份只作为兜底存在，却付出了阻塞首屏的代价。

首屏真实负载 ≈ **627KB(HTML) + 49KB(CSS) + 507KB(JSON) ≈ 1.18MB**，还不含字体。

**⚠️ 删除前必读：这不是一次单行删除**

内联 `ALL_ENTRIES` 被三处依赖，直接删会**打断日常热词入库流程**：

| 依赖方 | 删了会怎样 |
|---|---|
| `scripts/sync_all_entries.py` | 找不到数组 → `sys.exit(1)` |
| `scripts/check-consistency.py` 第 6 项 | 直接 FAIL → **阻断提交** |
| `scripts/batch_fill_1000.py` | 每批结束自动调同步，连带失败 |

**但数据本身可以放心删**（2026-10-29 实测）：
- `dictionary.json` 已 100% 覆盖全部展示字段（`card_titles`/`related`/`next`/`chapter`/`title`/`slug`）
- 逐条比对 934 条：内联副本与 `dictionary.json` 的 slug/title **差异 0 条** —— 内联副本是纯冗余，不含任何独有数据

**结论：删库有益无害，但必须连同脚本一起改。** 详见 §9。

**修复方向**
- 删掉内联 `ALL_ENTRIES`，只保留 `fetch('dictionary.json')` 一条路径（首页搜索本就不需要首屏直出全部词条），同步改上面三个脚本。
- 或反过来：只留内联，删掉 fetch。二者留一。
- 若搜索需要首屏可用，把 JSON 拆成「搜索索引（title+slug，约 60KB）」+「完整数据按需加载」。
- 无论哪种，`dictionary.json` 应加 `Cache-Control: immutable` 长缓存。

### 2.2 同步 XHR 阻塞主线程

```js
var xhr = new XMLHttpRequest();
xhr.open('GET', 'dictionary.json', false);   // ← false = 同步
xhr.send(null);
```

第三个参数 `false` 表示同步请求。一旦 `fetch` 失败（网络抖动、离线），这条兜底会**冻结整个页面**直到请求结束。这是已被废弃的 API 用法。

**修复**：直接删掉这个 catch 里的同步兜底，改为显示"词库加载失败"提示 + 保留内联兜底（或反之）。

### 2.3 Google Fonts 对国内用户不可靠

三个页面入口都直连：

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700
  &family=Noto+Serif+SC:wght@400;700;900
  &family=Fraunces:ital,wght@1,400;1,500&display=swap" rel="stylesheet">
```

问题：
- `fonts.googleapis.com` / `fonts.gstatic.com` 在国内经常不可达或 500ms–2s 延迟，934 个词条页**每一页**都在等这个请求。
- `Noto Serif SC` 三个字重（400/700/900）是完整中文字体，体积以 MB 计。
- 全站**没有任何 `rel="preload"`**，只有 `preconnect`，字体无法提前介入。

**修复方向（推荐顺序）**
1. **自托管 + 子集化**（最优）：用 `font-spider`（字蛛）/ `fonttools` / `cn-fontsub` 扫描站点实际用字，产出 woff2 子集，通常能压到原体积 10–20%。存到 Vercel 静态目录或国内 CDN。
2. **系统字体栈兜底**：`font-family: 'PingFang SC', 'HarmonyOS Sans SC', 'Microsoft YaHei', sans-serif`，保证字体加载失败时依然体面。
3. 若保留 Google Fonts，至少加 `preload` 并接受国内降级。
4. Fraunces 仅用于 en-title 装饰，可只加载 italic 400，或直接用 Georgia italic 本地替代（品牌规范 §2.4.2 本就认可"本地以 Georgia italic 替代"）。

---

## 3. P0 致命问题：品牌规范自相矛盾（对比度）

令牌文件 `css/mangofolio-tokens-v09.css` 里这样写：

```css
--mf-colors-text-link: #F97316;      /* 链接（橙电压色深档，对比度 ≥7:1） */
```

**实测不成立。** WCAG 2.1 相对亮度实测结果：

| 组合 | 实测对比度 | AA 正文(4.5) | AA 大字(3.0) | AAA(7.0) | 令牌声称 |
|---|---|---|---|---|---|
| 正文 `#3A332C` / 白 | 12.43 | ✅ | ✅ | ✅ | ≥7:1 ✅ 属实 |
| 正文 `#3A332C` / 暖灰 `#F7F5F2` | 11.42 | ✅ | ✅ | ✅ | ✅ 属实 |
| 弱灰 `#8A7D70` / 白 | **4.00** | ❌ | ✅ | ❌ | — |
| 弱灰 `#8A7D70` / 暖灰 | **3.68** | ❌ | ❌ | ❌ | — |
| **链接橙 `#F97316` / 白** | **2.80** | ❌ | ❌ | ❌ | 声称 ≥7:1，**严重不符** |
| **链接橙 `#F97316` / 暖灰** | **2.58** | ❌ | ❌ | ❌ | 同上 |
| **白字 / 橙底 `#F97316`（主 CTA）** | **2.80** | ❌ | ❌ | ❌ | 主按钮不达标 |
| 深橙 `#E05E0A` / 白 | 3.64 | ❌ | ✅ | ❌ | — |

这意味着：**站内每一个橙色链接、每一个橙色主按钮，都不满足 WCAG AA**。这是无障碍硬伤，也是 SEO 的负面信号。

### 建议替换值（已实测并修正）

> ⚠️ **本节曾给出错误建议**：初版推荐 `#C2410C`，理由是"白底 5.18:1 达标"。数字没错，但**色相错了**——
> `#F97316` 色相 24.6°（橙），`#C2410C` 色相 17.5°（铁锈红）。压暗时把色相一起拽低了，橙色变红色，品牌丢了。
> **正确做法是只降明度、锁死色相**，或换文字色。下方为修正后方案。

| 用途 | 现值 | 改值 | 色相 | 对比度 | 达标 |
|---|---|---|---|---|---|
| **主按钮底色**（配深墨字） | `#F97316` | **`#F97316` 不变** | 24.6° 橙 | 5.46（配 `#2A2420`） | AA ✅ |
| 主按钮 hover / active | — | `#FB8B3D` / `#F08018` | 24.6 / 24.9° | 6.46 / 5.31 | AA ✅ |
| 链接 / 小字强调 | `#F97316` | **`#B45309`** | 26.0° 琥珀橙 | 5.02 白底 / 4.61 暖灰 | AA ✅ |
| 链接 hover / active | — | `#A9500B` / `#8F4A12` | 26.2 / 26.9° | 5.47 / 6.65 | AA ✅ |
| 纯装饰（渐变/插画/角标） | — | `#F97316` | 24.6° | 不受对比度约束 | — |
| 次级文字 | `#8A7D70` | **`#6E6357`** | — | 5.86 / 5.38 | AA ✅ |

> **关键原则**：对比度不足时有三条路，优先级从高到低——
> 1. **换文字色**（橙底配深墨字）——品牌色一分不动，最优解；
> 2. **只降明度、锁死色相**（24.6° → 26° 琥珀橙，仍是橙）；
> 3. ❌ **压暗同时移色相**——会变成铁锈红/土黄，等于换了个品牌色。
>
> 本站实测合法色落在 23.6°~26.9°，铁锈红 `#C2410C` 为 17.5°。
> 已写入 `site-audit.py` 的「主色色相漂移」检查自动拦截。

---

## 4. P1 品牌规范违背

### 4.1 备份文件随站部署（486 个 / 14MB）

```
terms/           934 个正式页面 + 467 个 .bak 备份
web 根目录        另有 .bak 文件若干
合计             486 个备份文件，14 MB
```

`terms/货币.html.bak-step3-full-20260921` 这类文件是公开可访问的。风险：被搜索引擎索引成重复内容、暴露迭代历史、白占 14MB 部署体积。

**修复**：`vercel.json` 加 ignore，或直接从部署目录移除（本地 git 仍有历史）。

### 4.2 en-title 颜色违反规范

品牌规范 §2.1 明确：

> en-title | Fraunces italic + 橙 | 跟中文标题下方

实际 `index.html:58`：

```css
.hero__en { color: var(--mf-colors-text-accent-indigo); }   /* 实为 #8A7D70 灰 */
```

副标题 "Invest Dictionary" 是灰色，不是橙色。且该令牌名叫 `indigo` 值却是灰色，命名与实现不符，容易误导后续维护。

### 4.3 硬编码色值（品牌一票否决项）

`css/site.css` 中存在 6 处硬编码：

```
#F2EDE7 ×2   #FFFFFF ×1   #FFF3EA ×1
#F7F5F2 ×1   #EDE9E4 ×1   #B3A596 ×1   #241610 ×1
```

品牌规范 §2.3 一票否决清单含"硬编码色值"。应全部替换为 `--mf-colors-*` 令牌。

好消息：**全站 0 处朱砂红 `#C43A31`** —— 最重要的一条否决项守住了。

---

## 5. P1/P2 视觉与布局（基于 1440px + 390px 实拍）

### 5.1 卡片网格不齐（视觉粗糙感主因）

场景卡网格（7 个场景）存在：
- 各卡标题/描述长度不一 → 卡片高度参差
- 卡内"查看该场景 →"CTA 在行内不对齐，底边参差
- 预览图区域有的贴边、有的留白，节奏不统一

**修复**：
- 网格用 `grid-auto-rows: 1fr` + 卡内 `display:flex; flex-direction:column`，把 CTA 用 `margin-top:auto` 顶到底部，强制对齐。
- 标题用 `clamp()` 或 `-webkit-line-clamp: 2` 限行，描述限 3 行。

### 5.2 内嵌预览图文字不可读

场景卡里放的是 AI 输出截图缩略图（`assets/cases/*.png`），缩到卡片宽度后文字变成不可辨识的噪点纹理，**不仅没传递信息，反而增加视觉噪音**。

**修复**：换成**抽象化示意图**（图标 + 2-3 个示意色块 + 一句关键词），而非真实截图缩小。或改为 hover/focus 时才展开大图。

### 5.3 订阅卡与热词卡高度失衡

"今日热词"两栏：左卡（热词列表）高，右卡（邮箱订阅）矮，底部空出大片白。

**修复**：右卡内容垂直居中，或给右卡补足内容（如"已订阅 XXX 人"、往期热词回顾）。

### 5.4 移动端（390px）

- 顶部导航项 + "随机一词" 按钮点击区偏小，低于 44×44px 触控标准
- 热词标签行（M2 / CPI / M0）挤在一行，有横向溢出风险
- 统计行 "924 词条 · 7 个场景…" 折行后出现孤字
- 卡片间距在窄屏下过紧

**修复**：导航改汉堡菜单或横向滚动；标签行改 `flex-wrap`；统计行改 2×2 网格；卡片 gap 在 <480px 提至 16px。

---

## 6. 对标网站（Benchmark）

按"学什么"分类，不是泛泛看漂亮。

### 6.1 中文投资内容 · 最直接对标

| 站点 | 学什么 |
|---|---|
| **有知有行** youzhiyouxing.cn | **中文投资科普设计天花板**。莫兰迪色系、大留白、圆润卡片；刻意**弱化红绿**避免刺激用户情绪。与你的"暖灰 + 橙电压"调性高度契合，是你最该逐屏对照的对象 |
| **且慢** qieman.com | "四笔钱框架"——用框架替代信息罗列，**减少用户选择成本**。你的 22 篇章 → 7 场景就是这个思路，可学它怎么把框架视觉化 |

### 6.2 词典 / 词条交互范式

| 站点 | 学什么 |
|---|---|
| **剑桥词典** dictionary.cambridge.org | 词典类交互的成熟范式：**渐进式揭露**——核心释义立即可见，例句/词源折叠。你的词条页信息密度高，正需要这个 |
| **MDN Web Docs** developer.mozilla.org | 技术词条页典范：面包屑、侧边导航、上下篇、"本页内容"锚点。你的 934 个词条页可直接抄它的信息架构 |
| **Investopedia** investopedia.com | 全球投资词典标杆：词条内**相关概念互链**密度极高，是 SEO 内链矩阵的教科书 |
| **Gartner Glossary** gartner.com/en/information-technology/glossary | 按**分类维度**组织海量词条（而非纯 A-Z），对应你的 22 篇章结构 |

### 6.3 SaaS  Glossary 视觉参考（现代感）

- nikolaibain.com/examples/glossary —— 收录 Qonto / Clay / Vanta / Intercom / Webflow 等 glossary 页，**专门看人家的卡片网格与搜索交互**
- Uxcel UX Design Glossary（Dribbble 可搜）—— 极简 glossary 视觉
- COMPEON Fintech Glossary（Dribbble）—— 金融科技 glossary 直接参考

### 6.4 中文内容站 / 文档站质感

| 站点 | 学什么 |
|---|---|
| **少数派** sspai.com | 中文长内容排版标杆：行高、段距、中英混排间距 |
| **Linear / Vercel Docs** | 现代文档站的克制感：细边框、微妙阴影、层级分明的灰阶 |
| **Stripe Docs** | 三栏布局 + 上下文联动，适合你词条页改版参考 |

### 6.5 灵感库（找视觉方向）

Mobbin（真实 App 截屏）· Awwwards · Land-book · Godly.website · Dribbble（搜 `glossary` / `fintech`）

---

## 7. 优化工具清单

### 7.1 直接可用（免费，先跑这层）

| 工具 | 用途 | 备注 |
|---|---|---|
| **Lighthouse** | 性能/无障碍/最佳实践/SEO 五维评分 | Chrome DevTools 内置，零成本，先跑它拿基线分 |
| **PageSpeed Insights** | 补充真实用户 CrUX 数据 | 看真实用户而非实验室数据 |
| **WebPageTest** | 瀑布图，定位到底谁在拖慢 | Lighthouse 说慢但说不清原因时用 |
| **axe DevTools** | 无障碍扫描（Chrome 扩展） | 按严重度分级，直接给修复建议 |
| **WAVE** | 无障碍可视化叠加标注 | 缺失 alt、标题层级错乱一目了然 |
| **WebAIM Contrast Checker** | 对比度逐个验证 | 本报告的数据即用此标准算出 |
| **Microsoft Clarity** | 热力图 + 会话录制 | **免费且国内可用**，Hotjar 的平替，优先选它 |

### 7.2 AI 设计评审（补"主观质量"这一环）

Lighthouse 一分都不评视觉层次、排版、CTA 有效性。补位用：
- **SiteCritic** —— 8 个设计维度打分，给出"第 420px 处 CTA 用 #999 灰底白字，滚动时几乎不可见"这种具体到位置+色值的意见
- **Pixelait** —— 视觉/UI 质量评估

### 7.3 设计与工程侧

- **Stark**（Figma 插件）—— 设计阶段就查对比度
- **font-spider / fonttools / cn-fontsub** —— 中文字体子集化（P0 字体问题必备）
- **GTmetrix** —— 长期性能趋势追踪，验证优化是否真的生效

### 7.4 建议的审计顺序

```
1. Lighthouse 拿基线        → 量化现状
2. WebPageTest 查瀑布图      → 定位 627KB/507KB 双重下载
3. axe + WAVE 扫无障碍       → 拿到对比度/标签/层级问题清单
4. 本报告 §3 色板替换         → 修 P0 对比度
5. SiteCritic 评视觉         → 修 §5 布局与层级
6. 上线 Clarity 收一周数据    → 验证真实用户行为
```

---

## 8. 修复路线图

### 第一批（P0，1–2 天，收益最大）

1. 删除 `index.html` 内联 `ALL_ENTRIES`（378KB），保留单一 `fetch` 路径
2. 删除 `xhr.open(..., false)` 同步兜底
3. 令牌色板替换：链接/文字 → `#B45309`（色相 26°）；**按钮底保持 `#F97316` 不变**、文字改深墨 `#2A2420`；`--mf-colors-text-weak` → `#6E6357`（✅ 已按修正方案完成）
4. 字体：自托管 + 子集化，配系统字体栈兜底
5. `vercel.json` 排除 486 个 `.bak` 文件

> 预期：首屏负载 **1.18MB → ~120KB**，对比度全部达标。

### 第二批（P1，2–3 天）

6. 网格 `1fr` + CTA `margin-top:auto` 强制对齐
7. 场景卡预览图改抽象示意图
8. `site.css` 硬编码色值全部令牌化
9. hero en-title 改橙色

### 第三批（P2，2–3 天）

10. 移动端触控区 ≥44px、导航重构、标签 flex-wrap
11. 订阅卡/热词卡高度平衡
12. 上线 Clarity 观察一周

---

---

## 9. 删除内联数据的协调方案（待批准）

删掉内联 `ALL_ENTRIES` 不只是修性能，更是**永久消灭一类反复发作的 bug**。
`docs/PITFALLS.md` 记录该问题已发作 **3 次**：#20（461→472）、#24（461 vs 473，11 个词搜不到）、#26（914 vs 924，10 个词搜不到）。

根因是同一份数据存了两处。删掉一处，这类问题从根上消失。

### 需要同步改动的 4 处

| # | 文件 | 改法 |
|---|---|---|
| 1 | `scripts/sync_all_entries.py` | 退役。或改为 no-op 并打印"已改为运行时 fetch，无需同步" |
| 2 | `scripts/check-consistency.py` 第 6 项 | 改为反向校验：断言 `index.html` **不含** `ALL_ENTRIES` 且**含** `fetch('dictionary.json')` |
| 3 | `scripts/batch_fill_1000.py` | `sync_all_entries()` 调用改为 no-op（保留 `--skip-sync` 参数兼容） |
| 4 | `AGENTS.md` 第 54 行 | 不变式从"三者条数一致"改为"dictionary.json 唯一源，首页运行时拉取" |

### 风险与回滚

- 风险：首页搜索改为依赖 `fetch`，若 JSON 加载失败则搜索不可用
- 缓解：保留失败时的可见错误态，**不要**用 `__entriesDone([])` 清空（原实现的坑，已在本次修复）
- 回滚：脚本退役前 `index.html` 已备份在 `web/temp/`，可整体回退

### ⚠️ 当前门禁状态（2026-10-29 实测）

跑 `python scripts/check-consistency.py` 结果：**PASS 6 / FAIL 4**

```
[FAIL] manifest.json 硬数字与页数一致   found=['924']      ← 应为 934
[FAIL] llms.txt 硬数字与页数一致        found=['924']      ← 应为 934
[FAIL] sitemap 与磁盘页面双向一致       missing=10         ← 10 个新词条未进 sitemap
[FAIL] 首页 ALL_ENTRIES 与 dictionary 同步  924 vs 934     ← 首页搜索漏 10 个词
```

**这 4 项是本次改动前就存在的**，由同一根因（10 个新词条入库后未跑同步）导致 —— 即 PITFALLS #26 再现。
当前状态直接推送会被门禁拦下，且线上首页**搜不到最新的 10 个词条**。

修复命令（文档化的标准动作，会改动 4 个文件，需你确认后执行）：

```bash
python scripts/sync_all_entries.py     # ALL_ENTRIES 924 → 934（自动备份 web/temp/）
python scripts/generate-sitemap.py      # sitemap 补齐 10 页
# 再把 manifest.json / llms.txt 里的 924 改成 934
python scripts/check-consistency.py     # 应为 10/10 PASS
```

---

## 10. 本次新增发现（审计后补充）

| # | 问题 | 级别 | 状态 |
|---|---|---|---|
| 1 | `dictionary.html` 也有同步 XHR 兜底（不只是 index.html） | P0 | ✅ 已修 |
| 2 | `api/send-daily.js` **每日推送邮件**用朱砂红 `#C43A31`（5 处，含主 CTA） | P1 | ✅ 已改：CTA 用 `#F97316` 底 + 深墨字，文字/链接用 `#B45309` |
| 3 | 原失败兜底 `__entriesDone([])` 会**清空**内嵌 924 条，网络失败时搜索直接变空 | P0 | ✅ 已改为保留内嵌词库 |
| 4 | 门禁 4 项 FAIL（10 词条漂移） | P0 | ⬜ 待你确认后跑同步 |

> 第 2 条影响面比想象大：邮件 cron 每天 9:00 发给全部订阅者，等于每天用一票否决色发一次品牌物料。

---

## 附：值得肯定的部分（别改坏了）

- **934 个词条页 100% 带 `DefinedTerm` JSON-LD 结构化数据**，SEO 底子扎实
- **全站 0 处朱砂红** —— 品牌一票否决项守住
- 词条页 canonical / OG / Twitter Card / 面包屑完整
- 每张卡 `loading="lazy"`、有 `skip-link`、有 `aria-label`
- 零依赖零构建，纯静态，工程简洁

问题不在内容，在承载层。**内容是对的，包装拖了后腿。**
