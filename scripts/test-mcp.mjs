// 本地跑一遍 MCP 端点的四条主路径，不需要起服务：
//   node --experimental-default-type=module scripts/test-mcp.mjs
import handler from '../web/api/mcp.js';
import search from '../web/api/term-search.js';

const post = async (body) => {
  const r = await handler(
    new Request('http://127.0.0.1/api/mcp', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    }),
  );
  const txt = await r.text();
  return { status: r.status, body: txt ? JSON.parse(txt) : null };
};

const call = (name, args, id = 9) =>
  post({ jsonrpc: '2.0', id, method: 'tools/call', params: { name, arguments: args } });

const cases = [];

// 1. 握手
{
  const r = await post({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-03-26' } });
  cases.push(['initialize', r.status, r.body?.result?.protocolVersion, r.body?.result?.serverInfo?.name]);
}

// 2. 工具清单
{
  const r = await post({ jsonrpc: '2.0', id: 2, method: 'tools/list' });
  cases.push(['tools/list', r.status, r.body?.result?.tools?.map((t) => t.name).join(',')]);
}

// 3. 通知不回包
{
  const r = await post({ jsonrpc: '2.0', method: 'notifications/initialized' });
  cases.push(['notifications/initialized', r.status, r.body === null ? '无回包' : '有回包']);
}

// 4. 查词
for (const q of ['CPI', '美国 加息', '费半', '大A', '剪刀差', '这个东西我不懂']) {
  const r = await call('search_terms', { q, limit: 3 });
  const t = r.body?.result?.content?.[0]?.text || '';
  const first = t.split('\n')[0];
  cases.push([`search_terms(${q})`, r.status, first]);
}

// 5. 精确取单条
for (const title of ['剪刀差', 'CPI', '不存在的词']) {
  const r = await call('get_term', { title });
  const t = r.body?.result?.content?.[0]?.text || '';
  cases.push([`get_term(${title})`, r.status, t.split('\n')[0]]);
}

// 6. 章节
{
  const r = await call('list_chapters', {});
  const t = r.body?.result?.content?.[0]?.text || '';
  cases.push(['list_chapters', r.status, t.split('\n')[0] + ' / ' + t.split('\n')[1]]);
}

// 7. 未知方法
{
  const r = await post({ jsonrpc: '2.0', id: 3, method: 'foo/bar' });
  cases.push(['未知方法', r.status, JSON.stringify(r.body?.error)]);
}

// 8. 老的 REST 接口仍可用
{
  const r = await search(new Request('http://x/api/term-search?q=关税&n=2'));
  const j = await r.json();
  cases.push(['/api/term-search', r.status, JSON.stringify(j.hits.map((h) => h.t))]);
}

for (const c of cases) console.log(c.join(' | '));
