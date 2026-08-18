# ==========================================
# Builder Environment
# ==========================================
FROM python:3.13-slim AS builder

# Avoid prompt interaction during apt installation
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GOFLAGS="-buildvcs=false" \
    APP_HOME=/opt/storm-framework

WORKDIR ${APP_HOME}

# Install build dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    curl \
    golang \
    build-essential \
    libpcap-dev \
    clang \
    cmake \
    openssl \
    cargo \
    pkg-config \
    libssl-dev \
    rustc \
    python3-dev \
    libffi-dev \
    libreadline-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --extra-index-url https://pypi.org/simple -r requirements.txt -w /tmp/wheels

RUN python3 -m scripts.cpl.compiler
RUN chmod +x ${APP_HOME}/smfstart


# ==========================================
# Optimized Runtime
# ==========================================
FROM python:3.13-slim AS runner

LABEL maintainer="StormWorld0"
LABEL description="Offensive Security Framework"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/opt/storm-framework \
    TERM=xterm-256color \
    GOPATH=/go \
    PATH=/go/bin:$PATH

WORKDIR ${APP_HOME}

# Install Runtime Libraries & Optional Tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    nmap \
    git \
    pkg-config \
    procps \
    libpcap0.8 \
    libpcap-dev \
    libssl-dev \
    libffi-dev \
    ca-certificates \
    ffmpeg \
    openssl \
    libreadline8 \
    ncurses-bin \
    sqlite3 \
    libcap2-bin \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/lib/dpkg/status-old \
    && mkdir -p /go/bin /go/pkg /go/src

# Copy the build wheels results
COPY --from=builder /tmp/wheels /tmp/wheels

# Install wheels. pip maintained
# Reason: Offensive Framework has modules that require library installation
# third parties dynamically at runtime.
RUN pip install --no-cache-dir /tmp/wheels/* && rm -rf /tmp/wheels

# Copy source code & compilation results
COPY --from=builder ${APP_HOME} ${APP_HOME}

# Tagging container environment
RUN echo "smf" > ${APP_HOME}/.docker

# The entrypoint file is in the source code repo.
# which has been copied to ${APP_HOME} from the builder.
RUN chmod +x ${APP_HOME}/docker/entrypoint.sh \
    && ln -s ${APP_HOME}/docker/entrypoint.sh /usr/local/bin/entrypoint.sh

# To perform packet sniffing (libpcap) without full root privileges.
RUN setcap cap_net_raw,cap_net_admin=eip /usr/local/bin/python3.13 && \
    setcap cap_net_raw,cap_net_bind_service=eip /usr/bin/nmap

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["./smfstart"]
