#!/bin/bash
# Start one2one local server and a Chrome instance with remote debugging enabled for MCP
# Usage: bash start_mcp_dev.sh

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
ONE2ONE_DIR="$ROOT_DIR/one2one"
PORT=8765
CHROME_PORT=9222
CHROME_APP="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
USER_DATA_DIR="/tmp/chrome-profile-stable"

echo "📦 Project root: $ROOT_DIR"

# 1) Start local HTTP server if not running
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
  echo "✅ Local HTTP server already running on :$PORT"
else
  echo "🚀 Starting local HTTP server on :$PORT (serving $ONE2ONE_DIR)"
  (cd "$ONE2ONE_DIR" && python3 -m http.server $PORT >/dev/null 2>&1 &)
  sleep 1
  echo "✅ Server started"
fi

# 2) Start Chrome with remote debugging if not running
if lsof -Pi :$CHROME_PORT -sTCP:LISTEN -t >/dev/null ; then
  echo "✅ Chrome remote debugging already running on :$CHROME_PORT"
else
  echo "🧪 Launching Chrome with remote debugging on :$CHROME_PORT"
  "$CHROME_APP" --remote-debugging-port=$CHROME_PORT \
    --user-data-dir="$USER_DATA_DIR" >/dev/null 2>&1 &
  sleep 2
  echo "✅ Chrome started with remote debugging"
fi

URL="http://localhost:$PORT/one2one_C1_S1.html"
echo "🌐 Open: $URL"
open "$URL"

cat <<EOF

✅ Ready for MCP debugging.
You can now ask your MCP client to run tasks like:
  - Check the performance of $URL
  - Navigate to $URL and take a screenshot
  - List network requests after loading $URL

This repository already includes .mcp.config.json with:
  --browser-url=http://127.0.0.1:$CHROME_PORT

If you change ports, update .mcp.config.json accordingly.
EOF
