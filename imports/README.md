# Private card imports

`python -m helpers import-card --root . --source <local.png-or.json>` preserves original bytes in a SHA-256 directory alongside extracted JSON and provenance. V1 and V2/V3 envelopes are source material; unknown fields stay private. No scripts execute, remote assets download, or greetings become story events. Unsupported formats and malformed preferred metadata produce diagnostics.

Imports do not publish cast. Deliberately use `python -m helpers portrait --root . --source imports/<hash>/source.png` to export an appearance-preserving PNG without text/EXIF metadata. Add its relative name to a disclosed cast entry separately. Originals remain unchanged. Limits: 32 MiB source, 8 MiB decoded JSON.
