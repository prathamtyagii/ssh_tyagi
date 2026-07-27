from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from sshtyagi.data.resume import SKILLS
from sshtyagi.screens.base import ContentScreen


class SkillsScreen(ContentScreen):
    def compose(self) -> ComposeResult:
        yield from self.compose_header_footer()
        with VerticalScroll(classes="content-wrap") as box:
            box.border_title = "Skills"
            for category, items in SKILLS.items():
                yield Static(f"[bold]{category}[/bold]: {', '.join(items)}")
