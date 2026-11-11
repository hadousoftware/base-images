# Go compatibility image

Go is no longer part of the active Hadou application stack. This image remains
as a tested, non-published builder for downstream compatibility. It uses the
current supported Go release line on Debian 13, runs as UID/GID 10001, and does
not include application dependencies.

Remove it from `images.json` once all downstream consumers are confirmed gone.
