// GET /api/daily-hot
// 公开接口：读取 Upstash KV 中 hotwords.js 每日写入的 daily_hot 键
// KV 结构: { date: "2026-08-08", items: [{ title, desc, url }], summary: "一句话导读" }
// 返回: { ok: true, date, items, summary }；无数据时返回空结构
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

  try {
    const raw = await kv.get('daily_hot');
    let data = {};
    if (typeof raw === 'string') {
      try {
        data = JSON.parse(raw);
      } catch (e) {
        data = {};
      }
    } else if (raw && typeof raw === 'object') {
      data = raw;
    }
    const date = data.date || '';
    const items = Array.isArray(data.items) ? data.items : [];
    const summary = data.summary || '';
    return new Response(JSON.stringify({ ok: true, date, items, summary }), {
      status: 200,
      headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
    });
  } catch (e) {
    // 读取异常按无数据处理，前端走兜底
    return new Response(JSON.stringify({ ok: true, date: '', items: [], summary: '' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
