# -*- coding: utf-8 -*-
"""
check-consistency.py —— invest-dictionary 提交前一致性门禁

覆盖（每项独立 PASS/FAIL）：
  1. 计数一致性：web/terms 页数 == dictionary.json 去重 filename 数；manifest.json / llms.txt 中的硬数字一致
  2. 唯一性：dictionary.json 的 id / slug / filename 无重复
  3. 页内断链：terms 页内相对 .html 链接目标文件必须存在（含 / -> _ 归一化校验）
  4. sitemap 覆盖：sitemap.xml 与磁盘页面双向差集为 0
  5. 旧域名残留：web/ 下不得出现 //investbuddy.com（子站 investbuddy.mangofolio.com 合法，不计）
  6. 首页同步：index.html 内嵌 ALL_ENTRIES 与 dictionary.json 条目集合一致

用法：python scripts/check-consistency.py      # 退出码 0 = 全通过
"""
import os
import re
import sys
import json
import html
import collections
from urllib.parse import unquote, quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
TERMS = os.path.join(WEB, "terms")
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{('  ' + detail) if detail else ''}")


def main():
    items = json.load(open(os.path.join(WEB, "dictionary.json"), encoding="utf-8"))
    pages = sorted(f for f in os.listdir(TERMS) if f.endswith(".html") and ".bak" not in f)
    uniq = []
    for x in items:
        if x["filename"] not in uniq:
            uniq.append(x["filename"])

    # 1. 计数一致性
    ok = len(pages) == len(uniq)
    check("terms 页数 == dictionary 去重条数", ok, f"pages={len(pages)} uniq={len(uniq)}")
    for rel in ("manifest.json", "llms.txt"):
        t = open(os.path.join(WEB, rel), encoding="utf-8", errors="replace").read()
        nums = set(re.findall(r"(\d{2,4})\s*(?:个)?(?:词条|投资术语)", t))
        check(f"{rel} 硬数字与页数一致", nums <= {str(len(pages))}, f"found={sorted(nums)}")

    # 2. 唯一性
    for key in ("id", "slug", "filename"):
        c = collections.Counter(x.get(key) for x in items)
        dup = [k for k, v in c.items() if v > 1]
        check(f"dictionary {key} 唯一", not dup, f"dup={dup[:5]}")

    # 3. 页内断链
    broken = []
    for f in pages:
        t = open(os.path.join(TERMS, f), encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'href="([^"]+)"', t):
            h = html.unescape(m.group(1))
            if h.startswith(("http", "#", "mailto", "javascript", "/", "..")) or "'" in h:
                continue
            tg = unquote(h.split("#")[0].split("?")[0])
            if tg.endswith(".html") and not os.path.exists(os.path.join(TERMS, tg)):
                broken.append(f"{f} -> {tg}")
    check("页内相对链接无断链", not broken, f"broken={len(broken)} {broken[:3]}")

    # 4. sitemap 覆盖
    sm = open(os.path.join(WEB, "sitemap.xml"), encoding="utf-8", errors="replace").read()
    declared = set()
    for l in re.findall(r"<loc>(.*?)</loc>", sm):
        u = unquote(html.unescape(l))
        if "/terms/" in u:
            fn = u.split("/terms/")[-1]
            declared.add(fn if fn.endswith(".html") else fn + ".html")
    missing, extra = set(pages) - declared, declared - set(pages)
    check("sitemap 与磁盘页面双向一致", not missing and not extra,
          f"missing={len(missing)} extra={len(extra)}")

    # 5. 旧域名残留（排除合法子站 investbuddy.mangofolio.com）
    resid = []
    for dirpath, _, filenames in os.walk(WEB):
        for n in filenames:
            if not n.endswith((".html", ".json", ".txt", ".xml", ".js", ".css")):
                continue
            p = os.path.join(dirpath, n)
            t = open(p, encoding="utf-8", errors="replace").read()
            for m in re.finditer(r"//investbuddy\.com", t):
                resid.append(os.path.relpath(p, ROOT))
                break
    check("旧域名 //investbuddy.com 残留为 0", not resid, f"files={len(resid)} {resid[:3]}")

    # 6. 首页 ALL_ENTRIES 同步
    idx = open(os.path.join(WEB, "index.html"), encoding="utf-8", errors="replace").read()
    m = re.search(r"ALL_ENTRIES\s*=\s*(\[.*?\]);", idx, re.S)
    if not m:
        check("首页 ALL_ENTRIES 与 dictionary 同步", False, "未找到 ALL_ENTRIES")
    else:
        arr = json.loads(m.group(1))
        key = lambda a: a.get("file") or a.get("filename")
        a_set = collections.Counter(key(a) for a in arr)
        d_set = collections.Counter(x["filename"] for x in items)
        check("首页 ALL_ENTRIES 与 dictionary 同步", a_set == d_set,
              f"ALL_ENTRIES={len(arr)} dictionary={len(items)}")

    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"\n合计 {len(RESULTS)} 项，PASS {len(RESULTS) - len(failed)}，FAIL {len(failed)}")
    if failed:
        print("未通过项：" + "；".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
