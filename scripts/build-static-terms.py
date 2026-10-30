# -*- coding: utf-8 -*-
"""
build-static-terms.py —— 把词条静态写进 HTML（P0-2：词条链接服务端可见）

问题：
  首页与词库页的词条此前 100% 由 JS 从 ALL_ENTRIES 渲染，HTML 源码里没有任何
  词条链接。不执行 JS 的爬虫（含多数 AI 抓取器、部分 SEO 工具）抓不到任何一个词条页。

方案（渐进增强，不破坏现有交互）：
  1. dictionary.html  静态输出完整 chapter/term 结构，样式与 JS 版完全一致。
     JS 启动后 el.chapters.innerHTML='' 会接管，用户无感；爬虫拿到静态版。
  2. index.html       静态输出「全部词条」折叠区（<details>），
     内容在 HTML 里可被索引，用户默认折叠不影响视觉。

数据源：web/dictionary.json（唯一源），副标题优先复用 ALL_ENTRIES.card_titles[0]。

标记：插入内容被 <!-- STATIC-TERMS:BEGIN --> / <!-- STATIC-TERMS:END --> 包裹，
      重复执行会替换而非累积（幂等）。

用法：
  python scripts/build-static-terms.py            # dry-run
  python scripts/build-static-terms.py --apply    # 落盘
"""
import os
import re
import sys
import json
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DATA = os.path.join(WEB, "dictionary.json")
INDEX = os.path.join(WEB, "index.html")
DICT = os.path.join(WEB, "dictionary.html")

BEGIN = "<!-- STATIC-TERMS:BEGIN -->"
END = "<!-- STATIC-TERMS:END -->"
SAFE = "-_.!~*'()"


def js_encode(s):
    """模拟 JS encodeURIComponent：保留 A-Za-z0-9 与 -_.!~*'()"""
    return quote(s, safe=SAFE)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"))


def pad(n):
    return ("0" if n < 10 else "") + str(n)


def split_chapter(name):
    s = str(name or "")
    for sep in ("：", ":"):
        i = s.find(sep)
        if i > 0:
            return s[:i], (s[i + 1:].strip() or s)
    return "", s


def load():
    items = json.load(open(DATA, encoding="utf-8"))
    # 章节按首次出现顺序分组
    order, groups = [], {}
    for x in items:
        ch = x.get("chapter") or "未分类"
        if ch not in groups:
            groups[ch] = []
            order.append(ch)
        groups[ch].append(x)

    # 副标题：优先首页 ALL_ENTRIES 的 card_titles[0]（与站点展示一致）
    html = open(INDEX, encoding="utf-8", errors="replace").read()
    m = re.search(r"var ALL_ENTRIES = (\[.*?\]);", html, re.S)
    cards = {}
    if m:
        try:
            for e in json.loads(m.group(1)):
                k = e.get("file") or e.get("filename")
                ct = e.get("card_titles") or []
                if k and ct:
                    cards[k] = ct[0]
        except json.JSONDecodeError:
            pass
    return items, order, groups, cards


def link(x):
    fn = x.get("filename", "")
    stem = fn[:-5] if fn.endswith(".html") else fn
    return "terms/" + js_encode(stem)


def one_liner(x, cards):
    return cards.get(x.get("filename", "")) or x.get("description") or ""


def dict_html(order, groups, cards):
    """dictionary.html #chapters 的静态内容，结构/类名与 JS 渲染完全一致（紧凑排版省体积）。"""
    parts = []
    for ci, ch in enumerate(order):
        no, name = split_chapter(ch)
        entries = groups[ch]
        parts.append('<section class="chapter" id="ch-%d" data-chapter="%s" data-tone="%s">'
                     % (ci + 1, esc(ch), "base" if ci % 2 == 0 else "paper"))
        parts.append('<div class="chapter__head"><div class="chapter__id">'
                     '<span class="chapter__no">%s</span>'
                     '<h2 class="chapter__title">%s</h2>'
                     '<span class="chapter__count">%d 条</span>'
                     '</div></div>'
                     % (esc(no or pad(ci + 1)), esc(name), len(entries)))
        parts.append('<div class="chapter__body" id="body-%d"><div class="chapter__grid">' % (ci + 1))
        for i, x in enumerate(entries):
            desc = one_liner(x, cards)
            d = ('<span class="term__desc">%s</span>' % esc(desc)) if desc else ""
            parts.append('<a class="term" href="%s"><span class="term__no">%s</span>'
                         '<span class="term__body"><span class="term__name">%s</span>%s</span></a>'
                         % (link(x), pad(i + 1), esc(x.get("title") or x.get("slug")), d))
        parts.append('</div></div></section>')
    return "\n".join(parts)


def index_html(order, groups, cards):
    """index.html 的折叠式全量词条目录。"""
    total = sum(len(groups[c]) for c in order)
    L = []
    L.append('<section class="band band--base" id="terms">')
    L.append('  <div class="wrap">')
    L.append('    <div class="sec-head">')
    L.append('      <h2 class="sec-title">全部词条 · 按篇章</h2>')
    L.append('      <div class="sec-head__aside"><a href="/dictionary">打开完整词库 →</a></div>')
    L.append('    </div>')
    L.append('    <details class="terms-all">')
    L.append('      <summary>共 %d 个词条，%d 个篇章（点击展开）</summary>' % (total, len(order)))
    for ci, ch in enumerate(order):
        no, name = split_chapter(ch)
        L.append('      <div class="terms-group">')
        L.append('        <p class="terms-group__title">%s %s'
                 '<span class="terms-group__n">%d</span></p>'
                 % (esc(no), esc(name), len(groups[ch])))
        L.append('        <p class="terms-group__list">')
        L.append('          ' + " · ".join(
            '<a href="%s">%s</a>' % (link(x), esc(x.get("title") or x.get("slug")))
            for x in groups[ch]))
        L.append('        </p>')
        L.append('      </div>')
    L.append('    </details>')
    L.append('  </div>')
    L.append('</section>')
    return "\n".join(L)


def inject(path, html_part, apply):
    """把 html_part 注入标记之间；已存在则替换（幂等）。

    dictionary.html 必须注入到 <div id="chapters"> 容器【内部】，
    这样 JS 启动时的 el.chapters.innerHTML='' 会顺带清掉静态版，
    避免静态版与 JS 渲染版同时出现在页面上（重复内容）。
    """
    src = open(path, encoding="utf-8", errors="replace").read()
    block = BEGIN + "\n" + html_part + "\n" + END
    pat = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)

    if pat.search(src):
        mode, out = "替换已有静态块", pat.sub(lambda m: block, src, count=1)
    else:
        # 首次注入：定位到 #chapters 容器内（loadingState 占位一并替换掉）
        holder = re.search(
            r'(<div id="chapters">\s*)(?:<p class="state" id="loadingState">.*?</p>\s*)?', src)
        if holder:
            mode = "注入 #chapters 容器内"
            out = src[:holder.end()] + "\n" + block + "\n" + src[holder.end():]
        else:
            anchor = '<footer class="site-footer" id="footer">'
            i = src.find(anchor)
            if i < 0:
                return None, "未找到注入锚点"
            mode = "注入 footer 前"
            out = src[:i] + block + "\n\n" + src[i:]

    if apply:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(out)
    return mode, len(out) - len(src)


def main():
    apply = "--apply" in sys.argv
    items, order, groups, cards = load()
    print("=" * 60)
    print("P0-2 词条静态化 —— %s" % ("已落盘" if apply else "DRY-RUN"))
    print("=" * 60)
    print("词条 %d 条 / 章节 %d 个" % (len(items), len(order)))
    print()
    for path, part, label in ((DICT, dict_html(order, groups, cards), "dictionary.html #chapters"),
                              (INDEX, index_html(order, groups, cards), "index.html 折叠词条区")):
        mode, delta = inject(path, part, apply)
        if mode is None:
            print("[FAIL] %s：%s" % (label, delta))
            continue
        print("[OK] %-34s %s，体积变化 %+d 字节" % (label, mode, delta))
    if not apply:
        print("\n>>> 预览。执行：python scripts/build-static-terms.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
