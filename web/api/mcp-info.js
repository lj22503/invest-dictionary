// GET /api/mcp-info —— 给人和健康检查看的说明页
//
// 为什么单独开一个：MCP 的 GET 语义只有两种合法回应（SSE 流或 405）。
// 把「浏览器打开能看懂」的说明挂在 /api/mcp 上，会让每个 SDK 客户端把
// 200+JSON 理解成「服务端开了流又关掉」，每 1.4 秒重连一次——静置一小时
// 约 2500 次空转，且客户端 onerror 为 0，谁都不会发现。
// 所以说明搬到这里，/api/mcp 的 GET 老老实实回 405。
import INDEX from './_term-index.js';

export const config = { runtime: 'edge' };

const SITE = 'https://dictionary.mangofolio.com';

const INFO = {
  ok: true,
  name: 'mangofolio-dictionary',
  title: '投资词典 MCP 连接器',
  endpoint: `${SITE}/api/mcp`,
  transport: 'Streamable HTTP（单端点 POST，无状态，不需要 Mcp-Session-Id）',
  protocolVersions: ['2025-11-25', '2025-06-18', '2025-03-26'],
  auth: '无（公开只读）',
  terms: INDEX.length,
  tools: ['search_terms', 'get_term', 'list_chapters'],
  hint: '这里是说明页，不是 MCP 端点。浏览器直接打开看到这条说明是正常的；客户端请连 /api/mcp 并用 POST 发 JSON-RPC。',
  example: {
    request: {
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/call',
      params: { name: 'search_terms', arguments: { q: 'CPI', limit: 5 } },
    },
    curl: `curl -s ${SITE}/api/mcp -H 'content-type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_terms","arguments":{"q":"CPI"}}}'`,
  },
};

export default async function handler(req) {
  if (!['GET', 'HEAD'].includes(req.method)) {
    return new Response(JSON.stringify({ error: '只支持 GET' }), {
      status: 405,
      headers: { 'content-type': 'application/json', allow: 'GET, HEAD' },
    });
  }
  const body = JSON.stringify(INFO, null, 2);
  return new Response(req.method === 'HEAD' ? null : body, {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'public, max-age=300',
      'access-control-allow-origin': '*',
    },
  });
}
