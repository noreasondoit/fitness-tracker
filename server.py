import http.server
import os

DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 5000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIR, **kw)

print(f"Fitness Tracker running at http://0.0.0.0:{PORT}")
print("Open from phone: http://YOUR_IP:{PORT}")
http.server.HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
