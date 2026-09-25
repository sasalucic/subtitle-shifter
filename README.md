# 🎬 Subtitle Shifter

A lightweight self-hosted web app for permanently shifting `.srt` subtitle timing from any browser.

## 🌐 Languages

Subtitle Shifter supports:

- English
- Srpski

Use the language selector in the top-right corner. The selection is saved in your browser. On first visit, browsers configured for Serbian, Bosnian, or Croatian start in Serbian; other browsers start in English.

## 🐳 Docker

```bash
docker build -t subtitle-shifter .

docker run -d \
  --name subtitle-shifter \
  --restart unless-stopped \
  -e MEDIA_ROOT=/media \
  -e PORT=5070 \
  -p 5070:5070 \
  -v /mnt/media:/media:rw \
  subtitle-shifter
```

Open `http://SERVER_IP:5070`.

## Updating

Replace the project files, then rebuild and recreate the container with the commands above.

## Security

The app has no built-in authentication. Use LAN/VPN/Tailscale or an authenticated reverse proxy.
