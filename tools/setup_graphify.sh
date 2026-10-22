#!/usr/bin/env bash
# Install graphify and map this project's code. Run in WSL Ubuntu on carlie's PC from a clone:
#   bash ~/<repo>/tools/setup_graphify.sh
# Code-only, nothing uploaded. Output: graphify-out/ (gitignored). Shares ~/.graphify-venv.
set -euo pipefail
VERSION=0.9.86
if [ "$(~/.graphify-venv/bin/pip show graphifyy 2>/dev/null | sed -n 's/^Version: //p')" != "$VERSION" ]; then
  python3 -m venv ~/.graphify-venv
  ~/.graphify-venv/bin/pip install -q "graphifyy==$VERSION"
fi
mkdir -p ~/.local/bin && ln -sf ~/.graphify-venv/bin/graphify ~/.local/bin/graphify
cd "$(dirname "$0")/.."
~/.graphify-venv/bin/graphify extract . --code-only
echo "Done. Map is in graphify-out/graph.json. Ignore the Graphify Cloud ad: nothing here uploads."
