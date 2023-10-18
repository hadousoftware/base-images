ARG BASE_REGISTRY=registry1.dso.mil
ARG BASE_IMAGE=ironbank/redhat/ubi/ubi8
ARG BASE_TAG=8.8
ARG TZ=America/Los_Angeles 

FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG}

COPY terraform.zip /tmp

RUN dnf install -y unzip openssh bash git git-lfs \
    && dnf upgrade -y \
    && dnf clean all \
    && rm -rf /var/cache/dnf \
    && unzip -d /bin /tmp/terraform.zip \
    && chmod +x /bin/terraform \
    && rm /tmp/terraform.zip

RUN groupadd -g 1001 terraform \
    && useradd -r -u 1001 -m -s /sbin/nologin -g terraform terraform \
    && chmod g-s /usr/libexec/openssh/ssh-keysign \
    && chown -R terraform:terraform /etc/pki/ca-trust \
    && chmod -R 775 /etc/pki/ca-trust \
    && rm -f /usr/share/doc/perl-IO-Socket-SSL/example/simulate_proxy.pl \
    && find /usr/share/doc/perl-IO-Socket-SSL/certs -name "*.enc" -o -name "*.pem" | xargs rm -f \
    && find /usr/share/doc/perl-Net-SSLeay/examples -name "*.pem" | xargs rm -f

USER terraform

HEALTHCHECK --interval=30s --timeout=10s \
    CMD /usr/bin/curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/bin/terraform"]
