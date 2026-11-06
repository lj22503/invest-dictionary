# Skill 路由表

8 个 Skill 服务对象相邻，单靠 description 竞争容易误触发。按本表判定。

## 按用户意图路由

| 用户说的 | 走 | 不走 |
| :--- | :--- | :--- |
| "我买的理财亏了" / "我妈被推荐了个高息产品" / "听说黄金要涨" | symptom-lookup（理财痛点） | 不要走 question-probe：那是"面对产品该问什么" |
| "这个产品能买吗" / "我该问销售什么" / "保本保息靠谱吗" | question-probe（话术防坑） | 不要走 symptom-lookup：那是"我遇到这事该看什么词" |
| "A 还是 B" / "存定期还是买理财" / "买房还是租房" | duel-compare（产品对比） | 不要走 decision-mosaic：那是单边决策 |
| "我要不要做这件事" / "该不该提前还贷" / "该不该存教育金" | decision-mosaic（财务决策） | 不要走 duel-compare：这里没有对打的 B |
| "这段新闻什么意思" / "降准对我是好是坏" | combo-narrative（新闻拆解） | 不要走 daily-hotword：那是"今天在聊什么" |
| "今天市场在聊什么" / "今天有什么热点" | daily-hotword（热点追踪） | 不要走 combo-narrative：这里没有具体新闻原文 |
| "把这段做成客户能看懂的网页" / "6 屏" | concept-combinator（概念串联） | 不要走 combo-narrative：那是纯文本解读 |
| "帮我写一个 XX 词条" / "解释这个金融概念" | generator（投资翻译） | 不要走 combo-narrative：那是解读已有内容 |

## 三个高频歧义点

**1. "要不要" vs "还是"**
- 句子里只有一件事、缺一个"该不该做"的判断 → decision-mosaic
- 句子里有两个选项在对打 → duel-compare
- 特例：用户说"提前还贷还是买增额寿"，先走 duel-compare（两个选项确实在对打）；如果用户说"我要不要提前还贷"（只问一件事），才走 decision-mosaic

**2. "靠谱吗" 归属**
- "这个东西靠谱吗 / 保本保息可信吗" → question-probe（要问的问题）
- "我买的理财亏了，要不要卖" → symptom-lookup（该看的词条）
- 判定信号：用户手里**有产品名或话术** → question-probe；只有**情绪和现象** → symptom-lookup

**3. "什么意思" 归属**
- 单个词不懂 → 查词库（不启动 Skill），或用 generator 写词条
- 一段新闻 / 一句话里多个词不懂 → combo-narrative
- 想知道"今天大家在聊什么" → daily-hotword

## 组合用法

- 先 `symptom-lookup` 找到该懂的概念 → 再 `combo-narrative` 解读相关新闻
- 先 `question-probe` 拿到问题清单 → 问完销售后用 `duel-compare` 比对两个方案
- 先 `decision-mosaic` 拆变量 → 若拆出两个对打选项，切 `duel-compare`
- `combo-narrative` 得出结论 → 需要交付客户时用 `concept-combinator` 做成 6 屏网页
