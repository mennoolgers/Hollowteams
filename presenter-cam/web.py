"""A tiny web server, only reachable from this Mac (127.0.0.1), for the Stream Deck.

  /effect/<name>          press the effect (toggle or trigger)
  /effect/<name>/on       switch on      /effect/<name>/off   switch off
  /effect/<name>/<extra>  extra actions, e.g. /effect/slides/next
  /clear                  remove every effect
  /status                 which effects are on (JSON)
  /                       a simple page with buttons, handy for testing
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlparse

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Presenter Cam</title>
<style>
 body{font:16px -apple-system,Helvetica,sans-serif;background:%(deep)s;color:#fff;margin:0;padding:24px}
 h1{font-size:20px;margin:0 0 16px} .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px}
 button{font:inherit;padding:16px;border:0;border-radius:12px;background:%(primary)s;color:#fff;cursor:pointer}
 button.on{background:%(accent)s;color:%(deep)s} button.clear{background:#E07A5F}
 code{display:block;margin-top:18px;opacity:.75;font-size:13px;line-height:1.6;white-space:pre}
</style></head><body><h1>Presenter Cam</h1><div class="grid" id="g"></div><code id="u"></code>
<script>
async function load(){const s=await (await fetch('/status')).json();const g=document.getElementById('g');g.innerHTML='';
 for(const e of s.effects){const b=document.createElement('button');b.textContent=e.title;if(e.on)b.className='on';
  b.onclick=async()=>{await fetch('/effect/'+e.name);setTimeout(load,150)};g.appendChild(b)}
 const c=document.createElement('button');c.textContent='Clear all';c.className='clear';
 c.onclick=async()=>{await fetch('/clear');setTimeout(load,150)};g.appendChild(c);
 document.getElementById('u').textContent=s.effects.map(e=>location.origin+'/effect/'+e.name).join('\\n')+'\\n'+location.origin+'/clear'}
load();setInterval(load,1500);
</script></body></html>"""


def start_server(manager, port: int, colours: dict):
    """Start in the background. Returns (server, None) or (None, error message)."""

    class Handler(BaseHTTPRequestHandler):
        def _reply(self, code, body, kind="application/json"):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", f"{kind}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _handle(self):
            url = urlparse(self.path)
            parts = [p for p in url.path.split("/") if p]
            options = dict(parse_qsl(url.query))
            if not parts:
                return self._reply(200, PAGE % colours, "text/html")
            if parts == ["status"]:
                return self._reply(200, json.dumps({"effects": manager.status()}))
            if parts == ["clear"]:
                manager.command("clear")
                return self._reply(200, json.dumps({"ok": True, "done": "clear"}))
            if parts[0] == "effect" and len(parts) in (2, 3):
                action = parts[2].lower() if len(parts) == 3 else "press"
                if not action.isalpha():
                    return self._reply(400, json.dumps({"ok": False, "error": "unknown action"}))
                if manager.command(parts[1], "press" if action == "toggle" else action, options):
                    return self._reply(200, json.dumps({"ok": True, "effect": parts[1], "action": action}))
                return self._reply(404, json.dumps({"ok": False, "error": f"no effect '{parts[1]}'",
                                                    "effects": list(manager.effects)}))
            return self._reply(404, json.dumps({"ok": False, "error": "unknown address"}))

        do_GET = do_POST = _handle

        def log_message(self, *_args):
            pass  # keep the Terminal window quiet

    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except OSError as exc:
        return None, f"Web address port {port} is busy ({exc.strerror}). Is the app already open?"
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, None
