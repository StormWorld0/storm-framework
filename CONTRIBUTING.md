# 🛠️ Storm-Framework Contribution Guide

Hello! Thank you for your interest in enlarging **Storm-Framework**. This project is a project *open-source*, So your help means a lot to make this tool stronger and more solid!

---

## 📜 Rules
In order for the code merging process (*Merge*) to run smoothly, please follow these standards:

### 1. Code Quality & Standards
- **Python 3.12.x**: Make sure your code is compatible with the latest version.
- **Passed GitHub Actions**: Before sending a Pull Request (PR), make sure the indicator in your repo is colored. **Green ✅**. Our system will check *Syntax Error* automatically.
- **Clear Variables**: Don't use "ghost" variables. Define all variables. (like `VERSION`) correctly to avoid the `undefined name` error.

### 2. Module Structure & Dependencies
- **Modules Folder**: Save your new module in the `modules/` folder.
- **Requirements**: If your module requires additional libraries, please note them in the `requirements.txt` file.
- **Modules Guide**: You can read the explanation [here](https://github.com/StormWorld0/storm-framework/blob/main/docs/storm-framework.wiki/MODULE_GUIDE.md) to know how to implement modules correctly.

---

## 🚀 How to Submit a Contribution

| Step | Order / Action |
| :--- | :--- |
| **1. Fork** | Click the button **Fork** in the top right corner of this repo. |
| **2. Clone** | `git clone https://github.com/[your-username]/storm-framework.git` |
| **3. Branch** | `git checkout -b your new features` |
| **4. Commit** | `git commit -m "Add modules X"` |
| **5. Push** | `git push origin your new features` |
| **6. Test** | Please test your changes before committing to PR |
| **7. PR** | Open **Pull Request** to our `main` branch. |

---

## 🏆 Award
We really appreciate your hard work. The name of each contributor whose code was successfully-*merge* will be permanently displayed at:

* **File CONTRIBUTE.md** (Part Hall of Fame).

---

### 💡 Testing
If you want to make sure your code passes the censorship before it is-*push*, run this in terminal:
```bash
pip install flake8
flake8 . --count --select=E9,F63,F7,F82,F401,W191,B018 --show-source --statistics
