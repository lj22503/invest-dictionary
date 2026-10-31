# -*- coding: utf-8 -*-
"""
sync-site.py —— 站点衍生产物统一同步入口（一条命令跑完全链路）

背景：
  词条入库后，需要手工跑多个脚本才能让manifest / llms.txt / sitemap / 首页内嵌数据
  全部跟上。漏跑任何一步，门禁就会 FAIL，且线上「新词条搜不到」。
  本脚本把散落的步骤编排成一件事，遵循「唯一数据源 = web/dictionary.json」原则。

执行顺序（有依赖：llms 依赖 index.html 的 ALL_ENTRIES，故 sync 必须最先）：
  1. sync_all_entries.py      dictionary.json -> index.html 内嵌 ALL_ENTRIES
  2. generate-sitemap.py      dictionary.json -> web/sitemap.xml    （去 .html）
  3. generate-llms.py         dictionary.json -> web/llms.txt       （去 .html）
  4. update-manifest-count.py dictionary.json -> manifest.json 计数
  5. check-consistency.py     提交前门禁，逐项 PASS/FAIL

用法：
  python scripts/sync-site.py             # 同步 + 跑门禁
  python scripts/sync-site.py --no-gate   # 只同步，不跑门禁
"""
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")

STEPS = [
    ("sync_all_entries.py", "首页 ALL_ENTRIES 同步"),
    ("slim-inline-data.py", "首页/词典页内嵌数据瘦身 + 去重复下载"),
    (("fix-broken-links.py", "--apply"), "词条页相对链接断链修复"),
    ("generate-sitemap.py", "sitemap.xml 重建"),
    ("generate-llms.py", "llms.txt 重建"),
    ("update-manifest-count.py", "manifest.json 计数对齐"),
]


def run(step, desc):
    # step 可以是 "xxx.py"（无参）或 ("xxx.py", "--apply")（带参）
    name, args = step if isinstance(step, tuple) else (step, ())
    print("\n" + "-" * 60)
    print("[STEP] %s %s —— %s" % (name, " ".join(args), desc))
    print("-" * 60)
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, name)] + list(args),
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    out = (r.stdout or "") + (r.stderr or "")
    if out.strip():
        print(out.strip())
    if r.returncode != 0:
        print("!!! %s 失败（exit=%d），后续步骤已中止" % (name, r.returncode))
        return False
    return True


def main():
    no_gate = "--no-gate" in sys.argv
    print("=" * 60)
    print("站点全链路同步")
    print("=" * 60)

    for name, desc in STEPS:
        if not run(name, desc):
            return 1

    if no_gate:
        print("\n（--no-gate：已跳过门禁）")
        return 0

    print("\n" + "-" * 60)
    print("[GATE] check-consistency.py")
    print("-" * 60)
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "check-consistency.py")],
                       cwd=ROOT, text=True, encoding="utf-8")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
