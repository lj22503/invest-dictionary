# -*- coding: utf-8 -*-
"""
fix-broken-links.py —— 修复 terms 页内的相对链接断链（P0-4 回归）

两类断链，分别处理：
  A. 链接写成了完整 slug，但实际文件名是简称（如 slug「DR利率（银行间质押式回购利率）」
     对应 filename「DR利率.html」）→ 改写为正确的 filename 编码形式。**保留可点击**。
  B. 目标词条尚未创作（磁盘与 dictionary.json 均无）→ 降级为 <span> 纯文本，
     保留词面语义，但不再产生 404（SEO 与体验双输的死链）。

用法：
  python scripts/fix-broken-links.py           # dry-run
  python scripts/fix-broken-links.py --apply   # 落盘
"""
import os
import re
import sys
import html
import json
import collections
from urllib.parse import unquote, quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
TERMS = os.path.join(WEB, "terms")

PENDING_CLASS = "link-pending"


def load_map():
    items = json.load(open(os.path.join(WEB, "dictionary.json"), encoding="utf-8"))
    disk = set(f[:-5] for f in os.listdir(TERMS)
               if f.endswith(".html") and ".bak" not in f)
    # 目标名 -> 实际可用的 filename stem
    resolve = {}
    for x in items:
        fn = x.get("filename", "")
        stem = fn[:-5] if fn.endswith(".html") else fn
        if stem not in disk:
            continue
        resolve[x["slug"]] = stem
        resolve[stem] = stem

    # 简名别名：正文里常把「过度自信（频繁交易）」简写成「过度自信」。
    # 只在「该简名全库唯一」时建立别名，歧义的一律不建——宁可降级为纯文本，也不瞎指。
    base_count = collections.Counter()
    for stem in set(resolve.values()):
        b = stem.split("（")[0].strip()
        if b and b != stem:
            base_count[b] += 1
    alias = {b: s for s in set(resolve.values())
             for b in [s.split("（")[0].strip()]
             if b and b != s and base_count[b] == 1 and b not in resolve}
    resolve.update(alias)
    return disk, resolve


def process(text, disk, resolve, stat):
    """重写页内相对链接。返回新文本。"""
    out = text
    # 处理顺序：先 <a href="X" ...>Y</a> 的一般形式
    pat = re.compile(r'<a\s+href="([^"]+)"([^>]*)>(.*?)</a>', re.S)

    def repl(m):
        raw, attrs, label = m.group(1), m.group(2), m.group(3)
        h = html.unescape(raw)
        if h.startswith(("http", "#", "mailto", "javascript", "/", "..")) or "'" in h:
            return m.group(0)
        tgt = unquote(h.split("#")[0].split("?")[0])
        if not tgt:
            return m.group(0)
        cand = tgt if tgt.endswith(".html") else tgt + ".html"
        if os.path.exists(os.path.join(TERMS, cand)):
            return m.group(0)  # 正常，不动
        # A 类：slug -> filename 可映射
        if tgt in resolve:
            stat["A 修正为目标文件名"] += 1
            anchor = ("#" + h.split("#", 1)[1]) if "#" in h else ""
            return '<a href="%s%s"%s>%s</a>' % (quote(resolve[tgt], safe=""), anchor, attrs, label)
        # B 类：目标不存在
        stat["B 降级为纯文本"] += 1
        return '<span class="%s" title="该词条尚未收录">%s</span>' % (PENDING_CLASS, label)

    out = pat.sub(repl, out)
    return out


def main():
    apply = "--apply" in sys.argv
    pages = sorted(f for f in os.listdir(TERMS) if f.endswith(".html") and ".bak" not in f)
    disk, resolve = load_map()
    stat = collections.Counter()
    touched = []

    print("=" * 62)
    print("P0-4 断链修复 —— %s" % ("已落盘" if apply else "DRY-RUN"))
    print("=" * 62)
    print("扫描页面：%d   可解析目标：%d" % (len(pages), len(resolve)))
    print()

    for name in pages:
        p = os.path.join(TERMS, name)
        src = open(p, encoding="utf-8", errors="replace").read()
        st = collections.Counter()
        out = process(src, disk, resolve, st)
        if out != src:
            touched.append((name, sum(st.values())))
            if apply:
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write(out)
        stat.update(st)

    for k, v in sorted(stat.items()):
        print("  %-22s %6d" % (k, v))
    print("  %-22s %6d" % ("合计", sum(stat.values())))
    print()
    print("受影响文件：%d" % len(touched))
    for n, c in touched[:10]:
        print("   %-44s %3d 处" % (n, c))
    if not apply:
        print("\n>>> 预览。执行：python scripts/fix-broken-links.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
