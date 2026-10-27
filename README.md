# Uyir — one repository

Entraiot Solutions · Approvals: Shalini L (MD & CEO), Salvin Jones (Founder & Director)

| Folder | What it is | Where it runs |
|---|---|---|
| `web/` | The app + all 30 books (`web/data/`) | Vercel (Root Directory = `web`) |
| `android/` | Android wrapper (APK / Play Store) | GitHub Actions (`.github/workflows/`) |
| `book-tools/` | Scripts that turn textbook PDFs into book data | Team computers only |
| `PROOFREAD_PRIORITY_PAGES.csv` | Pages teachers should proofread first | — |

## Vercel
Add New → Project → import this repo → **Root Directory: `web`** → Framework Preset: Other → leave Build/Install commands empty → Output Directory `.` → Deploy.

Optional (stops the website redeploying when only Android files change):
Project → Settings → Git → **Ignored Build Step** → Run my Bash script:
`git diff HEAD^ HEAD --quiet -- web/ && exit 0 || exit 1`

## Android
Edit `android/gradle.properties` (`twaHost=` your Vercel address, no https://), then GitHub → Actions → **Build Uyir APK** → Run workflow. Full steps: `android/README.md`.
The `assetlinks.json` produced by the build goes into `web/.well-known/assetlinks.json`.

## Books
Already inside `web/data/`. The app has no server: it reads those files from the website itself. Details: `web/README.md`.
