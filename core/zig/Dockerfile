# move to support ARM64

ARG BASE_REGISTRY=registry.access.redhat.com
ARG BASE_IMAGE=ubi8/ubi-minimal
ARG BASE_TAG=latest
ARG ZIG_VERSION=0.7.1
ARG TZ=America/Los_Angeles

# Use UBI Minimal as the base image
FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG}

ENV HOME=/home/zig \
    USER=zig \
    TZ=${TZ}

# Install system dependencies
RUN microdnf --disableplugin=subscription-manager install -y --nodocs \
        shadow-utils \
        tar \
        gzip \
        wget && \
    groupadd -g 1000 zig && \
    adduser -r -u 1000 -m -s /sbin/nologin -g zig zig && \
    chown zig:0 ${HOME} && \
    chmod g=u ${HOME} && \
    microdnf --disableplugin=subscription-manager update && \
    microdnf --disableplugin=subscription-manager clean all && \
    rm -rf /var/cache/yum

# Download and install Zig
RUN wget https://ziglang.org/download/${ZIG_VERSION}/zig-linux-x86_64-${ZIG_VERSION}.tar.xz && \
    tar -xf zig-linux-x86_64-${ZIG_VERSION}.tar.xz -C /usr/local && \
    ln -s /usr/local/zig-linux-x86_64-${ZIG_VERSION}/zig /usr/local/bin/zig && \
    rm zig-linux-x86_64-${ZIG_VERSION}.tar.xz

# Set the timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR ${HOME}
USER 1000

# HEALTHCHECK --interval=30s --timeout=10s \
#    CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["zig"]
