FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GOFLAGS="-buildvcs=false" \
    APP_HOME=/opt/storm-framework
    
WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    golang \
    build-essential \
    libpcap-dev \
    clang \
    cmake \
    ffmpeg \
    openssl \
    cargo \
    pkg-config \
    libssl-dev \
    rustc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

RUN python3 -m scripts.cpl.compiler
RUN echo "smf" > ${APP_HOME}/.docker

COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["./smfstart"]
