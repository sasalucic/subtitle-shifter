# Security

Subtitle Shifter je napravljen kao privatni admin alat za LAN/VPN okruženje.

Aplikacija trenutno nema ugrađen login ili role-based access control i namjerno dobija write pristup subtitle direktorijima kako bi mogla mijenjati `.srt`/`.vtt` i praviti `.bak` fajlove.

Zato:

- nemoj port 5070 direktno port-forwardati na javni internet,
- koristi LAN, Tailscale/WireGuard/VPN ili reverse proxy sa autentikacijom,
- StreamPort data folder je mountan `:ro`; samo subtitle folder je `:rw`,
- čuvaj Docker pristup samo za pouzdane admin korisnike,
- prije većih promjena na media storageu imaj normalan server backup; `.bak` u ovoj aplikaciji nije zamjena za kompletan backup.

Path handling u aplikaciji ograničava API operacije na `MEDIA_ROOT`, ali to nije razlog da servis bude javno izložen bez autentikacije.
