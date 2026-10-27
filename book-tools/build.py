"""Build per-book JSON (biology chapters only) + catalog for the Uyir preview.
Each page: n = PDF page, pg = printed page, u = unit/chapter number, t = cleaned text.
"""
import json, os, re, sys, glob
sys.path.insert(0, os.path.dirname(__file__))
from clean import clean_ta, clean_common

ROOT = '/home/claude/books'
TXT = ROOT + '/txt'
OCR = ROOT + '/ocr'
OUT = ROOT + '/data'
os.makedirs(OUT + '/books', exist_ok=True)

# ---------- unit titles (from each book's contents page) ----------
U = {
 '3':  {1: ('My Body', 'எனது உடல்')},
 '4':  {1: ('My Body', 'எனது உடல்')},
 '5':  {1: ('Organ Systems', 'உறுப்பு மண்டலங்கள்')},
 '6':  {4: ('The World of Plants', 'தாவர உலகம்'), 5: ('The World of Animals', 'விலங்குலகம்'),
        6: ('Health and Hygiene', 'உடல் நலமும் சுகாதாரமும்')},
 '7':  {5: ('Reproduction and Modification in Plants', 'தாவரங்களின் இனப்பெருக்கம் மற்றும் மாற்றுருக்கள்'),
        6: ('Health and Hygiene', 'உடல் நலமும், சுகாதாரமும்')},
 '8':  {16: ('Microorganisms', None), 17: ('Plant Kingdom', None), 18: ('Organisation of Life', None),
        19: ('Movements in Animals', None), 20: ('Reaching the Age of Adolescence', None),
        21: ('Crop Production and Management', None), 22: ('Conservation of Plants and Animals', None)},
 '9':  {17: ('Animal Kingdom', None), 18: ('Organisation of Tissues', None), 19: ('Plant Physiology', None),
        20: ('Organ Systems in Animals', None), 21: ('Nutrition and Health', None), 22: ('World of Microbes', None),
        23: ('Economic Biology', None), 24: ('Environmental Science', None)},
 '10': {12: ('Plant Anatomy and Plant Physiology', None), 13: ('Structural Organisation of Animals', None),
        14: ('Transportation in Plants and Circulation in Animals', None), 15: ('Nervous System', None),
        16: ('Plant and Animal Hormones', None), 17: ('Reproduction in Plants and Animals', None),
        18: ('Genetics', None), 19: ('Origin and Evolution of Life', None), 20: ('Breeding and Biotechnology', None),
        21: ('Health and Diseases', None), 22: ('Environmental Management', None)},
 '12Z': {1: ('Reproduction in Organisms', None), 2: ('Human Reproduction', None), 3: ('Reproductive Health', None),
        4: ('Principles of Inheritance and Variation', None), 5: ('Molecular Genetics', None), 6: ('Evolution', None),
        7: ('Human Health and Diseases', None), 8: ('Immunology', None), 9: ('Microbes in Human Welfare', None),
        10: ('Applications of Biotechnology', None), 11: ('Organisms and Populations', None),
        12: ('Biodiversity and its Conservation', None), 13: ('Environmental Issues', None)},
}
# Tamil titles filled in later from the OCR'd contents pages (tamil_titles.json), else "அலகு N"
TT = {}
if os.path.exists(ROOT + '/scripts/tamil_titles.json'):
    TT = json.load(open(ROOT + '/scripts/tamil_titles.json', encoding='utf-8'))

BOOKS = [
 # id, std key, medium, label, source, file/dir, edition
 ('3_sci_en', '3', 'en', 'Science · Term 1', 'txt', 'Class_3_Science_English_Science_-_Term_1_-_2025_Edition', '2025'),
 ('3_sci_ta', '3', 'ta', 'அறிவியல் · பருவம் 1', 'txt', 'Class_3_Science_Tamil_Science_-_Term_1_-_2025_Edition', '2025'),
 ('4_sci_en', '4', 'en', 'Science · Term 1', 'txt', 'Class_4_Science_English_Science_-_Term_1_-_2025_Edition', '2025'),
 ('4_sci_ta', '4', 'ta', 'அறிவியல் · பருவம் 1', 'txt', 'Class_4_Science_Tamil_Science_-_Term_1_-_2025_Edition', '2025'),
 ('5_sci_en', '5', 'en', 'Science · Term 1', 'txt', 'Class_5_Science_English_Science_-_Term_1_-_2025_Edition', '2025'),
 ('5_sci_ta', '5', 'ta', 'அறிவியல் · பருவம் 1', 'txt', 'Class_5_Science_Tamil_Science_-_Term_1_-_2025_Edition', '2025'),
 ('6_sci_en', '6', 'en', 'Science · Term 1', 'txt', 'Class_6_Science_English_Science_-_Term_1_-_2025_edition', '2025'),
 ('6_sci_ta', '6', 'ta', 'அறிவியல் · பருவம் 1', 'txt', 'Class_6_Science_Tamil_Science_-_Term_1_-_2025_Edition', '2025'),
 ('7_sci_en', '7', 'en', 'Science · Term 1', 'txt', 'Class_7_Science_English_Science_-_Term_1_-_2025_Edition', '2025'),
 ('7_sci_ta', '7', 'ta', 'அறிவியல் · பருவம் 1', 'txt', 'Class_7_Science_Tamil_Science_-_Term_1_-_2025_Edition', '2025'),
 ('8_sci_en', '8', 'en', 'Science', 'txt', 'Class_8_Science_English_2024_Edition', '2024'),
 ('8_sci_ta', '8', 'ta', 'அறிவியல்', 'ocrfooter', ('Class_8_Science_Tamil_2024_Edition', '8_science_ta'), '2024'),
 ('9_sci_en', '9', 'en', 'Science', 'txt', 'Class_9_Science_English_2024_Edition', '2024'),
 ('9_sci_ta', '9', 'ta', 'அறிவியல்', 'ocrfooter', ('Class_9_Science_Tamil_2024_edition', '9_science_ta'), '2024'),
 ('10_sci_en', '10', 'en', 'Science', 'txt', 'Class_10_Science_English_2024_Edition', '2024'),
 ('10_sci_ta', '10', 'ta', 'அறிவியல்', 'ocrfooter', ('Class_10_Science_Tamil_2024_Edition', '10_science_ta'), '2024'),
 ('12_zoo_en', '12Z', 'en', 'Zoology', 'txt', 'Class_12_Zoology_English_2024_Edition', '2024'),
 ('12_zoo_ta', '12Z', 'ta', 'விலங்கியல்', 'ocrfooter', ('Class_12_Zoology_Tamil_2024_Edition', '12_zoology_ta'), '2024'),
 # scanned books: chapters detected from OCR text (see detect_chapters)
 ('11_biobot_en', '11B', 'en', 'Bio-Botany', 'ocr', '11_biobotany_en', '2024'),
 ('11_biobot_ta', '11B', 'ta', 'உயிர்-தாவரவியல்', 'ocr', '11_biobotany_ta', '2024'),
 ('11_biozoo_en', '11Z', 'en', 'Bio-Zoology', 'ocr', '11_biozoology_en', '2024'),
 ('11_biozoo_ta', '11Z', 'ta', 'உயிர்-விலங்கியல்', 'ocr', '11_biozoology_ta', '2024'),
 ('12_biobot_en', '12B', 'en', 'Bio-Botany', 'ocr', '12_biobotany_en', '2024'),
 ('12_biobot_ta', '12B', 'ta', 'உயிர்-தாவரவியல்', 'ocr', '12_biobotany_ta', '2024'),
 ('11_bot_en', '11B', 'en', 'Botany · Volume 1', 'ocr', '11_botany_en', '2024'),
 ('11_bot_ta', '11B', 'ta', 'தாவரவியல் · தொகுதி 1', 'ocr', '11_botany_ta', '2024'),
 ('11_zoo_en', '11Z', 'en', 'Zoology', 'ocr', '11_zoology_en', '2024'),
 ('11_zoo_ta', '11Z', 'ta', 'விலங்கியல்', 'ocr', '11_zoology_ta', '2024'),
 ('12_bot_en', '12B', 'en', 'Botany', 'ocr', '12_botany_en', '2024'),
 ('12_bot_ta', '12B', 'ta', 'தாவரவியல்', 'ocr', '12_botany_ta', '2024'),
]

FOOT = re.compile(r'(?:Unit|Chapter)[\s_\-]*0?(\d+)', re.I)


def footer_info(raw):
    ind = re.findall(r'[^\n]*\.indd\s*(\d+)?', raw)
    line = ' '.join(re.findall(r'[^\n]*\.indd[^\n]*', raw))
    m = FOOT.search(line)
    unit = int(m.group(1)) if m else None
    pm = re.search(r'\.indd\s+(\d+)', line)
    return unit, (int(pm.group(1)) if pm else None)


def fill_units(units):
    """pages between two pages of the same unit (no footer) belong to that unit"""
    first, last = {}, {}
    for i, u in enumerate(units):
        if u is None: continue
        first.setdefault(u, i); last[u] = i
    out = list(units)
    for u in first:
        for i in range(first[u], last[u] + 1):
            if out[i] is None: out[i] = u
    return out


JUNK = re.compile(r'(\|.*\|)|\.ind[d]?\b|\b(EM|TM)[_ ]?(Chap|Unit|Front)|Chapier|indd|^\W{0,3}\w{0,2}\W{0,3}$', re.I)


def drop_ocr_junk(text):
    keep = []
    for l in text.splitlines():
        t = l.strip()
        if t and JUNK.search(t) and not re.fullmatch(r'\d{1,3}', t): continue
        letters = sum(ch.isalpha() for ch in t)
        if t and len(t) > 4 and letters / len(t) < 0.45: continue
        keep.append(l)
    return '\n'.join(keep)


def clean(text, medium, ocr=False):
    if ocr: text = drop_ocr_junk(text)
    if medium == 'ta': text = clean_ta(text)
    text = clean_common(text)
    if ocr:
        from correct import fix          # OCR spelling correction (see correct.py)
        text = fix(text, medium)
    return text


def ocr_pages(d):
    files = sorted(glob.glob(f'{OCR}/{d}/p*.txt'))
    return {int(re.search(r'p(\d+)\.txt', f).group(1)): open(f, encoding='utf-8').read() for f in files}


def printed_number(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in lines[:2] + lines[-2:]:
        if re.fullmatch(r'\d{1,3}', l): return int(l)
    return None


OT = json.load(open(ROOT + '/scripts/ocr_titles.json', encoding='utf-8')) if os.path.exists(ROOT + '/scripts/ocr_titles.json') else {}
CH_RE = re.compile(r'^\s*(?:CHAPTER|Chapter|chapter|பாடம்|அலகு\s*\d+\s*பாடம்)\b')


def detect_chapters(pages, medium, bid):
    """scanned books: chapter start = printed page from the contents page + a constant offset.
    The offset is measured from the first page whose top lines begin with 'Chapter'/'பாடம்'."""
    cfg = OT.get(bid)
    if not cfg: return []
    heads = [n for n in sorted(pages) if n >= 3 and any(CH_RE.match(l) for l in [l for l in pages[n].splitlines() if l.strip()][:3])]
    if not heads and 'offset' not in cfg: return []
    from collections import Counter
    votes = Counter(h - pg for h in heads for _, pg in cfg['ch'] if 0 <= h - pg <= 30)
    off = cfg.get('offset', votes.most_common(1)[0][0] if votes else 0)
    starts = [(p + off, k + 1, t) for k, (t, p) in enumerate(cfg['ch'])]
    end = cfg['end_pdf'] if 'end_pdf' in cfg else cfg['end'] + off
    return starts, end, off


def build():
    catalog = []
    for bid, std, med, label, src, f, ed in BOOKS:
        pages_out = []
        chapters = []
        if src in ('txt', 'ocrfooter'):
            base = f if src == 'txt' else f[0]
            raw_pages = open(f'{TXT}/{base}.txt', encoding='utf-8', errors='replace').read().split('\f')
            info = [footer_info(p) for p in raw_pages]
            units = fill_units([u for u, _ in info])
            ocr = ocr_pages(f[1]) if src == 'ocrfooter' else {}
            if src == 'ocrfooter' and not ocr: continue
            umap = U[std]
            for i, p in enumerate(raw_pages):
                u = units[i]
                if u not in umap: continue
                text = ocr.get(i + 1) if src == 'ocrfooter' else p
                if text is None: continue
                t = clean(text, med, src == 'ocrfooter')
                if len(t) < 20: continue
                pages_out.append({'n': i + 1, 'pg': info[i][1], 'u': u, 't': t})
            for u, (en, ta) in umap.items():
                ps = [p for p in pages_out if p['u'] == u]
                if not ps: continue
                title = en if med == 'en' else (ta or TT.get(f'{std}:{u}') or f'அலகு {u}')
                chapters.append({'u': u, 'title': title, 'en': en, 'start': ps[0]['n'], 'end': ps[-1]['n'], 'count': len(ps)})
        else:
            pages = ocr_pages(f)
            if len(pages) < 20: continue
            det = detect_chapters(pages, med, bid)
            if not det: continue
            starts, last, off = det
            for k, (n, num, title) in enumerate(starts):
                end = (starts[k + 1][0] - 1) if k + 1 < len(starts) else last
                chapters.append({'u': num, 'title': title or (f'Chapter {num}' if med == 'en' else f'பாடம் {num}'), 'start': n, 'end': end})
            for c in chapters:
                for n in range(c['start'], c['end'] + 1):
                    if n not in pages: continue
                    t = clean(pages[n], med, True)
                    if len(t) < 20: continue
                    pages_out.append({'n': n, 'pg': n - off if n - off > 0 else None, 'u': c['u'], 't': t})
            for c in chapters:
                c['count'] = sum(1 for p in pages_out if p['u'] == c['u'])
        if not pages_out: continue
        book = {'id': bid, 'std': std, 'medium': med, 'label': label, 'edition': ed, 'chapters': chapters, 'pages': pages_out}
        json.dump(book, open(f'{OUT}/books/{bid}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        catalog.append({'id': bid, 'std': std, 'medium': med, 'label': label, 'edition': ed,
                        'chapters': [{k: c[k] for k in ('u', 'title', 'start', 'end', 'count')} for c in chapters],
                        'pages': len(pages_out)})
        print(f'{bid:14} {len(chapters):2} chapters {len(pages_out):4} pages  {os.path.getsize(f"{OUT}/books/{bid}.json")//1024} KB')
    json.dump(catalog, open(f'{OUT}/catalog.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


if __name__ == '__main__':
    build()
