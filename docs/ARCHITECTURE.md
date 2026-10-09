# Architecture

Subtitle Shifter uses a Flask backend and a single HTML/JavaScript frontend.

## Subtitle discovery

Version 1.2.3 scans only `*.srt` and `*.vtt`. This fixes the v1.2.2 regression that walked every file under the media root before filtering.

## StreamPort mapping

A filename matching `<media_id>.<language>.<subtitle_id>.vtt` is parsed, then `media_id` is batch-looked-up in `streamport.db`. The UI receives a human-readable display name while the physical subtitle filename remains unchanged.

## SQLite strategy

Lookup tries direct read-only, immutable read-only, then a temporary local snapshot. The original StreamPort database is never opened for writing.

## Backups

Before the first successful subtitle write, `<subtitle>.bak` is created. Later shifts do not overwrite that original backup.
