# Mangofolio Skill 包审阅报告

- 审阅对象：`skill/` 下 8 个 Skill
- 审阅目的：上架 WorkBuddy Marketplace / SkillHub，并打通 ima 知识库
- 审阅时间：2026-11-06
- 基线：`skill-creator` 官方规范（frontmatter、渐进披露、资源分层、打包校验）+ 已上架包 `a-share-analysis` 的实际结构

---

## 0. 一句话结论

**方法论质量是本项目最强资产，但"上架就绪度"只有约 55%。**

8 个 Skill 全部通过官方 `quick_validate.py`（name 连字符、description 无尖括号、frontmatter 完整），说明**格式没有硬伤**。真正卡住上架的是四类问题：

| 类别 | 结论 |
| :--- | :--- |
| 包形态 | 现在是 8 个平铺目录，缺 `plugin.json`，WorkBuddy 上架需要 plugin 包 |
| 可移植性 | 2 个 Skill 硬依赖仓库内文件（`web/terms/*.html`、`../../../docs/*`），上架后必然失效 |
| 事实一致性 | 6 个被引用词条在词典里**不存在**；2 处词条数过期（448 / 472 vs 实际 1115） |
| 可发现性 | 5 组触发词互撞（"说人话""提前还贷""增额寿""靠谱吗"），用户同一句话会触发不同 Skill |

---

## 1. 评分卡

维度说明：A 元数据与可发现性 / B 结构与渐进披露 / C 可执行性 / D 事实与内部一致性 / E 可移植性 / F 合规与上架合规。满分 10。

| Skill | A | B | C | D | E | F | 均分 | 定位判断 |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :--- |
| decision-mosaic 决策拆解桌 | 7 | 8 | 9 | 7 | 10 | 9 | **8.3** | 可上架，修元数据即可 |
| duel-compare 二选一擂台 | 7 | 8 | 9 | 7 | 10 | 9 | **8.3** | 可上架，修元数据即可 |
| daily-hotword 每日热词 | 6 | 8 | 7 | 6 | 10 | 8 | **7.5** | 需补"无实时数据"防线 |
| combo-narrative 新闻翻译机 | 6 | 8 | 8 | 6 | 10 | 8 | **7.7** | 需修示例越界 |
| question-probe 防坑提问器 | 7 | 8 | 6 | 7 | 10 | 9 | **7.8** | 第 2 步缺清单，需补内容 |
| symptom-lookup 理财急诊 | 7 | 8 | 8 | 5 | 10 | 7 | **7.5** | 核心词条不存在，须修 |
| generator 词条生成器 | 5 | 6 | 6 | 5 | 4 | 7 | **5.5** | 内部生产工具，建议不上架或重构 |
| concept-combinator 概念串联 | 5 | 3 | 8 | 6 | 3 | 7 | **5.3** | 内容最好但包最重，必须拆分 |

---

## 2. P0 阻断项（不改不能上架）

### P0-1 缺上架包结构

WorkBuddy 上架的实体是 **plugin**，不是裸 skill 目录。已上架包的实际结构：

```
a-share-analysis/
├── .codebuddy-plugin/plugin.json     ← 必需，缺它无法识别为可上架插件
├── skills/<skill-name>/SKILL.md
└── agents/<agent>.md                  ← 可选
```

`plugin.json` 字段（照抄已上架包）：

```json
{
  "name": "mangofolio",
  "version": "1.0.0",
  "description": "...",
  "description_zh": "...",
  "description_en": "...",
  "author": { "name": "Mangofolio" },
  "keywords": ["投资词典", "理财", "金融科普", "说人话", "投资决策"],
  "category": "finance"
}
```

现状：`skill/` 下 8 个目录平铺，无 `plugin.json`、无 README、无 LICENSE。**8 个 skill 应合并为 1 个 plugin**（`mangofolio`），而不是 8 个独立包——它们共用一套方法论和词条底座，拆开上架会互相抢触发。

### P0-2 两个 Skill 硬依赖仓库内文件，上架后必然报错

| 文件:行 | 引用内容 | 上架后的结果 |
| :--- | :--- | :--- |
| `generator/SKILL.md:68` | "必须先 read_text 该基准页 `web/terms/14天期逆回购.html`" | 文件不存在 → AI 读失败 → 要么卡住，要么凭空编样式 |
| `generator/SKILL.md:136` | "数据源：`web/dictionary.json`" | 同上 |
| `concept-combinator/SKILL.md:68,837` | `templates/narrative-page.html` | 相对路径在 plugin 里层级不同，易失效 |
| `concept-combinator/SKILL.md:839-840` | `../../docs/design-tokens.md`、`../../docs/specs/*.txt` | 仓库私有文件，上架包里根本不会带 |
| `concept-combinator/SKILL.md:813` | "放在 `~/.claude/skills/`" | 错误平台路径（WorkBuddy 是 `~/.workbuddy/skills/`） |

**修法**：把基准页/模板转成包内 `assets/`，把路径改成**相对于 skill 目录**的写法，并加一句"若资源缺失，按 SKILL.md 内联规则生成，不要报错中断"。

### P0-3 引用的词典词条有 6 个不存在

用 `web/dictionary.json`（1115 条）逐项比对，Skill 中作为"必看词条"出现的以下名称查不到：

| 缺失词条 | 出现在 | 严重度 |
| :--- | :--- | :--- |
| 浮亏 vs 实亏 | `symptom-lookup:50,115`（是示例 1 的**最该先看**） | 🔴 最高 |
| 净值型理财 | `symptom-lookup:50,118` | 🔴 |
| 赎回踩踏 | `symptom-lookup:50,120` | 🔴 |
| 增额寿 | `symptom-lookup:54`、`decision-mosaic`、`duel-compare` 触发词 | 🟠 |
| 长期资金 | `combo-narrative:110` | 🟠 |

后果：Skill 自己的红线写着"词条必须能在词典里查到"，但示例就在用不存在的词条。上架用户按示例去搜，搜不到 → 直接判定"这 Skill 是编的"。

**修法（二选一，推荐 A）**：
- A. 补词条（`浮亏 vs 实亏`、`净值型理财`、`赎回踩踏` 三个是理财高频词，本就该有）
- B. 换成真实存在的词条（如"浮亏 vs 实亏"→`最大回撤`，但示例说服力会下降）

### P0-4 词条数严重过期

| 位置 | 写的 | 实际 |
| :--- | :--- | :--- |
| `generator:13,136` | 448 个词条 | 1115 |
| `concept-combinator:23` | 472 个词条 | 1115 |

对一个以"词库体量"建立信任的产品，这是硬伤。**注意**：不要写死数字，改成"1000+ 词条（以站点实时数据为准）"，否则每次 cron 新增都要改一遍（这个坑项目里已经踩过）。

### P0-5 触发词互撞（5 组）

| 撞的词 | Skill A | Skill B | 后果 |
| :--- | :--- | :--- | :--- |
| 说人话 | combo-narrative | generator | 太泛，任何"说人话"请求都可能误触发 |
| 提前还房贷 / 提前还贷 | decision-mosaic | duel-compare | 用户问"提前还贷还是买增额寿"→ 两个都命中 |
| 增额寿 | decision-mosaic | duel-compare + question-probe | 三个抢一个词 |
| 靠谱吗 | symptom-lookup | question-probe | 高频口语，必撞 |
| 降准/LPR 什么意思 | daily-hotword | combo-narrative | 单词解释 vs 新闻解读，边界模糊 |

**修法**：每个 Skill 只保留 **2-3 个高辨识度触发词**，把区分规则写进 description 的"不适用于"从句（a-share-analysis 已用这个写法：`本技能不适用于：...`），并加一个顶层**路由表**（见 §5）。

---

## 3. P1 重要项（影响体验与可信度）

### P1-1 `question-probe` 第 2 步是空壳

`question-probe:46-48` 写"每类产品有 3-5 个必问问题"，但**没有给出任何清单**，第 3 步直接进入"翻译成用户能说出口的话"。AI 每次都要自创，输出质量随机。

对比：`decision-mosaic` 有 12 类场景库，`symptom-lookup` 有 5 类动作→词条簇映射表。`question-probe` 缺的正是这张表。

**修法**：补一张 6 类产品 × 3-5 问的清单（保险/基金/银行理财/债券/权益/说不清），每问标注"为什么问"。

### P1-2 红线与示例自相矛盾

- `combo-narrative:88` 红线"不允许预测涨跌"，但 `:105` 示例写"你的存款利率**大概率也会跟着降**一点"、`:117`"存款利率**大概率**缓慢下行"
- `symptom-lookup:94` 红线"不允许直接给买/不卖结论"，但 `:123` 示例写"**如果是前者，不急着卖**"

这不是文字挑刺——上架审核和用户投诉都会盯这个。**修法**：示例改成条件式表述（"如果 X 成立，卖与不卖的分界在这里"），或把"大概率"改为"历史上常见"。

### P1-3 `daily-hotword` 无实时数据防线

`:20` 要求"按当前日期选取当日市场热议的 1 条代表性话题"，但没有任何"如果拿不到实时信息怎么办"的兜底。上架后 AI 很可能**编造当日热点**（"今日 A 股缩量下跌"——可能是三个月前的行情）。

**修法**：加一条硬规则——「若无法联网获取当日行情，不得编造，反问用户'今天你看到的热点是什么'；示例中的日期与数字必须标注为示例」。

### P1-4 8 个 Skill 都要求"词条必须存在"，但没给查验手段

这是最系统性的缺陷。每个 Skill 都有类似红线：

> ✅ 热词必须是词典里能查到的词条（`daily-hotword:88`）
> ✅ 概念名必须能在投资词典里查到（`combo-narrative:97`）

但包里**没有任何词条索引**，AI 无从查起。上架后（没有仓库、没有 `dictionary.json`）只能凭记忆编，红线形同虚设。

**修法**：plugin 级共享 `references/term-index.json`（1115 条，仅 title + filename，实测 **66 KB**）+ 一行检索说明。所有 Skill 在输出前做一次命中校验。这是投入产出比最高的一项（详见 §6）。

### P1-5 `concept-combinator` 855 行，违反渐进披露

40 KB / 855 行塞在 SKILL.md 里，触发即全量进上下文，而其中 80% 是 S3-S6 四个模板的细节——用户一次只用到一个模板。

**修法**：SKILL.md 压到 ~120 行（保留定位、模板选择表、6 屏结构、通用质量红线、路由），把 S1-S6 拆到 `references/template-s1.md` … `template-s6.md`，按需加载。

### P1-6 包内 7 个 `.bak` 文件（148 KB，占包 35%）

```
templates/term-page.html.bak-20260919-task5
templates/term-page.html.bak-step3-typography-20260920
templates/term-page.html.bak-wave2-20260920
templates/term-page.html.bak_20260823_182703
templates/term-page-regular.html.bak-*  (3 个)
```

上架打包会全部带入，且会干扰 AI 选择"该用哪个模板"。**直接删**（git 里有历史）。

---

## 4. P2 优化项

| # | 问题 | 建议 |
| :--- | :--- | :--- |
| 1 | 8 个 Skill 都缺 `agent_created: true` | 官方规范要求（便于后续 `skill_manage` 修改），补上 |
| 2 | 目录名 `templates/`、`examples/` 不合规范 | 规范是 `assets/`（产物模板）、`references/`（按需加载的文档）；`examples/` 可保留但建议改名 `references/examples/` |
| 3 | 名称前缀 `mangofolio-` 冗长 | plugin 内可保留（品牌一致性），但 display name 建议用中文（"理财急诊"），description 首句给中文品牌名 |
| 4 | 交叉引用名称不一致 | `question-probe:190` 写"决策拼图"、`duel-compare:269` 写"二选一对打"，实际是"决策拆解桌""二选一擂台" |
| 5 | 版本号不统一 | generator 1.1.0，其余 1.0.0；建议 plugin 统一 1.0.0，skill 内部版本独立 |
| 6 | 无 `license` 文件 | frontmatter 有 MIT，包内应放 LICENSE |
| 7 | 无 CHANGELOG | 上架后迭代需要，建议每个 skill 一段简短变更记录 |
| 8 | `concept-combinator` 定位摇摆 | 同时讲"普通人自助"和"投顾生产"，建议二选一为主，另一个作为"进阶用法" |

---

## 5. 建议的上架形态

### 5.1 目标结构

```
mangofolio/                                  ← plugin 根
├── .codebuddy-plugin/
│   └── plugin.json                          ← P0-1
├── README.md                                ← 上架页文案（介绍 + 8 个技能一览）
├── LICENSE
├── skills/
│   ├── mangofolio-symptom-lookup/SKILL.md
│   ├── mangofolio-duel-compare/SKILL.md
│   ├── mangofolio-decision-mosaic/SKILL.md
│   ├── mangofolio-question-probe/SKILL.md
│   ├── mangofolio-combo-narrative/SKILL.md
│   ├── mangofolio-daily-hotword/SKILL.md
│   ├── mangofolio-concept-combinator/
│   │   ├── SKILL.md                         ← 压到 ~120 行
│   │   └── references/template-s1..s6.md    ← 拆分
│   └── mangofolio-generator/
│       ├── SKILL.md
│       └── assets/term-page.html            ← 基准页内置
└── references/
    ├── term-index.json                      ← 1115 条索引，66 KB，8 个 skill 共用
    └── routing.md                            ← 触发词路由表（见 5.2）
```

### 5.2 必须加的路由表

8 个 Skill 的服务对象高度相邻，仅靠 description 竞争会误触发。建议在 plugin 根放 `references/routing.md`，并在每个 SKILL.md 顶部加 3 行"何时用我 / 何时用别人"：

| 用户说什么 | 走哪个 |
| :--- | :--- |
| "我买的理财亏了 / 我妈被推荐了个高息产品" | symptom-lookup |
| "这个产品能买吗 / 我该问销售什么" | question-probe |
| "提前还贷还是买增额寿 / A 还是 B" | duel-compare |
| "我要不要提前还贷 / 该不该存教育金" | decision-mosaic |
| "这段新闻什么意思 / 降准什么意思" | combo-narrative |
| "今天市场在聊什么" | daily-hotword |
| "把这段做成客户能看的网页" | concept-combinator |
| "帮我写一个 XX 词条" | generator |

**边界规则**：`要不要` → 决策拆解；`还是` → 二选一；`亏了/买到坑里` → 急诊；`产品/话术` → 防坑。

### 5.3 上架范围建议

| Skill | 建议 | 理由 |
| :--- | :--- | :--- |
| decision-mosaic / duel-compare / symptom-lookup / question-probe / combo-narrative / daily-hotword | ✅ 首批上架 | 面向终端用户，方法论完整，改造成本低 |
| concept-combinator | ⏸ 二批（拆分后） | 内容最强但包最重，拆 references 后再上 |
| generator | ❌ 不建议上架 | 本质是**仓库内部生产工具**（依赖基准页、dictionary.json、命名规范、贡献流程），对外部用户价值低。若要上架，应重构为"通用词条写作"版，剥离所有仓库约定 |

---

## 6. ima 知识库怎么"用起来"

先说结论：**ima 不能作为唯一数据源，但可以作为"原文取用"层。**

原因：ima MCP 是**用户级连接器**，上架后其他用户不一定装了；把它写成硬依赖会让 Skill 在别人机器上直接失效。

推荐三层结构：

| 层 | 载体 | 作用 | 是否硬依赖 |
| :--- | :--- | :--- | :--- |
| L1 存在性校验 | plugin 内 `references/term-index.json`（66 KB） | 输出前确认"这个词条真的存在"，并拿到 slug/URL | ✅ 硬依赖（随包） |
| L2 原文引用 | 线上 `https://dictionary.mangofolio.com/terms/<slug>` | 需要引用完整定义时抓取 | 🟡 可选（有网即用） |
| L3 语义检索 | ima 知识库「投资词典」 | 用户口语 → 相关词条的语义匹配 | ⚪ 可选增强（检测到 ima 才用） |

落地动作：

1. **建 ima 知识库**「投资词典」，把 `web/terms_md/*.md`（1115 篇）批量导入。当前 ima 里**没有**这个库，只有 `skill`(40)、`research`(484) 等 12 个库。
2. SKILL.md 里写成分级指令：
   > 查询词条时按顺序尝试：① 读 `references/term-index.json` 确认存在；② 若当前环境有 ima 知识库「投资词典」，检索原文并注明"来自投资词典"；③ 都没有时，只输出词条名 + 站点链接，**不得自行编造完整定义**。
3. 这样三个层次都不阻塞主流程，也不会因为某个用户没装 ima 就失败。

---

## 7. 修复路线图

### 批 1（半天，可上架的最小集）

- [ ] 删 7 个 `.bak`（-148 KB）
- [ ] 建 `plugin.json` + README + LICENSE，8 个 skill 收进 `skills/`
- [ ] 全部补 `agent_created: true`
- [ ] 6 个 skill 的 description 收敛：只留 2-3 个高辨识触发词 + "不适用于"从句
- [ ] 修 6 个不存在词条（补词条 or 换词条）
- [ ] 词条数 448/472 → "1000+（以站点实时为准）"
- [ ] 删 `~/.claude/skills/`、`../../docs/*` 等失效路径引用
- [ ] 加 `references/term-index.json` + 各 skill 一句校验指令

### 批 2（1-2 天，质量提升）

- [ ] `question-probe` 补 6 类产品必问清单
- [ ] `concept-combinator` 拆 references，SKILL.md 压到 120 行
- [ ] 修 2 处红线/示例矛盾
- [ ] `daily-hotword` 加"无实时数据"防线
- [ ] `generator` 剥离仓库依赖（或决定不上架）
- [ ] 加 `references/routing.md` 路由表

### 批 3（上架前）

- [ ] 用官方 `package_skill.py` 逐个打包验证
- [ ] 本地安装试跑 8 条真实用户话术，检查触发正确率
- [ ] 建 ima「投资词典」知识库并导词条
- [ ] 提交 Marketplace 审核

---

## 附录 A：本次校验的原始证据

**官方校验（8/8 通过）**

```
mangofolio-combo-narrative       Skill is valid!
mangofolio-concept-combinator    Skill is valid!
mangofolio-daily-hotword         Skill is valid!
mangofolio-decision-mosaic       Skill is valid!
mangofolio-duel-compare          Skill is valid!
mangofolio-generator             Skill is valid!
mangofolio-question-probe        Skill is valid!
mangofolio-symptom-lookup        Skill is valid!
```

**规模**

| 指标 | 数值 |
| :--- | :--- |
| 文件数 | 23 |
| 总体积 | 420 KB（其中 .bak 148 KB） |
| SKILL.md 行数区间 | 133（daily-hotword）～ 855（concept-combinator） |
| description 字数区间 | 122 ～ 152 |
| 触发词数量区间 | 5 ～ 6 |

**包内无** `README` / `LICENSE` / `plugin.json`。

**示例 HTML 自包含性**：`examples/q3-2026.html` 与 `templates/term-page.html` 均 **0 处 CDN/字体外链**，只有站内域名与 schema.org 命名空间——这一点做得很好，可作为 assets 直接分发。
