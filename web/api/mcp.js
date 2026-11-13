// POST /api/mcp —— 把查词能力包成 MCP 连接器（Streamable HTTP，无状态）
//
// 为什么要有它：8 个技能各自装一份 51KB 的词库副本，词库一更新就要重打 8 个包
// 再让用户重装，而用户装到的是快照，永远滞后。改成 MCP 后词库更新即生效。
//
// 支持的 JSON-RPC 方法：initialize / notifications/initialized / ping / tools/list / tools/call
// 工具：search_terms（查词）、get_term（取单条）、list_chapters（列章节）
//
// ── 传输语义按 2025-06-18 办，三处踩过的坑，改之前先读 ────────────────────────
// 1) GET 必须回 405（或 SSE）。回 200+JSON 会让每个 SDK 客户端把 GET 理解成
//    「服务端开了流又被意外关掉」，于是每 1.4 秒重连一次，静置一小时约 2500 次空转，
//    而且客户端 onerror 是 0，谁都不会发现。说明页已搬去 /api/mcp-info。
// 2) 通知（无 id）不得有回包，一律 202 空体；非法请求必须回 -32600，不能静默 202。
//    这两件事同源：判据要用「有没有 id」，不是「方法名认不认识」。
// 3) 参数不合 schema 是协议错误（-32602），不是 isError 结果。走 isError 的话
//    HTTP 仍是 200，客户端统计里成功率 100%，故障永远不上报。
import INDEX from './_term-index.js';
import { search, norm } from './_term-query.js';

export const config = { runtime: 'edge' };

const SITE = 'https://dictionary.mangofolio.com';
const NAME = 'mangofolio-dictionary';
const SEMVER = '1.1.0';
const VERSION = process.env.VERCEL_GIT_COMMIT_SHA
  ? `${SEMVER}+${process.env.VERCEL_GIT_COMMIT_SHA.slice(0, 7)}`
  : SEMVER;

// 只声明「传输语义真实现了」的版本，顺序从新到旧，回落取 VERSIONS[0]。
// 2024-11-05 故意不在里面：那个版本只有 HTTP+SSE（/sse + /messages），本服务没实现，
// 声称支持它等于「声明了不存在的传输」——客户端会去连 404 的 /sse，最后报
// `unexpected token '<'`，没人能从这个错里看出是版本问题。
const VERSIONS = ['2025-11-25', '2025-06-18', '2025-03-26'];

// 但「不声明」不等于「拒收」。改版前服务端 bug 把未知版本回落成了 2024-11-05，
// 于是所有老连接都在请求头里带着这个值。上线后直接 400 会把正在工作的会话打断
// （实测 WorkBuddy 当场报 Unsupported protocol version），而要用户重连才能恢复。
// 所以这类"历史遗留的版本串"只收不说：头里带它照常服务，initialize 时不主动给。
const LEGACY_ACCEPT = ['2024-11-05'];
const ACCEPTED = new Set([...VERSIONS, ...LEGACY_ACCEPT]);

const ALLOWED_ORIGINS = new Set([SITE, 'https://www.mangofolio.com', 'https://mangofolio.com']);
const isLocalOrigin = (o) => /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o);

const CORS_BASE = {
  'access-control-allow-methods': 'POST, GET, OPTIONS',
  'access-control-allow-headers': 'content-type, accept, mcp-protocol-version',
  vary: 'origin',
};

// 有 Origin 时回显白名单来源（配合 Vary，避免缓存串味）；没有 Origin 的
// 是非浏览器客户端（桌面 / CLI / 服务端），照旧放行。
function cors(origin) {
  return origin ? { ...CORS_BASE, 'access-control-allow-origin': origin } : CORS_BASE;
}

const rpc = (id, result) => ({ jsonrpc: '2.0', id, result });
const rpcErr = (id, code, message, data) => ({
  jsonrpc: '2.0',
  id,
  error: data === undefined ? { code, message } : { code, message, data },
});

const text = (s) => ({ content: [{ type: 'text', text: s }], isError: false });

// ── 结构化链接项（resource_link）─────────────────────────────────────────────
// 只给纯文本时，模型必须把 `%E5%8F%AF%E8%BD%AC%E5%80%BA` 这种 percent-encoded
// 链接逐字抄进回答，抄错一个字节就是给用户一个 404——而这个服务存在的唯一目的
// 就是把用户导回站内。resource_link 让客户端直接渲染成卡片，模型只引用不转写。
//
// 但它是 2025-06-18 才有的 content type：更早的客户端（2025-03-26 / 2024-11-05）
// 拿到的 content 是判别式联合，未知 type 会让解析整体失败、工具调用直接报错。
// 所以只在协商版本明确 >= 2025-06-18 时附加；请求头没带版本时保守不发，
// 宁可少一个便利，不能把一个能用的调用改坏。
//
// 2024-11-05 是例外，且是唯一例外：那个版本压根没有 Streamable HTTP，真客户端
// 发不出我们这个 POST。头里出现它，只可能是旧版服务端 bug 回落出来的遗留值
// （客户端把这个假版本缓存进了会话）。它实际在用 Streamable HTTP，就按
// 2025-06-18 对待——否则一个假的版本号会把新能力永久关掉。
const effectiveProto = (p) => (p === '2024-11-05' ? '2025-06-18' : p);

const supportsResourceLink = (proto) => {
  const p = effectiveProto(proto);
  return typeof p === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(p) && p >= '2025-06-18';
};

// text 保持原样（它是老客户端唯一的取数路径，不因新能力而删内容），
// 链接项并列追加在后。
function withLinks(out, terms, enabled) {
  if (!enabled) return out;
  for (const t of terms) {
    out.content.push({
      type: 'resource_link',
      uri: SITE + t.u,
      name: t.t,
      description: t.c ? `${t.c}` : undefined,
      mimeType: 'text/html',
    });
  }
  return out;
}

// 回显用户的查询词之前先清洗。两件事都要做：
//   1) 控制字符会把「链接：」伪造行混进结果，而伪造行与真实行同前缀同缩进，模型分不出来；
//   2) 查询词里自带的 URL 会被模型当成站内链接抄走——这个服务唯一的产出就是站内链接，
//      不能让它由外部输入决定。所以回显里的 URL 一律打码。
// 只影响回显，不影响检索用的原词（检索用的是清洗后的串，正常查询词不含 URL）。
const sanitize = (s) =>
  String(s)
    .replace(/https?:\/\/\S+/gi, '［外部链接已移除］')
    .replace(/[\u0000-\u001f\u007f]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 200);

const TOOLS = [
  {
    name: 'search_terms',
    title: '查投资词典',
    description:
      `在投资词典的 ${INDEX.length} 条中文金融词条里查词。用户提到任何一个金融名词（CPI、剪刀差、可转债、北向资金）时先调它，确认站内有没有、拿到站内链接。支持多词查询（「美国 加息」）。返回词条名、链接、章节、四张卡片小标题。只在不知道确切词条名时用；知道确切名字用 get_term 更省。`,
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        q: { type: 'string', minLength: 1, maxLength: 200, description: '要查的词或一句话，例如 CPI、M1-M2剪刀差、关税 影响' },
        limit: { type: 'integer', minimum: 1, maximum: 20, default: 3, description: '返回条数，默认 3（够判断是哪一条），最多 20。想更全就换更精确的词，不要靠调大 limit' },
      },
      required: ['q'],
      additionalProperties: false,
    },
  },
  {
    name: 'get_term',
    title: '取词条骨架',
    description:
      `按词条名取一条词条的结构（章节、四张卡片小标题、站内链接）。知道确切词条名时用它，比 search_terms 省。只记得大概说法、不确定站内叫什么时用 search_terms。参数可与站内标题不完全一致（「剪刀差」能命中「M1-M2剪刀差」）。`,
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    inputSchema: {
      type: 'object',
      properties: {
        title: { type: 'string', minLength: 1, maxLength: 200, description: '词条名，可与站内标题不完全一致' },
      },
      required: ['title'],
      additionalProperties: false,
    },
  },
  {
    name: 'list_chapters',
    title: '列出篇章',
    description: `列出词典的全部篇章及每章词条数（共 ${INDEX.length} 条）。用户问「你们都有哪些内容」「从哪看起」时用它给出全貌，不要凭空罗列。`,
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
  },
];

// ── 参数校验：直接从 inputSchema 派生，避免 schema 与校验两处口头约定 ──────────
const typeOf = (v) => (Array.isArray(v) ? 'array' : v === null ? 'null' : typeof v);

const describe = (p) => {
  if (!p) return '无此参数';
  if (p.type === 'string') {
    if (p.minLength != null && p.maxLength != null) return `string（${p.minLength}–${p.maxLength} 字）`;
    return 'string';
  }
  if (p.type === 'integer' || p.type === 'number') {
    if (p.minimum != null && p.maximum != null) return `${p.type}（${p.minimum}–${p.maximum}）`;
    return p.type;
  }
  return p.type || '任意';
};

// 返回 null 表示通过；否则返回可直接放进 error.data 的定位信息
function checkArgs(schema, args) {
  const a = args === undefined || args === null ? {} : args;
  if (typeof a !== 'object' || Array.isArray(a)) {
    return { field: 'arguments', expected: 'object', received: typeOf(a) };
  }
  for (const k of schema.required || []) {
    if (!(k in a) || a[k] === undefined) return { field: k, expected: describe(schema.properties[k]) + '，必填', received: 'undefined' };
  }
  for (const [k, v] of Object.entries(a)) {
    const p = (schema.properties || {})[k];
    if (!p) {
      if (schema.additionalProperties === false) return { field: k, expected: '不在参数表内，请删除', received: typeOf(v) };
      continue;
    }
    if (p.type === 'string' && typeof v !== 'string') return { field: k, expected: describe(p), received: typeOf(v) };
    if ((p.type === 'integer' || p.type === 'number') && typeof v !== 'number') return { field: k, expected: describe(p), received: typeOf(v) };
    if (p.type === 'integer' && !Number.isInteger(v)) return { field: k, expected: describe(p), received: String(v) };
    if (typeof v === 'string') {
      if (p.minLength != null && v.length < p.minLength) return { field: k, expected: describe(p), received: '空字符串' };
      if (p.maxLength != null && v.length > p.maxLength) return { field: k, expected: describe(p), received: `长度 ${v.length}` };
    }
    if (typeof v === 'number') {
      if (p.minimum != null && v < p.minimum) return { field: k, expected: describe(p), received: String(v) };
      if (p.maximum != null && v > p.maximum) return { field: k, expected: describe(p), received: String(v) };
    }
  }
  return null;
}

// ── 工具实现（返回内容保持原样，只把回显的查询词做了清洗）──────────────────────
function callTool(name, args = {}, opts = {}) {
  const link = !!opts.linkTerms;
  if (name === 'search_terms') {
    const q = sanitize(args.q);
    const limit = args.limit === undefined ? 3 : args.limit;
    const { hits, total } = search(INDEX, q, limit);
    if (!hits.length) {
      return text(`「${q}」在站内没有对应词条。可以继续正常作答，但不要编造站内链接。`);
    }
    const lines = hits.map((h, i) => {
      const url = SITE + h.u;
      const cards = (h.k || []).map((x) => '· ' + x).join('\n    ');
      return `${i + 1}. ${h.t}\n   链接：${url}\n   章节：${h.c || '（未分章）'}${cards ? '\n   卡片：\n    ' + cards : ''}`;
    });
    return withLinks(text(`「${q}」命中 ${hits.length} 条（共 ${total} 条候选）：\n\n${lines.join('\n\n')}`), hits, link);
  }

  if (name === 'get_term') {
    const raw = sanitize(args.title);
    const q = norm(raw);
    const fmt = (x, note = '') =>
      withLinks(
        text(`${note}${x.t}\n链接：${SITE}${x.u}\n章节：${x.c || '（未分章）'}\n卡片：\n${(x.k || []).map((y, i) => `${i + 1}. ${y}`).join('\n') || '（无）'}`),
        [x],
        link,
      );

    const exact =
      INDEX.find((x) => norm(x.t) === q) ||
      // 别名完全相等时，优先主名以该别名开头的词条（「剪刀差」不该落到括号里带它的那条）
      INDEX.find((x) => (x.a || []).some((a) => norm(a) === q && norm(x.t).startsWith(q)));
    if (exact) return fmt(exact);

    // 用户写的是站内标题的一部分（「剪刀差」→「M1-M2剪刀差」），分够高就直接给
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

  return null;
}

// ── 消息处理 ────────────────────────────────────────────────────────────────
// 返回值：undefined 表示不需要回包（通知 / 客户端回传的 response）
function handle(msg, origin, proto) {
  // 非法消息一律 -32600，不要静默成 202——否则客户端会一直等一个永远不来的响应
  if (!msg || typeof msg !== 'object' || Array.isArray(msg)) {
    return rpcErr(null, -32600, 'Invalid Request: 必须是单个 JSON-RPC 对象');
  }
  if (typeof msg.method !== 'string') {
    // 客户端回传的 response（我们不发请求，收到就直接吞掉）
    if ('result' in msg || 'error' in msg) return undefined;
    return rpcErr(msg.id ?? null, -32600, 'Invalid Request: 缺 method');
  }
  if (msg.jsonrpc !== '2.0') return rpcErr(msg.id ?? null, -32600, 'Invalid Request: jsonrpc 必须为 "2.0"');

  const hasId = Object.prototype.hasOwnProperty.call(msg, 'id') && msg.id !== undefined;
  if (!hasId) {
    // 通知：JSON-RPC 规定不得回包。判据是「有没有 id」，不是「方法名认不认识」。
    return undefined;
  }
  if (msg.id === null) return rpcErr(null, -32600, 'Invalid Request: id 不能为 null');

  const { id, method, params } = msg;

  if (method === 'initialize') {
    const want = params?.protocolVersion;
    const pick = VERSIONS.includes(want) ? want : VERSIONS[0];
    return rpc(
      id,
      rpcResult({
        protocolVersion: pick,
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: NAME, title: '投资词典', version: VERSION, websiteUrl: SITE },
        // 最后一句是「怎么把链接交到用户手上」。不给这句，模型会把 `链接：https://…`
        // 原样抄进回答，用户看到的是一串 percent-encoded 字符；写成 Markdown 链接，
        // 客户端才会渲染成可点的词条名（技能包里一直就是这么约定的，见 generator/SKILL.md）。
        instructions: `投资词典：${INDEX.length} 条中文金融词条。用户提到金融名词时先用 search_terms 查，拿到站内链接后附在回答末尾；查不到就说没收录，不要编链接。引用站内链接时写成 Markdown 链接 [词条名](完整链接)，不要直接贴裸 URL。本服务只给词条骨架，不提供正文全文。`,
      }),
    );
  }

  if (method === 'notifications/initialized' || method === 'initialized') return undefined;
  if (method === 'ping') return rpc(id, {});

  if (method === 'tools/list') return rpc(id, { tools: TOOLS });

  if (method === 'tools/call') {
    const name = params?.name;
    const tool = TOOLS.find((t) => t.name === name);
    // 未知工具是协议错误，不是工具执行结果
    if (!tool) return rpcErr(id, -32602, `Unknown tool: ${String(name)}`, { supported: TOOLS.map((t) => t.name) });

    const bad = checkArgs(tool.inputSchema, params?.arguments);
    if (bad) return rpcErr(id, -32602, `Invalid params: ${bad.field} 应为 ${bad.expected}`, bad);

    try {
      const out = callTool(name, params?.arguments || {}, { linkTerms: supportsResourceLink(proto) });
      if (!out) return rpcErr(id, -32602, `Unknown tool: ${name}`);
      let bytes = 0;
      try {
        bytes = JSON.stringify(out).length;
      } catch {}
      // 只记结构化字段，不记查询内容（用户输入不入库），只记长度
      console.log(
        JSON.stringify({
          evt: 'mcp_tool',
          tool: name,
          q_len: String(params?.arguments?.q ?? params?.arguments?.title ?? '').length,
          limit: params?.arguments?.limit ?? null,
          isError: out.isError,
          bytes,
          proto: proto || null,
          links: out.content.filter((c) => c.type === 'resource_link').length,
          origin: origin || null,
        }),
      );
      return rpc(id, out);
    } catch (e) {
      console.error(JSON.stringify({ evt: 'mcp_tool_error', tool: name, msg: String(e?.message || e).slice(0, 200) }));
      // 对外只给固定文案，异常原文进日志
      return rpcErr(id, -32603, 'Internal error: 工具执行失败');
    }
  }

  return rpcErr(id, -32601, `不支持的方法：${method}`);
}

// 2026-07-28 起 result 要带 resultType；当前版本不需要，留个单点便于将来迁移
const rpcResult = (r) => r;

// ── 入口 ────────────────────────────────────────────────────────────────────
export default async function handler(req) {
  const origin = req.headers.get('origin');
  const allowed = !origin || ALLOWED_ORIGINS.has(origin) || isLocalOrigin(origin);
  const H = cors(origin);

  if (!allowed) {
    // 挡在 DNS rebinding 与「任意网页用 no-cors 空打接口」这条路上。
    return new Response(JSON.stringify({ error: 'origin not allowed' }), {
      status: 403,
      headers: { 'content-type': 'application/json' },
    });
  }

  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: H });

  // GET 必须 405：回 200+JSON 会让客户端以为流断了，每 1.4 秒重连一次
  if (req.method !== 'POST') {
    return new Response(null, {
      status: 405,
      headers: { ...H, allow: 'POST, OPTIONS', link: `<${SITE}/api/mcp-info>; rel="help"` },
    });
  }

  const ctype = req.headers.get('content-type') || '';
  if (!ctype.includes('application/json')) {
    // text/plain 的 POST 不触发 CORS 预检，是「网页直调」的入口，所以必须挡
    return new Response(JSON.stringify(rpcErr(null, -32600, 'Content-Type 必须是 application/json')), {
      status: 415,
      headers: { 'content-type': 'application/json', ...H },
    });
  }

  const proto = req.headers.get('mcp-protocol-version');
  if (proto && !ACCEPTED.has(proto)) {
    return new Response(
      JSON.stringify(rpcErr(null, -32600, `Unsupported protocol version: ${proto}`, { supported: VERSIONS })),
      { status: 400, headers: { 'content-type': 'application/json', ...H } },
    );
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify(rpcErr(null, -32700, 'JSON 解析失败')), {
      status: 400,
      headers: { 'content-type': 'application/json', ...H },
    });
  }

  // 2025-06-18 已移除 batch：POST 体必须是单个消息对象
  if (Array.isArray(body)) {
    return new Response(
      JSON.stringify(rpcErr(null, -32600, 'Invalid Request: batch 已不在 2025-06-18 规范内，请逐条发送')),
      { status: 400, headers: { 'content-type': 'application/json', ...H } },
    );
  }

  const out = handle(body, origin, proto);

  // 通知 / 客户端 response：202 且无体
  if (out === undefined) return new Response(null, { status: 202, headers: H });

  return new Response(JSON.stringify(out), {
    headers: { 'content-type': 'application/json; charset=utf-8', ...H },
  });
}
