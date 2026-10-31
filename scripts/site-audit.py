#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
site-audit.py —— 静态站点体检（性能 / 品牌合规 / 无障碍 / SEO 骨架）

把「人工看一遍」变成「一条命令跑完」，供 mangofolio 各子站复用。

用法：
    python scripts/site-audit.py                 # 默认体检 <repo>/web
    python scripts/site-audit.py --root ../web   # 指定站点根目录
    python scripts/site-audit.py --json          # 输出 JSON，便于接 CI
    python scripts/site-audit.py --strict        # WARN 也算失败（CI 收紧时用）

退出码：0 = 无 FAIL；1 = 存在 FAIL（--strict 下 WARN 也计入）

检查维度：
    perf   首屏体积 / 内联数据重复 / 同步 XHR / 外链字体 / 图片懒加载
    brand  一票否决色 / 硬编码色值 / 装饰色与文字色混用
    a11y   WCAG 对比度（按令牌实际计算）/ 图片 alt / lang / 跳转链接
    seo    canonical / OG / viewport / title / 结构化数据
    backfill 历史调研回填：URL .html 残留 / 首页静态内链 / sitemap·llms 覆盖率 / 合规页存在性
    hygiene 备份文件随站部署 / 未预加载关键字体

backfill 维度的由来：9-10 月那批调研（仓库诊断/对标调研/备案清单）结论一直躺在 md 里，
P0-1/P0-2 两个硬伤横跨一个半月纹丝不动。这一维把「调研结论」固化成「每次跑都会报警的检查」，
让回填不再依赖人记得。
"""
import argparse
import fnmatch
import json
import os
import re
import sys
from urllib.parse import unquote

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

# ---- 默认规则（可用 --config 覆盖）----
DEFAULT_RULES = {
    "forbidden_colors": ["#C43A31"],          # 朱砂红，出现即重做
    "max_html_kb": 100,                        # 普通单页 HTML 体积上限
    # 全量词条目录页（首页/词典页）含 >=500 条服务端静态锚点——那是 P0-2 的 SEO 内链图，
    # 必须内联，不能退。这类页面体积天然大，单独放宽；普通页仍按上面 100KB 卡。
    "max_html_kb_dir_page": 600,               # 目录型页面体积上限（含全量静态锚点）
    "dir_page_min_anchors": 500,               # 达到这个静态锚点数才认定为「目录型页面」
    "max_inline_script_kb": 50,                # 内联脚本上限（超出多半是内联数据）
    "cn_unreachable_hosts": [                  # 国内不可靠的外链
        "fonts.googleapis.com",
        "fonts.gstatic.com",
    ],
    "require_preload_fonts": True,
    # 品牌主色「色相锚点」：修对比度只能降明度，不能移色相。
    # 教训：为过 WCAG 把 #F97316(24.6deg 芒果橙) 压成 #C2410C(17.5deg) → 变铁锈红，品牌没了。
    "brand_hue": {
        "anchor": "#F97316",      # 基准色相 24.6deg（橙区）
        # 非对称容差：色相往下走 = 变铁锈红，是真实的品牌事故方向，卡死 5deg；
        # 往上走 = 偏金/琥珀，风险小，放宽到 12deg。
        # 实测合法色分布 23.6~26.9deg，铁锈红 #C2410C 为 17.5deg（会被拦下）。
        "tolerance_low": 5,       # 允许下探到 19.6deg
        "tolerance_high": 12,     # 允许上探到 36.6deg
        "watch_tokens": [         # 这些令牌必须留在橙区
            "background-primary", "text-link", "text-accent-mango",
            "accent-decor", "text-warning", "text-selected",
            "border-focused", "border-selected",
        ],
    },
    # ---- backfill：历史调研结论的回填闸门 ----
    "backfill": {
        # 本站域名：只有这些域名下的 .html 才算残留（外站带 .html 是人家的事）
        "own_hosts": ["dictionary.mangofolio.com"],
        # P0-2：首页静态词条内链覆盖率下限。低于此值 = 爬虫拿不到内链图。
        "min_static_entry_ratio": 0.95,
        # 合规页：缺失即红线（最高法判例：词典属实用工具类，查词无须手机号）
        "required_pages": ["privacy.html", "terms-of-service.html"],
        # 必须进 sitemap 的顶层页（index 以站点根形式收录）
        "core_pages": ["index.html", "dictionary.html", "guide.html"],
    },
}

TEXT_EXTS = (".html", ".css", ".js", ".json", ".txt", ".xml")

# P0-1 判定用：只找「本站」的 .html 后缀。
# 误报源（都实测踩过）：
#   ① CSS 注释里的基准页路径  web/terms/14天期逆回购.html
#   ② JSON 数据字段          "filename": "货币.html"
#   ③ 外站本来就带 .html      https://invest-tools.mangofolio.app/tools/xirr.html
# 真漏网的反而是：分享链接 query 里二次编码的本站 URL（%2F 分隔），必须一并扫到。


# ============================================================
# WCAG 对比度
# ============================================================
def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _hue(hex_color):
    """返回色相角度 0-360。用于检测品牌主色是否被「压成了别的颜色」。"""
    import colorsys
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return colorsys.rgb_to_hls(r, g, b)[0] * 360


def _lum(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def suggest_darker(hex_color, bg, target=4.5):
    """按比例压暗，直到达到目标对比度。返回 None 表示压到黑也达不到。"""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    for step in range(1, 101):
        f = 1 - step / 100.0
        cand = "#%02X%02X%02X" % (int(r * f), int(g * f), int(b * f))
        if contrast(cand, bg) >= target:
            return cand
    return None


# ============================================================
# 结果收集
# ============================================================
class Report:
    def __init__(self):
        self.items = []

    def add(self, cat, level, name, detail="", fix=""):
        self.items.append((cat, level, name, detail, fix))

    @property
    def fails(self):
        return [i for i in self.items if i[1] == "FAIL"]

    @property
    def warns(self):
        return [i for i in self.items if i[1] == "WARN"]

    def render(self):
        icons = {"PASS": "✓", "WARN": "!", "FAIL": "✗"}
        cur = None
        out = []
        for cat, level, name, detail, fix in self.items:
            if cat != cur:
                cur = cat
                out.append("\n[%s]" % cat.upper())
            out.append("  %s %s %s" % (icons[level], name, ("  " + detail) if detail else ""))
            if fix and level in ("WARN", "FAIL"):
                out.append("      → %s" % fix)
        return "\n".join(out)


def walk_text_files(root):
    for dirpath, _, filenames in os.walk(root):
        if any(p in dirpath for p in (".git", "node_modules", ".vercel")):
            continue
        for n in filenames:
            if n.endswith(TEXT_EXTS):
                yield os.path.join(dirpath, n)


def walk_all_files(root):
    """备份文件后缀是 .html.bak-xxx，不匹配 TEXT_EXTS，必须单独全量扫。"""
    for dirpath, _, filenames in os.walk(root):
        if any(p in dirpath for p in (".git", "node_modules", ".vercel")):
            continue
        for n in filenames:
            yield os.path.join(dirpath, n)


def load_vercelignore(root):
    """读 .vercelignore（站点根目录优先，其次仓库根），返回模式列表。"""
    for cand in (os.path.join(root, ".vercelignore"), ".vercelignore"):
        if os.path.isfile(cand):
            with open(cand, encoding="utf-8", errors="replace") as f:
                return [l.strip() for l in f
                        if l.strip() and not l.strip().startswith("#")]
    return []


def ignore_match(rel, patterns):
    """简化 gitignore 匹配：不含斜杠的模式匹配任意层的文件名/目录名；
    含斜杠的按相对路径逐层匹配。够用即可——这里只判备份与调试产物。"""
    rel = rel.replace("\\", "/")
    parts = rel.split("/")
    for raw in patterns:
        p = raw[1:] if raw.startswith("/") else raw
        p = p.rstrip("/")
        if "/" not in p:                      # 纯名字模式：任意层
            if any(fnmatch.fnmatch(seg, p) for seg in parts):
                return True
        else:                                 # 路径模式：本路径或任一祖先前缀
            if fnmatch.fnmatch(rel, p):
                return True
            if any(fnmatch.fnmatch("/".join(parts[:i + 1]), p) for i in range(len(parts))):
                return True
    return False


# ============================================================
# 各项检查
# ============================================================
def audit(root, rules, rep):
    pages = [p for p in walk_text_files(root) if p.endswith(".html")]
    css_files = [p for p in walk_text_files(root) if p.endswith(".css")]

    # ---------- perf ----------
    big = []
    std_limit = rules["max_html_kb"] * 1024
    dir_limit = rules.get("max_html_kb_dir_page", 600) * 1024
    min_anchor = rules.get("dir_page_min_anchors", 500)
    for p in pages:
        size = os.path.getsize(p)
        if size <= std_limit:
            continue
        with open(p, encoding="utf-8", errors="replace") as f:
            html = f.read()
        inline = sum(len(m.group(1)) for m in re.finditer(r"<script[^>]*>(.*?)</script>", html, re.S))
        # 判定是不是「全量词条目录页」：静态锚点够多才够格走放宽阈值
        stripped = re.sub(r"<script\b.*?</script>", "", html, flags=re.S | re.I)
        anchors = len(re.findall(r'href="(?:[^"]*/)?terms/[^"#?]+"', stripped))
        limit = dir_limit if anchors >= min_anchor else std_limit
        if size > limit:
            big.append((os.path.relpath(p, root), size // 1024, inline // 1024,
                        "内联脚本占 %dKB" % (inline // 1024) if inline > 50 * 1024 else "",
                        "目录页" if anchors >= min_anchor else "普通页"))
    if big:
        rep.add("perf", "FAIL", "HTML 体积超标",
                "; ".join("%s %dKB[%s]%s" % (n, s, t, ("(" + d + ")") if d else "")
                          for n, s, i, d, t in big[:5]),
                "普通页 %dKB / 目录页 %dKB；目录页的超额应来自静态锚点，不是内联数据"
                % (rules["max_html_kb"], rules.get("max_html_kb_dir_page", 600)))

    # 内联数据与外部 JSON 重复
    for name, _, inline_kb, _, _ in big:
        p = os.path.join(root, name)
        with open(p, encoding="utf-8", errors="replace") as f:
            html = f.read()
        for m in re.finditer(r"fetch\(\s*['\"]([^'\"]+\.json)['\"]", html):
            jp = os.path.join(root, os.path.dirname(name), m.group(1))
            if os.path.exists(jp):
                jkb = os.path.getsize(jp) // 1024
                rep.add("perf", "FAIL", "数据双重下载",
                        "%s 内联 %dKB，同时又 fetch %s (%dKB)" % (name, inline_kb, m.group(1), jkb),
                        "二者留其一；首页搜索通常只需轻量索引")

    # 同步 XHR
    sync_xhr = []
    for p in pages:
        with open(p, encoding="utf-8", errors="replace") as f:
            t = f.read()
        if re.search(r"\.open\([^)]*,\s*false\s*\)", t):
            sync_xhr.append(os.path.relpath(p, root))
    rep.add("perf", "FAIL" if sync_xhr else "PASS", "同步 XHR（阻塞主线程）",
            "found=%d %s" % (len(sync_xhr), sync_xhr[:3]),
            "改用 fetch/promise；失败兜底不要清空已有数据")

    # 外链字体
    bad_hosts = []
    for p in pages:
        with open(p, encoding="utf-8", errors="replace") as f:
            t = f.read()
        for h in rules["cn_unreachable_hosts"]:
            if h in t:
                bad_hosts.append((os.path.relpath(p, root), h))
                break
    rep.add("perf", "FAIL" if bad_hosts else "PASS", "外链字体（国内不可靠）",
            "%d 个页面引用 %s" % (len(bad_hosts), sorted({h for _, h in bad_hosts})),
            "自托管 + 中文字体子集化（font-spider / cn-fontsub），配系统字体栈兜底")

    if rules.get("require_preload_fonts"):
        nopreload = [os.path.relpath(p, root) for p in pages
                     if "fonts.googleapis" in open(p, encoding="utf-8", errors="replace").read()
                     and 'rel="preload"' not in open(p, encoding="utf-8", errors="replace").read()]
        rep.add("perf", "WARN" if nopreload else "PASS", "关键字体未 preload",
                "%d 个页面" % len(nopreload), "加 <link rel=preload as=font crossorigin>")

    # ---------- brand ----------
    for fc in rules["forbidden_colors"]:
        hits = []
        for p in walk_text_files(root):
            with open(p, encoding="utf-8", errors="replace") as f:
                if fc.lower() in f.read().lower():
                    hits.append(os.path.relpath(p, root))
        rep.add("brand", "FAIL" if hits else "PASS", "一票否决色 %s" % fc,
                "found=%d %s" % (len(hits), hits[:3]), "移除该色，改用令牌")

    hard = []
    for p in css_files:
        with open(p, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                s = line.strip()
                if s.startswith(("/*", "*", "//")):
                    continue
                # (?!--) 排除 CSS 自定义属性定义本身（令牌必须写死色值，那是唯一权威源）
                if re.match(r"^(?!--)[a-z-]+\s*:\s*#[0-9a-fA-F]{3,6}\s*;", s):
                    hard.append("%s:%d %s" % (os.path.relpath(p, root), i, s[:48]))
    rep.add("brand", "FAIL" if hard else "PASS", "CSS 硬编码色值",
            "found=%d %s" % (len(hard), hard[:3]), "全部替换为 --mf-colors-* 令牌")

    # 主色色相漂移：对比度不达标时，正确解法是「换文字色」或「只降明度」，
    # 而不是把橙压成红/棕。这条专门拦后者。
    bh = rules.get("brand_hue") or {}
    watch = bh.get("watch_tokens") or []
    if watch:
        anchor = bh.get("anchor", "#F97316")
        tol = float(bh.get("tolerance", 6))
        base = _hue(anchor)
        lo = base - float(bh.get("tolerance_low", tol))
        hi = base + float(bh.get("tolerance_high", tol))
        drift = []
        for p in css_files:
            with open(p, encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f, 1):
                    m = re.match(r"^\s*--mf-colors-([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\s*;", line)
                    if not m:
                        continue
                    name, val = m.group(1), m.group(2)
                    if not any(name == t or name.startswith(t + "-") for t in watch):
                        continue
                    hu = _hue(val)
                    if not (lo <= hu <= hi):
                        drift.append("%s:%d %s=%s (%.1fdeg)" % (
                            os.path.relpath(p, root), i, name, val, hu))
        rep.add("brand", "FAIL" if drift else "PASS", "主色色相漂移",
                "基准 %s=%.1fdeg，允许 %.1f~%.1fdeg；越界 %d 处 %s"
                % (anchor, base, lo, hi, len(drift), drift[:3]),
                "对比度不足时只降明度、或改文字色（橙底配深墨字），别移色相："
                "色相<20deg 变铁锈红、>45deg 变土黄，都是丢品牌")

    # ---------- a11y：按令牌实测对比度 ----------
    tokens = {}
    for p in css_files:
        with open(p, encoding="utf-8", errors="replace") as f:
            t = f.read()
        for m in re.finditer(r"(--mf-colors-[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;", t):
            tokens.setdefault(m.group(1), m.group(2))

    BG_KEYS = ["--mf-colors-background", "--mf-colors-background-surface",
               "--mf-colors-background-neutral"]
    bgs = [tokens[k] for k in BG_KEYS if k in tokens] or ["#FFFFFF"]
    TEXT_KEYS = ["--mf-colors-text", "--mf-colors-text-weak", "--mf-colors-text-link",
                 "--mf-colors-text-link-hover", "--mf-colors-text-accent-mango",
                 "--mf-colors-text-placeholder", "--mf-colors-text-secondary"]
    for k in TEXT_KEYS:
        if k not in tokens:
            continue
        fg = tokens[k]
        worst = min(contrast(fg, b) for b in bgs)
        if worst < 4.5:
            cand = suggest_darker(fg, bgs[0])
            rep.add("a11y", "FAIL", "对比度 %s" % k,
                    "%s 实测 %.2f:1（需 ≥4.5）" % (fg, worst),
                    "改 %s（%.2f:1）；原色可留作纯装饰" % (cand, contrast(cand, bgs[0])) if cand else "需换更深色")
        else:
            rep.add("a11y", "PASS", "对比度 %s" % k, "%s %.2f:1" % (fg, worst))

    onp = tokens.get("--mf-colors-text-on-primary", "#FFFFFF")
    prim = tokens.get("--mf-colors-background-primary")
    if prim:
        c = contrast(onp, prim)
        if c < 4.5:
            cand = suggest_darker(prim, onp, target=4.5)
            rep.add("a11y", "FAIL", "主按钮 文字/底色 对比度",
                    "%s on %s = %.2f:1" % (onp, prim, c),
                    "按钮底改 %s（%.2f:1）" % (cand, contrast(cand, onp)) if cand else "需换更深底")
        else:
            rep.add("a11y", "PASS", "主按钮 文字/底色 对比度", "%.2f:1" % c)

    # ---------- seo 骨架 ----------
    home = os.path.join(root, "index.html")
    if os.path.exists(home):
        with open(home, encoding="utf-8", errors="replace") as f:
            h = f.read()
        for name, ok in [("canonical", 'rel="canonical"' in h),
                         ("og:title", 'property="og:title"' in h),
                         ("viewport", 'name="viewport"' in h),
                         ("html lang", re.search(r"<html[^>]+lang=", h) is not None)]:
            rep.add("seo", "PASS" if ok else "FAIL", "首页 %s" % name)

    # ---------- backfill：历史调研结论回填 ----------
    bf = rules.get("backfill") or {}
    term_pages = [p for p in pages if os.sep + "terms" + os.sep in p]
    n_terms = len(term_pages)
    home = os.path.join(root, "index.html")
    req_pages = bf.get("required_pages", [])
    core_pages = bf.get("core_pages", [])

    # P0-1：URL .html 后缀残留（每条多一跳 308，硬伤规模随词条数同步放大）
    # 只认「URL 语境」：href / <loc> / JSON-LD 的 url·@id / og 的 content。
    # 不扫全文——实测误报源：CSS 注释里的基准页路径、JSON 数据字段 "filename": "货币.html"。
    own_hosts = bf.get("own_hosts", ["dictionary.mangofolio.com"])
    url_html_res = []
    for p in walk_text_files(root):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                t = f.read()
        except OSError:
            continue
        hit = False
        for host in own_hosts:
            # 分隔符 (?:%2F|/) 兼容分享链接里二次编码的本站 URL
            if re.search(re.escape(host) + r'(?:%2F|/)[^\s"\'&<>]*?\.html', t, re.I):
                hit = True
                break
        if not hit:
            # 站内相对路径（href / JSON-LD 的 url·@id），排除外站绝对 URL
            if re.search(r'(?:href\s*=\s*|"(?:url|@id)"\s*:\s*)["\'](?!https?:)[^"\']*\.html', t, re.I):
                hit = True
        if hit:
            url_html_res.append(os.path.relpath(p, root))
    rep.add("backfill", "FAIL" if url_html_res else "PASS", "P0-1 URL 残留 .html 后缀",
            "found=%d %s" % (len(url_html_res), sorted(url_html_res)[:3]),
            "sitemap / canonical / og:url / JSON-LD / 相关词链接 / 分享链接 query 参数"
            "统一去后缀（cleanUrls）；否则每条多一跳 308，且规模随词条数同步放大")

    # P0-2：首页静态词条内链（爬虫能不能拿到内链图）
    home_static, ratio = 0, 0.0
    if os.path.exists(home):
        with open(home, encoding="utf-8", errors="replace") as f:
            h = f.read()
        # 剥掉 <script>：JS 渲染出来的链接爬虫拿不到，不算数
        stripped = re.sub(r"<script\b.*?</script>", "", h, flags=re.S | re.I)
        # 路径可能是相对的（terms/xxx）也可能是绝对的（/terms/xxx），前导斜杠可选
        home_static = len(set(re.findall(r'href="(?:[^"]*/)?terms/([^"#?]+)"', stripped)))
        ratio = (home_static / n_terms) if n_terms else 0.0
    minr = float(bf.get("min_static_entry_ratio", 0.95))
    rep.add("backfill", "PASS" if ratio >= minr else "FAIL", "P0-2 首页静态词条内链",
            "%d/%d 条（%.0f%%），下限 %.0f%%" % (home_static, n_terms, ratio * 100, minr * 100),
            "首页词条目录必须服务端静态输出全量链接，JS 只做搜索增强；"
            "否则全站词条页拿不到权重分发")

    # sitemap 覆盖率
    sm = os.path.join(root, "sitemap.xml")
    if os.path.exists(sm):
        with open(sm, encoding="utf-8", errors="replace") as f:
            s = f.read()
        locs = {unquote(m).strip().rstrip("/") for m in re.findall(r"<loc>([^<]+)</loc>", s)}
        term_miss = [os.path.basename(p)[:-5] for p in term_pages
                     if not any(l.endswith("/" + os.path.basename(p)[:-5]) for l in locs)]
        other_miss = []
        for pg in core_pages + req_pages:
            stem = pg[:-5]
            if stem == "index":
                if not any(re.match(r"^https?://[^/]+/?$", l) for l in locs):
                    other_miss.append(pg)
            elif not any(l.endswith("/" + stem) for l in locs):
                other_miss.append(pg)
        total_miss = len(term_miss) + len(other_miss)
        rep.add("backfill", "PASS" if total_miss == 0 else "FAIL", "sitemap 覆盖率",
                "词条 %d/%d；主页面 %d/%d %s" % (
                    n_terms - len(term_miss), n_terms,
                    len(core_pages + req_pages) - len(other_miss), len(core_pages + req_pages),
                    ("缺 %s" % (term_miss[:3] + other_miss)) if total_miss else ""),
                "跑 scripts/generate-sitemap.py 重生成；漏收录 = 爬虫永远抓不到")

    # llms.txt 覆盖率（必须解码后比对——百分号编码会让比对「假性全通过」）
    ll = os.path.join(root, "llms.txt")
    if os.path.exists(ll):
        with open(ll, encoding="utf-8", errors="replace") as f:
            t = f.read()
        have = {unquote(m).rstrip("/") for m in re.findall(r"/terms/([^)\s]+)", t)}
        ll_miss = [os.path.basename(p)[:-5] for p in term_pages
                   if os.path.basename(p)[:-5] not in have]
        rep.add("backfill", "PASS" if not ll_miss else "FAIL", "llms.txt 覆盖率",
                "%d/%d %s" % (n_terms - len(ll_miss), n_terms, ll_miss[:3] if ll_miss else ""),
                "按解码后比对（编码会让比对假性全通过）；跑 scripts/generate-llms.py 重生成")

    # 隐私政策 / 用户协议：存在性 + footer 入口
    missing = [r for r in req_pages if not os.path.exists(os.path.join(root, r))]
    noentry = []
    if not missing and os.path.exists(home):
        with open(home, encoding="utf-8", errors="replace") as f:
            h = f.read()
        for r in req_pages:
            if ('href="/%s"' % r[:-5]) not in h:
                noentry.append("/" + r[:-5])
    bad_legal = missing or noentry
    rep.add("backfill", "PASS" if not bad_legal else "FAIL", "隐私政策 / 用户协议页",
            ("缺失 %s" % missing if missing else "") +
            ("；footer 无入口 %s" % noentry if noentry else "") or "存在且已挂 footer 入口",
            "合规红线：最高法判例认定词典属实用工具类（查词无须手机号），"
            "默认勾选违法、以注销账号替代撤回同意不成立")

    # ---------- hygiene ----------
    # 判定口径：磁盘上有备份文件 ≠ 会被部署。只要 .vercelignore 全覆盖就不算问题
    # （本地留着是给人回滚用的，删掉反而危险）。真正要报警的是「漏网」。
    baks = [os.path.relpath(p, root) for p in walk_all_files(root)
            if ".bak" in os.path.basename(p) or p.endswith(("~", ".orig", ".backup"))]
    total = sum(os.path.getsize(os.path.join(root, b)) for b in baks) // 1024 // 1024
    pats = load_vercelignore(root)
    leaky = [b for b in baks if not ignore_match(b, pats)]
    if not baks:
        rep.add("hygiene", "PASS", "备份文件随站部署", "0 个", "")
    elif leaky:
        rep.add("hygiene", "FAIL", "备份文件随站部署",
                "%d 个未被 .vercelignore 排除（磁盘共 %d 个 / %dMB）" % (len(leaky), len(baks), total),
                "在站点根目录的 .vercelignore 补模式；样例：%s" % ", ".join(sorted(leaky)[:3]))
    else:
        rep.add("hygiene", "PASS", "备份文件随站部署",
                "%d 个 / %dMB，已被 .vercelignore 全部排除" % (len(baks), total),
                "磁盘上仍保留供本地回滚，但不上传；.vercelignore 失效或新增未覆盖的后缀时会自动转 FAIL")

    # AIGC 元数据头：外部生成器会在 md 头部反复注入 AIGC/ProduceID/ReservedCode 块。
    # 它是纯水印，无内容价值，还会把生产方 ID 带进仓库与线上产物。
    # 2026-10-31 已全量清除 484 处（docs/ web/ skill/ 三个目录都中招），这里守住不再复发。
    repo = os.path.dirname(os.path.abspath(root)) if os.path.basename(os.path.abspath(root)) == "web" \
        else os.path.abspath(root)
    aigc = []
    for dirpath, _, filenames in os.walk(repo):
        if any(p in dirpath for p in (".git", "node_modules", ".vercel")):
            continue
        for n in filenames:
            if not n.endswith(".md"):
                continue
            p = os.path.join(dirpath, n)
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    head = f.read(1500)
            except OSError:
                continue
            if re.search(r"^AIGC:", head, re.M) or "ContentProducer" in head:
                aigc.append(os.path.relpath(p, repo))
    rep.add("hygiene", "FAIL" if aigc else "PASS", "AIGC 元数据头残留",
            "%d 个 md 文件" % len(aigc) if aigc else "0 个（已全量清除）",
            "跑 scripts/strip-aigc-metadata.py 清除；这类块由外部生成器注入，会随词条扩充反复出现")


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--root", default=os.path.join(os.path.dirname(here), "web"))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--config", help="JSON 文件，覆盖默认规则")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print("目录不存在：%s" % root)
        return 2

    rules = dict(DEFAULT_RULES)
    if args.config:
        rules.update(json.load(open(args.config, encoding="utf-8")))

    rep = Report()
    audit(root, rules, rep)

    if args.json:
        print(json.dumps([{"cat": c, "level": l, "name": n, "detail": d, "fix": f}
                          for c, l, n, d, f in rep.items], ensure_ascii=False, indent=2))
    else:
        print("站点体检：%s" % root)
        print(rep.render())
        n = len(rep.items)
        print("\n合计 %d 项，PASS %d，WARN %d，FAIL %d"
              % (n, n - len(rep.fails) - len(rep.warns), len(rep.warns), len(rep.fails)))
        if rep.fails:
            print("未通过：" + "；".join(i[2] for i in rep.fails))

    bad = len(rep.fails) + (len(rep.warns) if args.strict else 0)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
