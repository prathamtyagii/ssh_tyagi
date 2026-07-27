from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from sshtyagi.data.resume import ABOUT, NAME, TAGLINE, TITLE
from sshtyagi.screens.base import ContentScreen


class AboutScreen(ContentScreen):
    def compose(self) -> ComposeResult:
        yield from self.compose_header_footer()
        with VerticalScroll(classes="content-wrap") as box:
            box.border_title = "About"
            yield Static(f"[bold]{NAME}[/bold] -- {TITLE}", classes="section-title")
            yield Static(TAGLINE, classes="dim")
            yield Static("")
            yield Static(ABOUT)
