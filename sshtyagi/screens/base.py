from textual.screen import Screen
from textual.widgets import Footer, Header


class ContentScreen(Screen):
    """Base for every section pushed from the main menu: back to menu on escape/q."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "back", "Back"),
    ]

    def action_back(self) -> None:
        self.app.pop_screen()

    def compose_header_footer(self):
        yield Header(show_clock=False)
        yield Footer()
