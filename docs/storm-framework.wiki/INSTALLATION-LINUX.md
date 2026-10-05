# 🛠️ Installation Linux Storm Framework

For this Linux installation, it is actually an installation with an old version in a standard Linux environment, this will use commands like `--break-system-packages` while running `pip` which actually carries the risk of conflict with the Python dependencies used by the Linux system.

However, we still provide this option in case some users prefer installing using this legacy method. That said, we strongly recommend using a Virtual Machine (VM) when installing this way for better safety, or alternatively using other methods we have already provided **Venv/Docker.**

## 📖 Storm Framework Installation Steps

### 1. Clone Repository & Automated Installation

This URL will do the automatic installation and handle everything, you just have to wait until it's finished.

```bash
curl -fsSL https://raw.githubusercontent.com/StormWorld0/storm-framework/main/setuplinux | bash
```

### 2. Execute Command

This is the command to run Storm after the installation is complete.  
Run with `sudo` if you need an underground connection.
```bash
storm
```

### 3. External Update Command

This will run the update without having to enter the Storm interface.

```bash
storm --update
```

### 4. Help

Use this argument to display all valid arguments.

```bash
storm -h
```
or
```bash
storm --help
```
