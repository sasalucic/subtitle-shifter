# Changelog

## 1.2.3 - 2026-10-09

- Fixed the subtitle discovery performance regression from v1.2.2.
- Discovery now scans only `*.srt` and `*.vtt` instead of walking every media file first.
- Preserved StreamPort VTT metadata mapping and read-only SQLite fallback behavior.
- Sanitized public configuration, documentation and examples.
- Public documentation is in English.

## 1.2.2 - 2026-10-09

- Fixed StreamPort metadata lookup on read-only/WAL SQLite mounts.
- Added direct read-only, immutable read-only and temporary snapshot fallback modes.
- Added StreamPort lookup diagnostics.

## 1.2.1 - 2026-10-09

- Added automatic StreamPort VTT-to-media metadata lookup.
- Added human-readable media/episode display names and language badges.

## 1.2.0

- Added VTT support and StreamPort subtitle-folder integration.

## 1.1.0

- Added English / Serbian UI.
