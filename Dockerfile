# ==========================================
# STAGE 1: Builder Environment
# (Fokus: Kompilasi engine utama dan ekstensi Python)
# ==========================================
FROM python:3.13-slim AS builder

# Hindari interaksi prompt saat instalasi apt
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GOFLAGS="-buildvcs=false" \
    APP_HOME=/opt/storm-framework

WORKDIR ${APP_HOME}

# Install dependensi build. 
# Tambahan: libffi-dev (untuk CTYPES/kriptografi) dan libreadline-dev (untuk REPL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
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

# Build wheels terisolasi
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --extra-index-url https://pypi.org/simple -r requirements.txt -w /tmp/wheels

# Kompilasi engine internal
RUN python3 -m scripts.cpl.compiler

# Pastikan binary hasil kompilasi memiliki permission eksekusi
RUN chmod +x ${APP_HOME}/smfstart


# ==========================================
# STAGE 2: Optimized Polyglot Runtime
# (Fokus: Eksekusi framework, REPL UX, dan Payload Generation)
# ==========================================
FROM python:3.13-slim AS runner

LABEL maintainer="StormWorld0"
LABEL description="Offensive Security Framework"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/opt/storm-framework \
    # Opsional: Set terminal environment untuk rendering REPL yang sempurna
    TERM=xterm-256color

WORKDIR ${APP_HOME}

# Install Runtime Libraries & Optional Tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    # --- CORE RUNTIME (Wajib) ---
    libpcap0.8 \
    ffmpeg \
    openssl \
    # --- REPL & UX (Direkomendasikan) ---
    # Dibutuhkan untuk autocomplete, history, dan UI terminal yang responsif di Python REPL
    libreadline8 \
    ncurses-bin \
    # --- DATABASE DRIVERS (Opsional, uncomment jika pakai DB untuk workspace) ---
    # postgresql-client-common \
    # libpq5 \
    sqlite3 \
    # --- DYNAMIC PAYLOAD GENERATORS (Opsional, uncomment jika modul butuh compile on-the-fly) ---
    # Untuk membuat custom malware/dropper saat runtime butuh cross-compiler di sini.
    # gcc-mingw-w64-x86-64 \
    # golang-go \
    # --- NETWORK UTILS (Opsional, untuk pivoting/tunneling internal modul) ---
    # proxychains4 \
    # iproute2 \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/lib/dpkg/status-old

# Copy hasil build wheels
COPY --from=builder /tmp/wheels /tmp/wheels

# Install wheels. Pip TETAP DIPERTAHANKAN.
# Alasan: Framework Offensive seringkali memiliki modul yang membutuhkan instalasi library
# pihak ketiga secara dinamis saat runtime (misal: exploit spesifik butuh lib baru).
RUN pip install --no-cache-dir /tmp/wheels/* && rm -rf /tmp/wheels

# Copy source code & hasil kompilasi
COPY --from=builder ${APP_HOME} ${APP_HOME}

# Tagging container environment
RUN echo "smf" > ${APP_HOME}/.docker

# File entrypoint ada di dalam repo source code
# yang sudah di-copy ke ${APP_HOME} dari builder.
RUN chmod +x ${APP_HOME}/docker/entrypoint.sh \
    && ln -s ${APP_HOME}/docker/entrypoint.sh /usr/local/bin/entrypoint.sh

# Opsional: Jika framework tidak butuh full root, berikan kapabilitas network khusus pada binary Python
# agar bisa melakukan packet sniffing (libpcap) tanpa privileges root penuh.
# RUN apt-get install -y libcap2-bin && setcap cap_net_raw,cap_net_admin=eip /usr/local/bin/python3.13

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["./smfstart"]
