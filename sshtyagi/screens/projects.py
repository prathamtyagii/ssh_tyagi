from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import DataTable, LoadingIndicator, Static

from sshtyagi.clients.github import fetch_repos
from sshtyagi.config import GITHUB_USERNAME
from sshtyagi.screens.base import ContentScreen
from sshtyagi.screens.project_modal import ProjectModal


class ProjectsScreen(ContentScreen):
    def __init__(self) -> None:
        super().__init__()
        self.repos_by_name: dict[str, dict] = {}

    def compose(self) -> ComposeResult:
        yield from self.compose_header_footer()
        with VerticalScroll(classes="content-wrap") as box:
            box.border_title = "Projects"
            yield Static(
                f"live from github.com/{GITHUB_USERNAME} -- enter a row for details",
                classes="dim",
            )
            yield LoadingIndicator(id="loading")
            table = DataTable(id="repo-table", cursor_type="row")
            table.display = False
            yield table

    def on_mount(self) -> None:
        self.load_repos()

    @work
    async def load_repos(self) -> None:
        repos = await fetch_repos(GITHUB_USERNAME)
        self.query_one("#loading", LoadingIndicator).display = False
        table = self.query_one("#repo-table", DataTable)

        if not repos:
            self.query_one(VerticalScroll).mount(
                Static(
                    f"No public repos found for {GITHUB_USERNAME}.\n"
                    "(Check GITHUB_USERNAME in sshtyagi/config.py if this isn't right.)",
                    classes="dim",
                )
            )
            return

        self.repos_by_name = {r["name"]: r for r in repos}
        table.add_columns("Name", "Language", "Stars", "Updated", "Description")
        for r in repos:
            table.add_row(
                r["name"],
                r["language"] or "-",
                str(r["stars"]),
                r["updated_at"][:10],
                r["description"],
                key=r["name"],
            )
        table.display = True
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        repo = self.repos_by_name.get(event.row_key.value)
        if repo is not None:
            self.app.push_screen(ProjectModal(repo))
