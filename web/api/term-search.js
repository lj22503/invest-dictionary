// GET /api/term-search?q=CPI&n=5
//
// 给技能用的「查词」接口：一次调用拿到词条名、链接、所属章节、四张卡片的小标题。
// 有了这四个字段，模型就能判断该给用户讲哪个词、按什么结构讲，不必再读 51KB
// 的 term-index.txt，也不必读整篇词条页。
//
// 响应：
//   { ok, q, n, total, hits: [{ t, u, c, k }] }
//     t 词条名  u 站内链接  c 所属章节  k 四张卡片的小标题
import INDEX from './_term-index.js';

export const config = { runtime: 'edge' };

const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'GET, OPTIONS',
  'cache-control': 'public, max-age=3600',
};

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', ...CORS },
  });

const norm = (s) => String(s || '').toLowerCase().replace(/[\s\-_·、，,。.（）()《》"'"'']/g, '');

function score(term, q) {
  const t = norm(term.t);
  const k = (term.k || []).map(norm).join('');
  if (t === q) return 100;
  if (t.startsWith(q)) return 80;
  if (t.includes(q)) return 60;
  if (q.includes(t) && t.length >= 2) return 50;
  if (k.includes(q)) return 25;
  if (norm(term.c).includes(q)) return 10;
  return 0;
}

export default function handler(req) {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
  if (req.method !== 'GET') return json({ ok: false, error: '只支持 GET' }, 405);

  const u = new URL(req.url);
  const raw = (u.searchParams.get('q') || '').trim();
  const n = Math.min(Math.max(parseInt(u.searchParams.get('n') || '5', 10) || 5, 1), 20);
  if (!raw) return json({ ok: false, error: '缺 q 参数，例如 /api/term-search?q=CPI' }, 400);

  const q = norm(raw);
  const scored = [];
  for (const term of INDEX) {
    const s = score(term, q);
    if (s > 0) scored.push({ s, term });
  }
  scored.sort((a, b) => b.s - a.s || a.term.t.length - b.term.t.length || a.term.t.localeCompare(b.term.t));

  const hits = scored.slice(0, n).map((x) => ({
    t: x.term.t, u: x.term.u, c: x.term.c, k: x.term.k, s: x.s,
  }));

  return json({ ok: true, q: raw, n: hits.length, total: scored.length, hits });
}
