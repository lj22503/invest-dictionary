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
import time
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DATA = os.path.join(WEB, "dictionary.json")
SITEMAP = os.path.join(WEB, "sitemap.xml")
BASE = "https://dictionary.mangofolio.com"

# lastmod 口径必须与词条页 dateModified 完全一致（否则同一页面两个日期，爬虫无从判断）
# 故直接复用 stamp-freshness.py 的 stamp_date()（git 提交时间优先，回退 mtime）。
# 注意：文件名带连字符，不能当模块 import，只能按路径加载。
def _load_stamp_date():
    import importlib.util
    path = os.path.join(ROOT, "scripts", "stamp-freshness.py")
    spec = importlib.util.spec_from_file_location("stamp_freshness", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.stamp_date


stamp_date = _load_stamp_date()


def block(url, freq, pri, lastmod=None):
    # 多行缩进格式（与原 sitemap 保持一致，便于 review diff）
    # lastmod 取页面真实 mtime（与 stamp-freshness.py 同一口径）：
    # 不用「今天」，否则每次重建全站日期跳一遍，是假新鲜度。
    lm = f'    <lastmod>{lastmod}</lastmod>\n' if lastmod else ''
    return (f'  <url>\n    <loc>{url}</loc>\n{lm}'
            f'    <changefreq>{freq}</changefreq>\n'
            f'    <priority>{pri}</priority>\n  </url>\n')


def mdate(*paths):
    """取这组路径里最新的「真实变更日期」（主页面只有 HTML，词条页还会传 md）。"""
    best = None
    for p in paths:
        if p and os.path.exists(p):
            d = stamp_date(p)
            if d and (best is None or d > best):
                best = d
    return best


def main():
    items = json.load(open(DATA, encoding="utf-8"))
    order, seen = [], set()
    for x in items:
        fn = x["filename"]
        if fn not in seen:
            seen.add(fn)
            order.append(fn)

    urls = [block(BASE + "/", "weekly", "1.0", mdate(os.path.join(WEB, "index.html"))),
            block(BASE + "/dictionary", "weekly", "0.9", mdate(os.path.join(WEB, "dictionary.html"))),
            block(BASE + "/guide", "monthly", "0.7", mdate(os.path.join(WEB, "guide.html"))),
            block(BASE + "/about", "yearly", "0.5", mdate(os.path.join(WEB, "about.html"))),
            block(BASE + "/privacy", "yearly", "0.2", mdate(os.path.join(WEB, "privacy.html"))),
            block(BASE + "/terms-of-service", "yearly", "0.2",
                  mdate(os.path.join(WEB, "terms-of-service.html")))]
    # 用法示例页（/cases/*）：目录扫描，新增 case 自动进 sitemap，不用改代码
    cases_dir = os.path.join(WEB, "cases")
    if os.path.isdir(cases_dir):
        for fn in sorted(f for f in os.listdir(cases_dir) if f.endswith(".html")):
            urls.append(block(BASE + "/cases/" + quote(fn[:-5], safe=""), "monthly", "0.7",
                              mdate(os.path.join(cases_dir, fn))))
    for fn in order:
        # P0-1：cleanUrls:true 已生效，对外 URL 一律不带 .html
        stem = fn[:-5] if fn.endswith(".html") else fn
        lm = mdate(os.path.join(WEB, "terms", stem + ".html"),
                   os.path.join(WEB, "terms_md", stem + ".md"))
        urls.append(block(BASE + "/terms/" + quote(stem, safe=""), "monthly", "0.8", lm))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "".join(urls) + "</urlset>\n")

    with open(SITEMAP, "w", encoding="utf-8", newline="") as f:
        f.write(xml)

    # 写盘回读校验
    back = open(SITEMAP, encoding="utf-8", errors="replace").read()
    n = back.count("<loc>")
    # 顶层页数随 urls 定义走（含 /about），别再硬编码 5
    ok = n == len(urls)
    print(f"sitemap 重建：dictionary {len(items)} 条（去重 {len(order)}）-> loc {n} 条（含法律页） -> {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
