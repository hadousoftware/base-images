FROM docker.io/library/node:26-trixie-slim@sha256:5adad64f9a1fca2d51972caa65983634c8a774eb300d72b20f7f2a0f60368072

LABEL org.opencontainers.image.title="Hadou Node.js base" \
      org.opencontainers.image.description="Node.js 26 LTS runtime for Astro, Vite, and Node-compatible tooling" \
      org.opencontainers.image.source="https://github.com/hadousoftware/base-images" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV HOME=/home/hadou \
    NODE_ENV=production

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
    && node --version

WORKDIR /app
USER 10001:10001
CMD ["node"]
