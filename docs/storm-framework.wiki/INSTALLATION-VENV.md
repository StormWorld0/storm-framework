# 🛠️ Installation Venv Storm Framework

This installation follows the standard recommended by Python. Since Storm is Python-based, we implement Storm installation using a virtual environment (venv) because it is safer. This ensures that dependencies and packages are isolated within a virtual space without affecting the global `site-packages`, which is what we highly recommend for you.

## 📖 Storm Framework Installation Steps

### 1. Repository Clone & Automated Installation

This URL will run the installation automatically, including creating Venv and so on, you just have to wait for it to finish.

```bash
curl -fsSL https://raw.githubusercontent.com/StormWorld0/storm-framework/main/setupvenv | sudo bash
```

### 2. Execute Command

This is the command to run Storm.

```bash
sudo storm
```

### 3. External Update Command

Allows updates outside the Storm interface without having to startup.

```bash
sudo storm --update
```

### 4. Copy Storm Trusted Root CA

This Root CA can be copied from internal to `$HOME` and is usually used when you want to run a module `https_proxy`, the command is as below:

```bash
sudo storm --cp --crt
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

---

## Troubleshooting

If you encounter an error message `make: cargo: No such file or directory` in the compilation process, this is usually caused by the security hardening mechanism on `sudo` which resets the variable `PATH` your system. `sudo` does not automatically recognize the **Rust** installation located on `/root/.cargo/bin`.

### How to overcome it

To ensure the compiler script recognizes the Rust Toolchain, you need to modify `/etc/sudoers` in `secure_path` and look for;

```bash
Defaults secure_path=
```

And change it to something like this;

```bash
Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

After that you can call the command `sudo storm --update` to update the storm-framework and recompile anything that was not compiled during the initial installation. If it still fails I suggest running **setupdocker** which should be more stable in a bad environment like this.

If you feel that everything has been done but the same error still appears during the compilation process, you can open **Issue** by explaining everything in detail, we will be happy to help😁.
