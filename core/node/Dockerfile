ARG BASE_REGISTRY=registry.access.redhat.com
ARG BASE_IMAGE=ubi8/ubi-minimal
ARG BASE_TAG=latest
ARG NODE_VERSION=lts
ARG TZ=America/Los_Angeles 

FROM node:${NODE_VERSION} as base

FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG}

ENV HOME=/home/node \
    USER=node \
    TZ=${TZ}

# Install system dependencies
RUN microdnf --disableplugin=subscription-manager install -y --nodocs \
        shadow-utils \
        your-additional-dependencies && \
    groupadd -g 1000 node && \
    adduser -r -u 1000 -m -s /sbin/nologin -g node node && \
    chown node:0 ${HOME} && \
    chmod g=u ${HOME} && \
    microdnf --disableplugin=subscription-manager update && \
    microdnf --disableplugin=subscription-manager clean all && \
    rm -rf /var/cache/yum


# Copy necessary files from the base image
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /usr/local/include /usr/local/include
COPY --from=base /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=base /opt /opt
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Set the timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Working directory and user
WORKDIR ${HOME}
USER 1000

HEALTHCHECK --interval=30s --timeout=10s \
    CMD curl -f http://localhost:8080/health || exit 1

# Entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["node"]
