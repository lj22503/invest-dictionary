// GET /api/send-daily
// 每日定时任务：读取当日热词，群发给所有订阅者
// 由 Vercel Cron 触发（见 vercel.json crons 配置）
import { kv } from '@vercel/kv';
import { Resend } from 'resend';

export const config = {
  runtime: 'edge'
};

// 每日热词邮件正文（HTML）
function buildHtml(date, items, summary) {
  const list = items.map((it, i) => `
    <tr>
      <td style="padding:14px 20px;border-bottom:1px solid #eee;font-size:15px;line-height:1.7;">
        <div style="font-size:17px;font-weight:600;color:#111;">
          <span style="display:inline-block;background:#e23;color:#fff;font-size:11px;padding:2px 7px;border-radius:3px;margin-right:8px;vertical-align:2px;">HOT</span>${escapeHtml(it.title)}
        </div>
        <div style="color:#666;margin-top:4px;">${escapeHtml(it.desc || '')}</div>
        ${it.url ? `<div style="margin-top:6px;"><a href="${escapeHtml(it.url)}" style="color:#c00;text-decoration:none;font-size:14px;">查看词条详解 →</a></div>` : ''}
      </td>
    </tr>`).join('');

  return `
  <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'PingFang SC','Microsoft YaHei',sans-serif;max-width:600px;margin:0 auto;background:#fff;">
    <div style="background:#111;color:#fff;padding:22px 24px;border-radius:8px 8px 0 0;">
      <div style="font-size:20px;font-weight:700;">今日热词 · ${date}</div>
      <div style="font-size:13px;color:#bbb;margin-top:4px;">说人话 · 不装逼 · 每天一篇</div>
    </div>
    <div style="border:1px solid #eee;border-top:none;border-radius:0 0 8px 8px;">
      ${summary ? `<div style="padding:14px 20px;background:#faf7f3;color:#555;font-size:14px;line-height:1.7;border-bottom:1px solid #eee;">${escapeHtml(summary)}</div>` : ''}
      <table style="width:100%;border-collapse:collapse;">${list}</table>
      <div style="padding:16px 20px;font-size:13px;color:#999;line-height:1.7;">
        你收到这封邮件，是因为在 <a href="https://dictionary.mangofolio.com" style="color:#c00;">投资词典</a> 订阅了每日热词。<br>
        不想再收？<a href="https://dictionary.mangofolio.com/api/unsubscribe?email=__EMAIL__" style="color:#c00;">点此退订</a>
      </div>
    </div>
  </div>`;
}

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

export default async function handler(req) {
  if (req.method !== 'GET') {
    return new Response(JSON.stringify({ error: 'method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // 仅允许 Vercel Cron 触发（携带 CRON_SECRET）
  const cronSecret = process.env.CRON_SECRET;
  const auth = req.headers.get('authorization') || '';
  if (!cronSecret || auth !== `Bearer ${cronSecret}`) {
    return new Response(JSON.stringify({ error: 'unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const apiKey = process.env.RESEND_API_KEY;
  const fromEmail = process.env.FROM_EMAIL;
  if (!apiKey || !fromEmail) {
    return new Response(JSON.stringify({ error: 'RESEND_API_KEY / FROM_EMAIL 未配置' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const raw = await kv.get('daily_hot');
    if (!raw) {
      return new Response(JSON.stringify({ ok: true, skipped: 'no daily hot' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    const { date, items, summary } = typeof raw === 'string' ? JSON.parse(raw) : raw;

    const emails = await kv.smembers('subscribers');
    if (!emails.length) {
      return new Response(JSON.stringify({ ok: true, skipped: 'no subscribers' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const resend = new Resend(apiKey);
    let sent = 0, failed = 0;
    const errors = [];

    // 逐个发送（Resend 免费版建议逐封；量大可分批）
    for (const email of emails) {
      const html = buildHtml(date, items, summary).replace(/__EMAIL__/g, encodeURIComponent(email));
      try {
        const { error } = await resend.emails.send({
          from: fromEmail,
          to: [email],
          subject: `今日热词 · ${date}｜说人话，不装逼`,
          html
        });
        if (error) {
          failed++;
          errors.push(`${email}: ${error.message}`);
        } else {
          sent++;
        }
      } catch (e) {
        failed++;
        errors.push(`${email}: ${e.message}`);
      }
    }

    return new Response(JSON.stringify({ ok: true, date, sent, failed, errors: errors.slice(0, 5) }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: 'send failed: ' + e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
