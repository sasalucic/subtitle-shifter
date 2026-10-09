# Troubleshooting

## Quick diagnostics

```bash
sudo ./scripts/diagnose.sh
```

## UI shows 0 subtitles

Check the Docker mounts and verify the subtitle directory is visible inside the container. Version 1.2.3 scans only `*.srt` and `*.vtt`; it no longer enumerates every unrelated file in large media libraries.

## StreamPort VTT files show physical filenames only

Force a scan, then inspect health:

```bash
curl -s http://127.0.0.1:5070/api/files >/dev/null
curl http://127.0.0.1:5070/health
```

`streamport_db_available` should be true. A working lookup mode is `direct-ro`, `immutable-ro`, or `tmp-snapshot`.

If `streamport_lookup_error` is not null:

```bash
sudo docker logs --tail=150 subtitle-shifter
```

## Database unavailable

Verify the path configured in your local `.env`, for example:

```bash
ls -l /path/to/StreamPort/data/streamport.db
```

## Write permission errors

Media/subtitle mounts must be writable. The StreamPort database/data mount should remain read-only.

## Old UI after an upgrade

Perform a hard refresh in the browser after reinstalling the container.
