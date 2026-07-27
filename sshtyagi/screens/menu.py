import pyfiglet
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, OptionList, Static
from textual.widgets.option_list import Option

from sshtyagi.data.resume import NAME

BANNER = pyfiglet.Figlet(font="small").renderText("tyagi.web")
BANNER_LINES = BANNER.splitlines()
BANNER_WIDTH = max((len(line) for line in BANNER_LINES), default=0)

MENU_ITEMS = [
    ("about", "About"),
    ("experience", "Experience"),
    ("skills", "Skills"),
    ("projects", "Projects  (live from GitHub)"),
    ("real_madrid", "Real Madrid"),
    ("dashboard", "Dashboard  (live)"),
    ("contact", "Contact"),
]


class MenuScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(BANNER, id="banner")
        yield Static(
            f"{NAME}'s read-only terminal. Arrow keys + Enter to browse, q to quit.",
            id="subtitle",
        )
        with Vertical():
            yield OptionList(
                *[Option(label, id=key) for key, label in MENU_ITEMS],
                id="menu-list",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(OptionList).focus()
        self._shimmer_pos = -4
        self.set_interval(0.08, self._animate_banner)

    def _animate_banner(self) -> None:
        pos = self._shimmer_pos
        rendered = Text()
        for i, line in enumerate(BANNER_LINES):
            if i:
                rendered.append("\n")
            text = Text(line)
            start, end = max(0, pos - 2), min(len(line), pos + 3)
            if start < end:
                text.stylize("bold #ffffff", start, end)
            rendered.append_text(text)
        self.query_one("#banner", Static).update(rendered)
        self._shimmer_pos = (pos + 1) % (BANNER_WIDTH + 8) - 4

    def action_quit(self) -> None:
        self.app.exit()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        from sshtyagi.screens.about import AboutScreen
        from sshtyagi.screens.contact import ContactScreen
        from sshtyagi.screens.dashboard import DashboardScreen
        from sshtyagi.screens.experience import ExperienceScreen
        from sshtyagi.screens.projects import ProjectsScreen
        from sshtyagi.screens.real_madrid import RealMadridScreen
        from sshtyagi.screens.skills import SkillsScreen

        screens = {
            "about": AboutScreen,
            "experience": ExperienceScreen,
            "skills": SkillsScreen,
            "projects": ProjectsScreen,
            "real_madrid": RealMadridScreen,
            "dashboard": DashboardScreen,
            "contact": ContactScreen,
        }
        screen_cls = screens.get(event.option_id)
        if screen_cls is not None:
            self.app.push_screen(screen_cls())
