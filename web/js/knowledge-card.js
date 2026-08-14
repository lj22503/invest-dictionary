/* 投资词典 Invest Dictionary - 生成知识卡片（T5+）
 * 纯前端 canvas，无外部依赖。词条页自动注入按钮。
 * v2：承载原文长图——将词条页全部卡片（标题/正文/要点/一句话）渲染为自适应高度的竖长图。
 */
(function () {
  'use strict';
  if (window.__dictShareCardLoaded) return;
  window.__dictShareCardLoaded = true;

  var W = 750;            // 画布宽度
  var PAD = 60;           // 左右留白
  var MAXW = W - PAD * 2; // 正文可用宽度

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
    ctx.font = '30px "PingFang SC","Microsoft YaHei",sans-serif';
    if (block.type === 'ul') {
      var h = 0;
      block.items.forEach(function (it) {
        h += wrapLines(ctx, '• ' + it, MAXW - 16).length * lh;
        h += 6;
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

    var H_HEAD = 330;              // 头部区域高度（品牌+标题+分割线）
    var FOOT_H = 170;              // 底部区域高度
    var MIN_H = 1000;

    // ---- 第一遍：测量总高度 ----
    var ctx0 = document.createElement('canvas').getContext('2d');
    ctx0.font = '34px "PingFang SC","Microsoft YaHei",sans-serif';
    var titleFont = ctx0.measureText(name).width > MAXW ? 'bold 44px "PingFang SC","Microsoft YaHei",sans-serif' : 'bold 56px "PingFang SC","Microsoft YaHei",sans-serif';
    var bodyH = 0;
    var TITLE_LH = 64, BLOCK_LH = 48, QUOTE_LH = 46;
    cards.forEach(function (card) {
      bodyH += 44; // 卡片间距
      if (card.title) bodyH += measureTitle(ctx0, card.num + ' ' + card.title, 'bold 34px "PingFang SC","Microsoft YaHei",sans-serif', TITLE_LH);
      bodyH += 14;
      card.blocks.forEach(function (b) {
        if (b.type === 'quote') bodyH += measureBlock(ctx0, b, QUOTE_LH) + 18;
        else bodyH += measureBlock(ctx0, b, BLOCK_LH);
      });
    });
    var H = Math.max(MIN_H, H_HEAD + bodyH + FOOT_H);

    // ---- 第二遍：正式绘制 ----
    var canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    var ctx = canvas.getContext('2d');

    // 背景
    ctx.fillStyle = '#f5efe0';
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#c43a31';
    ctx.lineWidth = 6;
    ctx.strokeRect(18, 18, W - 36, H - 36);

    var y = 0;

    // 品牌
    y += 110;
    ctx.font = 'bold 34px "PingFang SC","Microsoft YaHei",sans-serif';
    ctx.fillStyle = '#c43a31';
    ctx.textAlign = 'left';
    ctx.fillText('投资词典 Invest Dictionary', PAD, y);

    // 术语名
    y += 120;
    ctx.font = titleFont;
    ctx.fillStyle = '#2c2c2c';
    ctx.fillText(name, PAD, y);
    y += 16;
    if (chapter) {
      ctx.font = '26px "PingFang SC","Microsoft YaHei",sans-serif';
      ctx.fillStyle = '#8b8b8b';
      ctx.fillText(chapter, PAD, y + 20);
      y += 48;
    }

    // 分割线
    y += 20;
    ctx.strokeStyle = '#d9d4cc';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(PAD, y);
    ctx.lineTo(W - PAD, y);
    ctx.stroke();

    // 正文卡片
    y += 60;
    cards.forEach(function (card) {
      y += 44;
      if (card.title) {
        ctx.font = 'bold 34px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillStyle = '#c43a31';
        var titleLines = wrapLines(ctx, card.num + ' ' + card.title, MAXW);
        titleLines.forEach(function (ln) {
          ctx.fillText(ln, PAD, y);
          y += TITLE_LH;
        });
        y += 8;
      }
      card.blocks.forEach(function (b) {
        if (b.type === 'quote') {
          // 一句话：左红竖线 + 红字
          y += 10;
          ctx.strokeStyle = '#c43a31';
          ctx.lineWidth = 4;
          ctx.beginPath();
          ctx.moveTo(PAD, y - 8);
          ctx.lineTo(PAD, y + 8);
          ctx.stroke();
          ctx.font = 'bold 30px "PingFang SC","Microsoft YaHei",sans-serif';
          ctx.fillStyle = '#c43a31';
          var qLines = wrapLines(ctx, b.text, MAXW - 12);
          var qStart = y;
          qLines.forEach(function (ln) {
            ctx.fillText(ln, PAD + 18, y);
            y += QUOTE_LH;
          });
          // 红竖线拉长到引语底部
          ctx.beginPath();
          ctx.moveTo(PAD, qStart - 12);
          ctx.lineTo(PAD, y - QUOTE_LH + 10);
          ctx.stroke();
          y += 8;
        } else if (b.type === 'ul') {
          ctx.font = '30px "PingFang SC","Microsoft YaHei",sans-serif';
          ctx.fillStyle = '#3a3a3a';
          b.items.forEach(function (it) {
            var ls = wrapLines(ctx, '• ' + it, MAXW - 16);
            ls.forEach(function (ln) {
              ctx.fillText(ln, PAD + 16, y);
              y += BLOCK_LH;
            });
            y += 4;
          });
        } else {
          ctx.font = '30px "PingFang SC","Microsoft YaHei",sans-serif';
          ctx.fillStyle = '#3a3a3a';
          var ps = wrapLines(ctx, b.text, MAXW);
          ps.forEach(function (ln) {
            ctx.fillText(ln, PAD, y);
            y += BLOCK_LH;
          });
        }
      });
    });

    // 底部
    y = H - FOOT_H + 50;
    ctx.font = '26px "PingFang SC","Microsoft YaHei",sans-serif';
    ctx.fillStyle = '#8b8b8b';
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
