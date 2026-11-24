#!/usr/bin/env python3
"""A dependency-free development server, including preview CLI options."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--host', default='127.0.0.1')
parser.add_argument('--port', type=int, default=8080)
parser.add_argument('--strictPort', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1] / 'docs'
handler = partial(SimpleHTTPRequestHandler, directory=str(root))
server = ThreadingHTTPServer((args.host, args.port), handler)
print(f'Local: http://{args.host}:{args.port}/', flush=True)
server.serve_forever()
