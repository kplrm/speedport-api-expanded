FROM python:3.12-slim

ARG SPEEDPORT_VERSION
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl iproute2 jq util-linux \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir "speedport-api-expanded==${SPEEDPORT_VERSION}"

LABEL org.opencontainers.image.source="https://github.com/kplrm/speedport-api-expanded" \
      org.opencontainers.image.version="${SPEEDPORT_VERSION}"
