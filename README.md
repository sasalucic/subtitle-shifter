# 🎬 Subtitle Shifter

<p align="center">
  <strong>Fix out-of-sync subtitles directly from your phone or browser.</strong>
</p>

<p align="center">
  A lightweight self-hosted web app for permanently shifting <code>.srt</code> subtitle timing without SSH, terminal commands, or manually entering file paths.
</p>

<p align="center">
  Built for Jellyfin, Plex, Emby, and other self-hosted media servers.
</p>

---

## ✨ Features

- 🔍 Automatically finds all `.srt` subtitle files in your media library
- 📱 Mobile-friendly web interface
- 🎞️ Works with both movies and TV shows
- ⏪ Shift subtitles earlier
- ⏩ Shift subtitles later
- ⚡ Quick adjustment buttons
- 🎯 Custom offset support
- 👀 Built-in subtitle preview
- 💾 Automatic `.bak` backup before the first modification
- ♻️ Restore the original subtitle with one click
- 🐳 Docker support
- ❤️ Health-check endpoint
- 🔒 Prevents access outside the configured media directory
- 🌐 Works over LAN, Tailscale, WireGuard, or another VPN

---

## 📸 How It Works

Subtitle Shifter recursively scans your configured media directory and finds all `.srt` subtitle files.

There is no need to manually type file paths.

Simply:

1. Open Subtitle Shifter in your browser.
2. Search for a movie, show, season, episode, or subtitle filename.
3. Select the subtitle.
4. Choose how much you want to shift it.
5. Reload playback in Jellyfin, Plex, or your preferred media player.

That's it.

---

## ⏱️ Subtitle Controls

Quick controls are available directly in the interface:

| Button | Effect |
|---|---|
| `-5 s` | Move subtitles 5 seconds earlier |
| `-2 s` | Move subtitles 2 seconds earlier |
| `-1 s` | Move subtitles 1 second earlier |
| `-0.5 s` | Move subtitles 0.5 seconds earlier |
| `+0.5 s` | Move subtitles 0.5 seconds later |
| `+1 s` | Move subtitles 1 second later |
| `+2 s` | Move subtitles 2 seconds later |
| `+5 s` | Move subtitles 5 seconds later |

You can also enter a custom value such as:

```text
-1.7
