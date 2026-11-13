// POST /api/mcp —— 把查词能力包成 MCP 连接器（Streamable HTTP，无状态）
//
// 为什么要有它：8 个技能各自装一份 51KB 的词库副本，词库一更新就要重打 8 个包
// 再让用户重装，而用户装到的是快照，永远滞后。改成 MCP 后词库更新即生效。
//
// 支持的 JSON-RPC 方法：initialize / notifications/initialized / ping / tools/list / tools/call
// 工具：search_terms（查词）、get_term（取单条）、list_chapters（列章节）
import INDEX from './_term-index.js';
import { search, norm } from './_term-query.js';

export const config = { runtime: 'edge' };

const SITE = 'https://dictionary.mangofolio.com';
const VERSIONS = ['2025-06-18', '2025-03-26', '2024-11-05'];
const NAME = 'mangofolio-dictionary';
const VERSION = '1.0.0';

const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'POST, GET, OPTIONS',
  'access-control-allow-headers': 'content-type, accept, mcp-session-id, mcp-protocol-version',
  'access-control-expose-headers': 'mcp-session-id',
};

const rpc = (id, result) => ({ jsonrpc: '2.0', id, result });
const rpcErr = (id, code, message) => ({ jsonrpc: '2.0', id, error: { code, message } });

const TOOLS = [
  {
    name: 'search_terms',
    description:
      '在投资词典的 1133 条中文金融词条里查词。用户提到任何一个金融名词（CPI、剪刀差、可转债、北向资金）时先调它，确认站内有没有、拿到可点击链接。支持多词查询（「美国 加息」）。返回词条名、链接、章节、四张卡片小标题。',
    inputSchema: {
      type: 'object',
      properties: {
        q: { type: 'string', description: '要查的词或一句话，例如 CPI、M1-M2剪刀差、关税 影响' },
        limit: { type: 'number', description: '返回条数，默认 5，最多 20' },
      },
      required: ['q'],
    },
  },
  {
    name: 'get_term',
    description:
      '按词条名精确取一条词条的结构（章节、四张卡片小标题、站内链接）。当你已经知道词条名、只想要它的讲解骨架时用；只记得大概说法就用 search_terms。',
    inputSchema: {
      type: 'object',
      properties: { title: { type: 'string', description: '词条名，可与站内标题不完全一致' } },
      required: ['title'],
    },
  },
  {
    name: 'list_chapters',
    description:
      '列出词典的全部篇章及每章词条数。用户问「你们都有哪些内容」「从哪看起」时用它给出全貌，不要凭空罗列。',
    inputSchema: { type: 'object', properties: {} },
  },
];

function text(s) {
  return { content: [{ type: 'text', text: s }], isError: false };
}

function callTool(name, args = {}) {
  if (name === 'search_terms') {
    const q = String(args.q || '').trim();
    if (!q) return { content: [{ type: 'text', text: '缺参数 q' }], isError: true };
    const limit = Math.min(Math.max(parseInt(args.limit || '5', 10) || 5, 1), 20);
    const { hits, total } = search(INDEX, q, limit);
    if (!hits.length) {
      return text(`「${q}」在站内没有对应词条。可以继续正常作答，但不要编造站内链接。`);
    }
    const lines = hits.map((h, i) => {
      const url = SITE + h.u;
      const cards = (h.k || []).map((x) => '· ' + x).join('\n    ');
      return `${i + 1}. ${h.t}\n   链接：${url}\n   章节：${h.c || '（未分章）'}${cards ? '\n   卡片：\n    ' + cards : ''}`;
    });
    return text(`「${q}」命中 ${hits.length} 条（共 ${total} 条候选）：\n\n${lines.join('\n\n')}`);
  }

  if (name === 'get_term') {
    const raw = String(args.title || '').trim();
    if (!raw) return { content: [{ type: 'text', text: '缺参数 title' }], isError: true };
    const q = norm(raw);
    const fmt = (x, note = '') => {
      const cards = (x.k || []).map((y, i) => `${i + 1}. ${y}`).join('\n');
      return text(
        `${note}${x.t}\n链接：${SITE}${x.u}\n章节：${x.c || '（未分章）'}\n卡片：\n${cards || '（无）'}`,
      );
    };

    const exact =
      INDEX.find((x) => norm(x.t) === q) ||
      // 别名完全相等时，优先主名以该别名开头的词条（「剪刀差」不该落到括号里带它的那条）
      INDEX.find((x) => (x.a || []).some((a) => norm(a) === q && norm(x.t).startsWith(q)));
    if (exact) return fmt(exact);

    // 用户写的是站内标题的一部分（「剪刀差」→「M1-M2剪刀差」），分够高就直接给，不再列一堆候选
    const { hits } = search(INDEX, raw, 1);
    if (hits.length && hits[0].s >= 56) {
      const found = INDEX.find((x) => x.t === hits[0].t);
      if (found) return fmt(found, `（站内标题为「${found.t}」）\n`);
    }
    if (!hits.length) return text(`站内没有「${raw}」。`);
    const cand = search(INDEX, raw, 3).hits.map((h) => `· ${h.t}　${SITE}${h.u}`).join('\n');
    return text(`站内没有「${raw}」，相近的有：\n${cand}`);
  }

  if (name === 'list_chapters') {
    const m = new Map();
    for (const t of INDEX) {
      const c = t.c || '（未分章）';
      m.set(c, (m.get(c) || 0) + 1);
    }
    const rows = [...m.entries()]
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], 'zh'))
      .map(([c, n]) => `· ${c}：${n} 条`);
    return text(`共 ${INDEX.length} 条词条，${m.size} 个篇章：\n${rows.join('\n')}`);
  }

  return { content: [{ type: 'text', text: `未知工具：${name}` }], isError: true };
}

function handle(msg) {
  const { id = null, method, params } = msg || {};

  if (method === 'initialize') {
    const want = params?.protocolVersion;
    return rpc(id, {
      protocolVersion: VERSIONS.includes(want) ? want : VERSIONS[VERSIONS.length - 1],
      capabilities: { tools: { listChanged: false } },
      serverInfo: { name: NAME, version: VERSION },
      instructions:
        '投资词典：1133 条中文金融词条。用户提到金融名词时先用 search_terms 查，拿到站内链接后附在回答末尾；查不到就说没收录，不要编链接。',
    });
  }

  // 通知类消息没有 id，按规范不回包体
  if (!method && !id) return null;
  if (method === 'notifications/initialized' || method === 'initialized') return null;
  if (method === 'ping') return rpc(id, {});

  if (method === 'tools/list') return rpc(id, { tools: TOOLS });

  if (method === 'tools/call') {
    const name = params?.name;
    try {
      return rpc(id, callTool(name, params?.arguments || {}));
    } catch (e) {
      return rpcErr(id, -32603, `工具执行失败：${e.message}`);
    }
  }

  if (method === 'resources/list') return rpc(id, { resources: [] });
  if (method === 'prompts/list') return rpc(id, { prompts: [] });

  return rpcErr(id, -32601, `不支持的方法：${method}`);
}

export default async function handler(req) {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });

  if (req.method === 'GET') {
    return new Response(
      JSON.stringify({
        ok: true,
        name: NAME,
        hint: '这是 MCP 端点，用 POST 发 JSON-RPC；浏览器直接打开看到这条说明是正常的。',
        tools: TOOLS.map((t) => t.name),
      }),
      { headers: { 'content-type': 'application/json; charset=utf-8', ...CORS } },
    );
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: '只支持 POST' }), { status: 405, headers: CORS });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify(rpcErr(null, -32700, 'JSON 解析失败')), {
      status: 400,
      headers: { 'content-type': 'application/json', ...CORS },
    });
  }

  const batch = Array.isArray(body);
  const out = (batch ? body : [body]).map(handle).filter(Boolean);

  // 全是通知（无回包）时按规范返回 202
  if (!out.length) return new Response(null, { status: 202, headers: CORS });

  return new Response(JSON.stringify(batch ? out : out[0]), {
    headers: { 'content-type': 'application/json; charset=utf-8', ...CORS },
  });
}
