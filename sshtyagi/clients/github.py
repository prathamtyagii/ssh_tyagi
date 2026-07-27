"""Live GitHub data: repos, profile stats, recent activity, contribution calendar.

Only api.github.com calls use the REST API. The contribution calendar isn't
exposed by the REST API without a GraphQL token, so it's parsed from the same
public HTML fragment GitHub's own profile page renders (no auth required).
"""

import base64
import os
import re
from typing import Any

import httpx

from .cache import cached

API = "https://api.github.com"
UA = {"User-Agent": "sshtyagi (read-only ssh portfolio)"}


def _headers() -> dict:
    headers = dict(UA)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def fetch_repos(username: str, ttl_seconds: int = 600) -> list[dict[str, Any]]:
    async def _fetch() -> list[dict[str, Any]]:
        async with httpx.AsyncClient(headers=_headers(), timeout=10) as client:
            resp = await client.get(
                f"{API}/users/{username}/repos",
                params={"sort": "updated", "per_page": 100, "type": "owner"},
            )
            resp.raise_for_status()
            repos = resp.json()

        cleaned = [
            {
                "name": r["name"],
                "description": r["description"] or "No description.",
                "url": r["html_url"],
                "language": r["language"] or "",
                "stars": r["stargazers_count"],
                "updated_at": r["updated_at"],
                "fork": r["fork"],
            }
            for r in repos
            if not r["fork"] and not r["archived"]
        ]
        cleaned.sort(key=lambda r: (r["stars"], r["updated_at"]), reverse=True)
        return cleaned

    try:
        return await cached(f"repos-{username}", ttl_seconds, _fetch)
    except (httpx.HTTPError, KeyError):
        return []


async def fetch_profile(username: str, ttl_seconds: int = 600) -> dict[str, Any]:
    async def _fetch() -> dict[str, Any]:
        async with httpx.AsyncClient(headers=_headers(), timeout=10) as client:
            resp = await client.get(f"{API}/users/{username}")
            resp.raise_for_status()
            u = resp.json()
        return {
            "login": u["login"],
            "name": u.get("name") or u["login"],
            "bio": u.get("bio") or "",
            "public_repos": u["public_repos"],
            "followers": u["followers"],
            "following": u["following"],
            "created_at": u["created_at"],
        }

    try:
        return await cached(f"profile-{username}", ttl_seconds, _fetch)
    except (httpx.HTTPError, KeyError):
        return {}


_EVENT_VERBS = {
    "PushEvent": "pushed to",
    "PullRequestEvent": "opened a PR in",
    "IssuesEvent": "opened an issue in",
    "CreateEvent": "created",
    "WatchEvent": "starred",
    "ForkEvent": "forked",
    "ReleaseEvent": "released a version of",
    "PullRequestReviewEvent": "reviewed a PR in",
}


async def fetch_recent_activity(username: str, limit: int = 8, ttl_seconds: int = 300) -> list[str]:
    async def _fetch() -> list[str]:
        async with httpx.AsyncClient(headers=_headers(), timeout=10) as client:
            resp = await client.get(
                f"{API}/users/{username}/events/public", params={"per_page": limit}
            )
            resp.raise_for_status()
            events = resp.json()

        lines = []
        for e in events[:limit]:
            verb = _EVENT_VERBS.get(e["type"])
            if not verb:
                continue
            repo = e["repo"]["name"]
            lines.append(f"{verb} {repo}")
        return lines

    try:
        return await cached(f"activity-{username}", ttl_seconds, _fetch)
    except (httpx.HTTPError, KeyError):
        return []


async def fetch_readme(username: str, repo: str, ttl_seconds: int = 3600) -> str:
    async def _fetch() -> str:
        async with httpx.AsyncClient(headers=_headers(), timeout=10) as client:
            resp = await client.get(f"{API}/repos/{username}/{repo}/readme")
            if resp.status_code == 404:
                return ""
            resp.raise_for_status()
            data = resp.json()
        content = data.get("content", "")
        try:
            return base64.b64decode(content).decode("utf-8", errors="replace")
        except (ValueError, UnicodeDecodeError):
            return ""

    try:
        return await cached(f"readme-{username}-{repo}", ttl_seconds, _fetch)
    except httpx.HTTPError:
        return ""


_DAY_RE = re.compile(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"')
_TOTAL_RE = re.compile(r"([\d,]+)\s+contributions?\s+in the last year")


async def fetch_contribution_calendar(username: str, ttl_seconds: int = 3600) -> dict[str, Any]:
    async def _fetch() -> dict[str, Any]:
        async with httpx.AsyncClient(headers=UA, timeout=10) as client:
            resp = await client.get(f"https://github.com/users/{username}/contributions")
            resp.raise_for_status()
            html = resp.text

        days = [(d, int(lvl)) for d, lvl in _DAY_RE.findall(html)]
        total_match = _TOTAL_RE.search(html)
        total = int(total_match.group(1).replace(",", "")) if total_match else sum(
            1 for _, lvl in days if lvl > 0
        )
        return {"days": days, "total": total}

    try:
        return await cached(f"calendar-{username}", ttl_seconds, _fetch)
    except httpx.HTTPError:
        return {"days": [], "total": 0}
