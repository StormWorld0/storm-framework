# 🛠️ Installation Linux Storm Framework

For this Linux installation, it is actually an installation with an old version in a standard Linux environment, this will use commands like `--break-system-packages` while running `pip` which actually carries the risk of conflict with the Python dependencies used by the Linux system.

However, we still provide this option in case some users prefer installing using this legacy method. That said, we strongly recommend using a Virtual Machine (VM) when installing this way for better safety, or alternatively using other methods we have already provided **Venv/Docker.**

## 📖 Storm Framework Installation Steps

### 1. Clone Repository & Automated Installation

This URL will do the automatic installation and handle everything, you just have to wait until it's finished.

```bash
curl -fsSL https://raw.githubusercontent.com/StormWorld0/storm-framework/main/setuplinux | sudo bash
```

### 2. Execute Command

This is the command to run Storm after the installation is complete.

```bash
sudo storm
```

### 3. External Update Command

This will run the update without having to enter the Storm interface.

```bash
sudo storm --update
```

### 4. Copy Storm Trusted Root CA

This Root CA can be copied from internal to `$HOME` and is usually used when you want to run a module `https_proxy`, the command is as below:

```bash
sudo storm -c --crt
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

### 5. Help

Use this argument to display all valid arguments.

```bash
sudo storm -h
```
or
```bash
sudo storm --help
```
