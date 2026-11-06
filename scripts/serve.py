# -*- coding: utf-8 -*-
"""
serve.py —— 本地预览服务器（对齐 Vercel cleanUrls 行为）

背景：
  P0-1 之后站内链接一律不带 .html。Python 自带的 http.server 不支持 cleanUrls，
  直接用它预览会看到满屏 404，容易误判成「改坏了」。
  生产环境 vercel.json 已开 cleanUrls:true + trailingSlash:false，
  本脚本在本地复现同一套规则，保证「本地所见 = 线上所得」。

规则（与 Vercel 一致）：
  1. /terms/货币          -> 返回 web/terms/货币.html
  2. /terms/货币.html     -> 301 重定向到 /terms/货币
  3. /dictionary          -> 返回 web/dictionary.html
  4. 静态资源（css/js/png 等）按原路径直出

API 兜底（web/api/*.js 是 Vercel serverless，本地跑不起来）：
  - 只读接口（daily-hot / hot-search / hotword）转发到线上，保证本地所见=线上所得
  - 写接口（events / subscribe / unsubscribe / send-daily）本地吞掉，
    绝不转发——否则本地预览会污染线上统计与订阅名单
  - 转发失败不报错，仍返回 404，前端本就有降级分支

用法：
  python scripts/serve.py            # 默认 8899
  python scripts/serve.py 9000       # 指定端口
  MF_API_UPSTREAM=https://xxx python scripts/serve.py   # 指到别的上游（如预发）
"""
import os
import sys
import html
import json
import posixpath
import http.server
import urllib.request
import urllib.error
import urllib.parse

API_UPSTREAM = os.environ.get("MF_API_UPSTREAM", "https://dictionary.mangofolio.com").rstrip("/")
# 只读：可以放心转发到线上
API_READONLY = {"/api/daily-hot", "/api/hot-search"}
# 一个都不许转发（会在线上产生写操作）
API_LOCAL_ONLY = {"/api/events", "/api/subscribe", "/api/unsubscribe", "/api/send-daily"}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")

SKIP_EXT = {".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
            ".json", ".txt", ".xml", ".webmanifest", ".woff", ".woff2"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self._dispatch("GET")

    def do_HEAD(self):
        self._dispatch("HEAD")

    def do_POST(self):
        self._dispatch("POST")

    def _dispatch(self, method):
        # 剥离 query / fragment
        raw = self.path
        clean = self.path.split("?", 1)[0].split("#", 1)[0]
        try:
            decoded = urllib.parse.unquote(clean)
        except Exception:
            decoded = clean

        # /api/* 交给转发层，不参与文件查找
        if decoded.startswith("/api/"):
            return self._api(decoded, raw, method)

        if decoded.endswith("/"):
            decoded = decoded.rstrip("/") or "/"

        fs = self._to_fs(decoded)
        if fs is None:
            return self._404(decoded)

        # Vercel 规则 2：显式 .html -> 301 到无后缀
        if self._is_page(decoded) and clean.endswith(".html"):
            target = clean[:-5]
            return self._301(target)

        if os.path.isdir(fs):
            idx = os.path.join(fs, "index.html")
            if os.path.exists(idx):
                return self._serve(idx)
            return self._404(decoded)

        if not os.path.exists(fs):
            # Vercel 规则 1：无后缀页面 -> 尝试补 .html
            if not self._is_page(decoded):
                return self._404(decoded)
            alt = fs + ".html"
            if os.path.exists(alt):
                return self._serve(alt)
            return self._404(decoded)

        return self._serve(fs)

    def _api(self, path, raw, method):
        p = path.rstrip("/") or "/"
        # 写接口本地吞掉——绝不能转发，否则本地预览会写脏线上数据
        if p in API_LOCAL_ONLY:
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if p not in API_READONLY:
            return self._404(path)

        body = None
        if method == "POST":
            n = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(n) if n > 0 else b""
        req = urllib.request.Request(API_UPSTREAM + raw, data=body, method=method)
        req.add_header("Accept", "application/json")
        if body:
            req.add_header("Content-Type", "application/json")
        try:
            # 显式绕过代理：shell 的 http_proxy 会把 127.0.0.1 的转发也代理掉 → 假 502
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(req, timeout=8) as resp:
                data = resp.read()
                ctype = resp.headers.get("Content-Type", "application/json")
        except Exception as exc:
            # 上游不可达不算本地故障，前端有降级分支，这里只留提示
            return self._json(404, {
                "ok": False,
                "error": "本地未取到线上数据：%s" % exc,
                "hint": "页面会自动降级，不影响版式预览",
                "upstream": API_UPSTREAM + raw,
            })
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Preview-Upstream", API_UPSTREAM)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _to_fs(self, decoded):
        rel = decoded.lstrip("/")
        rel = posixpath.normpath(rel) if rel else ""
        if rel.startswith(".."):
            return None
        return os.path.join(WEB, rel) if rel else WEB

    @staticmethod
    def _is_page(path):
        ext = os.path.splitext(path)[1].lower()
        return ext not in SKIP_EXT

    def _serve(self, fs_path):
        try:
            with open(fs_path, "rb") as f:
                body = f.read()
        except OSError:
            return self._404(fs_path)
        ctype = self.guess_type(fs_path)
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _301(self, target):
        self.send_response(301)
        self.send_header("Location", target)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _404(self, path):
        body = ("<h1>404 Not Found</h1><p>%s</p>" % html.escape(str(path))).encode("utf-8")
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    os.chdir(WEB)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("本地预览（cleanUrls 已模拟）：http://127.0.0.1:%d/" % port)
    print("Ctrl+C 停止")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
