// POST /api/hotwords
// 管理员写入当日热词（内容管线每天调用），存 KV 供 send-daily 群发使用
// 需带 Authorization: Bearer {ADMIN_TOKEN}
import { kv } from '@vercel/kv';

export const config = {
  runtime: 'edge'
};

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // 校验管理员 token
  const auth = req.headers.get('authorization') || '';
  const adminToken = process.env.ADMIN_TOKEN;
  if (!adminToken || auth !== `Bearer ${adminToken}`) {
    return new Response(JSON.stringify({ error: 'unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  let body;
  try {
    body = await req.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: 'invalid json' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // 期望结构: { date: "2026-08-08", items: [{title, desc, url}], summary: "一句话导读" }
  const date = body.date || new Date().toISOString().slice(0, 10);
  const items = Array.isArray(body.items) ? body.items.slice(0, 8) : [];
  if (items.length === 0) {
    return new Response(JSON.stringify({ error: 'items 不能为空' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    await kv.set('daily_hot', JSON.stringify({ date, items, summary: body.summary || '', updatedAt: new Date().toISOString() }));
    return new Response(JSON.stringify({ ok: true, date, count: items.length }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: '写入失败' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
