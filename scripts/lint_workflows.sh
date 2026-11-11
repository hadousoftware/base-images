#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
image=$(sed -n 's/^FROM //p' tools/actionlint.Dockerfile)
[[ "$image" =~ ^rhysd/actionlint:[0-9.]+@sha256:[0-9a-f]{64}$ ]]
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --user "$(id -u):$(id -g)" \
  --tmpfs /tmp:rw,noexec,nosuid,size=32m \
  --volume "$PWD:/repo:ro" --workdir /repo "$image" -color
