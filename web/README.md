# Uyir — web app (deploy on Vercel)

Entraiot Solutions · Approvals: Shalini L (MD & CEO), Salvin Jones (Founder & Director)

Biology teacher for Tamil Nadu State Board, Std 3–12, Tamil + English. Voice in, voice out, answers read from the textbooks. Plain static files: no build step, no server code, no API keys.

## Deploy on Vercel (from GitHub)

1. Create a new GitHub repository (private is fine), e.g. `uyir-web`.
2. Upload everything in this folder to it, **including the hidden `.well-known` folder** (on GitHub's web upload, drag the folder in; or use GitHub Desktop / `git push`).
3. On vercel.com → **Add New → Project** → import the `uyir-web` repository.
4. Settings when asked:
   - **Framework Preset:** Other
   - **Root Directory:** `./`
   - **Build Command:** leave empty (Override → empty)
   - **Output Directory:** `.` (a single dot)
   - **Install Command:** leave empty
5. Deploy. You get an address like `https://uyir-xxxx.vercel.app`. Every push to GitHub redeploys it automatically.
6. Optional: Project → Settings → Domains → add `uyir.entraiot.com` (then add the DNS record Vercel shows in your cPanel DNS zone).

Note: Vercel's free Hobby plan is for non-commercial personal use only; a company product needs the Pro plan.

## Try it on a phone

Open the address in **Chrome on Android** → menu ⋮ → **Install app**. Tap the speaker, allow the microphone once. For Tamil speech: Android Settings → Text-to-speech → Google → install **Tamil (India)**.

## Voice (listening and speaking)

- **Speaking:** always full volume; picks the best-sounding voice on the phone (Google network / natural voices first); reads clean text (no bullets, figure or section numbers; says %, °C, CO2 in words); long sentences are split so no phone stops mid-answer; if the phone's speech engine drops speech, it restarts it automatically.
- **Listening:** one tap; compares up to 5 possible hearings and keeps the one that matches the class textbook; misheard long science words are matched to the book's own words; fixes Android's repeated-word bug; listens in the language you used last (if it misses you, it says so aloud and tries the other language next).
- **Signals:** short beep + vibration when it starts and stops listening; spoken "I didn't hear you"; screen stays awake while listening, thinking, speaking or reading.
- **Settings:** "Wait longer for slow speakers", "Sound and vibration cues", voice speed, 10 teacher voices; all remembered on the phone.
- Loudness depends on the phone's **media volume** (the app already speaks at the maximum). For classrooms, a Bluetooth speaker works well.

## Text quality

Books typed in the PDF were used as-is. Scanned books and the 2024 Tamil books were read by OCR and then corrected automatically (known glyph confusions of these fonts, cross-checked against a 2.5-million-word Tamil word list, Tamil Wikipedia and the other books; English one-letter slips and joined words). Science words are protected from "correction".

Spot checks (reading random lines): typed books ~100% · Std 8–10 Tamil ~97% · scanned Std 11–12 Tamil ~90–95% · scanned English ~98% of words correct. Answer accuracy on 249 definition questions taken from the books: Tamil 94%, English 92% (most "misses" were the same term defined on another page).

`PROOFREAD_PRIORITY_PAGES.csv` (in the package) lists the pages most worth a teacher's proofreading, worst first per book. Corrected text can replace a page's `t` field in `data/books/<book>.json`.

## Files

| Path | What it is |
|---|---|
| `index.html` | The app |
| `data/catalog.json`, `data/books/*.json` | Biology pages of every book, with chapter and printed page |
| `manifest.webmanifest`, `icon-*.png`, `sw.js` | Install as an app; works offline for books already opened |
| `vercel.json` | Headers: microphone allowed, caching, correct file types |
| `.well-known/assetlinks.json` | Links the Android app to this site (fill in after the first APK build — see the Android folder) |

## Updating books

Replace the `data` folder and push. When you change the app code or books, also change `CACHE = 'uyir-v3'` in `sw.js` to a new name (`uyir-v4` …) so installed phones refresh.
