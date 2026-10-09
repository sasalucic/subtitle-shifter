# Setup from scratch

## Requirements

- Linux server
- Docker
- Git or the source archive
- A media directory
- StreamPort data directory containing `streamport.db`
- StreamPort subtitle directory

## Configure

Copy the example configuration:

```bash
cp .env.example .env
nano .env
```

Set host paths that exist on your own server:

```dotenv
MEDIA_HOST_PATH=/path/to/media
STREAMPORT_DATA_HOST_PATH=/path/to/StreamPort/data
STREAMPORT_SUBTITLES_HOST_PATH=/path/to/StreamPort/data/subtitles
STREAMPORT_SUBTITLE_DIR=STREAMPORT_TITLOVI
HOST_PORT=5070
PREVIEW_LINES=80
```

## Install

```bash
chmod +x install.sh
sudo ./install.sh
```

## Verify

```bash
sudo docker ps | grep subtitle-shifter
curl http://127.0.0.1:5070/health
```

After the first scan, `streamport_lookup_mode` should normally be `direct-ro`, `immutable-ro`, or `tmp-snapshot`.

## Upgrade

```bash
git pull
sudo ./install.sh
```

## Uninstall

```bash
sudo ./uninstall.sh
```

Upgrades and uninstall do not delete host subtitle files, backups, or StreamPort data.
