#!/usr/bin/env bash
set -euo pipefail

PORT="$(ls /dev/cu.usbmodem* 2>/dev/null | head -n 1)"

if [[ -z "${PORT}" ]]; then
  echo "No /dev/cu.usbmodem* device found. Is the board plugged in?"
  exit 1
fi

exec uv run mpremote connect "$PORT" repl
