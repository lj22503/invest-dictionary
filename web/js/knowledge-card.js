/* 投资词典 Invest Dictionary - 生成知识卡片（T5+）
 * 纯前端 canvas，无外部依赖。词条页自动注入按钮。
 * v2：承载原文长图——将词条页全部卡片（标题/正文/要点/一句话）渲染为自适应高度的竖长图。
 */
(function () {
  'use strict';
  if (window.__dictShareCardLoaded) return;
  window.__dictShareCardLoaded = true;

  var W = 1242;            // 画布宽度（朋友圈封面标准）
  var PAD = 90;            // 左右留白
  var MAXW = W - PAD * 2; // 正文可用宽度 = 1062

  var EYEBROW_FONT = 'bold 32px "Inter","PingFang SC","Microsoft YaHei","Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif';
  var TITLE_FONT_LG = 'bold 72px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
  var TITLE_FONT_MD = 'bold 56px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
  var ENTITLE_FONT = 'italic 36px "Fraunces","Noto Serif SC",serif';

  var TITLE_LH = 64;       // 章节标题 48px 64 行高（48 * 1.33）
  var BLOCK_LH = 70;       // 正文 38px 70 行高（38 * 1.85）
  var QUOTE_LH = 60;       // 引用 36px 60 行高
  var CARD_GAP = 56;       // 章节间距
  var HEADING_TO_BODY = 28; // 章节标题 → 正文
  var DIVIDER_GAP = 32;    // 分隔虚线 → 下一章节标题

  function getTermName() {
    var h1 = document.querySelector('h1.main-title, h1');
    return h1 ? h1.textContent.trim() : document.title.split('是什么意思')[0].trim();
  }

  function getChapter() {
    var crumbs = document.querySelectorAll('.term-breadcrumb span');
    if (crumbs && crumbs.length >= 3) {
      // 结构：首页 › 章节 › 词条名，取倒数第二个
      return crumbs[crumbs.length - 2].textContent.trim();
    }
    return '';
  }

  function cleanText(s) {
    return String(s || '').replace(/\s+/g, ' ').trim();
  }

  // 从页面 DOM 收集全部卡片内容
  function collectCards() {
    var cards = [];
    var nodes = document.querySelectorAll('article.card');
    nodes.forEach(function (card) {
      var numEl = card.querySelector('.card-number');
      var titleEl = card.querySelector('.card-title');
      var body = card.querySelector('.card-body');
      var item = {
        num: numEl ? cleanText(numEl.textContent) : '',
        title: titleEl ? cleanText(titleEl.textContent) : '',
        blocks: []
      };
      if (body) {
        body.childNodes.forEach(function (node) {
          if (node.nodeType !== 1) return;
          var tag = node.tagName.toLowerCase();
          var cls = node.className || '';
          if (tag === 'p') {
            var t = cleanText(node.textContent);
            if (t) item.blocks.push({ type: 'p', text: t });
          } else if (tag === 'ul') {
            var lis = [];
            node.querySelectorAll('li').forEach(function (li) {
              var t = cleanText(li.textContent);
              if (t) lis.push(t);
            });
            if (lis.length) item.blocks.push({ type: 'ul', items: lis });
          } else if (tag === 'div' && String(cls).indexOf('card-quote') !== -1) {
            var q = cleanText(node.textContent);
            if (q) item.blocks.push({ type: 'quote', text: q });
          } else if (tag === 'div' && String(cls).indexOf('card-divider') !== -1) {
            // 忽略分隔线
          }
        });
      }
      if (item.title || item.blocks.length) cards.push(item);
    });
    return cards;
  }

  // 按宽度切分为行（返回行数组）
  function wrapLines(ctx, text, maxW) {
    var chars = String(text).split('');
    var lines = [];
    var line = '';
    for (var i = 0; i < chars.length; i++) {
      var test = line + chars[i];
      if (ctx.measureText(test).width > maxW && line) {
        lines.push(line);
        line = chars[i];
      } else {
        line = test;
      }
    }
    if (line) lines.push(line);
    return lines;
  }

  // 绘制一行（返回行高占用）
  function drawLine(ctx, text, x, y, font, color, lineHeight) {
    ctx.font = font;
    ctx.fillStyle = color;
    ctx.fillText(text, x, y);
    return lineHeight;
  }

  // 计算某块内容的高度（用于预测量画布总高）
  function measureBlock(ctx, block, lh) {
    ctx.font = '38px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif';
    if (block.type === 'ul') {
      var h = 0;
      block.items.forEach(function (it) {
        h += wrapLines(ctx, '· ' + it, MAXW - 16).length * lh;
        h += 12;
      });
      return h;
    }
    return wrapLines(ctx, block.text, MAXW).length * lh;
  }

  function measureTitle(ctx, title, font, lh) {
    ctx.font = font;
    return wrapLines(ctx, title, MAXW).length * lh;
  }

  function buildCard() {
    var name = getTermName();
    var chapter = getChapter();
    var cards = collectCards();

    var H_HEAD = 280;              // 头部区域高度（eyebrow + 标题 + 橙条）
    var FOOT_H = 170;              // 底部区域高度
    var MIN_H = 1000;

    // ---- 第一遍：测量总高度 ----
    var ctx0 = document.createElement('canvas').getContext('2d');
    ctx0.font = TITLE_FONT_LG;
    var titleFont = ctx0.measureText(name).width > MAXW ? TITLE_FONT_MD : TITLE_FONT_LG;
    var bodyH = 0;
    cards.forEach(function (card) {
      bodyH += CARD_GAP;
      if (card.title) bodyH += measureTitle(ctx0, card.title, 'bold 48px "Noto Serif SC","Source Han Serif SC","Songti SC","SimSun",serif', TITLE_LH);
      bodyH += HEADING_TO_BODY;
      card.blocks.forEach(function (b) {
        if (b.type === 'quote') bodyH += measureBlock(ctx0, b, QUOTE_LH) + 24;
        else bodyH += measureBlock(ctx0, b, BLOCK_LH);
      });
      bodyH += DIVIDER_GAP; // 章节间分隔虚线 + 间距
    });
    var H = Math.max(1500, H_HEAD + bodyH + FOOT_H);

    // ---- 第二遍：正式绘制 ----
    var canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    var ctx = canvas.getContext('2d');

    // 背景（纯白）
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, W, H);

    var y = 0;

    // Eyebrow 眉题
    y += 70;
    ctx.font = EYEBROW_FONT;
    ctx.fillStyle = '#F97316';
    ctx.textAlign = 'left';
    ctx.fillText('MANGOFOLIO · 投资词典', PAD, y);

    // 主标题（Noto Serif SC 72px 900）
    y += 80;
    ctx.font = titleFont;
    ctx.fillStyle = '#241610';
    var titleLines = wrapLines(ctx, name, MAXW);
    titleLines.forEach(function (ln) {
      ctx.fillText(ln, PAD, y);
      y += 80;
    });

    // En-title（Fraunces italic 橙）
    y += 8;
    var enTitle = 'Invest Dictionary · ' + (chapter || '14-day reverse repo');
    ctx.font = ENTITLE_FONT;
    ctx.fillStyle = '#F97316';
    ctx.fillText(enTitle, PAD, y);

    // 2px 橙条 80% 宽
    y += 24;
    ctx.fillStyle = '#F97316';
    ctx.fillRect(PAD, y, MAXW * 0.8, 2);

    // 正文卡片
    y += 60;
    cards.forEach(function (card) {
      y += 44;
      if (card.title) {
        ctx.font = 'bold 34px "Inter","PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillStyle = '#E05E0A';
        var titleLines = wrapLines(ctx, card.num + ' ' + card.title, MAXW);
        titleLines.forEach(function (ln) {
          ctx.fillText(ln, PAD, y);
          y += TITLE_LH;
        });
        y += 8;
      }
      card.blocks.forEach(function (b) {
        if (b.type === 'quote') {
          // 一句话：左橙竖线 + 深橙字
          y += 10;
          ctx.strokeStyle = '#F97316';
          ctx.lineWidth = 4;
          ctx.beginPath();
          ctx.moveTo(PAD, y - 8);
          ctx.lineTo(PAD, y + 8);
          ctx.stroke();
          ctx.font = 'bold 30px "Inter","PingFang SC","Microsoft YaHei",sans-serif';
          ctx.fillStyle = '#E05E0A';
          var qLines = wrapLines(ctx, b.text, MAXW - 12);
          var qStart = y;
          qLines.forEach(function (ln) {
            ctx.fillText(ln, PAD + 18, y);
            y += QUOTE_LH;
          });
          // 橙竖线拉长到引语底部
          ctx.beginPath();
          ctx.moveTo(PAD, qStart - 12);
          ctx.lineTo(PAD, y - QUOTE_LH + 10);
          ctx.stroke();
          y += 8;
        } else if (b.type === 'ul') {
          ctx.font = '30px "Inter","PingFang SC","Microsoft YaHei",sans-serif';
          ctx.fillStyle = '#3A332C';
          b.items.forEach(function (it) {
            var ls = wrapLines(ctx, '• ' + it, MAXW - 16);
            ls.forEach(function (ln) {
              ctx.fillText(ln, PAD + 16, y);
              y += BLOCK_LH;
            });
            y += 4;
          });
        } else {
          ctx.font = '30px "Inter","PingFang SC","Microsoft YaHei",sans-serif';
          ctx.fillStyle = '#3A332C';
          var ps = wrapLines(ctx, b.text, MAXW);
          ps.forEach(function (ln) {
            ctx.fillText(ln, PAD, y);
            y += BLOCK_LH;
          });
        }
      });
    });

    // 底部（暖灰副标）
    y = H - FOOT_H + 50;
    ctx.font = '26px "Inter","PingFang SC","Microsoft YaHei",sans-serif';
    ctx.fillStyle = '#8A7D70';
    ctx.fillText('https://dictionary.mangofolio.com', PAD, y);
    ctx.fillText('内容仅供学习参考，不构成投资建议', PAD, y + 50);
    return canvas;
  }

  function downloadCanvas(canvas, filename) {
    try {
      canvas.toBlob(function (blob) {
        if (!blob) return;
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 3000);
      }, 'image/png');
    } catch (e) {
      var url2 = canvas.toDataURL('image/png');
      var a2 = document.createElement('a');
      a2.href = url2;
      a2.download = filename;
      document.body.appendChild(a2);
      a2.click();
      document.body.removeChild(a2);
    }
  }

  function init() {
    var back = document.querySelector('.term-back');
    if (!back) return;
    if (document.querySelector('.ft-knowledge-card-btn')) return;

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'share-btn ft-knowledge-card-btn';
    btn.textContent = '生成知识卡片';
    btn.style.cssText = 'margin-right:8px;';
    btn.onclick = function () {
      var canvas = buildCard();
      downloadCanvas(canvas, 'knowledge-' + Date.now() + '.png');
    };
    back.insertBefore(btn, back.firstChild);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
