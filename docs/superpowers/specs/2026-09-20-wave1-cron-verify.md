# Task 8 Wave 1 cron 验证（2026-09-20）

## 验证方式
直接 one-shot 渲染 `skill/invest-dictionary-generator/templates/term-page-regular.html` × 2 个 placeholder 替换（TestTokenW1/W2），写 `web/terms/test-token-w{1,2}.html`。

## 结果（grep = 0 残留）
- 楷体 / 仿宋 / KaiTi / FangSong / STFangsong / STKaiti：0
- 朱砂红 hex + rgba（#C43A31 / rgba(196,58,49,*) / rgba(184,34,30,*)）：0
- 米色 rgba（rgba(180,160,130,*) / rgba(180,155,120,*) / rgba(230,215,190,*) / rgba(220,205,175,*)）：0
- 老国风橙（#e8784a / #d4745c / rgba(232,120,74,*)）：0
- `theme-color` 每页 1 处 = `#F97316` ✅

## 结论
**Task 4 + Task 5 模板已彻底 v1.0 化**，下次 cron 跑出来（新词条）自动符合 v1.0 体系，无需额外 sweep。

## cleanup
测试 HTML / MD / 渲染脚本已删除，不入 commit。

## 为何不走 `batch_fill_1000.py --mode file`
batch_fill 读 V3 清单（`docs/prod_*_扩充词条清单v3_批次N.md.md`），不接受自定义 MD。测试 MD 不在 V3 清单 → 不会被跑。

## 关联
- 模板 commit：Task 4 = `e307f1c` + `c2659c3`，Task 5 = `243a667`
- Sweep commit：Task 6 redo = `d87a66e`，Task 7 redo = `0122524`
- 模板文件：`skill/invest-dictionary-generator/templates/term-page-regular.html` & `term-page.html`（均为 0 残留）
