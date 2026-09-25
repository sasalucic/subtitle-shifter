#!/usr/bin/env bash
set -euo pipefail
IMAGE_NAME="${IMAGE_NAME:-subtitle-shifter}"
CONTAINER_NAME="${CONTAINER_NAME:-subtitle-shifter}"
MEDIA_PATH="${MEDIA_PATH:-/mnt/media}"
PORT="${PORT:-5070}"

docker build -t "${IMAGE_NAME}" .
if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
  docker rm -f "${CONTAINER_NAME}"
fi

docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  -e MEDIA_ROOT=/media \
  -e PORT="${PORT}" \
  -p "${PORT}:${PORT}" \
  -v "${MEDIA_PATH}:/media:rw" \
  "${IMAGE_NAME}"

echo "Subtitle Shifter radi na: http://SERVER_IP:${PORT}"
