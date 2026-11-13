FROM ghcr.io/astral-sh/uv:0.13.8@sha256:5cc1805e2426484abca4ad46ea783bab281fdb225fd82d8ce6d66a81254bac85 AS uv
FROM docker.io/library/python:3.15-slim-trixie@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928

LABEL org.opencontainers.image.title="Hadou Python base" \
      org.opencontainers.image.description="Python 3.12 and uv runtime for Hadou services" \
      org.opencontainers.image.source="https://github.com/hadousoftware/base-images" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV HOME=/home/hadou \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_CACHE_DIR=/home/hadou/.cache/uv

COPY --from=uv /uv /uvx /usr/local/bin/

RUN apt-get -o APT::Update::Error-Mode=any update \
    && DEBIAN_FRONTEND=noninteractive apt-get --yes --no-remove --with-new-pkgs upgrade \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends ca-certificates \
    && test -z "$(apt-mark showhold)" \
    && groupadd --gid 10001 hadou \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin hadou \
    && passwd --lock root \
    && mkdir -p /app /usr/share/hadou-base-images \
    && chown 10001:10001 /app \
    && dpkg-query -W -f='${binary:Package}\t${Version}\t${Architecture}\n' > /usr/share/hadou-base-images/packages.tsv \
    && find / -xdev -type f -perm /6000 -exec chmod a-s {} + \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python3 --version \
    && uv --version

WORKDIR /app
USER 10001:10001
CMD ["python3"]
