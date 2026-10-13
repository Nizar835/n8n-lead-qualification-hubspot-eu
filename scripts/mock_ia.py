"""Faux Ollama pour les tests de rupture (G2, E). /g2 = chiffre inventé, /e = JSON invalide. Port 8099."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        c = '{"categorie":"autre","resume":"Reçoit 500 devis par semaine"}' if self.path == "/g2" else '{"categorie": "autre", "resume": '
        b = json.dumps({"message": {"role": "assistant", "content": c}}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b)
HTTPServer(("127.0.0.1", 8099), H).serve_forever()
