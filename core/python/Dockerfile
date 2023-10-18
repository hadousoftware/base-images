# Use a minimal base image
ARG BASE_REGISTRY=registry.access.redhat.com
ARG BASE_IMAGE=ubi8/ubi-minimal
ARG BASE_TAG=8.8
ARG TZ=America/Los_Angeles

FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG}

ENV HOME=/home/python \
    USER=python \
    TZ=${TZ}

# Install system dependencies and create a non-root user
RUN microdnf --disableplugin=subscription-manager install -y --nodocs \
        shadow-utils \
    && groupadd -g 1000 python \
    && adduser -r -u 1000 -m -s /sbin/nologin -g python python \
    && chown python:0 ${HOME} \
    && chmod g=u ${HOME} \
    && microdnf --disableplugin=subscription-manager update \
    && microdnf --disableplugin=subscription-manager clean all \
    && rm -rf /var/cache/yum

# Set the timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s \
    CMD /usr/bin/python3 -c "print('Healthy')"

# Entry point
ENTRYPOINT ["python3"]
CMD ["--version"]
