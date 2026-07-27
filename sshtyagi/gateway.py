"""SSH gateway: accepts any connection with no auth, spawns the Textual app
as a subprocess attached to a real pty (via ptyprocess, so it gets a proper
controlling terminal), and bridges raw bytes between the SSH channel and
the pty in both directions. Same architecture Textualize's own
textual-serve uses for browser access, just swapping the websocket for an
SSH channel.
"""

import asyncio
import datetime as dt
import os
import sys
from pathlib import Path

import asyncssh
import ptyprocess

HOST_KEY_PATH = Path(__file__).parent.parent / "host_key"
STARTED_AT = dt.datetime.now(dt.timezone.utc).isoformat()


def ensure_host_key() -> str:
    if not HOST_KEY_PATH.exists():
        key = asyncssh.generate_private_key("ssh-ed25519")
        key.write_private_key(str(HOST_KEY_PATH))
    return str(HOST_KEY_PATH)


class OpenServer(asyncssh.SSHServer):
    """Read-only public app: no authentication required, anyone can connect."""

    def begin_auth(self, username: str) -> bool:
        return False


async def handle_client(process: asyncssh.SSHServerProcess) -> None:
    if process.get_terminal_type() is None:
        process.stdout.write(
            "This needs an interactive terminal. Try: ssh -t <host>\n"
        )
        process.exit(1)
        return

    width, height, _pixw, _pixh = process.get_terminal_size()

    env = dict(os.environ)
    env["TERM"] = process.get_terminal_type() or "xterm-256color"
    env["SSHTYAGI_START_TIME"] = STARTED_AT

    child = ptyprocess.PtyProcess.spawn(
        [sys.executable, "-m", "sshtyagi.app"],
        env=env,
        dimensions=(height or 24, width or 80),
    )

    def on_resize(width: int, height: int, _pixwidth: int, _pixheight: int) -> None:
        try:
            child.setwinsize(height, width)
        except OSError:
            pass

    process.terminal_size_changed = on_resize

    loop = asyncio.get_event_loop()

    async def pump_child_to_client() -> None:
        # Deliberately uses a thread-pool blocking read rather than
        # loop.add_reader(child.fileno(), ...): registering a raw fd reader
        # on the same loop asyncssh's own transport uses breaks delivery of
        # further SSH channel data after the first packet (reproduced and
        # confirmed in isolation -- not an issue with a plain blocking read).
        while True:
            try:
                data = await loop.run_in_executor(None, child.read, 65536)
            except EOFError:
                break
            process.stdout.write(data)
            await process.stdout.drain()

    async def pump_client_to_child() -> None:
        while True:
            data = await process.stdin.read(65536)
            if not data:
                break
            child.write(data)

    to_client = asyncio.create_task(pump_child_to_client())
    to_child = asyncio.create_task(pump_client_to_child())

    try:
        await asyncio.wait(
            {to_client, to_child}, return_when=asyncio.FIRST_COMPLETED
        )
    finally:
        to_client.cancel()
        to_child.cancel()
        if child.isalive():
            child.terminate(force=True)
        process.exit(0)


async def main(host: str = "", port: int = 8022) -> None:
    host_key = ensure_host_key()
    await asyncssh.listen(
        host,
        port,
        server_factory=OpenServer,
        server_host_keys=[host_key],
        process_factory=handle_client,
        encoding=None,
        line_editor=False,
    )
    print(f"Listening -- try: ssh -p {port} localhost")
    await asyncio.Event().wait()


def run() -> None:
    port = int(os.environ.get("SSHTYAGI_PORT", 8022))
    try:
        asyncio.run(main(port=port))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
