ARG BASE_REGISTRY=hadou.io
ARG BASE_IMAGE=base/abi
ARG BASE_TAG=edge
ARG TZ=America/Los_Angeles
ARG GOVERSION=1.19.3-r0

FROM ${BASE_REGISTRY}/${BASE_IMAGE}:${BASE_TAG} as base


# Configure Go
ENV GOVERSION=${GOVERSION} \
    GOROOT=/usr/lib/go \    
    GOPATH=/go \
    PATH=/go/bin:$PATH \
    TZ=${TZ}

RUN apk add --no-cache git make musl-dev go=${GOVERSION} upx

RUN mkdir -p ${GOPATH}/src ${GOPATH}/bin

# Set the timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR $GOPATH
