from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os, webbrowser
root=Path(__file__).resolve().parents[1];os.chdir(root)
url='http://127.0.0.1:8010/'
print(f'PRISMA disponible en {url}  · Ctrl+C para detener')
webbrowser.open(url)
ThreadingHTTPServer(('127.0.0.1',8010),SimpleHTTPRequestHandler).serve_forever()
