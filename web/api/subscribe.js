// POST /api/subscribe
// 接收邮箱，校验格式，写入 KV 订阅列表
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

  let body;
  try {
    body = await req.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: 'invalid json' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const email = String(body.email || '').trim().toLowerCase();
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !re.test(email)) {
    return new Response(JSON.stringify({ error: '邮箱格式不对' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    // 去重写入订阅集合，并记录订阅时间
    const added = await kv.sadd('subscribers', email);
    await kv.hset('subscriber:meta', { [email]: new Date().toISOString() });
    return new Response(JSON.stringify({ ok: true, added: added === 1 }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: '订阅失败，请稍后重试' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
