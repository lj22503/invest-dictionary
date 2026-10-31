#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""清除 md 文件里的 AIGC 元数据头，并去掉被重复追加的尾部免责声明。

用法：
    python scripts/strip-aigc-metadata.py            # 全仓清理
    python scripts/strip-aigc-metadata.py --dry      # 只看会改哪些，不落盘

背景：
    外部内容生成器会在 md 头部注入这样的 YAML frontmatter：

        ---
        AIGC:
            Label: "1"
            ContentProducer: 001191440300708461136T1XGW3
            ProduceID: 1c835e55...
            ReservedCode1: QqZ2RJd0...
        ---

    它是纯水印，无内容价值，还会把生产方 ID 带进仓库与线上产物，
    且会在词条扩充时反复出现。2026-10-31 首次全量清除 484 处
    （docs/ 353 + web/ 103 + skill/ 6 等），并在 site-audit.py 的
    hygiene 维度加了常驻检查，复发即报警。

踩过的坑（改这个脚本前先看）：
    1. 正则必须 re.S，否则 .*? 跨不过 frontmatter 里的换行 —— 会静默什么都不做。
    2. 全量删而非只删第一个：合并稿会在每条词条前各挂一个块，散落在正文中间。
       判定靠「--- 后紧跟 AIGC:」，正文的水平分隔线不会被误伤。
    3. 别顺手统一行尾：仓库是 CRLF，重写成 LF 会让 32 个文件产生纯噪声 diff。
       正确做法是改完按 HEAD 的原行尾后缀补回去。
    4. 范围要全仓 os.walk，不能只扫 docs/ —— web/markdown、web/terms、
       web/terms_md、skill/ 里都有，且 web/ 下的是随站部署的。
"""
import argparse
import os
import re
import sys

# 关键：re.S，否则 .*? 无法跨行匹配 frontmatter 内容。
# 删全部而非只删第一个：合并稿（如 web/markdown/*扩充词条*.md）会在每条词条前各挂一个块，
# 散落在正文里。模式要求 `---` 后紧跟 `AIGC:`，正文的水平分隔线不会被误伤。
BLOCK = re.compile(r"(?m)^---[ \t]*\r?\nAIGC:.*?\r?\n---[ \t]*\r?\n[ \t]*\r?\n?", re.S)
SKIP_DIRS = {".git", "node_modules", ".next", ".vercel"}
DISCLAIMER = "内容由AI生成"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def iter_md(repo):
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for n in filenames:
            if n.endswith(".md"):
                yield os.path.join(dirpath, n)


def strip(text):
    """返回 (新文本, 是否剥离了 frontmatter, 是否去掉了重复声明)。"""
    new_text, n = BLOCK.subn("", text)
    did_block = n > 0
    if did_block:
        text = new_text.lstrip("\ufeff").lstrip("\r\n")

    lines = text.rstrip().split("\n")
    did_dup = False
    while (len(lines) >= 2 and lines[-1].strip()
           and lines[-1].strip() == lines[-2].strip()
           and DISCLAIMER in lines[-1]):
        lines.pop()
        did_dup = True
    return "\n".join(lines) + "\n", n, did_dup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只报告不落盘")
    ap.add_argument("--root", default=".", help="仓库根目录")
    args = ap.parse_args()

    repo = os.path.abspath(args.root)
    n_block = n_dup = 0
    for p in iter_md(repo):
        raw = open(p, encoding="utf-8", errors="replace").read()
        new, b, d = strip(raw)
        if new == raw:
            continue
        n_block += b
        n_dup += d
        if not args.dry:
            open(p, "w", encoding="utf-8", newline="").write(new)

    print("%s 剥离 frontmatter %d 个，去重尾部声明 %d 个"
          % ("[dry-run] 将" if args.dry else "已", n_block, n_dup))
    return 0


if __name__ == "__main__":
    sys.exit(main())
