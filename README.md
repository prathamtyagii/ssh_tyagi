# tyagi.web

A read-only, interactive terminal portfolio you reach over SSH — no login,
no password, just:

```
ssh -p 8022 localhost   # (or your real host/port once deployed)
```

Inspired by [terminal.shop](https://terminal.shop), but read-only: a
menu-driven TUI instead of a shop.

## What's in it

- **About / Experience / Skills / Contact** — static profile content
- **Projects** — live from your GitHub account (name, language, stars,
  last updated); select a row to open a modal with the full README
  rendered as markdown
- **Real Madrid** — a fan section: history/trophies/legends plus two
  live widgets (next fixture, last result) from TheSportsDB, and a
  "Starting XI" modal (`l` key) showing the last match's real lineup
- **Dashboard** — live GitHub stats: contribution heatmap, language
  breakdown, recent activity, profile stats

## How it works

- [`textual`](https://textual.textualize.io/) renders the actual TUI —
  the menu and every screen are a normal Textual `App`.
- [`asyncssh`](https://asyncssh.readthedocs.io/) runs the SSH server and
  accepts any connection with no authentication (`begin_auth` returns
  `False` — this is a deliberately public, read-only app).
- Each SSH session spawns the Textual app as a **subprocess attached to a
  real pty** (via `ptyprocess`), so Textual gets a genuine controlling
  terminal exactly as if it were run locally. The gateway just bridges
  raw bytes between the SSH channel and that pty in both directions.
  This is the same architecture Textualize's own `textual-serve` uses
  for browser access, just swapping the websocket for an SSH channel.
- `pyfiglet` renders the ASCII banners/logos; `httpx` talks to the
  GitHub and TheSportsDB APIs.

```
sshtyagi/
  app.py              Textual App entry point
  gateway.py           asyncssh server + pty bridge
  config.py             GITHUB_USERNAME
  data/
    resume.py            your About/Experience/Skills/Contact content
    real_madrid.py        your Real Madrid fan content
  clients/
    github.py             GitHub REST API (repos, profile, README, contributions)
    football.py           TheSportsDB API (fixtures, results, lineup)
    cache.py              tiny file-backed TTL cache shared across sessions
  screens/                one file per menu section + the two modals
  styles.tcss             Textual CSS for the whole app
```

## Running it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

./start.sh   # starts the gateway in the background
ssh -p 8022 localhost
./stop.sh    # stops it and cleans up any stray session subprocesses
```

`start.sh` writes `gateway.log` and `.gateway.pid`; override the port with
`SSHTYAGI_PORT=2222 ./start.sh`.

## Configuration

All via environment variables, all optional:

| Variable | Purpose |
|---|---|
| `GITHUB_TOKEN` | Raises the GitHub API rate limit from 60/hr to 5000/hr |
| `THESPORTSDB_KEY` | Your own TheSportsDB key instead of the shared free demo key (`3`) |
| `SSHTYAGI_PORT` | Port for `start.sh`/`stop.sh` to use (default `8022`) |

Your GitHub username lives in `sshtyagi/config.py`.

## Customizing your content

Edit these two files — no code changes needed:

- `sshtyagi/data/resume.py` — name, title, about, experience, skills, contact
- `sshtyagi/data/real_madrid.py` — trophies (update `TROPHIES_AS_OF` when
  they win something new), legends, your personal favorites

## Known limitations

- TheSportsDB's free demo key returns partial lineup data (consistently
  3 of 11 starters across matches tested) — the Starting XI modal shows
  whatever comes back with an honest "partial data" note rather than
  pretending it's complete. A paid key would likely fix this.
- Not yet deployed publicly. Needs: a real domain (not `.web`, that's not
  a live TLD), a host that can hold a raw inbound TCP port open, and
  moving the box's own admin SSH off port 22 so this app can own it.
