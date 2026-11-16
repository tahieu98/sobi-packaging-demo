#!/bin/sh
set -eu
cd "$(dirname "$0")"
if curl --max-time 1 -fsS http://localhost:4173/ 2>/dev/null | head -c 4096 | grep -q 'sobi-root'; then
  open 'http://localhost:4173/'
  exit 0
fi
open 'http://localhost:4173/'
exec python3 tools/serve.py
