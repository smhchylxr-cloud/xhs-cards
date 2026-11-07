"""A tiny local web UI: paste JSON, get cards. For people who will not touch a terminal.

    xhs-cards serve            # http://127.0.0.1:8000
    xhs-cards serve --open     # opens the browser too

Stdlib only — no Flask, no extra dependency. Binds 127.0.0.1, renders in a temp
directory, and returns the images inline so nothing is written to your disk
unless you click "download".
"""

import base64
import json
import os
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .render import build
from .theme import PRESETS

SAMPLE = """{
  "theme": "ikb",
  "compact": true,
  "pages": [
    {
      "type": "cover",
      "eyebrow": "EXAMPLE",
      "no": "NO.001",
      "headline": ["六行 JSON", "出一张图"],
      "repo": "you/xhs-cards",
      "stats": ["★ 0 stars", "MIT"],
      "cmd": "xhs-cards build minimal.json",
      "hook": ["先能跑，再谈好看"]
    }
  ]
}"""

PAGE = """<!doctype html><meta charset="utf-8"><title>xhs-cards</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family: -apple-system, "Microsoft YaHei", sans-serif;
         background:#f4f1ea; color:#0b0b0c; }}
  header {{ padding:22px 28px; border-bottom:2px solid #0b0b0c; display:flex;
            justify-content:space-between; align-items:baseline; }}
  h1 {{ margin:0; font-size:20px; letter-spacing:.02em; }}
  .hint {{ color:#7a756c; font-size:13px; }}
  main {{ display:grid; grid-template-columns: minmax(320px, 460px) 1fr; gap:0; height:calc(100vh - 68px); }}
  .pane {{ padding:20px 24px; overflow:auto; }}
  .pane + .pane {{ border-left:1px solid rgba(0,0,0,.12); background:#faf8f3; }}
  textarea {{ width:100%; height:calc(100vh - 260px); font-family: Consolas, monospace;
              font-size:13px; line-height:1.55; padding:14px; border:1px solid #cbc6ba;
              border-radius:8px; background:#fff; resize:vertical; }}
  button {{ margin-top:14px; padding:11px 20px; font-size:15px; font-weight:700;
            background:#002fa7; color:#fff; border:0; border-radius:8px; cursor:pointer; }}
  button:disabled {{ opacity:.5; cursor:default; }}
  img {{ width:100%; max-width:360px; border:1px solid rgba(0,0,0,.1);
         border-radius:10px; box-shadow:0 12px 28px rgba(10,10,20,.16); margin:0 12px 18px 0; }}
  .err {{ background:#fdecea; border:1px solid #e0b4ae; color:#8c2f22;
          padding:14px; border-radius:8px; font-size:14px; white-space:pre-wrap; }}
  .row {{ display:flex; flex-wrap:wrap; }}
</style>
<header>
  <h1>xhs-cards</h1>
  <span class="hint">粘贴 JSON → 生成 → 右键保存图片</span>
</header>
<main>
  <div class="pane">
    <textarea id="spec">{sample}</textarea>
    <button id="go">生成图片</button>
    <span class="hint" id="status"></span>
  </div>
  <div class="pane"><div class="row" id="out"></div></div>
</main>
<script>
const btn = document.getElementById('go');
btn.onclick = async () => {{
  const out = document.getElementById('out');
  const status = document.getElementById('status');
  out.innerHTML = '';
  status.textContent = '渲染中…';
  btn.disabled = true;
  try {{
    const r = await fetch('/render', {{ method:'POST', body: document.getElementById('spec').value }});
    const data = await r.json();
    if (data.error) {{
      out.innerHTML = '<div class="err">' + data.error.replace(/</g,'&lt;') + '</div>';
    }} else {{
      out.innerHTML = data.images.map(function(src, i) {{
        return '<img src="' + src + '" title="第 ' + (i + 1) + ' 张">';
      }}).join('');
      status.textContent = data.images.length + ' 张';
    }}
  }} catch (e) {{
    out.innerHTML = '<div class="err">' + e + '</div>';
  }} finally {{
    btn.disabled = false;
  }}
}};
</script>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the console quiet
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/index.html"):
            self._send(200, PAGE.format(sample=SAMPLE.replace("<", "&lt;")))
        else:
            self._send(404, "not found")

    def do_POST(self):
        if self.path.split("?")[0] != "/render":
            return self._send(404, "not found")
        length = int(self.headers.get("Content-Length") or 0)
        if length > 2_000_000:
            return self._send(200, json.dumps({"error": "请求太大（上限 2MB）"}), "application/json")
        raw = self.rfile.read(length).decode("utf-8", "replace")
        try:
            spec = json.loads(raw)
        except json.JSONDecodeError as exc:
            return self._send(200, json.dumps({"error": f"JSON 解析失败：{exc}"}), "application/json")

        try:
            with tempfile.TemporaryDirectory() as tmp:
                paths = build(spec, tmp)
                images = []
                for path in paths:
                    with open(path, "rb") as fh:
                        images.append("data:image/png;base64," + base64.b64encode(fh.read()).decode())
            self._send(200, json.dumps({"images": images}), "application/json")
        except Exception as exc:  # noqa: BLE001 - show the message to the user
            self._send(200, json.dumps({"error": f"{type(exc).__name__}: {exc}"}), "application/json")


def serve(host="127.0.0.1", port=8000, open_browser=False):
    httpd = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}"
    print(f"xhs-cards web UI → {url}   (Ctrl+C 退出)")
    print(f"themes: {', '.join(PRESETS)}")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    finally:
        httpd.server_close()
