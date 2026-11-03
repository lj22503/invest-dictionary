// GET /api/hot-search
// 首页「大家都在搜」的数据源。两路数据，**都只为「词条」服务**：
//   1. 站内真实搜索 / 查词：KV 里 evt:dictionary:YYYY-MM-DD 的 word_lookup / search_submit，
//      聚合最近 7 天 —— 这才是真正意义上的「大家都在搜」。
//   2. 全网热榜（百度 / 微博 / 头条）→ 财经词根过滤 → 只作为「哪些词条今天值得推」的信号。
//      前端把它映射到具体词条，映射不上的直接丢掉，不会出现「点了没地方去」的热词。
//
// 响应：{ ok, source, updatedAt, search: [{ w, n }], hot: [w], daily: [w] }
import { kv } from '@vercel/kv';

export const config = {
  runtime: 'edge'
};

const CACHE_KEY = 'hot_search:v6';
const CACHE_TTL = 600; // 10 分钟
const MAX_HOT = 12;
const STAT_DAYS = 7;

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36';

// 财经词根：命中任意一个才认为这条热榜词与理财有关
const FIN_PATTERN = new RegExp([
  '股', '基金', '债', '利率', '息', '贷', '汇率', '人民币', '美元', '日元', '欧元',
  '央行', '美联储', '通胀', 'CPI', 'PPI', 'GDP', '楼市', '房价', '房贷', '地产',
  '黄金', '原油', '白银', '比特币', '加密', '稳定币',
  'ETF', '指数', 'IPO', '上市', '退市', '减持', '回购', '增持', '并购', '重组',
  '财报', '营收', '利润', '估值', '市值', '期货', '期权',
  '理财', '存款', '保险', '社保', '养老金', '养老', '个税', '关税', '财政',
  '货币', '信贷', '社融', 'MLF', 'LPR', '降准', '降息', '加息', '化债', '城投',
  '专项债', '特别国债', '大宗', '铜价', '锂', '光伏', '芯片', '算力', '大模型',
  '经济', '消费', '出口', '贸易', '制裁', '风险'
].join('|'));

// 非财经领域热词（娱乐 / 体育 / 社会花边）：命中就丢
const NEG_PATTERN = new RegExp([
  '明星', '演员', '歌手', '艺人', '作家', '导演', '剧组', '综艺', '电影', '电视剧', '演唱会',
  '恋情', '结婚', '离婚', '出轨', '怀孕', '生娃', '去世', '病逝', '悼念',
  '夺冠', '球队', '球员', '比分', '国足', '球赛',
  '游戏', '手游', '主播', '网红', '减肥', '美食', '景区', '高考', '考生', '司机', '外卖'
].join('|'));

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
    if (NEG_PATTERN.test(s)) continue;
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

/* ---------- 全网热榜（都是公开 JSON 接口）---------- */

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

async function fromWeibo(signal) {
  const j = await getJson('https://weibo.com/ajax/side/hotSearch', signal, {
    referer: 'https://weibo.com/'
  });
  const list = (j && j.data && j.data.realtime) || [];
  return list.map(function (it) { return it.word || it.note; });
}

async function fromToutiao(signal) {
  const j = await getJson('https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc', signal, {
    referer: 'https://www.toutiao.com/'
  });
  const list = (j && j.data) || [];
  return list.map(function (it) { return it.Title || it.title; });
}

/* ---------- 站内真实搜索 / 查词（KV 事件聚合）---------- */

async function collectSearchStats() {
  const counts = Object.create(null);
  const now = Date.now();
  const jobs = [];
  for (let i = 0; i < STAT_DAYS; i++) {
    const day = new Date(now - i * 86400000).toISOString().slice(0, 10);
    jobs.push(kv.lrange('evt:dictionary:' + day, -400, -1).catch(function () { return []; }));
  }
  const lists = await Promise.all(jobs);
  lists.forEach(function (list) {
    (list || []).forEach(function (raw) {
      let e = null;
      try { e = typeof raw === 'string' ? JSON.parse(raw) : raw; } catch (err) { return; }
      if (!e || !e.d) return;
      let w = '';
      if (e.e === 'word_lookup') w = e.d.word || '';
      else if (e.e === 'search_submit') w = e.d.query || '';
      w = String(w).replace(/\s+/g, ' ').trim().slice(0, 24);
      if (w.length < 2) return;
      counts[w] = (counts[w] || 0) + 1;
    });
  });
  return Object.keys(counts)
    .map(function (w) { return { w: w, n: counts[w] }; })
    .sort(function (a, b) { return b.n - a.n; })
    .slice(0, 30);
}

/* ---------- 每日热词（内容管线产出）做补位 ---------- */
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

function dedupe(list) {
  const seen = Object.create(null);
  const out = [];
  (list || []).forEach(function (w) {
    if (!w || seen[w]) return;
    seen[w] = 1;
    out.push(w);
  });
  return out;
}

export default async function handler(req) {
  if (req.method !== 'GET') {
    return json({ error: 'method not allowed' }, 405, 0);
  }

  // 缓存命中直接返回（省掉 3 次外网请求 + 7 次 KV 读）
  try {
    const raw = await kv.get(CACHE_KEY);
    let cached = raw;
    if (typeof raw === 'string') {
      try { cached = JSON.parse(raw); } catch (e) { cached = null; }
    }
    if (cached && Date.now() - (cached.ts || 0) < CACHE_TTL * 1000) {
      return json({
        ok: true,
        source: 'cache',
        updatedAt: cached.updatedAt,
        search: cached.search || [],
        hot: cached.hot || [],
        daily: cached.daily || []
      }, 200, 600);
    }
  } catch (e) { /* KV 挂了不阻断主流程 */ }

  const results = await Promise.allSettled([
    withTimeout(fromBaidu, 3000),
    withTimeout(fromWeibo, 3000),
    withTimeout(fromToutiao, 3000),
    collectSearchStats(),
    fromDailyHot()
  ]);

  const val = function (i, fallback) {
    return results[i] && results[i].status === 'fulfilled' ? results[i].value : fallback;
  };

  // 热榜三源交错合并，避免某一家霸榜
  const buckets = [pick(val(0, [])), pick(val(1, [])), pick(val(2, []))];
  const merged = [];
  const seen = Object.create(null);
  for (let i = 0; i < MAX_HOT; i++) {
    for (let b = 0; b < buckets.length; b++) {
      const w = buckets[b][i];
      if (w && !seen[w]) { seen[w] = 1; merged.push(w); }
    }
  }

  const search = val(3, []);
  const daily = dedupe(pick(val(4, []))).slice(0, 8);

  if (!merged.length && !search.length && !daily.length) {
    return json({ ok: false, search: [], hot: [], daily: [], reason: 'all sources failed' }, 200, 60);
  }

  const now = new Date();
  const payload = {
    ts: now.getTime(),
    updatedAt: now.toISOString(),
    search: search,
    hot: merged.slice(0, MAX_HOT),
    daily: daily
  };
  try { await kv.set(CACHE_KEY, JSON.stringify(payload), { ex: CACHE_TTL }); } catch (e) { /* 缓存失败不影响返回 */ }

  return json({
    ok: true,
    source: merged.length ? 'live' : 'partial',
    updatedAt: payload.updatedAt,
    search: payload.search,
    hot: payload.hot,
    daily: payload.daily
  }, 200, 300);
}

function json(body, status, maxAge) {
  const headers = { 'Content-Type': 'application/json; charset=utf-8' };
  headers['Cache-Control'] = maxAge
    ? 'public, s-maxage=' + maxAge + ', stale-while-revalidate=86400'
    : 'no-store';
  return new Response(JSON.stringify(body), { status: status, headers: headers });
}
