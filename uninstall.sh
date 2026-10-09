#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Cannot access Docker daemon. Run: sudo ./uninstall.sh" >&2
  exit 1
fi

docker rm -f subtitle-shifter >/dev/null 2>&1 || true
echo "Subtitle Shifter container removed."
echo "Subtitle files, .bak files, StreamPort data, and the Docker image were not deleted."
