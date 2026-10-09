#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source ./.env
  set +a
fi

MEDIA_HOST_PATH="${MEDIA_HOST_PATH:-/mnt/media}"
STREAMPORT_DATA_HOST_PATH="${STREAMPORT_DATA_HOST_PATH:-/opt/streamport/data}"
STREAMPORT_SUBTITLES_HOST_PATH="${STREAMPORT_SUBTITLES_HOST_PATH:-/opt/streamport/data/subtitles}"
STREAMPORT_SUBTITLE_DIR="${STREAMPORT_SUBTITLE_DIR:-STREAMPORT_TITLOVI}"
HOST_PORT="${HOST_PORT:-5070}"
PREVIEW_LINES="${PREVIEW_LINES:-80}"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker is not installed. See docs/SETUP.md." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Cannot access Docker daemon." >&2
  echo "Run this installer with: sudo ./install.sh" >&2
  exit 1
fi

[[ -d "$MEDIA_HOST_PATH" ]] || { echo "ERROR: MEDIA_HOST_PATH does not exist: $MEDIA_HOST_PATH" >&2; exit 1; }
[[ -d "$STREAMPORT_SUBTITLES_HOST_PATH" ]] || { echo "ERROR: StreamPort subtitle directory does not exist: $STREAMPORT_SUBTITLES_HOST_PATH" >&2; exit 1; }
[[ -f "$STREAMPORT_DATA_HOST_PATH/streamport.db" ]] || { echo "ERROR: StreamPort database not found: $STREAMPORT_DATA_HOST_PATH/streamport.db" >&2; exit 1; }

echo "Building Subtitle Shifter v1.2.2..."
docker build -t subtitle-shifter:1.2.2 -t subtitle-shifter:latest .

docker rm -f subtitle-shifter >/dev/null 2>&1 || true

docker run -d   --name subtitle-shifter   --restart unless-stopped   -e MEDIA_ROOT=/media   -e STREAMPORT_DB=/streamport/streamport.db   -e STREAMPORT_SUBTITLE_DIR="$STREAMPORT_SUBTITLE_DIR"   -e PORT=5070   -e PREVIEW_LINES="$PREVIEW_LINES"   -p "$HOST_PORT:5070"   -v "$MEDIA_HOST_PATH:/media:rw"   -v "$STREAMPORT_SUBTITLES_HOST_PATH:/media/$STREAMPORT_SUBTITLE_DIR:rw"   -v "$STREAMPORT_DATA_HOST_PATH:/streamport:ro"   subtitle-shifter:1.2.2 >/dev/null

echo "Subtitle Shifter v1.2.2 started."
echo "Health check: http://127.0.0.1:$HOST_PORT/health"
