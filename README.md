# Subtitle Shifter v1.2.2

Subtitle Shifter is a lightweight self-hosted web app for shifting `.srt` and `.vtt` subtitle timing directly on a media server.

It also supports **StreamPort** subtitle metadata lookup. A physical file such as:

```text
42.en.1234567.vtt
```

can be shown in the UI as:

```text
Example Show — S01E02 — Example Episode
```

The physical VTT filename is never renamed.

## Features

- SRT and VTT support
- Quick offsets: ±0.5 s, ±1 s, ±2 s, ±5 s
- Custom offset input
- Automatic `.bak` backup before the first modification
- One-click restore from `.bak`
- Subtitle preview
- English / Serbian UI
- Search by path, media title, season/episode and subtitle language
- StreamPort VTT metadata lookup via SQLite
- Read-only access to `streamport.db`
- SQLite WAL/read-only fallbacks: direct RO → immutable RO → temporary snapshot
- Docker health check

## Quick start

Clone the repository:

```bash
git clone https://github.com/sasalucic/subtitle-shifter.git
cd subtitle-shifter
```

Create your local configuration:

```bash
cp .env.example .env
nano .env
```

Set the host paths for your media and StreamPort installation, then run:

```bash
chmod +x install.sh
sudo ./install.sh
```

Verify the service:

```bash
curl http://127.0.0.1:5070/health
```

Open:

```text
http://SERVER_IP:5070
```

## Configuration

Example `.env`:

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

Expected VTT filename pattern:

```text
<media_id>.<language>.<subtitle_id>.vtt
```

The first number is looked up in the StreamPort `media` table:

```sql
SELECT id, title, kind, series, season, episode, episode_title, year, path
FROM media
WHERE id = ?;
```

## Docker Compose

```bash
docker compose up -d --build
```

## Documentation

- [Setup](docs/SETUP.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [HTTP API](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security](SECURITY.md)

## Security

The app has no built-in authentication and needs write access to subtitle directories. Do **not** expose port `5070` directly to the public internet. Use a LAN, VPN/Tailscale/WireGuard, or an authenticated reverse proxy.

## Version

`1.2.2`
