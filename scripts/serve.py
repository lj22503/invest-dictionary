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

用法：
  python scripts/serve.py            # 默认 8899
  python scripts/serve.py 9000       # 指定端口
"""
import os
import sys
import html
import posixpath
import http.server
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")

SKIP_EXT = {".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
            ".json", ".txt", ".xml", ".webmanifest", ".woff", ".woff2"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self._dispatch("GET")

    def do_HEAD(self):
        self._dispatch("HEAD")

    def _dispatch(self, method):
        # 剥离 query / fragment
        clean = self.path.split("?", 1)[0].split("#", 1)[0]
        try:
            decoded = urllib.parse.unquote(clean)
        except Exception:
            decoded = clean

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
