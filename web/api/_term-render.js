// 词条页服务端渲染：模型只交结构化 JSON，套模板在这里做。
//
// 为什么要有这个文件：原来「投资翻译」技能让模型先读 32KB 基准页、再逐字写出
// 31KB HTML。一进一出约 16k token，一次两三分钟。改成模型产出几百 token 的
// JSON、服务端套模板出整页，模型不再当模板引擎，模板也不再随包下发。
//
// 契约（POST /api/term-page）：
//   {
//     "title":    "货币",                     // 必填
//     "chapter":  "第一篇：钱的本质",          // 可选，缺省查索引
//     "summary":  "一句话定义，进 meta 描述",  // 必填，≤120 字
//     "keywords": ["信用", "购买力"],          // 可选
//     "cards": [                              // 2~6 张
//       {
//         "q": "你手里攥着的100块",            // 小标题，口语化提问或结论
//         "body": [ {"p": "段落"}, {"quote": "金句"}, {"ul": ["步骤1", "步骤2"]}, {"note": "浅色小字"} ],
//         "quote": "金句"                     // 可选，等价于 body 里的 {"quote": ...}
//       }
//     ],
//     "related": ["信用", "购买力"]            // 可选，缺省取同章节的词条
//   }
//
// 正文里可以用 **双星号** 标记要高亮的词。

import { SHELL } from './_term-shell.js';
import INDEX from './_term-index.js';

const SITE = 'https://dictionary.mangofolio.com';
const NUM = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧'];

const esc = (s) => String(s ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

// 双星号 → 高亮（黄色马克笔），下划线对 → 标签胶囊（米色小药丸），其余一律转义
const inline = (s) => esc(s)
  .replace(/\*\*([^*]+)\*\*/g, '<span class="highlight">$1</span>')
  .replace(/__([^_]+)__/g, '<span class="tag">$1</span>');

const termUrl = (title) => `${SITE}/terms/${encodeURIComponent(title)}`;

function findTerm(title) {
  if (!title) return null;
  const t = String(title).trim();
  return INDEX.find((x) => x.t === t) || INDEX.find((x) => x.t.replace(/\s/g, '') === t.replace(/\s/g, '')) || null;
}

function chapterOf(title) {
  const hit = findTerm(title);
  if (hit) return hit.c;
  const probe = INDEX.find((x) => x.t && title && (x.t.includes(title) || title.includes(x.t)));
  return probe ? probe.c : '投资词典';
}

function neighbors(title) {
  const i = INDEX.findIndex((x) => x.t === title);
  if (i < 0) return { prev: null, next: null, siblings: [] };
  const cur = INDEX[i];
  const siblings = INDEX.filter((x) => x.c === cur.c && x.t !== cur.t).slice(0, 3);
  return {
    prev: i > 0 ? INDEX[i - 1] : null,
    next: i < INDEX.length - 1 ? INDEX[i + 1] : null,
    siblings,
  };
}

function renderBody(blocks) {
  const out = [];
  for (const b of blocks) {
    if (!b || typeof b !== 'object') continue;
    if (b.p) out.push(`      <p>${inline(b.p)}</p>`);
    else if (b.quote) out.push(`      <div class="card-quote">\n        ${inline(b.quote)}\n      </div>`);
    else if (Array.isArray(b.ul) && b.ul.length) {
      out.push('      <ul class="step-list">');
      for (const li of b.ul) out.push(`        <li>${inline(li)}</li>`);
      out.push('      </ul>');
    } else if (b.note) out.push(`      <p style="color:var(--ink-light); font-size:0.9rem;">${inline(b.note)}</p>`);
  }
  return out.join('\n');
}

function renderPaper(d) {
  const cards = d.cards.map((c, i) => {
    const blocks = Array.isArray(c.body) ? c.body.slice() : [];
    if (c.quote && !blocks.some((b) => b && b.quote)) blocks.push({ quote: c.quote });
    return [
      '  <article class="card">',
      `    <div class="card-number">${NUM[i] || i + 1}</div>`,
      `    <h2 class="card-title">${inline(c.q || '')}</h2>`,
      '    <div class="card-body">',
      renderBody(blocks),
      '    </div>',
      '  </article>',
      '  <div class="card-divider"></div>',
    ].join('\n');
  }).join('\n\n');

  return [
    '<!-- ===== Header ===== -->',
    '  <header class="header">',
    '    <div class="title-wrap">',
    `      <h1 class="main-title">${esc(d.title)}</h1>`,
    `      <p class="subtitle">—— 投资词典 · ${esc(d.chapter)} · 最后更新：${esc(d.date)}</p>`,
    '    </div>',
    '  </header>',
    '',
    cards,
  ].join('\n');
}

function renderRelated(d, sib) {
  const list = (d.related && d.related.length ? d.related : sib.siblings.map((x) => x.t)).slice(0, 5);
  if (!list.length) return '<span>投资词典</span>';
  return list.map((t) => `<a href="/terms/${encodeURIComponent(t)}">${esc(t)}</a>`).join(' · ');
}

function renderPager(sib) {
  const prev = sib.prev
    ? `<a href="/terms/${encodeURIComponent(sib.prev.t)}" class="pager-prev" title="${esc(sib.prev.t)}">← ${esc(sib.prev.t)}</a>`
    : '<span class="pager-prev pager-disabled">← 已是第一篇</span>';
  const next = sib.next
    ? `<a href="/terms/${encodeURIComponent(sib.next.t)}" class="pager-next" title="${esc(sib.next.t)}">${esc(sib.next.t)} →</a>`
    : '<span class="pager-next pager-disabled">已是最后一篇 →</span>';
  return `<nav class="term-pager">${prev}${next}</nav>`;
}

function jsonld(d, url) {
  return JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'DefinedTerm',
    name: d.title,
    description: d.summary,
    termCode: String(findTerm(d.title)?.t || d.title),
    url,
    inDefinedTermSet: { '@type': 'DefinedTermSet', name: '投资词典 · Invest Dictionary' },
    dateModified: d.date,
  }, null, 2);
}

/** 校验入参，返回错误清单（空数组表示通过）。 */
export function validate(payload) {
  const errs = [];
  if (!payload || typeof payload !== 'object') return ['请求体必须是 JSON 对象'];
  const tag = '（用双星号标记要高亮的词，例如 100块 写成 **100块**）';
  if (!payload.title || String(payload.title).trim().length === 0) errs.push('缺 title');
  if (!payload.summary || String(payload.summary).length < 8) errs.push('summary 至少 8 个字，会进 meta 描述');
  if (String(payload.summary || '').length > 160) errs.push('summary 超过 160 字，搜索引擎会截断');
  const cards = Array.isArray(payload.cards) ? payload.cards : [];
  if (cards.length < 2) errs.push('cards 至少 2 张');
  if (cards.length > 6) errs.push('cards 最多 6 张，多了页面拖沓');
  cards.forEach((c, i) => {
    if (!c || !c.q) errs.push(`cards[${i}] 缺 q（小标题）`);
    const body = Array.isArray(c?.body) ? c.body : [];
    if (!body.length && !c?.quote) errs.push(`cards[${i}] 的 body 为空`);
  });
  if (typeof payload.summary === 'string' && /<[a-z]/i.test(payload.summary)) errs.push('summary 里不要写 HTML');
  if (errs.length) errs.push(tag);
  return errs;
}

/** 结构化 JSON → 整页 HTML。 */
export function renderTermPage(payload) {
  const d = {
    title: String(payload.title).trim(),
    summary: String(payload.summary || '').trim(),
    chapter: (payload.chapter && String(payload.chapter).trim()) || chapterOf(payload.title),
    keywords: Array.isArray(payload.keywords) ? payload.keywords : [],
    related: Array.isArray(payload.related) ? payload.related : [],
    cards: payload.cards || [],
    date: payload.date || new Date().toISOString().slice(0, 10),
  };
  const url = termUrl(d.title);
  const sib = neighbors(d.title);

  const headTitle = `${d.title}是什么意思？小白也能看懂的理财术语解释 - 投资词典`;
  const ogTitle = `${d.title} - 投资词典 · Invest Dictionary`;
  const kw = (d.keywords.length ? d.keywords : (sib.siblings || []).map((x) => x.t)).join(', ');
  const crumb = `\n  <a href="/">投资词典</a>\n  <span class="bc-sep">›</span>\n  <a href="/#${encodeURIComponent(d.chapter)}">${esc(d.chapter)}</a>\n  <span class="bc-sep">›</span>\n  <span class="bc-current">${esc(d.title)}</span>\n`;
  const weibo = `https://service.weibo.com/share/share.php?url=${encodeURIComponent(url)}&title=${encodeURIComponent(ogTitle)}`;

  return SHELL
    .replace('@@HEAD_TITLE@@', esc(headTitle))
    .replaceAll('@@OG_TITLE@@', esc(ogTitle))
    .replaceAll('@@DESC@@', esc(d.summary))
    .replaceAll('@@KEYWORDS@@', esc(kw))
    .replaceAll('@@URL@@', esc(url))
    .replace('@@JSONLD@@', jsonld(d, url))
    .replace('@@CRUMB@@', crumb)
    .replace('@@WEIBO@@', esc(weibo))
    .replace('@@PAPER@@', renderPaper(d))
    .replace('@@RELATED@@', renderRelated(d, sib))
    .replace('@@PAGER@@', renderPager(sib));
}
