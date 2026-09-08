#!/usr/bin/env bash
# Optional compatibility adapter. Read docs/SETUP.md before enabling.
set -euo pipefail
: "${CLAUDE_AUTOPILOT_TOKEN:?CLAUDE_AUTOPILOT_TOKEN is required}"
METER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
HEADERS_FILE=$(mktemp)
trap 'rm -f "$HEADERS_FILE"' EXIT
STATUS=$(curl -sS --max-time 30 -D "$HEADERS_FILE" -o /dev/null -w '%{http_code}' \
  https://api.anthropic.com/v1/messages \
  -H "Authorization: Bearer $CLAUDE_AUTOPILOT_TOKEN" \
  -H 'anthropic-beta: oauth-2025-04-20' \
  -H 'anthropic-version: 2023-06-01' \
  -H 'content-type: application/json' \
  -d '{"model":"claude-haiku-4-5-20251001","max_tokens":1,"messages":[{"role":"user","content":"."}]}')
if [ "$STATUS" != 200 ]; then
  echo 'meter: usage call failed; no snapshot published' >&2
  exit 1
fi
python3 "$METER_DIR/parse_meter.py" claude < "$HEADERS_FILE"
