# 🛠️ Installation Docker Storm Framework

We provide a dedicated installation method for Docker to accommodate users who prefer containerized environments. This approach is carefully designed to ensure a smooth, reliable, and predictable setup process aligned with expected deployment standards.

## 📖 Storm Framework Installation Steps

### 1. Repository Clone & Automated Installation

This is a special URL for Storm installation and creating Docker Containers and so on automatically.

```bash
curl -fsSL https://raw.githubusercontent.com/StormWorld0/storm-framework/main/setupdocker | sudo bash
```

### 2. Execute Command

This is the command to run Storm after the installation is complete.

```bash
sudo storm
```

### 3. External Update Command

This will run updates outside of the Storm interface without having to startup.

```bash
sudo storm --update
```

### 4. Copy Storm Trusted Root CA

This Root CA can be copied from internal to `$HOME` and is usually used when you want to run a module `https_proxy`, the command is as below:

```bash
sudo storm -cp -crt
```

After finishing copying CA to `$HOME` use the following command to insert into the trust store certificate:

```bash
sudo cp smf_ca.crt /usr/local/share/ca-certificates/smf_ca.crt
```

Then confirm with the command:

```bash
sudo update-ca-certificates
```

You can also install Storm Trust Root CA to Firefox Browser and so on.
