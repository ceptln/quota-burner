#!/usr/bin/env bash
# Optional local adapter; tokens are supplied by the operator, never refreshed here.
set -euo pipefail
: "${CODEX_ACCESS_TOKEN:?Supply a current access token through the environment; see docs/SETUP.md}"
METER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
CURL_ARGS=(-sS --max-time 30 --fail
  https://chatgpt.com/backend-api/wham/usage
  -H 'User-Agent: quota-burner-meter/1.0'
  -H "Authorization: Bearer $CODEX_ACCESS_TOKEN"
  -H 'Accept: application/json')
if [ -n "${CODEX_ACCOUNT_ID:-}" ]; then
  CURL_ARGS+=(-H "ChatGPT-Account-Id: $CODEX_ACCOUNT_ID")
fi
RESPONSE=$(curl "${CURL_ARGS[@]}") || {
  echo 'meter: usage request failed; renew your login through Codex' >&2
  exit 1
}
printf '%s' "$RESPONSE" | python3 "$METER_DIR/parse_meter.py" codex
