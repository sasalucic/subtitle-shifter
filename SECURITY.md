# Security

Subtitle Shifter v1.0.0 does not include authentication.

Do not expose port `5070` directly to the public internet. Use it on a trusted LAN, through Tailscale/WireGuard, or behind an authenticated reverse proxy.

The app has write access to the mounted media directory, so treat it as an administrative media-management tool.
