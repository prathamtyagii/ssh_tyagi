import pyfiglet
from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import LoadingIndicator, Static

from sshtyagi.clients.football import fetch_last_lineup

TITLE_BANNER = pyfiglet.Figlet(font="small").renderText("STARTING XI")

_POSITION_GROUPS = [
    ("Goalkeeper", ("goalkeeper",)),
    ("Defence", ("back", "defender")),
    ("Midfield", ("midfield",)),
    ("Attack", ("wing", "forward", "striker")),
]


def _group_for(position: str) -> str:
    p = position.lower()
    for group_name, keywords in _POSITION_GROUPS:
        if any(k in p for k in keywords):
            return group_name
    return "Other"


class LineupModal(ModalScreen):
    BINDINGS = [
        ("escape", "close", "Close"),
        ("q", "close", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="modal-box") as box:
            box.border_title = "Last Match Lineup"
            yield Static(TITLE_BANNER, classes="dim")
            yield LoadingIndicator(id="lineup-loading")
            yield Static("", id="lineup-body")

    def on_mount(self) -> None:
        self.load_lineup()

    @work
    async def load_lineup(self) -> None:
        lineup = await fetch_last_lineup()
        self.query_one("#lineup-loading", LoadingIndicator).display = False
        body = self.query_one("#lineup-body", Static)

        if not lineup or not lineup["players"]:
            body.update("[dim]Lineup data unavailable right now.[/dim]")
            return

        lines = [f"vs {lineup['opponent']}  --  {lineup['date']}", ""]
        groups: dict[str, list[str]] = {}
        for p in lineup["players"]:
            group = _group_for(p["position"])
            groups.setdefault(group, []).append(
                f"#{p['number']} {p['player']} ({p['position']})"
            )

        for group_name, _keywords in _POSITION_GROUPS:
            if group_name in groups:
                lines.append(f"[bold]{group_name}[/bold]")
                lines.extend(f"  {entry}" for entry in groups[group_name])
                lines.append("")

        if len(lineup["players"]) < 11:
            lines.append(
                f"[dim](free API returned {len(lineup['players'])} of 11 starters "
                "-- partial data)[/dim]"
            )

        body.update("\n".join(lines))

    def action_close(self) -> None:
        self.dismiss()
