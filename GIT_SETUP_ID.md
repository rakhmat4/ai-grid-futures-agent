# Panduan Upload ke GitHub

## 1. Buat repository baru di GitHub

Nama yang disarankan:

```text
ai-grid-futures-agent
```

Saat membuat repo:

- Jangan centang README.
- Jangan centang .gitignore.
- Jangan pilih license, karena file sudah ada di lokal.

## 2. Buka PowerShell di folder project

```powershell
cd "$env:USERPROFILE\Downloads\ai-grid-futures-agent-github-repo"
```

Cek isi folder:

```powershell
dir
```

Harus ada:

```text
grid_agent
scripts
requirements.txt
README.md
ROADMAP.md
```

## 3. Inisialisasi Git

```powershell
git init
git add .
git commit -m "Initial commit: AI grid futures agent"
```

## 4. Hubungkan ke GitHub

Ganti USERNAME dengan username GitHub Anda:

```powershell
git remote add origin https://github.com/USERNAME/ai-grid-futures-agent.git
git branch -M main
git push -u origin main
```

## 5. Update setelah revisi

```powershell
git status
git add .
git commit -m "Update research engine"
git push
```

## 6. Branch untuk V3

```powershell
git checkout -b feature/v3-atr-trend-filter
```

Setelah selesai:

```powershell
git add .
git commit -m "Add V3 ATR adaptive grid and trend filter"
git push -u origin feature/v3-atr-trend-filter
```
