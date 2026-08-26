#!/usr/bin/env bash
set -e

APP_ROOT="/opt/storm-framework"
cd "$APP_ROOT"

write_to_file() {
    local content=$1
    local file=$2
    local append=$3

    if [ "$append" = true ]; then
        echo "$content" | tee -a "$file" > /dev/null
    else
        echo "$content" | tee "$file" > /dev/null
    fi
}

# --- Security Identity Generation (Version: The 60-Char Fix) ---
if [ ! -f .env ]; then
    # Generate Private Key
    PRIV_KEY=$(openssl genpkey -algorithm ed25519 2>/dev/null | openssl pkey -outform DER 2>/dev/null | base64 -w 0 | tr -d '[:space:]')

    # Generate Public Key
    PUB_KEY=$(echo -n "$PRIV_KEY" | base64 -d | openssl pkey -inform DER -pubout -outform DER 2>/dev/null | base64 -w 0 | tr -d '[:space:]')

    # This code just adds '=' when PUBKEY is only 59 characters long
    # Rust with its dependencies is very sensitive, it doesn't want anything odd.
    # Storm's security logic is written in Rust, and this Key is to make it run.
    if [ ${#PUB_KEY} -eq 59 ]; then
        PUB_KEY="${PUB_KEY}="
    fi

    # This code will insert the key into .env
    # This is very crucial because if there is only 1 space it will not be usable.
    write_to_file "STORM_PRIVKEY=${PRIV_KEY}" ".env" false
    write_to_file "STORM_PUBKEY=${PUB_KEY}" ".env" true
    write_to_file "STORM_API=https://api.cant.workers.dev" ".env" true
fi

if [ ! -f data/smf_ca.key ] || [ ! -f data/smf_ca.crt ]; then
    cd "$APP_ROOT/data"
    
    openssl genrsa -out smf_ca.key 2048 >/dev/null 2>&1
    chmod 600 smf_ca.key

    cat > openssl_v3.cnf <<-EOF
[req]
distinguished_name = req_distinguished_name
[req_distinguished_name]
[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign
EOF

    # Redirect stderr ke /dev/null untuk mematikan log subject & issuer
    openssl req -x509 -new -nodes -key smf_ca.key -sha256 -days 3650 -out smf_ca.crt \
        -subj "/CN=Storm Trusted Root CA/O=StormWorld0/OU=Network-Security-Storm" \
        -extensions v3_ca -config openssl_v3.cnf >/dev/null 2>&1

    rm openssl_v3.cnf
    cd "$APP_ROOT"
fi

exec "$@"
