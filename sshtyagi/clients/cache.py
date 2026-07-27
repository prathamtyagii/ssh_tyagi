"""Tiny file-backed TTL cache shared across subprocesses (one per SSH session)."""

import json
import time
from pathlib import Path
from typing import Any, Awaitable, Callable

CACHE_DIR = Path.home() / ".cache" / "sshtyagi"


async def cached(key: str, ttl_seconds: int, fetch_fn: Callable[[], Awaitable[Any]]) -> Any:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{key}.json"

    if path.exists():
        try:
            payload = json.loads(path.read_text())
            if time.time() - payload["ts"] < ttl_seconds:
                return payload["data"]
        except (json.JSONDecodeError, KeyError, OSError):
            pass

    data = await fetch_fn()
    try:
        path.write_text(json.dumps({"ts": time.time(), "data": data}))
    except OSError:
        pass
    return data

