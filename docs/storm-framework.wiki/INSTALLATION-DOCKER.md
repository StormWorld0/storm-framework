# 🛠️ Installation Docker Storm Framework

We provide a dedicated installation method for Docker to accommodate users who prefer containerized environments. This approach is carefully designed to ensure a smooth, reliable, and predictable setup process aligned with expected deployment standards.

## 📖 Storm Framework Installation Steps Linux or MacOS

### 1. Automated Installation Docker Images

This is a special URL for Storm installation and creating Docker Containers and so on automatically.

```bash
curl -fsSL https://raw.githubusercontent.com/StormWorld0/storm-framework/main/setupdocker | sudo bash
```

### 2. Execute Commands

This is the command to run Storm after the installation is complete.

```bash
sudo storm
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

## 📝 Performing CA Copy

To copy **smf_ca.crt** on Linux / MacOS / Windows. Use the command below.

### Linux / MacOS / Windows

Just adjust it to the OS you are using, for **Windows** use **PowerShell** to run the command, if you can't activate the Administrator.

```bash
storm -cp -crt
```
or
```bash
sudo storm -cp -crt
```
