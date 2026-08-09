// GET /api/send-daily
// 每日定时任务：读取当日热词，群发给所有订阅者
// 由 Vercel Cron 触发（见 vercel.json crons 配置）
import { kv } from '@vercel/kv';
import { Resend } from 'resend';

export const config = {
  runtime: 'edge'
};

// 每日热词邮件正文（HTML）
// 风格：投资词典网站自有视觉（纸感米白底 + 朱砂红主色 + 墨色正文 + 衬线标题），
// 排版参考：顶部导航 + 居中大标题 + 白色圆角卡片嵌热词列表 + 朱砂红圆角 CTA + 底部品牌信息
function buildHtml(date, items, summary) {
  const list = items.map((it, i) => `
    <tr>
      <td style="padding:16px 22px;border-bottom:1px solid #D9D4CC;font-size:15px;line-height:1.7;">
        <div style="font-size:16px;font-weight:600;color:#2C2C2C;">
          <span style="display:inline-block;background:#C43A31;color:#fff;font-size:11px;padding:3px 8px;border-radius:999px;margin-right:8px;vertical-align:2px;">HOT</span>${escapeHtml(it.title)}
        </div>
        <div style="color:#5A5A5A;margin-top:5px;">${escapeHtml(it.desc || '')}</div>
        ${it.url ? `<div style="margin-top:7px;"><a href="${escapeHtml(it.url)}" style="color:#C43A31;text-decoration:none;font-size:13px;font-weight:600;border-bottom:2px solid #C43A31;">查看词条详解 →</a></div>` : ''}
      </td>
    </tr>`).join('');

  return `
  <div style="font-family:'PingFang SC','Microsoft YaHei','Hiragino Sans GB',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:600px;margin:0 auto;background:#F5F2EC;border:1px solid #D9D4CC;border-radius:12px;overflow:hidden;">
    <div style="background:#fff;padding:14px 24px;text-align:right;font-size:12px;color:#5A5A5A;border-bottom:1px solid #D9D4CC;">
      <a href="https://dictionary.mangofolio.com" style="color:#C43A31;text-decoration:none;font-weight:600;">投资词典</a>
    </div>
    <div style="padding:36px 24px 10px;text-align:center;">
      <div style="font-size:26px;font-weight:800;color:#2C2C2C;letter-spacing:1px;font-family:'Noto Serif SC','KaiTi','STKaiti',serif;">今日热词 · ${date}</div>
      <div style="font-size:14px;color:#C43A31;margin-top:8px;font-weight:600;">说人话 · 不装逼 · 每天一篇</div>
      ${summary ? `<div style="max-width:440px;margin:16px auto 0;font-size:14px;color:#5A5A5A;line-height:1.8;">${escapeHtml(summary)}</div>` : ''}
    </div>
    <div style="padding:20px 24px;">
      <div style="background:#fff;border:1px solid #D9D4CC;border-radius:12px;padding:6px 8px;">
        <table style="width:100%;border-collapse:collapse;">${list}</table>
        <div style="padding:18px 22px;text-align:center;">
          <a href="https://dictionary.mangofolio.com" style="display:inline-block;background:#C43A31;color:#fff;text-decoration:none;font-size:14px;font-weight:700;padding:11px 26px;border-radius:999px;">查看全部词条</a>
        </div>
      </div>
    </div>
    <div style="padding:20px 24px 28px;text-align:center;font-size:12px;color:#8C867B;line-height:1.8;">
      <div style="font-weight:600;color:#2C2C2C;">投资词典 · dictionary.mangofolio.com</div>
      <div style="margin-top:4px;">你收到这封邮件，是因为订阅了投资词典每日热词。</div>
      <div style="margin-top:8px;">
        <a href="https://dictionary.mangofolio.com/api/unsubscribe?email=__EMAIL__" style="color:#C43A31;text-decoration:underline;">退订</a>
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
