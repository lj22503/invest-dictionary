# -*- coding: utf-8 -*-
"""
generate-sitemap.py —— 由 dictionary.json 同源生成 web/sitemap.xml

背景：sitemap 曾是手写/一次性产物，扩充词条后不更新，导致 33 个页面不在 sitemap（SEO 收录缺失）。
规则：
  1. 词条唯一数据源 = web/dictionary.json（按其中出现顺序，filename 去重）
  2. 首页 https://dictionary.mangofolio.com/  changefreq=weekly  priority=1.0
  3. 词条页 /terms/<URL编码文件名>    changefreq=monthly priority=0.8
  4. 禁止手改 web/sitemap.xml —— 一律重跑本脚本

用法：python scripts/generate-sitemap.py
"""
import os
import json
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DATA = os.path.join(WEB, "dictionary.json")
SITEMAP = os.path.join(WEB, "sitemap.xml")
BASE = "https://dictionary.mangofolio.com"


def block(url, freq, pri):
    # 多行缩进格式（与原 sitemap 保持一致，便于 review diff）
    return (f'  <url>\n    <loc>{url}</loc>\n    <changefreq>{freq}</changefreq>\n'
            f'    <priority>{pri}</priority>\n  </url>\n')


def main():
    items = json.load(open(DATA, encoding="utf-8"))
    order, seen = [], set()
    for x in items:
        fn = x["filename"]
        if fn not in seen:
            seen.add(fn)
            order.append(fn)

    urls = [block(BASE + "/", "weekly", "1.0")]
    for fn in order:
        urls.append(block(BASE + "/terms/" + quote(fn, safe=""), "monthly", "0.8"))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "".join(urls) + "</urlset>\n")

    with open(SITEMAP, "w", encoding="utf-8", newline="") as f:
        f.write(xml)

    # 写盘回读校验
    back = open(SITEMAP, encoding="utf-8", errors="replace").read()
    n = back.count("<loc>")
    ok = n == len(order) + 1
    print(f"sitemap 重建：dictionary {len(items)} 条（去重 {len(order)}）-> loc {n} 条 -> {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
