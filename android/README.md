# Uyir — Android app (APK / Play Store)

Entraiot Solutions · Approvals: Shalini L (MD & CEO), Salvin Jones (Founder & Director)

This is a **Trusted Web Activity**: a small Android app that opens the Uyir website full-screen inside Chrome. Voice input and spoken answers work exactly as on the website, and app updates are just website updates. The APK is built by **GitHub Actions** — you do not need Android Studio.

Package name: `com.entraiot.uyir`

## 1. Put this folder on GitHub

Create a repository (private is fine), e.g. `uyir-android`, and upload everything in this folder **including the hidden `.github` folder**.

## 2. Tell it your website address

Edit `gradle.properties` → `twaHost=` your Vercel address **without** `https://` (for example `uyir-abc.vercel.app` or `uyir.entraiot.com`). Commit.

## 3. Build a test APK (no key needed)

GitHub → **Actions → Build Uyir APK → Run workflow**. When it finishes (about 3–5 minutes), open the run → **Artifacts → uyir-android** → download. Inside is `app-debug.apk`. Copy it to the phone and install (allow "install unknown apps").

A test build shows a thin address bar at the top; that disappears once step 5 is done with your release key.

## 4. Create your release signing key (once)

Option A — on GitHub: **Actions → Make signing key (run once) → Run workflow**, type a strong password. Download the artifact, then **delete that workflow run**.
Option B — on your computer (Java installed): `scripts/make-keystore.sh`.

Then GitHub → repository **Settings → Secrets and variables → Actions → New repository secret**, add:

| Secret | Value |
|---|---|
| `KEYSTORE_BASE64` | contents of `KEYSTORE_BASE64.txt` |
| `KEYSTORE_PASSWORD` | your password |
| `KEY_PASSWORD` | your password |
| `KEY_ALIAS` | `uyir` |

Keep `uyir-release.jks` and the password safe (e.g. company password manager). **Every future update must be signed with this same key.**

Run **Build Uyir APK** again: you now get `app-release.apk` (to share) and `app-release.aab` (for the Play Store).

## 5. Link the app to the website (removes the address bar)

The build's **Summary** page shows a ready-made `assetlinks.json`. Copy it into the web repository at `.well-known/assetlinks.json`, push, and wait for Vercel to redeploy. Check it opens at `https://YOUR-SITE/.well-known/assetlinks.json`.

If you upload to Google Play with **Play App Signing**, Play re-signs the app: also add the SHA-256 shown in Play Console → Setup → App signing to the `sha256_cert_fingerprints` list.

## 6. Play Store

Play Console → create app → upload `app-release.aab`. For each new upload, run the workflow with a higher **version code** (2, 3, …). The app is for school students, so complete the Families / Data safety sections carefully (microphone use, no ads, data collected).

## Files

| Path | What it is |
|---|---|
| `app/src/main/AndroidManifest.xml` | Opens `https://<twaHost>/` full-screen |
| `app/build.gradle` | Package name, versions, signing, website address |
| `.github/workflows/build-apk.yml` | Builds APK + AAB, prints the assetlinks fingerprint |
| `.github/workflows/make-signing-key.yml` | Creates the release key once |
