# -*- coding: utf-8 -*-
"""
stamp-freshness.py —— 全站「新鲜度信号」落章（SEO P0-3）

体检发现：sitemap 无 lastmod、词条页无 dateModified、页面上看不到任何日期，
爬虫与 AI 都无法判断内容是不是新的；YMYL（理财）领域尤其吃亏。

本脚本补齐两处，且必须幂等（cron 每天新增词条，脚本要能天天跑）：
  1. 词条页 JSON-LD 加 "dateModified":"YYYY-MM-DD"
  2. 词条页标题下可见一行「最后更新：YYYY-MM-DD」
  3. 主页面（index/dictionary/guide/about/privacy/terms-of-service）JSON-LD 同步 dateModified

日期口径的坑（踩过一次，别改回去）：
  ❌ 用 mtime —— 本脚本自己写文件就会刷新 mtime，下一轮把日期读到「今天」，
     于是每次跑全站日期跳一遍，816 页反复重写，是彻头彻尾的假新鲜度。
  ❌ 用「今天」 —— 同上。
  ✅ 用 git 最后一次改动该文件的提交时间（内容真变了才会变）；
     未入库的新文件回退到 mtime。写盘后再用 os.utime 把 mtime 还原回去，
     保证「跑脚本」这件事本身不算一次内容更新。

用法：python scripts/stamp-freshness.py [--dry]
"""
import io
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
TERMS = os.path.join(WEB, "terms")
TERMS_MD = os.path.join(WEB, "terms_md")

MAIN_PAGES = ["index.html", "dictionary.html", "guide.html", "about.html",
              "privacy.html", "terms-of-service.html"]

DRY = "--dry" in sys.argv


def ymd(ts):
    return time.strftime("%Y-%m-%d", time.localtime(ts))


_git_cache = None


def git_mtimes():
    """一次性取全库「每个文件最后一次被提交改动的时间」。
    git log 默认按时间倒序，因此每个路径只记第一次出现即可。
    """
    global _git_cache
    if _git_cache is not None:
        return _git_cache
    _git_cache = {}
    try:
        import subprocess
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "--pretty=format:T\t%ct", "--name-only"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=180)
        cur = None
        for line in out.stdout.split("\n"):
            if line.startswith("T\t"):
                cur = int(line[2:].strip() or 0)
            elif line.strip() and cur and line not in _git_cache:
                _git_cache[line.strip()] = cur
    except Exception:
        pass
    return _git_cache


def stamp_date(html_path):
    """HTML 与其 md 源中较新的「真实变更时间」：git 提交时间优先，回退 mtime。"""
    rel = os.path.relpath(html_path, ROOT).replace("\\", "/")
    stem = os.path.splitext(os.path.basename(html_path))[0]
    rel_md = os.path.relpath(os.path.join(TERMS_MD, stem + ".md"), ROOT).replace("\\", "/")
    g = git_mtimes()
    ts = g.get(rel)
    if rel_md in g:
        ts = max(ts, g[rel_md]) if ts else g[rel_md]
    if ts:
        return ymd(ts)
    # 未入库的新文件：回退 mtime
    mts = os.path.getmtime(html_path)
    md = os.path.join(TERMS_MD, stem + ".md")
    if os.path.exists(md):
        mts = max(mts, os.path.getmtime(md))
    return ymd(mts)


def add_date_modified(blk, date):
    """给 JSON-LD 块补/改 dateModified。保持原缩进风格。"""
    if re.search(r'^\s*"dateModified"\s*:', blk, re.M):
        new = re.sub(r'(^\s*"dateModified"\s*:\s*")[^"]*(")',
                     lambda m: m.group(1) + date + m.group(2), blk, count=1, flags=re.M)
        return new, new != blk
    # 插到 "@context" 之后（多数块）或首行之后
    m = re.search(r'^((\s*)"@context"\s*:\s*"[^"]*",?\s*\n)', blk, re.M)
    if m:
        indent = m.group(2)
        ins = '%s"dateModified": "%s",\n' % (indent, date)
        return blk[:m.end()] + ins + blk[m.end():], True
    m = re.search(r'^(\s*\{\s*\n)', blk)
    if m:
        indent = "  "
        ins = '%s"dateModified": "%s",\n' % (indent, date)
        return blk[:m.end()] + ins + blk[m.end():], True
    return blk, False


def process(path, with_visible):
    raw = io.open(path, encoding="utf-8", newline="").read()
    stat = os.stat(path)
    date = stamp_date(path)
    t = raw
    changed = False

    # ---- 1. JSON-LD dateModified ----
    parts = re.split(r'(<script type="application/ld\+json">.*?</script>)', t, flags=re.S)
    for i, seg in enumerate(parts):
        if not seg.startswith('<script type="application/ld+json">'):
            continue
        head = seg[:seg.find(">") + 1]
        tail = "</script>"
        blk = seg[len(head):-len(tail)]
        try:
            json.loads(blk)
        except Exception:
            continue  # 坏了的不碰（site-audit 会报）
        nb, ch = add_date_modified(blk, date)
        if ch:
            parts[i] = head + nb + tail
            changed = True
    t = "".join(parts)

    # ---- 2. 可见日期（仅词条页）----
    if with_visible:
        m = re.search(r'(<p class="subtitle">)(.*?)(</p>)', t, re.S)
        if m:
            base = re.sub(r'\s*[·•]\s*最后更新：\d{4}-\d{2}-\d{2}', '', m.group(2)).rstrip()
            new = base + " · 最后更新：" + date
            if new != m.group(2):
                t = t[:m.start()] + m.group(1) + new + m.group(3) + t[m.end():]
                changed = True

    if changed and not DRY and t != raw:
        io.open(path, "w", encoding="utf-8", newline="").write(t)
        # 还原 mtime：盖章不算内容更新，否则下一轮日期自引用漂移
        os.utime(path, (stat.st_atime, stat.st_mtime))
    return changed


def main():
    n = 0
    for f in sorted(os.listdir(TERMS)):
        if not f.endswith(".html"):
            continue
        if process(os.path.join(TERMS, f), with_visible=True):
            n += 1
    m = 0
    for name in MAIN_PAGES:
        p = os.path.join(WEB, name)
        if os.path.exists(p) and process(p, with_visible=False):
            m += 1
    print("%s词条页 %d 个 / 主页面 %d 个 已盖章（新鲜度 dateModified）"
          % ("[dry] " if DRY else "", n, m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
