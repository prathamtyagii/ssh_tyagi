#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDFILE="$DIR/.gateway.pid"

if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    PID="$(cat "$PIDFILE")"
    kill "$PID"
    for _ in {1..10}; do
        kill -0 "$PID" 2>/dev/null || break
        sleep 0.5
    done
    kill -9 "$PID" 2>/dev/null || true
    echo "Stopped (pid $PID)."
else
    echo "Not running."
fi
rm -f "$PIDFILE"

# Safety net: a killed gateway can't run its own per-session cleanup,
# so clear out any subprocess apps left behind from active connections.
pkill -f "sshtyagi\.app" 2>/dev/null || true
