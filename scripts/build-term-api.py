#!/usr/bin/env python3
"""从现成的词条页抽出「页面外壳」，生成技能接口用的两个资源文件。

    web/terms/货币.html        已有 1130 个词条页，样式与页脚都在里面
        ↓  抽壳（把动态部分换成 @@TOKEN@@）
    web/api/_term-shell.js     SHELL：整页 HTML 字符串，带占位符
    web/api/_term-index.js     INDEX：1130 条词条的紧凑索引（查词用）

为什么要抽壳：技能让模型「照着基准页写整页 HTML」，等于让模型当模板引擎，
输入 32KB 模板、输出 31KB HTML，一次两三分钟。改成接口后，模型只产出结构化
JSON，套模板在服务端做，模型不再读写 HTML。

用法：
    python scripts/build-term-api.py            # 重建
    python scripts/build-term-api.py --check    # 只比对，有差异返回 1
"""
import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
SHELL_SRC = os.path.join(WEB, "terms", "货币.html")
OUT_SHELL = os.path.join(WEB, "api", "_term-shell.js")
OUT_INDEX = os.path.join(WEB, "api", "_term-index.js")

SITE = "https://dictionary.mangofolio.com"


def cut(shell, pattern, token, flags=0):
    """把命中的整段换成 token，命中数必须正好 1，否则报错（防止模板漂移后静默失效）。"""
    new, n = re.subn(pattern, token, shell, count=1, flags=flags)
    if n != 1:
        sys.exit(f"抽壳失败：{pattern[:60]} 命中 {n} 次")
    return new


def build_shell():
    s = io.open(SHELL_SRC, encoding="utf-8").read()

    # —— head 动态项 ——
    s = cut(s, r"<title>[^<]*</title>", "<title>@@HEAD_TITLE@@</title>")
    s = cut(s, r'<meta name="description" content="[^"]*">', '<meta name="description" content="@@DESC@@">')
    s = cut(s, r'<meta name="keywords" content="[^"]*">', '<meta name="keywords" content="@@KEYWORDS@@">')
    s = cut(s, r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="@@URL@@">')
    s = cut(s, r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="@@OG_TITLE@@">')
    s = cut(s, r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="@@DESC@@">')
    s = cut(s, r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="@@URL@@">')
    s = cut(s, r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="@@OG_TITLE@@">')
    s = cut(s, r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="@@DESC@@">')
    s = cut(s, r'(<script type="application/ld\+json">).*?(</script>)', r"\1@@JSONLD@@\2", re.S)

    # —— 面包屑 / 分享 ——
    s = cut(s, r'(<nav class="term-breadcrumb"[^>]*>).*?(</nav>)', r"\1@@CRUMB@@\2", re.S)
    s = cut(s, r'(<a class="share-btn weibo-btn" href=")[^"]*(")', r"\1@@WEIBO@@\2")

    # —— 正文 ——
    s = cut(s, r'<div class="paper">.*?(?=\n<!-- 底部：关联功法)', '<div class="paper">@@PAPER@@', re.S)
    s = cut(s, r'(<div class="related-links">).*?(</div>)', r"\1@@RELATED@@\2", re.S)
    s = cut(s, r'<nav class="term-pager">.*?</nav>', '@@PAGER@@', re.S)

    return s


def build_index():
    d = json.load(io.open(os.path.join(WEB, "dictionary.json"), encoding="utf-8"))
    out = []
    for x in d:
        fn = x.get("filename") or (x["title"] + ".html")
        out.append({
            "t": x["title"],
            "u": "/" + fn[:-5],
            "c": x.get("chapter", ""),
            "k": x.get("card_titles") or [],
        })
    return out


def dump_js(path, body):
    io.open(path, "w", encoding="utf-8", newline="\n").write(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    shell = build_shell()
    index = build_index()

    shell_js = (
        "// 由 scripts/build-term-api.py 从 web/terms/货币.html 抽壳生成，勿手改。\n"
        "// 改词条页样式后重跑该脚本，_term-render.js 会同步生效。\n"
        "export const SHELL = " + json.dumps(shell, ensure_ascii=False) + ";\n"
    )
    index_js = (
        "// 由 scripts/build-term-api.py 从 web/dictionary.json 生成，勿手改。\n"
        "export default " + json.dumps(index, ensure_ascii=False, separators=(",", ":")) + ";\n"
    )

    if args.check:
        bad = []
        for path, body in ((OUT_SHELL, shell_js), (OUT_INDEX, index_js)):
            old = io.open(path, encoding="utf-8").read() if os.path.exists(path) else ""
            if old != body:
                bad.append(os.path.basename(path))
        if bad:
            print("⚠ 与词条页/词典不一致：" + "、".join(bad))
            print("  跑 python scripts/build-term-api.py 重建")
            return 1
        print("✅ 接口资源与词条页一致")
        return 0

    dump_js(OUT_SHELL, shell_js)
    dump_js(OUT_INDEX, index_js)
    print(f"外壳 {round(len(shell.encode())/1024,1)} KB → {os.path.relpath(OUT_SHELL, ROOT)}")
    print(f"索引 {len(index)} 条 {round(len(json.dumps(index, ensure_ascii=False).encode())/1024,1)} KB → {os.path.relpath(OUT_INDEX, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
