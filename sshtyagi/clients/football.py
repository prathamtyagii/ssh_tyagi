"""Live Real Madrid fixture data via TheSportsDB's free public API.

Uses the shared free demo key ("3", ~30 req/min, no signup required). If you
want your own key later, sign up at thesportsdb.com and set it via
THESPORTSDB_KEY.
"""

import os
from typing import Any

import httpx

from .cache import cached

REAL_MADRID_TEAM_ID = "133738"  # confirmed via searchteams.php?t=Real_Madrid


def _key() -> str:
    return os.environ.get("THESPORTSDB_KEY", "3")


def _base() -> str:
    return f"https://www.thesportsdb.com/api/v1/json/{_key()}"


def _summarize(event: dict[str, Any]) -> dict[str, Any]:
    is_home = event.get("idHomeTeam") == REAL_MADRID_TEAM_ID
    opponent = event["strAwayTeam"] if is_home else event["strHomeTeam"]
    return {
        "id_event": event.get("idEvent"),
        "opponent": opponent,
        "venue": "Home" if is_home else "Away",
        "competition": event.get("strLeague") or "",
        "date": event.get("dateEvent") or "",
        "time": (event.get("strTime") or "")[:5],
        "home_score": event.get("intHomeScore"),
        "away_score": event.get("intAwayScore"),
    }


async def fetch_next_fixture(ttl_seconds: int = 1800) -> dict[str, Any] | None:
    async def _fetch() -> dict[str, Any] | None:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{_base()}/eventsnext.php", params={"id": REAL_MADRID_TEAM_ID}
            )
            resp.raise_for_status()
            events = resp.json().get("events") or []
        return _summarize(events[0]) if events else None

    try:
        return await cached("rm-next-fixture", ttl_seconds, _fetch)
    except httpx.HTTPError:
        return None


async def fetch_last_result(ttl_seconds: int = 1800) -> dict[str, Any] | None:
    async def _fetch() -> dict[str, Any] | None:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{_base()}/eventslast.php", params={"id": REAL_MADRID_TEAM_ID}
            )
            resp.raise_for_status()
            events = resp.json().get("results") or []
        return _summarize(events[0]) if events else None

    try:
        return await cached("rm-last-result", ttl_seconds, _fetch)
    except httpx.HTTPError:
        return None


async def fetch_last_lineup(ttl_seconds: int = 1800) -> dict[str, Any] | None:
    last_result = await fetch_last_result(ttl_seconds)
    if last_result is None or not last_result.get("id_event"):
        return None

    async def _fetch() -> dict[str, Any] | None:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{_base()}/lookuplineup.php",
                params={"id": last_result["id_event"]},
            )
            resp.raise_for_status()
            lineup = resp.json().get("lineup") or []
        starters = [
            {
                "position": p.get("strPosition") or "",
                "player": p.get("strPlayer") or "",
                "number": p.get("intSquadNumber") or "",
            }
            for p in lineup
            if p.get("idTeam") == REAL_MADRID_TEAM_ID
            and p.get("strSubstitute") == "No"
        ]
        return {
            "opponent": last_result["opponent"],
            "date": last_result["date"],
            "players": starters,
        }

    try:
        return await cached(
            f"rm-lineup-{last_result['id_event']}", ttl_seconds, _fetch
        )
    except httpx.HTTPError:
        return None
