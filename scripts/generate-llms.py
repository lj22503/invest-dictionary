# -*- coding: utf-8 -*-
"""
generate-llms.py —— 由 dictionary.json 同源生成 web/llms.txt

背景：
  llms.txt 曾是手维护产物。词条从 381 涨到 985 的过程中它停在 924 条，
  且 URL 长期带 .html 后缀。本脚本对齐 generate-sitemap.py 的同源原则：
  唯一数据源 = web/dictionary.json，禁止手改产出物。

规则：
  1. 词条区按 dictionary.json 顺序逐条输出，标题优先用 slug（展示名）
  2. URL 不带 .html（vercel cleanUrls:true 已生效）
  3. 简介优先取 ALL_ENTRIES 的 card_titles[0]（与首页一致），回退到 description
  4. 计数一处不写死，全部由 len(items) 推导

用法：python scripts/generate-llms.py
"""
import os
import re
import json
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DATA = os.path.join(WEB, "dictionary.json")
INDEX = os.path.join(WEB, "index.html")
OUT = os.path.join(WEB, "llms.txt")
BASE = "https://dictionary.mangofolio.com"


def term_url(fn):
    stem = fn[:-5] if fn.endswith(".html") else fn
    return "%s/terms/%s" % (BASE, quote(stem, safe=""))


def load_card_titles():
    """首页 ALL_ENTRIES 的 card_titles[0] 是已校准的展示副标题，优先复用。"""
    html = open(INDEX, encoding="utf-8", errors="replace").read()
    m = re.search(r"var ALL_ENTRIES = (\[.*?\]);", html, re.S)
    if not m:
        return {}
    try:
        arr = json.loads(m.group(1))
    except json.JSONDecodeError:
        return {}
    out = {}
    for e in arr:
        key = e.get("file") or e.get("filename")
        ct = e.get("card_titles") or []
        if key and ct:
            out[key] = ct[0]
    return out


def main():
    items = json.load(open(DATA, encoding="utf-8"))
    cards = load_card_titles()
    n = len(items)
    chapters = []
    seen_ch = set()
    for x in items:
        c = x.get("chapter") or ""
        if c and c not in seen_ch:
            seen_ch.add(c)
            chapters.append(c)

    L = []
    L.append("# 投资词典 Invest Dictionary")
    L.append("")
    L.append("> 投资术语，说人话，不装逼。覆盖货币、股票、基金、债券、保险、房产、宏观、"
             "AI 金融等 %d 个篇章、%d 个词条。" % (len(chapters), n))
    L.append("> 网址：https://dictionary.mangofolio.com")
    L.append("")
    L.append("## 首页")
    L.append("- [投资词典首页](%s/): 全部词条目录与篇章导航" % BASE)
    L.append("")
    L.append("## 词条（共 %d 条）" % n)
    for x in items:
        title = x.get("title") or x.get("slug")
        fn = x.get("filename", "")
        desc = cards.get(fn) or x.get("description") or ""
        L.append("- [%s](%s): %s" % (title, term_url(fn), desc))
    L.append("")
    L.append("## 词库与指南")
    L.append("- [全部词条（词库）](%s/dictionary): %d 个词条按篇章全部列出，"
             "支持搜索与章节筛选" % (BASE, n))
    L.append("- [使用指南（8 个场景）](%s/guide): 8 个场景 × 提示词样例 × 对应 Skill，"
             "照抄就能用" % BASE)
    L.append("- [隐私政策](%s/privacy): 信息收集与使用说明" % BASE)
    L.append("- [用户协议](%s/terms-of-service): 服务边界与不构成投资建议的约定" % BASE)
    L.append("")
    L.append("## 相关站点")
    L.append("- [财务工具箱](https://invest-tools.mangofolio.app): "
             "复利、定投、房贷、个税等免费计算器")
    L.append("")
    L.append("（内容由AI生成，仅供参考）")

    text = "\n".join(L) + "\n"
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    # 回读校验
    back = open(OUT, encoding="utf-8").read()
    cnt = back.count("\n- [")
    total_links = len(re.findall(r"^- \[", back, re.M))
    ok = str(n) in back and back.count(".html") == 0
    print("llms.txt 重建：%d 条词条，章节 %d 个，文案/链接条目 %d 行" % (n, len(chapters), total_links))
    print("  计数已写入源码：%s" % ("OK" if str(n) in back else "FAIL"))
    print("  残留 .html：%d -> %s" % (back.count(".html"), "OK" if ok else "FAIL"))
    return 0


if __name__ == "__main__":
    main()
