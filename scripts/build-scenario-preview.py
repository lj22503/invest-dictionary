#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 web/data/hot-scenarios.json 渲染成单页 HTML，用于预览「当日 8 场景」长什么样。

产物：dist/scenario-preview.html（不入库、不部署、不接入站点）
用途：验证数据形态够不够撑一个真实模块；确认后再决定接到哪个展示面。

用法：
  python scripts/build-scenario-preview.py
"""
import html
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "web" / "data" / "hot-scenarios.json"
OUT = ROOT / "dist" / "scenario-preview.html"

# 场景 → Skill 展示名（与 skill/skills 的 display_name 对齐）
SKILL_OF = {
    "查词学词": "投资翻译",
    "看新闻": "新闻拆解",
    "持仓亏了": "理财痛点",
    "产品对比": "产品对比",
    "重大决定": "财务决策",
    "防坑提问": "话术防坑",
    "复杂事件": "概念串联",
    "今日热词": "热点追踪",
}

MD_LINK = re.compile(r"^\[([^\]]+)\]\((https?://[^)]+)\)$")


def esc(s):
    return html.escape(s, quote=True)


def render_sources(sources):
    out = []
    for s in sources:
        m = MD_LINK.match(s.strip())
        if m:
            text, url = m.group(1), m.group(2)
            out.append(
                f'<li><a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a></li>'
            )
        else:
            out.append(f"<li><span>{esc(s)}</span></li>")
    return "\n".join(out)


def render_card(i, it):
    scene_name = it.get("sceneName") or it.get("scene", "")
    skill = SKILL_OF.get(it.get("scene", ""), "")
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in it.get("tags", []))
    return f"""
    <article class="card">
      <header class="card__head">
        <span class="card__no">{it.get('id', 's%02d' % i).upper()}</span>
        <span class="card__scene">{esc(it.get('scene', ''))}</span>
        <span class="card__skill">{esc(skill)}</span>
      </header>
      <h2>{esc(it.get('title', ''))}</h2>

      <div class="ask">
        <div class="ask__label">用户会这样问</div>
        <p>{esc(it.get('question', ''))}</p>
        <button class="copy" type="button" data-q="{esc(it.get('question', ''))}">复制这句去问 AI</button>
      </div>

      <details class="ans">
        <summary>按「{esc(skill)}」的结构回答（{len(it.get('answer', ''))} 字）</summary>
        <p>{esc(it.get('answer', ''))}</p>
      </details>

      <div class="fact"><span class="fact__label">今日事实</span>{esc(it.get('hot', ''))}</div>

      <ul class="src">{render_sources(it.get('sources', []))}</ul>
      <div class="tags">{tags}</div>
    </article>"""


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    items = data["items"]
    cards = "\n".join(render_card(i, it) for i, it in enumerate(items, 1))
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>今日 {len(items)} 场景 · 数据预览（{esc(data.get('date',''))}）</title>
<style>
  :root {{
    --orange: #F97316; --orange-d: #E05E0A; --ink: #241610;
    --ink-2: #3A332C; --ink-3: #8A7D70; --paper: #FBF7F2; --line: #EDE3D8;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--paper); color: var(--ink-2);
    font: 16px/1.75 "PingFang SC", "Microsoft YaHei", -apple-system, sans-serif;
  }}
  .wrap {{ max-width: 860px; margin: 0 auto; padding: 40px 20px 72px; }}
  .note {{
    background: #FFF3E8; border: 1px solid #F7D3B4; border-radius: 10px;
    padding: 12px 16px; font-size: 13.5px; color: #8A4A12; margin-bottom: 28px;
  }}
  h1 {{
    font: 700 30px/1.3 "Songti SC", Georgia, serif; color: var(--ink);
    margin: 0 0 8px; letter-spacing: -.01em;
  }}
  .meta {{ color: var(--ink-3); font-size: 14px; margin-bottom: 14px; }}
  .summary {{
    font-size: 15px; color: var(--ink-2); background: #fff; border-left: 3px solid var(--orange);
    padding: 14px 18px; border-radius: 0 10px 10px 0; margin: 0 0 32px;
  }}
  .card {{
    background: #fff; border: 1px solid var(--line); border-radius: 14px;
    padding: 22px 24px; margin-bottom: 18px;
  }}
  .card__head {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }}
  .card__no {{ font: 700 12px/1 ui-monospace, monospace; color: var(--orange); letter-spacing: .08em; }}
  .card__scene {{ font-size: 13px; color: var(--ink); font-weight: 600; }}
  .card__skill {{
    font-size: 12px; color: var(--orange-d); background: #FFF1E4;
    border-radius: 999px; padding: 2px 10px;
  }}
  .card h2 {{ font: 700 20px/1.45 "Songti SC", Georgia, serif; margin: 0 0 16px; color: var(--ink); }}
  .ask {{ background: #FAF7F3; border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; }}
  .ask__label {{ font-size: 12px; color: var(--ink-3); letter-spacing: .04em; margin-bottom: 6px; }}
  .ask p {{ margin: 0 0 10px; font-size: 15px; color: var(--ink); }}
  .copy {{
    font: inherit; font-size: 13px; color: var(--orange-d); background: #fff;
    border: 1px solid #F2C79E; border-radius: 8px; padding: 5px 12px; cursor: pointer;
  }}
  .copy:hover {{ background: #FFF6ED; }}
  details.ans {{ border-top: 1px dashed var(--line); padding-top: 12px; }}
  details.ans summary {{ cursor: pointer; font-size: 13.5px; color: var(--orange-d); }}
  details.ans p {{ font-size: 15px; margin: 12px 0 0; color: var(--ink-2); }}
  .fact {{
    font-size: 13.5px; color: var(--ink-2); background: #F6F2EC;
    border-radius: 8px; padding: 10px 14px; margin: 14px 0 10px;
  }}
  .fact__label {{
    color: var(--ink-3); font-size: 12px; margin-right: 8px; letter-spacing: .04em;
  }}
  .src {{ list-style: none; padding: 0; margin: 0 0 12px; font-size: 13px; }}
  .src li {{ margin: 4px 0; }}
  .src a {{ color: #0B6E9E; text-decoration: none; border-bottom: 1px solid #CFE3EE; }}
  .src a:hover {{ border-color: #0B6E9E; }}
  .tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .tag {{
    font-size: 12px; color: var(--ink-3); background: #F6F2EC;
    border-radius: 6px; padding: 2px 8px;
  }}
  footer {{ margin-top: 32px; font-size: 12.5px; color: var(--ink-3); text-align: center; }}
  @media (max-width: 560px) {{
    .wrap {{ padding: 24px 14px 56px; }}
    h1 {{ font-size: 24px; }}
    .card {{ padding: 18px 16px; }}
    .card h2 {{ font-size: 18px; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <div class="note">
    这是 <code>web/data/hot-scenarios.json</code> 的渲染预览，用来判断数据够不够撑一个真实模块。
    文件只生成在 <code>dist/</code>，没有接入站点任何页面。
  </div>
  <h1>今天这 {len(items)} 个问题，都能问</h1>
  <div class="meta">{esc(data.get('date',''))} · 更新于 {esc(data.get('updatedAt',''))} · 共 {len(items)} 个场景</div>
  <p class="summary">{esc(data.get('summary',''))}</p>
  {cards}
  <footer>{esc(data.get('disclaimer',''))}</footer>
</div>
<script>
  document.addEventListener('click', function (e) {{
    var b = e.target.closest('.copy');
    if (!b) return;
    var text = b.getAttribute('data-q');
    (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject())
      .then(function () {{ b.textContent = '已复制'; }})
      .catch(function () {{ b.textContent = '复制失败'; }})
      .then(function () {{ setTimeout(function () {{ b.textContent = '复制这句去问 AI'; }}, 1600); }});
  }});
</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8", newline="\n")
    kb = OUT.stat().st_size / 1024
    print(f"✅ {OUT.relative_to(ROOT)}  {kb:.0f} KB  {len(items)} 个场景")


if __name__ == "__main__":
    main()
