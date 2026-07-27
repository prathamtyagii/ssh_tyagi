from pathlib import Path

from textual.app import App

from sshtyagi.screens.menu import MenuScreen


class TyagiApp(App):
    CSS_PATH = Path(__file__).parent / "styles.tcss"
    TITLE = "tyagi.web"

    def on_mount(self) -> None:
        self.push_screen(MenuScreen())


def main() -> None:
    TyagiApp().run()


if __name__ == "__main__":
    main()
