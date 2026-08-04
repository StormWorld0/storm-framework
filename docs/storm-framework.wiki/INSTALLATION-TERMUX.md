# 🛠️ Installation Termux Storm Framework

The installation for Termux is flexible, you don't have to root the device you are using and even if the device is rooted it will still run very well as it should.

## 📖 Step Instalasi Storm Framework

### 1. Repository Cloning & Automated Installation

Use this command to install in Termux, it will run the installation automatically and handle everything and you just have to wait until it is finished.

```bash
curl -fsSL https://raw.githubusercontent.com/StormWorld0/storm-framework/main/setuptermux | bash
```

### 2. Execute Command

Use this command to run Storm.

```bash
storm
```

### 3. External Update Command

Use this if you want to perform updates outside the Storm interface.

```bash
storm --update
```

### 4. Copy Storm Trusted Root CA

This Root CA can be copied from internal to `$HOME` and is usually used when you want to run a module `https_proxy`, the command is as below:

```bash
storm --cp --crt
```

Next after copying CA `$HOME` use the command below to copy to `sdcard` Android internal storage:

```bash
cp smf_ca.crt /sdcard
```

After the previous copy is complete, use it directly by:

1. **Go to Android Settings**
2. **Go to Privacy & Security**
3. **Go to Install certificate from storage**
4. **Install CA Certificate**
5. **Import smf_ca.crt from storage**
