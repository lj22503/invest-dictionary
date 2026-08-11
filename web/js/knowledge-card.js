/* 投资词典 Invest Dictionary - 生成知识卡片（T5）
 * 纯前端 canvas，无外部依赖。词条页自动注入按钮。
 */
(function () {
  'use strict';
  if (window.__dictShareCardLoaded) return;
  window.__dictShareCardLoaded = true;

  function getTermName() {
    var h1 = document.querySelector('h1.main-title, h1');
    return h1 ? h1.textContent.trim() : document.title.split('是什么意思')[0].trim();
  }

  function getCoreSentence() {
    // 优先取 meta description，其次取第一张卡片的引语/正文
    var meta = document.querySelector('meta[name="description"]');
    if (meta && meta.content) return meta.content.trim();
    var quote = document.querySelector('.card-quote');
    if (quote) return quote.textContent.replace(/\s+/g, ' ').trim();
    var body = document.querySelector('.card-body');
    if (body) return body.textContent.replace(/\s+/g, ' ').trim().slice(0, 60);
    return '';
  }

  function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    var chars = String(text).split('');
    var line = '';
    var lines = [];
    for (var i = 0; i < chars.length; i++) {
      var test = line + chars[i];
      if (ctx.measureText(test).width > maxWidth && line) {
        lines.push(line);
        line = chars[i];
      } else {
        line = test;
      }
    }
    if (line) lines.push(line);
    lines.forEach(function (ln, idx) {
      ctx.fillText(ln, x, y + idx * lineHeight);
    });
    return lines.length * lineHeight;
  }

  function buildCard() {
    var W = 750, H = 1000;
    var canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    var ctx = canvas.getContext('2d');

    // 背景
    ctx.fillStyle = '#f5efe0';
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#c43a31';
    ctx.lineWidth = 6;
    ctx.strokeRect(18, 18, W - 36, H - 36);

    // 品牌
    ctx.fillStyle = '#c43a31';
    ctx.font = 'bold 34px "PingFang SC","Microsoft YaHei",sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('投资词典 Invest Dictionary', 60, 110);

    // 术语名
    ctx.fillStyle = '#2c2c2c';
    ctx.font = 'bold 56px "PingFang SC","Microsoft YaHei",sans-serif';
    var name = getTermName();
    if (ctx.measureText(name).width > W - 120) {
      ctx.font = 'bold 44px "PingFang SC","Microsoft YaHei",sans-serif';
    }
    ctx.fillText(name, 60, 230);

    // 分割线
    ctx.strokeStyle = '#d9d4cc';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(60, 290);
    ctx.lineTo(W - 60, 290);
    ctx.stroke();

    // 核心结论
    var core = getCoreSentence();
    if (core) {
      ctx.fillStyle = '#c43a31';
      ctx.font = 'bold 34px "PingFang SC","Microsoft YaHei",sans-serif';
      ctx.fillText('一句话解释', 60, 370);
      ctx.fillStyle = '#3a3a3a';
      ctx.font = '32px "PingFang SC","Microsoft YaHei",sans-serif';
      wrapText(ctx, core, 60, 440, W - 120, 52);
    }

    // 底部
    ctx.fillStyle = '#8b8b8b';
    ctx.font = '26px "PingFang SC","Microsoft YaHei",sans-serif';
    ctx.fillText('https://dictionary.mangofolio.com', 60, H - 120);
    ctx.fillText('内容仅供学习参考，不构成投资建议', 60, H - 70);
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
