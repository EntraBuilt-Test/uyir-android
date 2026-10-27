# Book build tools

Turn the textbook PDFs into `data/books/*.json` for the app.

| File | What it does |
|---|---|
| `ocr_book.sh`, `ocr_page.sh` | OCR for scanned or garbled-font books (Tesseract, Tamil `tam` model from tessdata_fast; 150 dpi English, 160–200 dpi Tamil) |
| `clean.py` | Fixes Tamil text-layer glitches (doubled ், vowel signs in visual order, stray symbols) |
| `lexicon.py` | Builds word-frequency lists: Tamil Wikipedia + Project Madurai + open-tamil word lists + typed textbooks; English dictionary + typed textbooks |
| `correct.py` | Conservative OCR correction (Tamil glyph confusions, cross-book consistency, English joined words / one-letter slips). Only changes a word when the original is unknown and the result is a known word; science terms are protected |
| `build.py` | Finds chapters (page footers for typed books; contents page + offset for scanned books), keeps biology chapters for Std 3–10, applies `correct.py`, writes `data/` |
| `quality.py` | Scores every page (share of known words) and writes the per-page list used for proofreading |
| `ocr_titles.json`, `tamil_titles.json` | Chapter titles and start pages from each book's contents page |

Order: OCR → `lexicon.py` → `build.py` → `quality.py`.
