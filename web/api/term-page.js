// POST /api/term-page
//
// 传结构化 JSON，拿一整页词条 HTML。样式、页脚、面包屑、上下篇、结构化数据
// 全部在服务端拼好，模型不再逐字写 HTML（原来一次要写 31KB）。
//
// 用法（技能里）：
//   curl -s -X POST https://dictionary.mangofolio.com/api/term-page \
//        -H 'content-type: application/json' -d @payload.json -o 新词条.html
//
// 校验不过会返回 400 + errors 数组，照着改 JSON 再传一次即可。
// 想要便于解析的形态，加 ?format=json，返回 { ok, url, bytes, html }。
//
// 字段说明见 _term-render.js 顶部注释。
import { renderTermPage, validate } from './_term-render.js';

export const config = { runtime: 'edge' };

const SITE = 'https://dictionary.mangofolio.com';

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });

export default async function handler(req) {
  if (req.method === 'GET') {
    return json({
      ok: true,
      usage: 'POST 一段 JSON 上来，返回整页 HTML',
      example: {
        title: '货币',
        summary: '货币就是一条信任链，链条不断，钱就是钱。',
        chapter: '第一篇：钱的本质',
        keywords: ['信用', '购买力'],
        cards: [
          { q: '你手里攥着的**100块**', body: [{ p: '其实是一张投票券。' }, { quote: '货币就是一条信任链。' }] },
          { q: '打开手机银行', body: [{ ul: ['看一眼活期余额', '算一下三个月生活费'] }] },
        ],
      },
    });
  }
  if (req.method !== 'POST') return json({ ok: false, error: '只支持 POST' }, 405);

  let payload;
  try {
    payload = await req.json();
  } catch {
    return json({ ok: false, error: '请求体不是合法 JSON' }, 400);
  }

  const errs = validate(payload);
  if (errs.length) return json({ ok: false, error: '参数不完整', errors: errs }, 400);

  const html = renderTermPage(payload);
  const url = `${SITE}/terms/${encodeURIComponent(String(payload.title).trim())}`;

  if (new URL(req.url).searchParams.get('format') === 'json') {
    return json({ ok: true, url, bytes: new TextEncoder().encode(html).length, html });
  }

  return new Response(html, {
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'x-term-url': url,
      'x-term-bytes': String(new TextEncoder().encode(html).length),
      'cache-control': 'no-store',
    },
  });
}
