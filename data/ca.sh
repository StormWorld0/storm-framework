# Generate ROOT CA TRUST STORE
if [ -f smf_ca.key ] && [ -f smf_ca.crt ]; then
else
    # Delete CA lama
    rm -f smf_ca.key smf_ca.crt

    # Generate CA private key
    openssl genrsa -out smf_ca.key 2048

    # Allow standard owner read/write
    chmod 600 smf_ca.key

    # Generate self-signed CA certificate
    openssl req -x509 -new -nodes \
        -key smf_ca.key \
        -sha256 \
        -days 3650 \
        -out smf_ca.crt \
        -subj "/CN=Storm Trusted Root CA/O=StormWorld0/OU=Network-Security-Storm" \
        -extensions v3_ca \
        -config <(cat <<-EOF
[req]
distinguished_name = req_distinguished_name
[req_distinguished_name]
[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign
EOF
        )
fi
