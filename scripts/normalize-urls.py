# -*- coding: utf-8 -*-
"""
normalize-urls.py —— 全站 URL 去除 .html 后缀（P0-1）

背景：
  sitemap / canonical / og:url / JSON-LD / 词条互链 长期带 .html 后缀。
  vercel.json 已开 cleanUrls:true，服务端本就支持无后缀 URL，
  缺的只是「链接写法」这一层。本脚本一次性对齐。

替换规则（有序，先特殊后一般）：
  R1  绝对词条 URL    https://<domain>/terms/X.html      -> /terms/X
  R2  回首页          ../index.html[#锚]                 -> /[#锚]
  R3  上级目录页      ../guide.html | ../dictionary.html -> /guide | /dictionary
  R4  顶层页自身链接  index.html -> /   guide/dictionary.html -> /guide /dictionary
  R5  词条互链（同目录相对，含百分号编码）
                      href="%E4%BF%A1...html"            -> href="%E4%BF%A1..."

不触碰：../css/*、../js/*、../manifest.json、外站链接。

用法：
  python scripts/normalize-urls.py            # dry-run，只报告
  python scripts/normalize-urls.py --apply    # 落盘
"""
import os
import re
import sys
import glob
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")

DOMAIN = r"https?://(?:dictionary|invest-dictionary)\.mangofolio\.com"

# (名称, 编译后的正则, 替换串或回调)
RULES = [
    # 不要求协议前缀：同时覆盖明文 https:// 与分享链接里的 %3A 双重编码形式
    ("R1 词条绝对URL",
     re.compile(r'(dictionary\.mangofolio\.com/terms/[^"\'\s<>]+?)\.html'),
     r"\1"),
    ("R2 回首页",
     re.compile(r'\.\./index\.html(#[^"\'\s<>]*)?'),
     lambda m: "/" + (m.group(1) or "")),
    ("R3 上级目录页",
     re.compile(r'\.\./(guide|dictionary)\.html'),
     r"/\1"),
    ("R4a 自身 index",
     re.compile(r'(?<![\w/.\-])index\.html(\?[^"\'\s<>]*)?(#[^"\'\s<>]*)?(?=["\'])'),
     lambda m: "/" + (m.group(1) or "") + (m.group(2) or "")),
    ("R4b 自身 guide/dictionary",
     re.compile(r'(?<![\w/.\-])(guide|dictionary)\.html(?=["\'#])'),
     r"/\1"),
    # R5 只处理「同目录相对」：href 值内不得含 / 或 :（排除协议与子路径）
    ("R5 词条互链",
     re.compile(r'href="([^"/:]*?)\.html(#[^"]*?)?"'),
     lambda m: 'href="%s%s"' % (m.group(1), m.group(2) or "")),
]

TERMS_PAGE_RULES = ("R5 词条互链",)


def term_files():
    return [f for f in glob.glob(os.path.join(WEB, "terms", "*.html")) if ".bak" not in f]


def target_files():
    fs = term_files()
    for n in ("index.html", "dictionary.html", "guide.html", "sw.js"):
        p = os.path.join(WEB, n)
        if os.path.exists(p):
            fs.append(p)
    return fs


def normalize(text, stat):
    """按序应用规则，返回新文本。stat: Counter。"""
    out = text
    for name, pat, rep in RULES:
        cache = collections.Counter()

        def _sub(m, _pat=pat, _rep=rep, _n=name, _c=cache):
            _c["n"] += 1
            return _rep(m) if callable(_rep) else m.expand(_rep)

        out = pat.sub(_sub, out)
        if cache["n"]:
            stat[name] += cache["n"]
    return out


def main():
    apply = "--apply" in sys.argv
    files = target_files()
    total = collections.Counter()
    changed = []

    for p in files:
        src = open(p, encoding="utf-8", errors="replace").read()
        stat = collections.Counter()
        out = normalize(src, stat)
        if out != src:
            changed.append((os.path.relpath(p, ROOT), sum(stat.values())))
            if apply:
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write(out)
        total.update(stat)

    print("=" * 64)
    print("P0-1 全站 URL 去 .html —— %s" % ("已落盘" if apply else "DRY-RUN 预览"))
    print("=" * 64)
    print("目标文件：%d（terms 页面 %d）" % (len(files), len(term_files())))
    print()
    for k, v in sorted(total.items()):
        print("  %-20s %8d" % (k, v))
    print("  %-20s %8d" % ("合计", sum(total.values())))
    print()
    print("受影响文件：%d" % len(changed))
    for n, c in changed[:6]:
        print("   %-44s %5d 处" % (n, c))
    if len(changed) > 6:
        print("   ... 另 %d 个" % (len(changed) - 6))
    if not apply:
        print("\n>>> 预览模式。确认无误后执行：python scripts/normalize-urls.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
