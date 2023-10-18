FROM library/alpine:edge as edge
RUN apk --no-cache upgrade
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

FROM scratch
COPY --from=edge / /
