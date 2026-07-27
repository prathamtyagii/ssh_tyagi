from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import LoadingIndicator, Markdown, Static

from sshtyagi.clients.github import fetch_readme
from sshtyagi.config import GITHUB_USERNAME


class ProjectModal(ModalScreen):
    BINDINGS = [
        ("escape", "close", "Close"),
        ("q", "close", "Close"),
    ]

    def __init__(self, repo: dict) -> None:
        super().__init__()
        self.repo = repo

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="modal-box") as box:
            box.border_title = self.repo["name"]
            meta = (
                f"{self.repo['language'] or '-'}  |  {self.repo['stars']} stars  |  "
                f"updated {self.repo['updated_at'][:10]}  |  {self.repo['url']}"
            )
            yield Static(meta, classes="dim")
            yield Static(self.repo["description"])
            yield Static("")
            yield LoadingIndicator(id="readme-loading")
            yield Markdown("", id="readme")

    def on_mount(self) -> None:
        self.load_readme()

    @work
    async def load_readme(self) -> None:
        readme = await fetch_readme(GITHUB_USERNAME, self.repo["name"])
        self.query_one("#readme-loading", LoadingIndicator).display = False
        if readme:
            await self.query_one("#readme", Markdown).update(readme)
        else:
            self.query_one("#readme", Markdown).display = False
            self.query_one(VerticalScroll).mount(
                Static("No README found for this repo.", classes="dim")
            )

    def action_close(self) -> None:
        self.dismiss()
