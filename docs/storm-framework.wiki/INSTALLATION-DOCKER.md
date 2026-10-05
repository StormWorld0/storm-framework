# 🛠️ Installation Docker Storm Framework

We provide a dedicated installation method for Docker to accommodate users who prefer containerized environments. This approach is carefully designed to ensure a smooth, reliable, and predictable setup process aligned with expected deployment standards.

## 📖 Storm Framework Installation Steps Linux or MacOS

### 1. Automated Installation Docker Images

This is a special URL for Storm installation and creating Docker Containers and so on automatically.

```bash
curl -fsSL https://raw.githubusercontent.com/StormWorld0/storm-framework/main/setupdocker | bash
```

### 2. Execute Commands

This is the command to run Storm after the installation is complete.  
Run with `sudo` if you need an underground connection.
```bash
storm
```

---

## 📖 Storm Framework Installation Steps Windows

### 1. Automated Installation Docker Images

Open PowerShell and then run the command below to install the Docker Image.

```powershell
Invoke-Expression (New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/StormWorld0/storm-framework/main/docker/install.ps1')
```

### 2. Execute Commands

Make sure you are using PowerShell with Administrator privileges to run this.

```powershell
storm
```

---
