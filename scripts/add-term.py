#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""add-term.py —— 手工补词条：md -> 词条页 + dictionary.json 条目

背景：
    每日热词的自动扩充只能覆盖清单里的词条，但调研/内容线里发现的词库缺口
    （比如社媒方案里排查出的「七日年化收益率」「业绩比较基准」）需要手工补。
    手工改容易和现网形态不一致：URL 带不带 .html、链接相对还是绝对、
    related 是否命中真实 slug —— 任一不对都会被 check-consistency / site-audit 打回。
    所以统一走这个脚本，产出形态以「最近一批标准词条页」为准。

产出：
    web/terms/<标题>.html        词条页（相对链接、无 .html 后缀、canonical 百分号编码）
    web/dictionary.json          追加条目，id = max(id)+1
    web/terms_md/<标题>.md       原 md 就地保留（本脚本不重写它）

用法：
    python scripts/add-term.py web/terms_md/七日年化收益率.md --chapter "第六篇：投资武器库 · 基金篇"
    python scripts/add-term.py docs/incoming/          # 批跑目录下所有 md
    python scripts/add-term.py xxx.md --dry            # 只校验不落盘

md 规范（与现网一致）：
    # 标题
    > 一句话钩子（进 meta description）
    ## 1. 这是什么
    ...（## 2. 为什么重要 / ## 3. 怎么用 / ## 4. 常见坑）
    **相关词条**：A、B、C            # 顿号分隔，必须是 dictionary.json 里真实存在的 slug

踩过的坑（改这个脚本前先看）：
    1. 外壳不要手写。网页模板里 950+ 行是 CSS，只有 ~100 行是内容；
       本脚本以 --tpl 指定的标准页为外壳做「局部替换」，保证与现网字节一致。
    2. canonical / og:url / 关联链接的 URL 必须百分号编码，但 termCode 用原文，
       两者不能搞反（termCode 是给结构化数据看的，不是 URL）。
    3. 链接一律相对（"%E4%B8%89..."），绝对 URL 或带 .html 后缀会被 P0-1 规则判 FAIL。
    4. related 必须在 dictionary.json 里真实存在，否则词条页出断链、门禁红；
       本脚本先校验再落盘，宁可不生成也不留坏链。
    5. 幂等：同名条目默认跳过，不会重复追加；要覆盖加 --force。
"""
import argparse
import html as html_mod
import json
import os
import re
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DICT_JSON = os.path.join(WEB, "dictionary.json")
TERMS = os.path.join(WEB, "terms")
DEFAULT_TPL = os.path.join(TERMS, "鸵鸟效应.html")
SITE = "https://dictionary.mangofolio.com"

NUM_CIRCLED = ["①", "②", "③", "④"]


# ---------- md 解析 ----------

def parse_md(text):
    """返回 dict(title, tagline, cards=[(title, [html])], related=[str])"""
    lines = text.split("\n")
    title = None
    tagline = None
    for i, ln in enumerate(lines):
        if title is None and ln.startswith("# "):
            title = ln[2:].strip()
            rest = lines[i + 1:]
            break
    else:
        rest = lines
    if title is None:
        raise ValueError("找不到一级标题（# xxx）")

    # 钩子：标题之后、第一个 ## 之前的第一个引用行
    for ln in rest:
        s = ln.strip()
        if s.startswith("## "):
            break
        if tagline is None and s.startswith("> "):
            tagline = s[2:].strip()
    if not tagline:
        raise ValueError("找不到一句话钩子（标题后的 > xxx）")

    body = "\n".join(rest)
    related = []
    m = re.search(r"^\*\*相关词条\*\*[：:]\s*(.+?)\s*$", body, re.M)
    if m:
        related = [x.strip() for x in re.split(r"[、,，;；]", m.group(1)) if x.strip()]
        body = body[:m.start()]

    chunks = re.split(r"(?m)^##\s+\d+\.\s+", body)[1:]
    cards = []
    for ch in chunks:
        ch = ch.strip()
        if not ch:
            continue
        head, _, tail = ch.partition("\n")
        cards.append((head.strip(), md_to_html(tail)))
    if not cards:
        raise ValueError("没有解析到任何 ## N. 卡片")

    return {"title": title, "tagline": tagline, "cards": cards, "related": related}


def inline(s):
    """**x** -> <strong>x</strong>（其余保持原文，不做全量 markdown 渲染）"""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def md_to_html(body):
    """卡片正文 md -> 卡片内片段"""
    paras = []
    list_buf = []

    def flush_list():
        if list_buf:
            paras.append('<ul class="step-list">' + "".join(
                "<li>%s</li>" % inline(x) for x in list_buf) + "</ul>")
            del list_buf[:]

    for raw in body.split("\n"):
        line = raw.strip()
        if not line or line == "---":
            continue
        if line.startswith("> "):
            flush_list()
            paras.append('<div class="card-quote">%s</div>' % inline(line[2:].strip()))
        elif line.startswith("- ") or line.startswith("* "):
            list_buf.append(line[2:].strip())
        else:
            flush_list()
            paras.append("<p>%s</p>" % inline(line))
    flush_list()
    return paras


# ---------- 渲染 ----------

def render_cards(cards):
    blocks = []
    for i, (title, paras) in enumerate(cards):
        num = NUM_CIRCLED[i] if i < len(NUM_CIRCLED) else "•"
        inner = "".join("      %s\n" % p for p in paras)
        blocks.append(
            '<article class="card">\n'
            '    <div class="card-number">%s</div>\n'
            '    <h2 class="card-title">%s</h2>\n'
            '    <div class="card-body">\n'
            "%s"
            "    </div>\n"
            "  </article>" % (num, html_mod.escape(title), inner)
        )
    # 卡片之间用 <div class="card-divider"></div> 分隔（对齐现网形态）
    return ("        " + blocks[0] + "\n\n  " + "\n\n  ".join(
        ['<div class="card-divider"></div>\n\n  ' + b for b in blocks[1:]])
        + "\n\n  " + '<div class="card-divider"></div>')


def render_page(tpl, spec):
    title = spec["title"]
    tagline = spec["tagline"]
    enc = quote(title)
    esc = html_mod.escape
    # 关键词：标题 + 关联词去括号后的主干
    kws = [title] + [re.sub(r"（[^）]*）", "", r) for r in spec["related"][:4]]
    keywords = ", ".join(kws)
    url = "%s/terms/%s" % (SITE, enc)

    # (正则, 新值, 是否 html 转义)。替换一律走 lambda：词条内容里若含字面 \1，
    # 直接用字符串会被 re 当反向引用。
    subs = [
        (r"(<title>).*?(</title>)",
         "%s是什么意思？小白也能看懂的理财术语解读 - 投资词典" % title, True),
        (r'(<meta name="keywords" content=").*?(">)', keywords, True),
        (r'(<link rel="canonical" href=").*?(">)', url, True),
        (r'(<meta property="og:title" content=").*?(">)',
         "%s - 投资词典 · Invest Dictionary" % title, True),
        (r'(<meta property="og:url" content=").*?(">)', url, True),
        (r'(<meta name="twitter:title" content=").*?(">)',
         "%s - 投资词典 · Invest Dictionary" % title, True),
        (r'(  "name": ").*?(",)', title, True),
        # termCode 用原文，termCode 不是 URL，别编码
        (r'(  "termCode": ").*?(",)', "dict-%s" % title, True),
        (r'(  "url": ").*?(")', url, True),
        (r'(<span class="bc-current">).*?(</span>)', title, True),
        (r'(<h1 class="main-title">).*?(</h1>)', title, True),
    ]
    out = tpl
    for pat, value, need_esc in subs:
        def _rep(m, v=value, e=need_esc):
            return m.group(1) + (esc(v) if e else v) + m.group(2)
        out, n = re.subn(pat, _rep, out, count=1)
        if n == 0:
            print("  ! 外壳未命中（形态可能变了，需校准模板）：%s" % pat[:36])

    # description / og:description / twitter:description / JSON-LD description 同文案（钩子句）
    for pat in [r'(<meta name="description" content=").*?(">)',
                r'(<meta property="og:description" content=").*?(">)',
                r'(<meta name="twitter:description" content=").*?(">)',
                r'(  "description": ").*?(",)']:
        out = re.sub(pat, lambda m: m.group(1) + esc(tagline) + m.group(2), out, count=1)

    # 卡片区：从第一张 <article class="card"> 到 pager 之前最后一张 </article>
    start = out.index('<div class="paper">')
    pager = out.index('<nav class="term-pager">', start)
    i = out.index('<article class="card">', start)
    j = out.rindex('</article>', start, pager) + len('</article>')
    out = out[:i] + render_cards(spec["cards"]) + out[j:]

    # 关联词条：相对链接 + 百分号编码，绝不带 .html
    rel = " · ".join('<a href="%s">%s</a>' % (quote(r), esc(r)) for r in spec["related"])
    out = re.sub(r'<div class="related-links">.*?</div>',
                 '<div class="related-links">%s</div>' % rel, out, count=1, flags=re.S)

    # 翻页：上一页留空（新词条按字典序插在末尾），下一页回目录
    out = re.sub(r'<nav class="term-pager">.*?</nav>',
                 '<nav class="term-pager"><span class="pager-disabled">← 暂无上篇</span>'
                 '<a href="/" class="pager-next" title="返回目录">返回目录 →</a></nav>',
                 out, count=1, flags=re.S)
    return out


# ---------- 主流程 ----------

def write_dict(data):
    """写回 dictionary.json —— 必须还原原文件的行尾与「末尾有没有换行」。

    这个文件是全站唯一数据源，一旦被 json.dump 重写成 LF + 末尾换行，
    git diff 会炸出上千行噪声，后面谁都看不出真正改了什么。
    """
    with open(DICT_JSON, encoding="utf-8", newline="") as f:
        raw = f.read()
    crlf = "\r\n" in raw
    ends_with_nl = raw.endswith("\n")
    nl = "\r\n" if crlf else "\n"
    text = json.dumps(data, ensure_ascii=False, indent=2)
    text = text.replace("\r\n", "\n").replace("\n", nl)
    if not ends_with_nl:
        text = text.rstrip("\r\n")
    with open(DICT_JSON, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def load_dict():
    with open(DICT_JSON, encoding="utf-8") as f:
        return json.load(f)


def add_term(md_path, chapter, dry=False, force=False):
    rel_path = os.path.relpath(md_path, ROOT)
    with open(md_path, encoding="utf-8") as f:
        text = f.read()

    spec = parse_md(text)
    title = spec["title"]

    # 章节也可以写在 md 里：<!-- chapter: 第六篇：投资武器库 · 基金篇 -->
    m = re.search(r"<!--\s*chapter:\s*(.+?)\s*-->", text)
    if m:
        chapter = m.group(1)
    if not chapter:
        raise SystemExit("%s：未指定章节（用 --chapter 或在 md 里写 <!-- chapter: xxx -->）" % rel_path)

    data = load_dict()
    slugs = set(x["slug"] for x in data)
    exist = [x for x in data if x["slug"] == title]
    if exist and not force:
        print("  跳过（已存在 id=%s）：%s" % (exist[0]["id"], title))
        return None

    # related 必须真实存在，否则词条页出断链
    bad = [r for r in spec["related"] if r not in slugs]
    if bad:
        raise SystemExit("%s：关联词条在 dictionary.json 里不存在 -> %s" % (rel_path, "、".join(bad)))

    html_page = render_page(open(DEFAULT_TPL, encoding="utf-8").read(), spec)
    html_path = os.path.join(TERMS, "%s.html" % title)

    if dry:
        print("  [dry] 将生成 %s（%d 卡，关联 %d 条）"
              % (os.path.basename(html_path), len(spec["cards"]), len(spec["related"])))
        return None

    if not force and os.path.exists(html_path):
        print("  ! 词条页已存在将被覆盖：%s" % os.path.basename(html_path))

    with open(html_path, "w", encoding="utf-8", newline="") as f:
        f.write(html_page)

    if exist:
        entry = exist[0]
    else:
        entry = {"id": max(x["id"] for x in data) + 1}
        data.append(entry)
    entry.update({
        "slug": title,
        "title": title,
        "chapter": chapter,
        "card_titles": [c[0] for c in spec["cards"][:4]],
        "related": spec["related"],
        "next": "",
        "filename": "%s.html" % title,
    })
    write_dict(data)
    print("  + %s  id=%s  %s" % (title, entry["id"], chapter))
    print("    -> %s" % os.path.relpath(html_path, ROOT))
    return entry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="md 文件或目录")
    ap.add_argument("--chapter", help="所属篇章，如「第六篇：投资武器库 · 基金篇」")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--force", action="store_true", help="已存在则覆盖")
    args = ap.parse_args()

    files = []
    for p in args.paths:
        if os.path.isdir(p):
            files += [os.path.join(p, n) for n in sorted(os.listdir(p)) if n.endswith(".md")]
        else:
            files.append(p)

    if not files:
        raise SystemExit("没有找到 md 文件")

    ok = 0
    for md in files:
        print("[%s]" % os.path.basename(md))
        add_term(md, args.chapter, args.dry, args.force)
        ok += 1
    print("\n共处理 %d 个。下一步必须跑：python scripts/sync-site.py" % ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
