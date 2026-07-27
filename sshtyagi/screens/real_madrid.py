import pyfiglet
from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from sshtyagi.clients.football import fetch_last_result, fetch_next_fixture
from sshtyagi.data.real_madrid import (
    FOUNDED,
    LEGENDS,
    MY_FAVORITE_MATCH,
    MY_FAVORITE_PLAYER,
    MY_NOTE,
    NICKNAMES,
    STADIUM,
    TROPHIES,
    TROPHIES_AS_OF,
)
from sshtyagi.screens.base import ContentScreen
from sshtyagi.screens.lineup_modal import LineupModal

LOGO = pyfiglet.Figlet(font="small").renderText("REAL MADRID")


def _fixture_line(fixture: dict | None) -> str:
    if fixture is None:
        return "  (couldn't load -- try again later)"
    return (
        f"  vs {fixture['opponent']} ({fixture['venue']}) -- {fixture['competition']}\n"
        f"  {fixture['date']} {fixture['time']}"
    )


def _result_line(result: dict | None) -> str:
    if result is None:
        return "  (couldn't load -- try again later)"
    home, away = result["home_score"], result["away_score"]
    return (
        f"  vs {result['opponent']} ({result['venue']}) -- {result['competition']}\n"
        f"  Final score: {home} - {away}   [{result['date']}]"
    )


class RealMadridScreen(ContentScreen):
    BINDINGS = [("l", "lineup", "Starting XI")]

    def compose(self) -> ComposeResult:
        yield from self.compose_header_footer()
        with VerticalScroll(classes="content-wrap") as box:
            box.border_title = "Real Madrid"
            yield Static(LOGO, classes="rm-logo")
            yield Static(
                f"founded {FOUNDED}  --  {STADIUM}  --  {' / '.join(NICKNAMES)}",
                classes="dim",
            )
            yield Static("")

            yield Static("Next fixture (live)", classes="section-title")
            yield Static("  loading...", id="next-fixture")

            yield Static("Last result (live)", classes="section-title")
            yield Static("  loading...", id="last-result")

            yield Static(f"Trophies (as of {TROPHIES_AS_OF})", classes="section-title")
            yield Static("  " + "  |  ".join(f"{n}: {c}" for n, c in TROPHIES.items()))

            yield Static("Legends", classes="section-title")
            yield Static("  " + ", ".join(LEGENDS))

            yield Static("Why I'm a fan", classes="section-title")
            yield Static(f"  Favorite player: {MY_FAVORITE_PLAYER}")
            yield Static(f"  Favorite match: {MY_FAVORITE_MATCH}")
            yield Static(f"  {MY_NOTE}")

            yield Static("")
            yield Static("Press 'l' for the last match's starting XI", classes="dim")

    def on_mount(self) -> None:
        self.load_live_data()

    @work
    async def load_live_data(self) -> None:
        fixture = await fetch_next_fixture()
        self.query_one("#next-fixture", Static).update(_fixture_line(fixture))

        result = await fetch_last_result()
        self.query_one("#last-result", Static).update(_result_line(result))

    def action_lineup(self) -> None:
        self.app.push_screen(LineupModal())
