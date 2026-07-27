#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/.gateway.pid"
LOGFILE="$DIR/gateway.log"
export SSHTYAGI_PORT="${SSHTYAGI_PORT:-8022}"

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Already running (pid $(cat "$PIDFILE"))."
    exit 0
fi

source "$DIR/.venv/bin/activate"
cd "$DIR"
nohup python -m sshtyagi.gateway > "$LOGFILE" 2>&1 &
echo $! > "$PIDFILE"

sleep 1
if kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Started (pid $(cat "$PIDFILE")). Try: ssh -p $SSHTYAGI_PORT localhost"
else
    echo "Failed to start -- check $LOGFILE"
    rm -f "$PIDFILE"
    exit 1
fi
