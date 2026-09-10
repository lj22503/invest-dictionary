// POST /api/events
// 接收前端 SDK 事件，写入 Vercel KV（Upstash Redis）
// key 命名：evt:dictionary:YYYY-MM-DD（按天 list）
// 与 subscribe.js 共享同一 KV database，但命名空间隔离
import { kv } from '@vercel/kv';

export const config = {
  runtime: 'edge',
};

const SAFE_PAYLOAD_KEYS = new Set([
  'cta',
  'ref',
  'qid',
  'word',
  'query',
  'site',
  'page_referrer',
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_term',
  'utm_content',
]);

function sanitizePayload(raw) {
  if (!raw || typeof raw !== 'object') return undefined;
  const out = {};
  for (const [k, v] of Object.entries(raw)) {
    if (!SAFE_PAYLOAD_KEYS.has(k)) continue;
    if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') {
      out[k] = String(v).slice(0, 256);
    }
  }
  return Object.keys(out).length ? out : undefined;
}

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  let body;
  try {
    body = await req.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: 'invalid json' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  if (typeof body.event !== 'string' || !body.event) {
    return new Response(JSON.stringify({ error: 'bad_request' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const event = body.event.slice(0, 64);
  const path = typeof body.path === 'string' ? body.path.slice(0, 128) : '';
  const ts = typeof body.ts === 'number' ? body.ts : Date.now();
  const payload = sanitizePayload(body.payload);

  const entry = {
    e: event,
    p: path,
    t: ts,
    ...(payload ? { d: payload } : {}),
  };

  try {
    const key = `evt:dictionary:${new Date(ts).toISOString().slice(0, 10)}`;
    await kv.rpush(key, JSON.stringify(entry));
    // 30 天过期，避免长期堆积
    await kv.expire(key, 60 * 60 * 24 * 30);
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: 'kv' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
