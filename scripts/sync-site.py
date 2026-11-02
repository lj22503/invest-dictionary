# -*- coding: utf-8 -*-
"""
sync-site.py —— 站点衍生产物统一同步入口（一条命令跑完全链路）

背景：
  词条入库后，需要手工跑多个脚本才能让manifest / llms.txt / sitemap / 首页内嵌数据
  全部跟上。漏跑任何一步，门禁就会 FAIL，且线上「新词条搜不到」。
  本脚本把散落的步骤编排成一件事，遵循「唯一数据源 = web/dictionary.json」原则。

执行顺序（有依赖：llms 依赖 index.html 的 ALL_ENTRIES，故 sync 必须最先）：
  0. strip-aigc-metadata.py  清掉外部生成器注入的 AIGC 水印头（必须最先）
  1. sync_all_entries.py      dictionary.json -> index.html 内嵌 ALL_ENTRIES
  2. slim-inline-data.py      首页/词典页内嵌数据瘦身
  3. fix-broken-links.py      词条页相对链接断链修复（--apply）
  4. stamp-freshness.py       JSON-LD dateModified + 可见「最后更新」
                              （必须在 sitemap 之前：sitemap 的 lastmod 同口径取 mtime）
  5. generate-sitemap.py      dictionary.json -> web/sitemap.xml（去 .html + lastmod）
  6. generate-llms.py         dictionary.json -> web/llms.txt       （去 .html）
  7. update-manifest-count.py dictionary.json -> manifest.json 计数
  8. check-consistency.py     提交前门禁，逐项 PASS/FAIL

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
    # 必须放最前：外部内容生成器会在 md 头部注入 AIGC 水印，后续步骤要把干净内容带上
    ("strip-aigc-metadata.py", "清除 AIGC 元数据头 / 去重尾部声明"),
    ("sync_all_entries.py", "首页 ALL_ENTRIES 同步"),
    # 必须紧随 sync：首页/词库页的服务端静态锚点（P0-2 内链图）由本脚本重建。
    # 漏跑它 = 静态块冻结在旧条数，新词条对不执行 JS 的爬虫「不存在」。
    (("build-static-terms.py", "--apply"), "首页/词库页静态词条锚点重建"),
    ("slim-inline-data.py", "首页/词库页内嵌数据瘦身 + 去重复下载"),
    (("fix-broken-links.py", "--apply"), "词条页相对链接断链修复"),
    # cron 的内容生成器仍按旧模板产出带 .html 的 canonical / og:url / 相关链接，
    # 每天复发（P1-5）。改不动那个模板，就在链路里每次自动规范化——幂等，二次跑 0 处。
    (("normalize-urls.py", "--apply"), "全站 URL 去 .html 后缀（P0-1 防复发）"),
    ("stamp-freshness.py", "dateModified / 可见更新日期盖章"),
    ("generate-sitemap.py", "sitemap.xml 重建（含 lastmod）"),
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
