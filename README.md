# Subtitle Shifter v1.2.3

Subtitle Shifter is a lightweight self-hosted web app for permanently shifting `.srt` and `.vtt` subtitle timing from a browser.

It also supports **StreamPort** metadata lookup. A physical subtitle filename such as:

```text
42.en.1234567.vtt
```

can be displayed as:

```text
Example Show — S01E02 — Example Episode
```

The physical VTT filename is never renamed.

## Features

- SRT and VTT support
- Quick shifts: ±0.5 s, ±1 s, ±2 s, ±5 s
- Custom decimal-second offsets
- Automatic `.bak` backup before the first modification
- One-click restore from `.bak`
- Subtitle preview
- English / Serbian UI
- Search by file path, media title, season/episode and subtitle language
- StreamPort VTT metadata lookup through `streamport.db`
- Read-only StreamPort database access
- SQLite read-only/WAL fallbacks: direct RO → immutable RO → temporary snapshot
- Efficient subtitle-only scan (`*.srt` and `*.vtt`) for large media libraries
- Docker health check

## Quick start

```bash
git clone https://github.com/sasalucic/subtitle-shifter.git
cd subtitle-shifter
cp .env.example .env
nano .env
sudo ./install.sh
```

Verify:

```bash
curl http://127.0.0.1:5070/health
```

Open from a trusted network:

```text
http://SERVER_IP:5070
```

## Configuration

Example local `.env`:

```dotenv
MEDIA_HOST_PATH=/path/to/media
STREAMPORT_DATA_HOST_PATH=/path/to/StreamPort/data
STREAMPORT_SUBTITLES_HOST_PATH=/path/to/StreamPort/data/subtitles
STREAMPORT_SUBTITLE_DIR=STREAMPORT_TITLOVI
HOST_PORT=5070
PREVIEW_LINES=80
```

`STREAMPORT_DATA_HOST_PATH` is mounted read-only. Subtitle Shifter does not modify `streamport.db`.

## StreamPort mapping

Expected filename pattern:

```text
<media_id>.<language>.<subtitle_id>.vtt
```

The first number is matched against the StreamPort `media` table. The UI uses the returned media metadata to build a human-readable title while leaving the physical VTT filename unchanged.

## Documentation

- [Setup](docs/SETUP.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [HTTP API](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security](SECURITY.md)

## Security

The app has no built-in authentication and requires write access to subtitle directories. Do **not** expose it directly to the public internet. Use a trusted LAN, VPN/Tailscale/WireGuard, or an authenticated reverse proxy.

## Version

`1.2.3`
