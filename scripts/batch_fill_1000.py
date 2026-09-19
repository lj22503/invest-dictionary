#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_fill_1000.py —— 批量生成投资词典词条
流程：
  1. 读 v3 清单（批次 1-6 + 7-12）解析 P1/P2/P3
  2. 读 dictionary.json 已有词条，归一化去重
  3. 待生成列表 = 清单 - 已有
  4. 分批调 Claude API 生成 MD（few-shot + checklist）
  5. 解析 MD → 渲染 HTML（用 term-page-regular.html）→ 写文件 → 更新 dict
  6. 每批跑完调 sync_all_entries.py
  7. 失败单条跳过 + 错误日志

用法：
  python scripts/batch_fill_1000.py --batch-size 5   # 先跑 5 条验证
  python scripts/batch_fill_1000.py --batch-size 10  # 跑 10 条
  python scripts/batch_fill_1000.py                  # 默认跑 10/批，跑完全部
  python scripts/batch_fill_1000.py --max 30         # 只跑前 30 条（限上限）

环境：ANTHROPIC_AUTH_TOKEN（不读 ANTHROPIC_API_KEY）
"""
import os, sys, io, re, json, time, urllib.parse, urllib.request, argparse, subprocess
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============== 路径 ==============
ROOT = Path(r'D:\claudework\invest-dictionary')
TPL  = ROOT / 'skill/invest-dictionary-generator/templates/term-page-regular.html'
DICT = ROOT / 'web/dictionary.json'
MD_DIR = ROOT / 'docs/terms-md'
HTML_DIR = ROOT / 'web/terms'
V3_FILES = [
    ROOT / 'docs/prod_1a03777205b_404d10e62275_投资词典_扩充词条清单v3_批次1-6.md.md',
    ROOT / 'docs/prod_1a03777205f_f403b3634564_投资词典_扩充词条清单v3_批次7-12.md.md',
]

# ============== 批次 → 章节映射 ==============
BATCH_TO_CHAPTER = {
    1: '第二篇：个人财务底盘',  # 钱的本质与个人财务底盘
    2: '第三篇：风险护城河',     # 保险 + 风险（保险可细分到第七篇，先合并）
    3: '第四篇：投资武器库 · 股票篇',
    4: '第六篇：投资武器库 · 基金篇',
    5: '第十四篇：策略与数学',
    6: '第十篇：交易规则与摩擦成本',
    # 7-12 待用户确认映射，先跑 1-6
}

# ============== 工具：归一化匹配 ==============
def norm(s):
    return re.sub(r'[\s（()）\/\\*<>、,，。:：!?？·\-—]', '', s).lower()

# ============== Step 1: 解析 v3 清单 ==============
def parse_v3():
    """返回 [(batch_id, term, priority), ...] 列表，按文件内"## 批次 N"标题动态切换 batch_id"""
    items = []
    for f in V3_FILES:
        if not f.exists():
            print(f'⚠️  缺失: {f.name}')
            continue
        text = f.read_text(encoding='utf-8')
        current_batch = 1  # 默认值，遇到批次标题行会更新
        for line in text.split('\n'):
            # 检测批次标题行：## 批次 N · ...
            m_batch = re.match(r'^\s*##\s*批次\s*(\d+)\s*[·\.\s]', line)
            if m_batch:
                current_batch = int(m_batch.group(1))
                continue
            if not line.strip().startswith('-'):
                continue
            # 移除列表前缀
            line = line.lstrip('-').strip()
            # 按 ｜ 拆
            for chunk in line.split('｜'):
                # 找优先级标记
                m = re.match(r'^(.+?)\s*P([123])\s*$', chunk.strip())
                if m:
                    term = m.group(1).strip()
                    priority = int(m.group(2))
                    if term:
                        items.append((current_batch, term, priority))
    return items

# ============== Step 2: 读现有 dict ==============
def load_existing():
    data = json.loads(DICT.read_text(encoding='utf-8'))
    titles_norm = set(norm(t['title']) for t in data)
    max_id = max(t['id'] for t in data)
    return titles_norm, max_id

# ============== Step 3: 待生成列表 ==============
def get_pending(v3_items, existing_norm):
    seen = set()
    pending = []
    # P1 → P2 → P3 排序
    sorted_items = sorted(v3_items, key=lambda x: (x[2], x[0]))
    for batch_id, term, priority in sorted_items:
        key = norm(term)
        if key in existing_norm or key in seen:
            continue
        seen.add(key)
        pending.append((batch_id, term, priority))
    return pending

# ============== Step 4: 调 Claude API 生成 MD ==============
def call_claude(terms_batch):
    """terms_batch: [(term, priority, chapter), ...]"""
    api_key = os.environ.get('ANTHROPIC_AUTH_TOKEN', '')
    if not api_key:
        raise RuntimeError('缺少 ANTHROPIC_AUTH_TOKEN 环境变量')

    # few-shot：从 examples 货币.md + docs/terms-md 应急金.md 取样
    fewshot_1 = (ROOT / 'skill/invest-dictionary-generator/examples/货币.md').read_text(encoding='utf-8')
    fewshot_2_path = MD_DIR / '应急金.md'
    fewshot_2 = fewshot_2_path.read_text(encoding='utf-8') if fewshot_2_path.exists() else ''

    # 构造 prompt
    term_list = '\n'.join(f'- {t[0]}' for t in terms_batch)
    prompt = f'''你是"投资词典"的内容官。按下面的格式和风格，为列表中的每个词条生成 Markdown。

【输出格式（每两个词条之间用 ====TERM==== 分隔）】

# {{词条名}}

> {{一句话定义，≤30 字，必须大白话}}

## 1. 这是什么

{{大白话定义 + 比喻/生活例子}}

## 2. 为什么重要

{{关我什么事，结合赚钱/亏钱/避坑场景，给出具体数字或对比}}

## 3. 怎么用 / 怎么看

- 步骤 1
- 步骤 2
- 步骤 3

## 4. 常见坑 / 误区

- 坑 1
- 坑 2

---

**相关词条**：词条A、词条B

====TERM====

{{下一个词条}}

====END====

【风格要求】
- 第一句必须是外行能听懂的大白话，禁止术语套术语
- 必须有真实场景或具体数字
- 4 卡都写（这是什么 / 为什么重要 / 怎么用 / 常见坑）
- 至少 1 个常见坑（除非概念确无坑）
- "相关词条"列出 3-5 个真正相关的概念（不要硬凑）
- 全文 800-1500 字

【Few-shot 样例 1：货币】

{fewshot_1}

【Few-shot 样例 2：应急金】

{fewshot_2}

====NOW_GENERATE====

请为以下 {len(terms_batch)} 个词条生成 MD（用 ====TERM==== 分隔词条）：

{term_list}'''

    body = json.dumps({
        'model': 'claude-sonnet-4-5',
        'max_tokens': 16000,
        'messages': [{'role': 'user', 'content': prompt}],
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=body,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
        }
    )

    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode('utf-8'))

    return result['content'][0]['text']

# ============== Step 5: 解析 LLM 输出 ==============
def parse_llm_output(raw):
    """按 ====TERM==== 切分，返回 [(title, md_body), ...]"""
    chunks = raw.split('====TERM====')
    result = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk or chunk == '====END====':
            continue
        # 去掉结尾的 ====END====
        if chunk.endswith('====END===='):
            chunk = chunk[:-len('====END====')].strip()
        # 提取标题（第一行 # 开头）
        m = re.match(r'^#\s+(.+?)$', chunk, re.MULTILINE)
        if m:
            title = m.group(1).strip()
            result.append((title, chunk))
    return result

# ============== Step 6: 渲染 HTML ==============
def md_to_cards(md_body):
    """从 MD 提取 4 卡标题 + 段落，渲染 HTML"""
    cards = []
    # 找 4 个 ## 段
    sections = re.split(r'\n##\s+\d+\.\s+', md_body)
    # sections[0] = 第一行 # 标题 + 简介 + 空段（丢弃）
    # sections[1..4] = 4 卡内容
    for i, sec in enumerate(sections[1:5], 1):
        sec = sec.strip()
        if not sec:
            continue
        # 标题 = 第一行
        lines = sec.split('\n', 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ''
        # 简化 MD → 段落（每行一段，列表转 ul）
        paragraphs = []
        in_list = False
        list_buf = []
        for line in body.split('\n'):
            line = line.rstrip()
            if not line or line == '---':
                continue
            if line.startswith('- ') or line.startswith('* '):
                list_buf.append(line[2:].strip())
                in_list = True
            else:
                if in_list and list_buf:
                    paragraphs.append('<ul class="step-list">' + ''.join(f'<li>{item}</li>' for item in list_buf) + '</ul>')
                    list_buf = []
                    in_list = False
                if line.strip():
                    # 简单加粗转换 **x** → <strong>x</strong>
                    line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                    paragraphs.append(f'<p>{line}</p>')
        if in_list and list_buf:
            paragraphs.append('<ul class="step-list">' + ''.join(f'<li>{item}</li>' for item in list_buf) + '</ul>')

        cards.append({'title': title, 'paragraphs': paragraphs})
    return cards

def render_html(title, cards, related):
    """用 term-page-regular.html 模板 + 数据渲染"""
    tpl = TPL.read_text(encoding='utf-8')
    encoded = urllib.parse.quote(title)
    # 钩子句用 cards[0] 第一段
    hook = re.sub(r'<[^>]+>', '', cards[0]['paragraphs'][0])[:60] if cards and cards[0]['paragraphs'] else title
    keywords = ', '.join([title] + related[:4])
    term_code = f'dict-{title}'

    tpl = tpl.replace('{{词条名}}', title)
    tpl = tpl.replace('{{编码URL}}', encoded)
    tpl = tpl.replace('{{一句话钩子}}', hook)
    tpl = tpl.replace('{{关键词}}', keywords)
    tpl = tpl.replace('{{词条编码}}', term_code)

    # 4 张卡片
    def render_card(num, card):
        body_html = ''
        for p in card['paragraphs']:
            body_html += f'      {p}\n'
        return f'''<article class="card">
    <div class="card-number">{num}</div>
    <h2 class="card-title">{card['title']}</h2>
    <div class="card-body">
{body_html}    </div>
  </article>'''

    new_first = render_card('①', cards[0]) if cards else ''
    first_pat = re.compile(r'<article class="card">.*?</article>', re.DOTALL)
    tpl = first_pat.sub(new_first, tpl, count=1)

    middle = ''
    for i, c in enumerate(cards[1:4], 2):
        middle += f'<div class="card-divider"></div>\n\n  {render_card(["②","③","④"][i-2], c)}\n\n  '
    middle += '<div class="card-divider"></div>'

    paper_pat = re.compile(r'(<article class="card">.*?</article>)(.*?)(</div>\s*<nav class="term-pager">)', re.DOTALL)
    m = paper_pat.search(tpl)
    if m:
        tpl = tpl[:m.start(2)] + '\n\n  ' + middle + '\n\n' + tpl[m.start(3):]

    # related
    related_html = ' · '.join(f'<a href="https://dictionary.mangofolio.com/terms/{urllib.parse.quote(r)}.html">{r}</a>' for r in related)
    tpl = re.sub(r'<div class="related-links">.*?</div>',
                 f'<div class="related-links">{related_html}</div>', tpl, flags=re.DOTALL)

    # pager（新增的都先 disabled + next 是 related[0]）
    next_link = related[0] if related else ''
    next_html = f'<a href="https://dictionary.mangofolio.com/terms/{urllib.parse.quote(next_link)}.html">{next_link} →</a>' if next_link else '<span class="pager-disabled">无 →</span>'
    tpl = re.sub(r'<nav class="term-pager">.*?</nav>',
                 f'<nav class="term-pager"><span class="pager-disabled">← 无</span>{next_html}</nav>',
                 tpl, flags=re.DOTALL)
    return tpl

def extract_related(md_body):
    """从 MD 末尾的 **相关词条**：行提取"""
    m = re.search(r'\*\*相关词条\*\*[：:]\s*(.+?)(?:\n|$)', md_body)
    if not m:
        return []
    return [x.strip() for x in re.split(r'[、,，;；]', m.group(1)) if x.strip()][:6]

# ============== Step 7: 写文件 + 更新 dict ==============
def slugify(name):
    """按 SKILL.md 规则归一化文件名：/ * > 替换为 _ （保留空格和括号）"""
    return name.replace('/', '_ ').replace('*', '_ ').replace('>', '_ ')

def save_term(title, md_body, batch_id, new_id):
    """写 MD + HTML + 更新 dict entry"""
    chapter = BATCH_TO_CHAPTER.get(batch_id, '第二篇：个人财务底盘')
    slug = slugify(title)

    # 写 MD（文件名用归一化 slug）
    md_path = MD_DIR / f'{slug}.md'
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_body, encoding='utf-8')

    # 渲染 HTML
    cards = md_to_cards(md_body)
    related = extract_related(md_body)
    html = render_html(title, cards, related)

    html_path = HTML_DIR / f'{slug}.html'
    html_path.write_text(html, encoding='utf-8')

    # 更新 dict
    data = json.loads(DICT.read_text(encoding='utf-8'))
    entry = {
        'id': new_id,
        'slug': slug,
        'title': title,
        'chapter': chapter,
        'card_titles': [c['title'] for c in cards[:4]],
        'related': related,
        'next': related[0] if related else '',
        'filename': f'{slug}.html',
    }
    data.append(entry)
    DICT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    return entry

def sync_all_entries():
    """调 sync_all_entries.py 同步首页"""
    sync_script = ROOT / 'scripts/sync_all_entries.py'
    if sync_script.exists():
        subprocess.run([sys.executable, str(sync_script)], cwd=str(ROOT), capture_output=True)

# ============== 主流程 ==============
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['api', 'file'], default='api',
                        help='api=调 Claude API 生成；file=读 docs/terms-md/ 已有 MD')
    parser.add_argument('--batch-size', type=int, default=10, help='每批多少条（默认 10）')
    parser.add_argument('--max', type=int, default=0, help='最多生成多少条（0=全部）')
    parser.add_argument('--skip-sync', action='store_true', help='不调 sync_all_entries.py')
    args = parser.parse_args()

    print(f'[{datetime.now():%H:%M:%S}] === batch_fill_1000 启动 ===')
    print(f'  batch_size={args.batch_size}, max={args.max}')

    # 解析清单
    v3_items = parse_v3()
    print(f'  v3 清单解析: {len(v3_items)} 条候选')
    priority_count = {1: 0, 2: 0, 3: 0}
    for _, _, p in v3_items:
        priority_count[p] += 1
    print(f'  P1={priority_count[1]}, P2={priority_count[2]}, P3={priority_count[3]}')

    # 比对
    existing_norm, max_id = load_existing()
    print(f'  已有词条: {len(existing_norm)} 条 (max_id={max_id})')

    pending = get_pending(v3_items, existing_norm)
    print(f'  待生成: {len(pending)} 条')

    if args.max > 0:
        pending = pending[:args.max]
        print(f'  限制为前 {args.max} 条')

    if not pending:
        print('✅ 没有待生成词条，退出')
        return

    # 分批
    total = len(pending)
    batch_size = args.batch_size
    batches = [pending[i:i+batch_size] for i in range(0, total, batch_size)]

    print(f'\n  计划: {len(batches)} 批 × {batch_size} 条/批 = {total} 条')
    print()

    # 跑每批
    success = 0
    failed = []
    next_id = max_id + 1

    for batch_idx, batch in enumerate(batches, 1):
        print(f'[{datetime.now():%H:%M:%S}] --- 批 {batch_idx}/{len(batches)} ({len(batch)} 条) ---')
        for _, term, _ in batch:
            print(f'    · {term}')

        # 按 mode 分支
        if args.mode == 'api':
            try:
                raw = call_claude(batch)
            except Exception as e:
                print(f'  ❌ LLM 调用失败: {e}')
                failed.extend([(t[1], str(e)) for t in batch])
                continue
            parsed = parse_llm_output(raw)
            print(f'  解析: LLM 返回 {len(parsed)} 条')
            if len(parsed) != len(batch):
                print(f'  ⚠️  数量不匹配: 期望 {len(batch)} 实际 {len(parsed)}')
        else:  # file mode
            parsed = []
            for _, term, _ in batch:
                md_path = MD_DIR / f'{term}.md'
                if not md_path.exists():
                    # 尝试 fuzzy 找：归一化比较时把 _ 和 空格 都忽略
                    target = re.sub(r'[\s_\-_]+', '', norm(term))
                    found = None
                    for p in MD_DIR.glob('*.md'):
                        if re.sub(r'[\s_\-_]+', '', norm(p.stem)) == target:
                            found = p
                            break
                    if not found:
                        print(f'    ⚠️  缺 MD: {term}')
                        failed.append((term, f'无 MD 文件: {md_path}'))
                        continue
                    md_path = found
                    print(f'    ↪ fuzzy 命中: {term} → {md_path.name}')
                # 用 batch term 作 title（保证 dict 字段与 v3 一致）
                parsed.append((term, md_path.read_text(encoding='utf-8')))

        # 按 title 匹配回 batch
        batch_by_title = {norm(t[1]): t for t in batch}

        for title, md_body in parsed:
            key = norm(title)
            if key not in batch_by_title:
                print(f'    ⚠️  跳过未知词条: {title}')
                continue
            batch_id = batch_by_title[key][0]
            try:
                entry = save_term(title, md_body, batch_id, next_id)
                print(f'    ✅ {title} (id={entry["id"]}, chapter={entry["chapter"]})')
                success += 1
                next_id += 1
            except Exception as e:
                print(f'    ❌ {title}: {e}')
                failed.append((title, str(e)))

        # 每批跑完同步 ALL_ENTRIES
        if not args.skip_sync:
            print(f'  同步 ALL_ENTRIES...')
            sync_all_entries()

        print(f'  批 {batch_idx} 完成（累计成功 {success}/{total}）')
        print()

    # 报告
    print(f'[{datetime.now():%H:%M:%S}] === 完成 ===')
    print(f'  ✅ 成功: {success}')
    print(f'  ❌ 失败: {len(failed)}')
    if failed:
        print(f'  失败列表:')
        for t, e in failed[:20]:
            print(f'    • {t}: {e[:80]}')

    # 写错误日志
    if failed:
        log_path = ROOT / 'scripts/batch_fill_errors.log'
        log_path.write_text(
            f'[{datetime.now():%Y-%m-%d %H:%M:%S}] 失败 {len(failed)} 条\n\n'
            + '\n'.join(f'{t}\t{e[:200]}' for t, e in failed),
            encoding='utf-8'
        )
        print(f'  错误日志: {log_path}')

if __name__ == '__main__':
    main()
