#!/usr/bin/env bash
set -e

APP_ROOT="/opt/storm-framework"
cd "$APP_ROOT"

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
    cd "$APP_ROOT"                                                                      fi
fi
exec "$@"
