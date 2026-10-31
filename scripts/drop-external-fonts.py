#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""移除 Google Fonts 外链，改走系统字体栈。

为什么：fonts.googleapis.com / fonts.gstatic.com 在国内访问不稳定，且是
渲染阻塞资源——字库拉不到时首屏会长时间白屏。站点已有的字体栈变量本身
就带系统兜底（PingFang SC / Microsoft YaHei / Songti SC / SimSun），
移除后不会「没字体」，只是从 Noto Serif SC 回退到系统衬线。

用法：
    python scripts/drop-external-fonts.py [--dry]

坑（改过一次就记住）：
1. 只删 fonts.googleapis.com / fonts.gstatic.com 的 link，别碰其他 preconnect
   （站点可能还有自己的 CDN / API 需要预热）。
2. 页面是 CRLF 行尾，写入时必须 newline=''，否则整仓炸出噪声 diff。
3. 移除前先确认 tokens CSS 里的字体栈有系统兜底，否则会掉进默认 serif/sans。
"""
import argparse
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ROOT = os.path.abspath(ROOT)

# 只匹配指向 Google 字体域名的 <link ...>，含前后空白与换行
FONT_LINK = re.compile(
    r"[ \t]*<link\b[^>]*fonts\.(?:googleapis|gstatic)\.com[^>]*>[ \t]*\r?\n?",
    re.I,
)

SKIP_DIRS = {".git", "node_modules", ".vercel", ".next"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只报告不写盘")
    args = ap.parse_args()

    changed, total_links = [], 0
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for n in fns:
            if not n.endswith((".html", ".htm")):
                continue
            if n.endswith(".bak") or ".bak-" in n:
                continue
            p = os.path.join(dp, n)
            raw = open(p, encoding="utf-8", errors="replace").read()
            new, cnt = FONT_LINK.subn("", raw)
            if cnt:
                total_links += cnt
                changed.append((os.path.relpath(p, ROOT), cnt))
                if not args.dry:
                    open(p, "w", encoding="utf-8", newline="").write(new)

    print("移除 Google Fonts 外链：%d 个文件 / %d 条 link" % (len(changed), total_links))
    for f, c in changed[:5]:
        print("   %s (-%d)" % (f, c))
    if len(changed) > 5:
        print("   ... 其余 %d 个" % (len(changed) - 5))
    if args.dry:
        print("(dry run，未写盘)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
