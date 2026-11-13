// 查词的打分逻辑，/api/term-search 与 /api/mcp 共用一个实现。
// 两处各写一份的话，改了一处忘了另一处，站内和 MCP 搜出来的结果会慢慢分叉。

export const norm = (s) =>
  String(s || '')
    .toLowerCase()
    .replace(/[\s\-_·、，,。.（）()《》"'“”‘’]/g, '');

// 用户嘴里的说法 → 词库里更常见的写法。只在直接查不到时补一条检索词，不覆盖原查询。
// 每条都要在词库里真能命中，映射到不存在的词等于白搭一次扫描。
export const COLLOQUIAL = {
  '大a': 'A股',
  'a股': 'A股',
  美债: '国债',
  通胀: '通货膨胀',
  关税战: '关税',
  降息降准: '降息',
  打新: '新股',
  北向: '沪股通',
  南向: '港股通',
  油价: '原油',
};

// 一句自然语言拆成若干检索词：「美国 加息 影响」→ [美国, 加息, 影响]
// 太长的那一段（整句话）不单独参与，否则几乎必然零命中
export function tokens(raw) {
  const parts = String(raw || '')
    .split(/[\s,，、;；/／|]+/)
    .map(norm)
    .filter((s) => s && s.length <= 12);
  const out = new Set(parts.length ? parts : [norm(raw)]);
  const extra = COLLOQUIAL[norm(raw)];
  if (extra) out.add(norm(extra));
  for (const p of parts) {
    const e = COLLOQUIAL[p];
    if (e) out.add(norm(e));
  }
  return [...out].filter(Boolean);
}

export function score(term, q) {
  const t = norm(term.t);
  const as = (term.a || []).map(norm);
  const ks = (term.k || []).map(norm);

  if (t === q) return 100;
  // 主名本身就以查询词开头，说明这是它"本名"，应压过只把该词放在括号里的词条
  // （查 CPI → 「CPI（居民消费价格指数）」优先于「通货膨胀（CPI）」）
  if (t.startsWith(q) && as.includes(q)) return 99;
  if (as.includes(q)) return 92;
  if (t.startsWith(q)) return 86;
  if (as.some((x) => x.startsWith(q))) return 78;
  if (t.includes(q)) return 60;
  if (as.some((x) => x.includes(q))) return 56;
  if (q.includes(t) && t.length >= 2) return 50;
  if (ks.some((x) => x.includes(q))) return 25;
  if (norm(term.c).includes(q)) return 10;
  return 0;
}

/** 返回 [{ t, u, c, k, s }]，按相关度降序。 */
export function search(index, raw, limit = 5) {
  const qs = tokens(raw);
  if (!qs.length) return { hits: [], total: 0, tokens: [] };

  const scored = [];
  for (const term of index) {
    let best = 0;
    let hit = 0;
    for (const q of qs) {
      const s = score(term, q);
      if (s > best) best = s;
      if (s > 0) hit += 1;
    }
    if (best === 0) continue;
    // 命中多个检索词说明更贴题（「美国 加息」同时命中加息和美股相关词）
    const s = best + (hit >= 2 ? 6 * hit : 0);
    scored.push({ s, term });
  }

  scored.sort(
    (a, b) =>
      b.s - a.s ||
      a.term.t.length - b.term.t.length ||
      a.term.t.localeCompare(b.term.t),
  );

  const hits = scored.slice(0, limit).map((x) => ({
    t: x.term.t,
    u: x.term.u,
    c: x.term.c,
    k: x.term.k,
    s: x.s,
  }));
  return { hits, total: scored.length, tokens: qs };
}
