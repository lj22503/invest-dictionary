# -*- coding: utf-8 -*-
"""
sync_all_entries.py —— 将 dictionary.json 同步进 index.html 内嵌 ALL_ENTRIES

背景：首页搜索框与章节卡片渲染的数据源是 index.html 中内嵌的 var ALL_ENTRIES 静态数组，
而不是直接读 dictionary.json。新增词条（每日热词）后如果不同步，新词条会“搜不到”。

用法：
    python scripts/sync_all_entries.py

规则：
1. 以 web/dictionary.json 为主源（顺序、id 以它为准），全量重建 ALL_ENTRIES。
2. 展示字段（slug/title/card_titles/related/next）优先沿用 index.html 中已有的同 slug 条目
   （历史版本已将 “_” 规范化为 “/” 展示），新词条直接用 dictionary.json 原值。
3. file 字段指向 web/terms/ 下真实存在的 HTML 文件，探测顺序：
   a. 已有 ALL_ENTRIES 中同 slug 的 file（已验证存在）
   b. terms/{slug}.html
   c. dictionary.json 的 filename（可能是 -final.html 旧命名）
   若三者都找不到磁盘文件，则报错退出，防止生成死链。
4. dictionary.json 中不存在的旧条目会被移除（如冗余的“打新”条目）。
5. 自动备份 index.html 到 web/temp/ 后写入。
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
INDEX = os.path.join(WEB, "index.html")
DICT_JSON = os.path.join(WEB, "dictionary.json")
TERMS = os.path.join(WEB, "terms")
TEMP = os.path.join(WEB, "temp")

def main():
    # 1. 读取 dictionary.json
    with open(DICT_JSON, encoding="utf-8") as f:
        djson = json.load(f)

    # 2. 读取 index.html 与现有 ALL_ENTRIES
    with open(INDEX, encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"var ALL_ENTRIES = (\[.*?\]);", html, re.S)
    if not m:
        print("错误：index.html 中未找到 var ALL_ENTRIES 数组")
        sys.exit(1)
    old_entries = json.loads(m.group(1))
    # 注意：dictionary.json 的 slug 用下划线（同磁盘文件名 stem），而 ALL_ENTRIES 的 slug 是
    # 斜杠展示版（如 "M0 / M1 / M2（货币供应量）"），因此必须用 file（磁盘文件名）作为匹配键，
    # 才能保留历史展示字段。
    # 同一 file 可能对应多条旧条目（如"新股"与"打新"指向同一 HTML），此时优先按 id 精确匹配，
    # 避免后写入的重复条目覆盖主条目的展示字段。
    old_by_file = {}
    for e in old_entries:
        old_by_file.setdefault(e.get("file"), e)
    old_by_id = {e["id"]: e for e in old_entries}

    # 3. 磁盘文件索引
    disk_files = {f for f in os.listdir(TERMS) if f.endswith(".html")}

    def resolve_file(e):
        slug = e["slug"]
        candidates = []
        if slug + ".html" in disk_files:
            candidates.append(slug + ".html")
        fn = e.get("filename", "")
        if fn and fn in disk_files:
            candidates.append(fn)
        # 优先已有 ALL_ENTRIES 中指向同一磁盘文件的条目
        for c in candidates:
            if c in old_by_file:
                return c
        if candidates:
            return candidates[0]
        return None

    # 4. 全量重建
    new_entries = []
    problems = []
    for e in djson:
        slug = e["slug"]
        fname = resolve_file(e)
        old = old_by_id.get(e["id"]) or old_by_file.get(fname)
        if fname is None:
            problems.append(f'id {e["id"]} {slug}: 无法定位磁盘文件')
            continue
        item = {
            "id": e["id"],
            "slug": (old or e)["slug"],
            "title": (old or e)["title"],
            "chapter": e.get("chapter", ""),
            "card_titles": (old or e).get("card_titles", []),
            "related": (old or e).get("related", []),
            "next": (old or e).get("next", ""),
            "filename": fname,
            "file": fname,
        }
        new_entries.append(item)

    if problems:
        print("存在无法解析的词条，已中止（防止产生死链）：")
        for p in problems:
            print(" ", p)
        sys.exit(1)

    # 5. 备份并替换
    os.makedirs(TEMP, exist_ok=True)
    bak = os.path.join(TEMP, "index.html.bak")
    shutil.copy2(INDEX, bak)

    new_text = "var ALL_ENTRIES = [\n" + ",\n".join(
        "  " + json.dumps(e, ensure_ascii=False, indent=2).replace("\n", "\n  ")
        for e in new_entries
    ) + "\n];"
    new_html = html[: m.start()] + new_text + html[m.end():]
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"同步完成：dictionary.json {len(djson)} 条 -> ALL_ENTRIES {len(new_entries)} 条")
    print(f"备份：{bak}")
    print(f"新增条目：{[e['slug'] for e in new_entries if e['id'] not in {o['id'] for o in old_entries}]}")
    new_ids = {x["id"] for x in new_entries}
    removed = [f'{e["id"]} {e["slug"]}' for e in old_entries if e["id"] not in new_ids]
    print(f"移除条目：{removed}")

if __name__ == "__main__":
    main()
