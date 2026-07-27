import datetime as dt
import os
from collections import Counter

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import LoadingIndicator, Static

from sshtyagi.clients.github import (
    fetch_contribution_calendar,
    fetch_profile,
    fetch_recent_activity,
    fetch_repos,
)
from sshtyagi.config import GITHUB_USERNAME
from sshtyagi.screens.base import ContentScreen

_LEVEL_COLORS = {
    0: "#30363d",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}
_HEATMAP_WEEKS = 24


def _build_heatmap(days: list[tuple[str, int]]) -> str:
    if not days:
        return "  (no contribution data)"

    parsed = [(dt.date.fromisoformat(d), lvl) for d, lvl in days]
    min_date = min(d for d, _ in parsed)
    grid_start = min_date - dt.timedelta(days=(min_date.weekday() + 1) % 7)

    grid: dict[int, dict[int, int]] = {row: {} for row in range(7)}
    max_week = 0
    for date, level in parsed:
        weekday = (date.weekday() + 1) % 7  # Sunday=0 .. Saturday=6
        week = (date - grid_start).days // 7
        grid[weekday][week] = level
        max_week = max(max_week, week)

    start_week = max(0, max_week - _HEATMAP_WEEKS + 1)
    lines = []
    for weekday in range(7):
        cells = []
        for week in range(start_week, max_week + 1):
            level = grid[weekday].get(week)
            if level is None:
                cells.append(" ")
            else:
                color = _LEVEL_COLORS[level]
                cells.append(f"[{color}]■[/{color}]")
        lines.append("".join(cells))
    return "\n".join(lines)


def _language_breakdown(repos: list[dict]) -> list[tuple[str, int]]:
    counts = Counter(r["language"] for r in repos if r["language"])
    return counts.most_common(8)


def _format_uptime() -> str | None:
    started_at = os.environ.get("SSHTYAGI_START_TIME")
    if not started_at:
        return None
    try:
        start = dt.datetime.fromisoformat(started_at)
    except ValueError:
        return None
    delta = dt.datetime.now(dt.timezone.utc) - start
    total_minutes = int(delta.total_seconds() // 60)
    days, rem = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


class DashboardScreen(ContentScreen):
    def compose(self) -> ComposeResult:
        yield from self.compose_header_footer()
        with VerticalScroll(classes="content-wrap") as box:
            box.border_title = "Dashboard (live)"
            yield LoadingIndicator(id="loading")
            yield Static("", id="dashboard-body")

    def on_mount(self) -> None:
        self.load_dashboard()

    @work
    async def load_dashboard(self) -> None:
        profile = await fetch_profile(GITHUB_USERNAME)
        repos = await fetch_repos(GITHUB_USERNAME)
        activity = await fetch_recent_activity(GITHUB_USERNAME)
        calendar = await fetch_contribution_calendar(GITHUB_USERNAME)

        self.query_one("#loading", LoadingIndicator).display = False

        lines = []

        uptime = _format_uptime()
        if uptime:
            lines.append(f"[dim]This server has been up for {uptime}.[/dim]\n")

        if profile:
            member_since = profile["created_at"][:10]
            lines.append("[bold]GitHub profile[/bold]")
            lines.append(
                f"  {profile['public_repos']} public repos, "
                f"{profile['followers']} followers, {profile['following']} following"
            )
            lines.append(f"  On GitHub since {member_since}")
            lines.append("")

        if calendar["days"]:
            lines.append(
                f"[bold]Contribution activity[/bold]  "
                f"({calendar['total']} in the last year)"
            )
            lines.append(_build_heatmap(calendar["days"]))
            lines.append("")

        langs = _language_breakdown(repos)
        if langs:
            lines.append("[bold]Top languages[/bold]")
            max_count = langs[0][1]
            for lang, count in langs:
                bar = "█" * max(1, round(count / max_count * 20))
                lines.append(f"  {lang:<12} {bar} {count}")
            lines.append("")

        if activity:
            lines.append("[bold]Recent activity[/bold]")
            for line in activity:
                lines.append(f"  - {line}")
        elif not profile and not repos:
            lines.append("[dim]Couldn't load GitHub data right now.[/dim]")

        self.query_one("#dashboard-body", Static).update("\n".join(lines))
