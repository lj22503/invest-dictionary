// GET /api/hot-search
// 首页「大家都在搜」数据源：抓互联网热榜 → 过滤出理财相关词 → KV 缓存 10 分钟
//
// 设计取舍：
// 1. 只碰「公开热榜」的 JSON 接口，不爬页面；任一源失败不影响其它源。
// 2. 中文财经词只占全网热榜一小撮，过滤后常常不足 8 条 → 与 daily_hot（内容管线
//    从互联网新闻产出的每日热词）合并补齐，保证首页永远有词可显示。
// 3. 全部失败时返回 ok:false，前端保留 HTML 里的静态兜底词，不留白。
// 4. 不缓存失败结果，避免「一次抽风挂 10 分钟」。
import { kv } from '@vercel/kv';

export const config = {
  runtime: 'edge'
};

const CACHE_KEY = 'hot_search:v3';
const CACHE_TTL = 600; // 10 分钟
const MAX_ITEMS = 12;

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36';

// 理财相关词根：命中任意一个才认为这条热榜词值得放到首页
const FIN_PATTERN = new RegExp([
  '股', '基金', '债', '利率', '息', '贷', '汇率', '人民币', '美元', '日元', '欧元',
  '央行', '美联储', '通胀', 'CPI', 'PPI', 'GDP', '楼市', '房价', '房贷', '地产',
  '黄金', '原油', '白银', '比特币', '加密', '稳定币',
  'ETF', '指数', 'IPO', '上市', '退市', '减持', '回购', '增持', '并购', '重组',
  '财报', '营收', '利润', '估值', '市值', '期货', '期权', '期权',
  '理财', '存款', '保险', '社保', '养老金', '养老', '个税', '关税', '财政',
  '货币', '信贷', '社融', 'MLF', 'LPR', '降准', '降息', '加息', '化债', '城投',
  '专项债', '特别国债', '大宗', '铜价', '锂', '光伏', '芯片', '算力', 'AI',
  '经济', '消费', '出口', '贸易', '制裁', '风险'
].join('|'));

// 热榜词尾巴上常见的角标，清掉以后才做词条匹配
const NOISE = /^(热|沸|新|爆|荐|热榜|热搜)|\s*(热|沸|新|爆|荐)$/g;

function clean(word) {
  let s = String(word || '')
    .replace(/[【】\[\]（）()「」《》""'']/g, ' ')
    .replace(NOISE, '')
    .replace(/\s+/g, ' ')
    .trim();
  /* 热搜榜要的是「搜索词」，不是新闻标题：先在分隔符处截断，只留前半句 */
  s = s.split(/[ 　|｜·:：，,、—–]/)[0].trim();
  if (s.length < 2 || s.length > 14) return '';
  if (!/[\u4e00-\u9fa5A-Za-z]/.test(s)) return '';
  return s;
}

function pick(list) {
  const out = [];
  for (const w of list || []) {
    const s = clean(w);
    if (!s) continue;
    if (!FIN_PATTERN.test(s)) continue;
    if (out.indexOf(s) === -1) out.push(s);
  }
  return out;
}

async function withTimeout(run, ms) {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), ms);
  try {
    return await run(ctl.signal);
  } finally {
    clearTimeout(timer);
  }
}

async function getJson(url, signal, extraHeaders) {
  const res = await fetch(url, {
    signal,
    headers: Object.assign({
      'user-agent': UA,
      accept: 'application/json, text/plain, */*'
    }, extraHeaders || {})
  });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  return res.json();
}

/* ---------- 各热榜源（都是公开 JSON 接口）---------- */

// 百度热搜
async function fromBaidu(signal) {
  const j = await getJson('https://top.baidu.com/api/board?platform=wise&tab=realtime', signal, {
    referer: 'https://top.baidu.com/board?tab=realtime'
  });
  const cards = (j && j.data && j.data.cards) || [];
  const words = [];
  cards.forEach(function (card) {
    (card.content || []).forEach(function (it) {
      words.push(it.word || it.query || it.title);
    });
  });
  return words;
}

// 微博热搜
async function fromWeibo(signal) {
  const j = await getJson('https://weibo.com/ajax/side/hotSearch', signal, {
    referer: 'https://weibo.com/'
  });
  const list = (j && j.data && j.data.realtime) || [];
  return list.map(function (it) { return it.word || it.note; });
}

// 今日头条热榜
async function fromToutiao(signal) {
  const j = await getJson('https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc', signal, {
    referer: 'https://www.toutiao.com/'
  });
  const list = (j && j.data) || [];
  return list.map(function (it) { return it.Title || it.title; });
}

/* ---------- 用内容管线产出的每日热词补齐 ---------- */
async function fromDailyHot() {
  try {
    const raw = await kv.get('daily_hot');
    let d = raw;
    if (typeof raw === 'string') {
      try { d = JSON.parse(raw); } catch (e) { d = {}; }
    }
    const items = (d && d.items) || [];
    return items.map(function (it) { return it.title; }).filter(Boolean);
  } catch (e) {
    return [];
  }
}

export default async function handler(req) {
  if (req.method !== 'GET') {
    return json({ error: 'method not allowed' }, 405);
  }

  // 缓存命中直接返回（命中时省掉 3 次外网请求）
  try {
    const raw = await kv.get(CACHE_KEY);
    let cached = raw;
    if (typeof raw === 'string') {
      try { cached = JSON.parse(raw); } catch (e) { cached = null; }
    }
    if (cached && cached.items && cached.items.length && Date.now() - (cached.ts || 0) < CACHE_TTL * 1000) {
      return json({ ok: true, source: 'cache', updatedAt: cached.updatedAt, items: cached.items }, 200, 600);
    }
  } catch (e) { /* KV 挂了不阻断主流程 */ }

  const tasks = [
    withTimeout(fromBaidu, 3000),
    withTimeout(fromWeibo, 3000),
    withTimeout(fromToutiao, 3000)
  ];
  const settled = await Promise.allSettled(tasks);

  // 按「百度 → 微博 → 头条」顺序交错合并，避免某一家霸榜
  const buckets = settled.map(function (r) {
    return r.status === 'fulfilled' ? pick(r.value) : [];
  });
  const merged = [];
  const seen = {};
  for (let i = 0; i < MAX_ITEMS; i++) {
    for (let b = 0; b < buckets.length; b++) {
      const w = buckets[b][i];
      if (w && !seen[w]) { seen[w] = 1; merged.push(w); }
    }
  }

  /* 收口：同 2 字前缀最多留 2 条（既有「A股」，也还能留一条 A股 具体事件），再短词优先 */
  const shaped = [];
  const prefixCount = {};
  merged.forEach(function (w) {
    var key = w.slice(0, 2);
    var n = prefixCount[key] || 0;
    if (n >= 2) return;
    prefixCount[key] = n + 1;
    shaped.push(w);
  });
  shaped.sort(function (a, b) { return a.length - b.length; });
  merged.length = 0;
  shaped.forEach(function (w) { merged.push(w); });

  const liveCount = merged.length;
  if (merged.length < 8) {
    pick(await fromDailyHot()).forEach(function (w) {
      if (merged.length < MAX_ITEMS && !seen[w]) { seen[w] = 1; merged.push(w); }
    });
  }

  if (!merged.length) {
    return json({ ok: false, items: [], reason: 'all sources failed' }, 200, 60);
  }

  const now = new Date();
  const payload = {
    ts: now.getTime(),
    updatedAt: now.toISOString(),
    items: merged.slice(0, MAX_ITEMS)
  };
  try { await kv.set(CACHE_KEY, JSON.stringify(payload), { ex: CACHE_TTL }); } catch (e) { /* 缓存失败不影响返回 */ }

  return json({
    ok: true,
    source: liveCount >= 8 ? 'live' : 'mixed',
    updatedAt: payload.updatedAt,
    items: payload.items
  }, 200, 300);
}

function json(body, status, maxAge) {
  return new Response(JSON.stringify(body), {
    status: status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, s-maxage=' + (maxAge || 60) + ', stale-while-revalidate=86400'
    }
  });
}
