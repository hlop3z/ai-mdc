# WSL Cheat-Sheet

---

## 🚀 Launching WSL

- **Open your default distro**

  ```bash
  wsl
  ```

  Drops you into your Linux home.

- **Open a specific distro**

  ```bash
  wsl -d Ubuntu
  ```

- **Change Default distro**

  ```bash
  # 1. List available distros
  wsl -l -v

  # 2. Set your default distro
  wsl --set-default <DistroName>

  # e.g.
  wsl --set-default Ubuntu
  ```

---

## 📂 Working Directory

WSL automatically maps Windows drives under `/mnt`.

| Windows Path             | WSL Path                     |
| ------------------------ | ---------------------------- |
| `C:\Users\you\…\project` | `/mnt/c/Users/you/…/project` |
| `D:\Work\…\repo`         | `/mnt/d/Work/…/repo`         |

- **CD into a Windows folder from WSL**

  ```bash
  cd /mnt/c/Users/you/Projects/my-wasm-app
  ```

---

## 🎯 Launching WSL from CMD / PowerShell

1. **Navigate** to your Windows project folder:

   ```powershell
   cd C:\Users\you\Projects\my-wasm-app
   ```

2. **Start WSL** in that directory:

   ```powershell
   wsl
   ```

   You’ll land directly in `/mnt/c/Users/you/Projects/my-wasm-app`.

---

## ⚡ Shortcut via Batch Script

Create `launch-wsl.bat` anywhere:

```bat
@echo off
cd C:\Users\you\Projects\my-wasm-app
wsl
```

- **Double-click** this file (or run from CMD) to drop into your project inside WSL.

---

## 💡 Pro Tips

- **Open VS Code** in WSL from that folder:

  ```bash
  code .
  ```

- **Avoid** editing code on `/mnt` for faster I/O—copy to WSL’s native FS (`~/…`) when possible.
- **Check your distro list** and status:

  ```bash
  wsl --list --verbose
  ```

- **Set WSL 2 as default** if you haven’t:

  ```powershell
  wsl --set-default-version 2
  ```
