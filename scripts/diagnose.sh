#!/usr/bin/env bash
set -u

PORT="${HOST_PORT:-5070}"
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source ./.env
  set +a
  PORT="${HOST_PORT:-5070}"
fi

echo "=== Docker access ==="
if docker info >/dev/null 2>&1; then
  echo "OK"
else
  echo "NO ACCESS (try sudo ./scripts/diagnose.sh)"
fi

echo
echo "=== Container ==="
docker ps -a --filter name='^/subtitle-shifter$' --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' 2>&1 || true

echo
echo "=== Health ==="
curl -fsS "http://127.0.0.1:${PORT}/health" 2>&1 || true

echo
echo
echo "=== Force metadata scan ==="
curl -fsS "http://127.0.0.1:${PORT}/api/files" >/tmp/subtitle-shifter-files.json 2>/dev/null || true
curl -fsS "http://127.0.0.1:${PORT}/health" 2>&1 || true

echo
echo
echo "=== Recent logs ==="
docker logs --tail=80 subtitle-shifter 2>&1 || true
