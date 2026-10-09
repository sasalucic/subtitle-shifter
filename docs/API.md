# HTTP API

## GET /health

Returns version, media-root state and StreamPort lookup diagnostics.

## GET /api/files

Returns discovered SRT/VTT files. StreamPort items can include fields such as:

```json
{
  "name": "42.en.1234567.vtt",
  "display_name": "Example Show — S01E02 — Example Episode",
  "subtitle_language": "en",
  "streamport": true,
  "streamport_media_id": 42,
  "streamport_subtitle_id": 1234567
}
```

## GET /api/preview?path=...

Returns subtitle preview text, type and backup state.

## POST /api/shift

```json
{
  "path": "STREAMPORT_TITLOVI/42.en.1234567.vtt",
  "delta_ms": 500
}
```

Negative values move subtitles earlier; positive values move them later.

## POST /api/restore

```json
{
  "path": "STREAMPORT_TITLOVI/42.en.1234567.vtt"
}
```

Restores the original content from the `.bak` file.
