FROM docker.io/hashicorp/terraform:1.17.1@sha256:a5d5a5a892c98f60fcbfa81eac2a40fc19e7b3fa7719bccae10ff6111d22524a AS terraform
FROM docker.io/library/debian:13-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2

LABEL org.opencontainers.image.title="Hadou Terraform base" \
      org.opencontainers.image.description="Terraform 1.17 CLI for Hadou infrastructure workflows" \
      org.opencontainers.image.source="https://github.com/hadousoftware/base-images" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV HOME=/home/hadou \
    TF_IN_AUTOMATION=1 \
    TF_PLUGIN_CACHE_DIR=/home/hadou/.terraform.d/plugin-cache

COPY --from=terraform /bin/terraform /usr/local/bin/terraform

RUN apt-get -o APT::Update::Error-Mode=any update \
    && DEBIAN_FRONTEND=noninteractive apt-get --yes --no-remove --with-new-pkgs upgrade \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends ca-certificates git openssh-client \
    && test -z "$(apt-mark showhold)" \
    && groupadd --gid 10001 hadou \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin hadou \
    && passwd --lock root \
    && mkdir -p /workspace /home/hadou/.terraform.d/plugin-cache /usr/share/hadou-base-images \
    && chown -R 10001:10001 /workspace /home/hadou \
    && dpkg-query -W -f='${binary:Package}\t${Version}\t${Architecture}\n' > /usr/share/hadou-base-images/packages.tsv \
    && find / -xdev -type f -perm /6000 -exec chmod a-s {} + \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && terraform version

WORKDIR /workspace
USER 10001:10001
ENTRYPOINT []
CMD ["terraform", "version"]
