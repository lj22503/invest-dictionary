#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把首页/词典页内嵌的词条数据瘦身为「搜索索引」，并去掉重复的 dictionary.json 请求。

背景：
  两个页面都是「服务端静态输出 995 条词条锚点（给爬虫）+ 内嵌/外链 JS 数据（给搜索）」。
  原本 index.html 内嵌 397KB 完整数据，随后又 fetch 一份字段完全相同的
  dictionary.json（571KB）—— 同一份数据下载两遍，且第二次还会整体覆盖第一次。

做法：
  1. 只保留 JS 真正读到的字段：id / title / chapter / card_titles[0] / file / filename
     （search 只匹配 title，词典页的 oneLiner 只读 card_titles[0]，
       related / next / slug 详情页才用，详情页是独立 HTML，不需要 JSON）
  2. 内嵌数据已是全量 => 删掉 fetch，改成直接就绪

用法：
    python scripts/slim-inline-data.py [--dry]

坑：
  1. 页面是 CRLF，写入必须 newline=''。
  2. 精确替换靠锚点字符串，锚点变了脚本会直接报错退出——不要静默跳过。
  3. ensure_ascii=False：中文直接存 UTF-8（3 字节/字）比 \\uXXXX（6 字节）省一半。
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ROOT = os.path.abspath(ROOT)
SRC = os.path.join(ROOT, "web", "dictionary.json")

KEEP_FIELDS_NOTE = "id/title/chapter/card_titles[0]/file/filename"


def build_slim():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)
    slim = []
    for e in data:
        file_ = e.get("file") or e.get("filename") or ""
        slim.append({
            "id": e.get("id"),
            "title": e.get("title", ""),
            "chapter": e.get("chapter", "未分类"),
            "card_titles": (e.get("card_titles") or [])[:1],
            "file": file_,
            "filename": e.get("filename") or file_,
        })
    # 每条一行，紧凑分隔：可读性够，且没有多余缩进字节
    lines = [json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in slim]
    return "[\n" + ",\n".join(lines) + "\n]"


def must_find(text, needle, where):
    i = text.find(needle)
    if i < 0:
        sys.exit("锚点未找到，已中止（%s）：%s" % (where, needle))
    return i


def must_search(pat, text, where, start=0):
    """页面是 CRLF 且原文含换行，一律用正则找锚点，别用字面串。"""
    m = re.compile(pat, re.S).search(text, start)
    if not m:
        sys.exit("锚点未找到，已中止（%s）：%s" % (where, pat))
    return m


def patch_index(slim):
    p = os.path.join(ROOT, "web", "index.html")
    h = open(p, encoding="utf-8", errors="replace").read()

    # 1) 换掉内嵌大数组（数组与后面的 __entriesReady 之间可能有换行/CRLF）
    m = must_search(r"var ALL_ENTRIES = \[.*?\];\s*var __entriesReady = false;",
                    h, "index.html 数组")
    new_arr = "var ALL_ENTRIES = " + slim + ";\nvar __entriesReady = false;"
    h = h[:m.start()] + new_arr + h[m.end():]

    # 2) 删掉 fetch 块（内嵌已是全量，再拉一次纯浪费；失败兜底逻辑一并失效）
    i = must_find(h, "fetch('dictionary.json')", "index.html fetch")
    m = must_search(r"\r?\n[ \t]*\}\);", h, "index.html fetch 块结束", i)
    block = (
        "/* 内嵌词库已是全量（构建时由 dictionary.json 同步生成），不再 fetch ——\r\n"
        "   省一次 571KB 请求，也避免「先内嵌后覆盖」的双重下载。 */\r\n"
        "__entriesReady = true;\r\n"
        "__entriesWaiters.splice(0).forEach(function (fn) { fn(); });"
    )
    h = h[:i] + block + h[m.end():]

    open(p, "w", encoding="utf-8", newline="").write(h)
    return p


def patch_dictionary(slim):
    p = os.path.join(ROOT, "web", "dictionary.html")
    h = open(p, encoding="utf-8", errors="replace").read()

    # 1) 空数组 -> 内嵌精简索引
    old = "var ALL_ENTRIES = [];"
    i = must_find(h, old, "dictionary.html 空数组")
    h = h[:i] + "var ALL_ENTRIES = " + slim + ";" + h[i + len(old):]

    # 2) load() 里的 fetch -> 直接用内嵌数据
    i = must_find(h, "fetch('dictionary.json')", "dictionary.html fetch")
    m = must_search(r"\r?\n[ \t]*\}\);", h, "dictionary.html fetch 块结束", i)
    block = (
        "/* 内嵌精简索引已是全量（构建时由 dictionary.json 同步生成），不再 fetch ——\r\n"
        "       省一次 571KB 请求，也避免首屏白屏等网络。 */\r\n"
        "      if (!ALL_ENTRIES.length) {\r\n"
        "        el.chapters.innerHTML = '<p class=\"state state--error\">词条库为空，请刷新重试。</p>';\r\n"
        "        el.countNow.textContent = '词条库加载失败';\r\n"
        "        return;\r\n"
        "      }\r\n"
        "      start(ALL_ENTRIES);"
    )
    h = h[:i] + block + h[m.end():]

    open(p, "w", encoding="utf-8", newline="").write(h)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只报告不写盘")
    args = ap.parse_args()

    slim = build_slim()
    print("精简索引：%d 条 / %.0f KB（保留字段 %s）" % (
        slim.count("\n") - 1, len(slim.encode("utf-8")) / 1024, KEEP_FIELDS_NOTE))
    if args.dry:
        print("(dry run，未写盘)")
        return 0

    for p in (patch_index(slim), patch_dictionary(slim)):
        print("已改写:", os.path.relpath(p, ROOT), "→ %.0f KB" % (os.path.getsize(p) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
