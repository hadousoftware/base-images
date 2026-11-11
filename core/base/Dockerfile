FROM docker.io/library/debian:13-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2

LABEL org.opencontainers.image.title="Hadou Debian base" \
      org.opencontainers.image.description="Minimal Debian 13 application runtime; non-root and multi-architecture" \
      org.opencontainers.image.source="https://github.com/hadousoftware/base-images" \
      org.opencontainers.image.licenses="Apache-2.0"

RUN apt-get -o APT::Update::Error-Mode=any update \
    && DEBIAN_FRONTEND=noninteractive apt-get --yes --no-remove --with-new-pkgs upgrade \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends ca-certificates \
    && test -z "$(apt-mark showhold)" \
    && groupadd --gid 10001 hadou \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin hadou \
    && passwd --lock root \
    && mkdir -p /app /usr/share/hadou-base-images \
    && chown 10001:10001 /app \
    && dpkg-query -W -f='${binary:Package}\t${Version}\t${Architecture}\n' > /usr/share/hadou-base-images/packages.tsv \
    && find / -xdev -type f -perm /6000 -exec chmod a-s {} + \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
USER 10001:10001
CMD ["/bin/sh"]
