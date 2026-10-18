# 1. Base image
FROM python:3.12-slim

# 2. Python settings that make containers behave better:
#   - PYTHONUNBUFFERED: print logs immediately instead of buffering them.
#   - PIP_NO_CACHE_DIR: don't keep pip's download cache in the image (smaller).
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 3. System tools that woninet shells out to:
#    - net-tools   -> `arp`   (reads the ARP table)
#    - iproute2    -> `ip`    (finds the default gateway)
#    - iputils-ping-> `ping`  (fallback when raw ICMP sockets are unavailable)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        net-tools \
        iproute2 \
        iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# 4. Install woninet from the source in this repository.
WORKDIR /build
COPY pyproject.toml README.md ./
COPY woninet ./woninet
RUN pip install .

# 5. Runtime directory. woninet reads config.json and writes woninet.db
#    relative to its working directory, so we make /data that directory and
#    mount a volume there (see compose.yaml) to keep your data between runs.
WORKDIR /data
VOLUME ["/data"]

# 6. The dashboard's default port (informational; with host networking the
#    port is opened directly on the host and `-p` is not needed).
EXPOSE 8080

# 7. ENTRYPOINT is the fixed command; CMD holds default arguments that users
#    can override.
ENTRYPOINT ["woninet"]
CMD ["--config", "/data/config.json"]
