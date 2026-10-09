# Security

Subtitle Shifter is intended for a trusted LAN/VPN environment.

- The app has no built-in authentication.
- Do not expose the service directly to the public internet.
- Keep StreamPort metadata/database storage read-only.
- Keep only subtitle/media directories that must be edited read-write.
- Keep `.env` local and out of Git.
- Do not commit private IP addresses, credentials, tokens, secrets, or machine-specific sensitive paths.
- Treat Docker daemon access as privileged/root-equivalent access.
- Keep normal server backups; subtitle `.bak` files are not a full backup solution.
