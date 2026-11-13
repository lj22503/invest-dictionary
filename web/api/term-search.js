// GET /api/term-search?q=CPI&n=5
//
// 给技能用的「查词」接口：一次调用拿到词条名、链接、所属章节、四张卡片的小标题。
// 有了这四个字段，模型就能判断该给用户讲哪个词、按什么结构讲，不必再读 51KB
// 的 term-index.txt，也不必读整篇词条页。
//
// 响应：
//   { ok, q, n, total, tokens, hits: [{ t, u, c, k, s }] }
//     t 词条名  u 站内链接  c 所属章节  k 四张卡片的小标题  s 相关度
import INDEX from './_term-index.js';
import { search } from './_term-query.js';

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

export default function handler(req) {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
  if (req.method !== 'GET') return json({ ok: false, error: '只支持 GET' }, 405);

  const u = new URL(req.url);
  const raw = (u.searchParams.get('q') || '').trim();
  const n = Math.min(Math.max(parseInt(u.searchParams.get('n') || '5', 10) || 5, 1), 20);
  if (!raw) return json({ ok: false, error: '缺 q 参数，例如 /api/term-search?q=CPI' }, 400);

  const { hits, total, tokens } = search(INDEX, raw, n);
  return json({ ok: true, q: raw, n: hits.length, total, tokens, hits });
}
