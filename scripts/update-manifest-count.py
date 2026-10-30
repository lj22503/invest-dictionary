# -*- coding: utf-8 -*-
"""
update-manifest-count.py —— 把 PWA manifest 里的词条硬数字对齐到 dictionary.json

背景：manifest.json 的 description 写死了词条数（如 "924 个投资术语…"）。
手写数字会随词条增长而漂移，门禁第 1 项因此长期 FAIL。改为由数据源推导。

用法：python scripts/update-manifest-count.py
"""
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DATA = os.path.join(WEB, "dictionary.json")
MANIFEST = os.path.join(WEB, "manifest.json")

PAT = re.compile(r"(\d{2,4})\s*个投资术语")


def main():
    items = json.load(open(DATA, encoding="utf-8"))
    n = len(items)
    mf = json.load(open(MANIFEST, encoding="utf-8"))

    old = mf.get("description", "")
    new, cnt = PAT.subn(lambda m: "%d 个投资术语" % n, old)
    if cnt == 0:
        print("警告：description 中未匹配到「NNN 个投资术语」模式，未修改")
        print("  现值：%s" % old)
        return 1
    if new == old:
        print("manifest 计数已是最新：%d" % n)
        return 0

    mf["description"] = new
    with open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        json.dump(mf, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("manifest 计数更新：")
    print("  旧：%s" % old)
    print("  新：%s" % new)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
