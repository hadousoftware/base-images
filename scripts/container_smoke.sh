#!/usr/bin/env bash
set -euo pipefail

image=${1:?usage: container_smoke.sh IMAGE IMAGE_NAME}
image_name=${2:?usage: container_smoke.sh IMAGE IMAGE_NAME}

case "$image_name" in
  base|python|node|bun|terraform|go) ;;
  *) echo "Unsupported image name" >&2; exit 2 ;;
esac

test "$(docker image inspect --format '{{.Config.User}}' "$image")" = '10001:10001'
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 64 --memory 256m \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=16m \
  --env "IMAGE_NAME=$image_name" --entrypoint /bin/sh "$image" -eu -c '
    . /etc/os-release
    test "$ID" = debian
    test "${VERSION_ID%%.*}" = 13
    test "$(id -u)" = 10001
    test "$(id -g)" = 10001
    test "$(awk "/^CapEff:/ {print \$2}" /proc/self/status)" = 0000000000000000
    test "$(awk "/^NoNewPrivs:/ {print \$2}" /proc/self/status)" = 1
    if touch /must-not-be-writable 2>/dev/null; then exit 1; fi
    test -r /etc/ssl/certs/ca-certificates.crt
    test -s /usr/share/hadou-base-images/packages.tsv
    if command -v sshd >/dev/null; then exit 1; fi
    if command -v sudo >/dev/null; then exit 1; fi
    test -z "$(find /usr /bin /sbin -xdev -type f -perm /6000 -print 2>/dev/null)"
    case "$IMAGE_NAME" in
      base) /bin/sh -c "test -n \"\$(id -u)\"" ;;
      python) python3 --version; uv --version ;;
      node) node --version; npm --version ;;
      bun) bun --version ;;
      terraform) terraform version ;;
      go) go version ;;
    esac
  '
