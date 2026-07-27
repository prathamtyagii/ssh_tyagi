from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from sshtyagi.data.resume import EXPERIENCE
from sshtyagi.screens.base import ContentScreen


class ExperienceScreen(ContentScreen):
    def compose(self) -> ComposeResult:
        yield from self.compose_header_footer()
        with VerticalScroll(classes="content-wrap") as box:
            box.border_title = "Experience"
            for job in EXPERIENCE:
                bullets = "\n".join(f"  - {b}" for b in job["bullets"])
                yield Static(
                    f"[bold]{job['role']}[/bold] @ {job['company']}  "
                    f"[dim]({job['period']})[/dim]\n{bullets}",
                    classes="card",
                )
