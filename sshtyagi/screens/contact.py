from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from sshtyagi.data.resume import CONTACT
from sshtyagi.screens.base import ContentScreen


class ContactScreen(ContentScreen):
    def compose(self) -> ComposeResult:
        yield from self.compose_header_footer()
        with VerticalScroll(classes="content-wrap") as box:
            box.border_title = "Contact"
            for label, value in CONTACT.items():
                yield Static(f"[bold]{label}[/bold]: {value}")
