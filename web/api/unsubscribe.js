// GET /api/unsubscribe?email=xxx
// 一键退订：从订阅列表移除邮箱
import { kv } from '@vercel/kv';

export const config = {
  runtime: 'edge'
};

export default async function handler(req) {
  if (req.method !== 'GET') {
    return new Response(JSON.stringify({ error: 'method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const url = new URL(req.url);
  const email = (url.searchParams.get('email') || '').trim().toLowerCase();
  if (!email) {
    return new Response('缺少 email 参数', {
      status: 400,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
  }

  try {
    await kv.srem('subscribers', email);
    await kv.hdel('subscriber:meta', email);
    return new Response('已退订成功，感谢曾经关注。', {
      status: 200,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
  } catch (e) {
    return new Response('退订失败，请稍后重试', {
      status: 500,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
  }
}
