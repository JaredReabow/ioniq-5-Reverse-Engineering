FROM --platform=linux/amd64 debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 openssh-client ca-certificates xz-utils \
    && rm -rf /var/lib/apt/lists/*
