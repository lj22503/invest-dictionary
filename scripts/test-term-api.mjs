// 本地跑一遍两个接口，不需要起服务。
//   node --experimental-default-type=module scripts/test-term-api.mjs
import { writeFileSync, mkdirSync } from 'node:fs';
import { renderTermPage, validate } from '../web/api/_term-render.js';
import searchHandler from '../web/api/term-search.js';

const call = (fn, url, init) => fn(new Request(url, init));

async function searchTest() {
  for (const q of ['CPI', '货币', '关税', '缩量', '不存在的词zzz']) {
    const res = await call(searchHandler, `http://x/api/term-search?q=${encodeURIComponent(q)}&n=3`);
    const j = await res.json();
    console.log(`\n[search] ${q} → ${res.status} total=${j.total}`);
    for (const h of j.hits || []) {
      console.log(`   ${h.t}  (${h.c})  卡片：${(h.k || []).slice(0, 2).join(' / ')}`);
    }
  }
}

function pageTest() {
  const payload = {
    title: '货币',
    summary: '货币就是一条信任链。链条不断，钱就是钱。链条断了，它就是废纸。',
    keywords: ['信用', '购买力', '通货膨胀'],
    cards: [
      {
        q: '你手里攥着的**100块**',
        body: [
          { p: '其实是一张__别人愿意收它__的投票券。' },
          { p: '它本身什么都不是。' },
          { quote: '货币就是一条**信任链**。链条不断，钱就是钱。链条断了，它就是废纸。' },
          { note: '想想看：你的存款，到底是财富，还是别人打给你的信任白条？' },
        ],
      },
      {
        q: '100万亿买半个面板',
        body: [
          { p: '2015 年，一个津巴布韦大爷揣着一捆面值 **100万亿** 的纸币去买面包。' },
        ],
      },
      {
        q: '打开手机银行',
        body: [
          { ul: ['看一眼活期存款余额。', '算一下三个月生活费是多少。', '把超出部分换成不容易被印钞稀释的东西。'] },
        ],
      },
    ],
  };

  const errs = validate(payload);
  console.log('\n[page] 校验：', errs.length ? errs : '通过');

  const html = renderTermPage(payload);
  const left = html.match(/@@[A-Z_]+@@/g);
  console.log('[page] 长度', html.length, '残留占位符', left || '无');
  console.log('[page] 标题标签', /<title>(.*?)<\/title>/.exec(html)?.[1]);
  console.log('[page] canonical', /rel="canonical" href="([^"]+)"/.exec(html)?.[1]);
  console.log('[page] 高亮 span', (html.match(/class="highlight"/g) || []).length);
  console.log('[page] 卡片数', (html.match(/class="card"/g) || []).length);
  console.log('[page] 上下篇', /class="pager-next" title="([^"]*)"/.exec(html)?.[1]);

  const ld = /<script type="application\/ld\+json">([\s\S]*?)<\/script>/.exec(html)?.[1];
  try {
    const o = JSON.parse(ld);
    console.log('[page] JSON-LD ok:', o['@type'], o.name, o.url);
  } catch (e) {
    console.log('[page] JSON-LD 解析失败', e.message);
  }

  mkdirSync('dist', { recursive: true });
  writeFileSync('dist/term-api-out.html', html);
  console.log('[page] 已写出 dist/term-api-out.html');
}

function badTest() {
  const bad = validate({ title: '', cards: [] });
  console.log('\n[validate] 空请求 →', bad);
}

await searchTest();
pageTest();
badTest();
