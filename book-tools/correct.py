"""Conservative OCR correction for Tamil and English book text.

Tamil: only known glyph confusions of these textbooks' fonts (e.g. டு read as ரு / டூ, வர read as ஹ,
ந்த read as ர்த), applied only when the original word is NOT a known word and the corrected word IS.
English: rejoin words split by a hyphen at line end, split run-together words, and fix one-letter
OCR slips, again only when the original is unknown and the result is a known textbook/dictionary word.
"""
import re, os

LEX = '/home/claude/lex'


def _load(p, minc=1):
    d = {}
    with open(p, encoding='utf-8') as f:
        for line in f:
            w, c = line.rstrip('\n').split('\t')
            c = int(c)
            if c >= minc: d[w] = c
    return d


TA = _load(LEX + '/ta_freq.tsv', 3)
EN = _load(LEX + '/en_freq.tsv', 1)
EN_TEXT = {w for w, c in EN.items() if c >= 20}          # words that occur in the typed textbooks

# --- Tamil ---------------------------------------------------------------
# (wrong, right, minimum frequency of the corrected word)
TA_RULES = [
    ('ரு', 'டு', 3), ('ரூ', 'டு', 3), ('டூ', 'டு', 3), ('ரூ', 'டூ', 3),
    ('ஹ', 'வர', 3), ('ஹ', 'வ', 20), ('ஷ', 'வ', 20),
    ('ர்த', 'ந்த', 3), ('ர்து', 'ந்து', 3), ('ர்', 'ந்', 30),
    ('ல்வ', 'ல்ல', 10), ('வ்வ', 'ல்ல', 10),
    ('ச்க', 'க்க', 10), ('ச்ச', 'க்க', 50), ('க்ச', 'க்க', 10),
    ('ஞு', 'று', 20), ('ூ', 'ு', 30),
    ('ணப்பரு', 'ணப்படு', 1), ('ப்பரு', 'ப்படு', 3),
    ('க்ம', 'க்டீ', 2), ('ச்ம', 'க்டீ', 2), ('க்மர', 'க்டீர', 1), ('ச்மர', 'க்டீர', 1), ('ண்ற', 'ன்ற', 10), ('ல்வை', 'ல்லை', 10),
    ('ச', 'க', 60), ('ப', 'ய', 60), ('ன', 'ள', 60), ('ள', 'ன', 60), ('ம', 'ம்', 60),
    ('வ', 'ல', 20), ('ா', 'ர', 10), ('ே', 'ெ', 20), ('மு', 'ழு', 20), ('ண', 'ன', 20), ('ண்ன', 'ன்றன', 3),
    ('வவ', 'வெ', 10), ('ோவப', 'ோப', 3), ('ஸ', 'ல', 30),
    ('ச்கி', 'க்கி', 3), ('ச்கு', 'க்கு', 3), ('ச்க', 'க்க', 3), ('ட்ப', 'ட்டு', 10),
]
TA_WORD = re.compile(r'[஀-௿]+')
# the ai-sign (ை) is drawn before its letter and is often read as ஸ: 'ஸல' -> 'லை'
TA_RULES += [('ஸ' + c, c + 'ை', 3) for c in 'கஙசஞடணதநபமயரலவழளறன']
_ta_cache = {}
TA_MAP = {}
DOMAIN = {}


def _ta_fix(w):
    if w in _ta_cache: return _ta_cache[w]
    if w in TA_MAP:
        _ta_cache[w] = TA_MAP[w]; return TA_MAP[w]
    res = w
    if len(w) >= 3 and w not in TA:
        best = None
        frontier = {w}
        seen = {w}
        for depth in range(3):                     # up to 3 rule applications in one word
            nxt = set()
            for cur in frontier:
                for a, b, minf in TA_RULES:
                    i = cur.find(a)
                    while i >= 0:
                        cand = cur[:i] + b + cur[i + len(a):]
                        if cand not in seen:
                            seen.add(cand); nxt.add(cand)
                            f = TA.get(cand, 0)
                            if f >= minf and (best is None or f > best[1]): best = (cand, f)
                        i = cur.find(a, i + 1)
            if best: break
            frontier = nxt
        if best: res = best[0]
    _ta_cache[w] = res
    return res


TA_DIGITS = str.maketrans({'௮': 'அ', '௦': '0', '௫': 'டு', '௪': '4', '௯': '9', '௭': 'எ'})

# Science words from the better-quality Tamil books (typed-font books read by OCR at full resolution):
# words seen 3+ times there, that our rules would not change, are accepted as real words.
def _add_domain_words():
    import json, collections
    c = collections.Counter()
    for bid in ('8_sci_ta', '9_sci_ta', '10_sci_ta', '12_zoo_ta'):
        f = '/home/claude/books/data/books/%s.json' % bid
        if not os.path.exists(f): continue
        for p in json.load(open(f, encoding='utf-8'))['pages']:
            c.update(w for w in TA_WORD.findall(p['t'].translate(TA_DIGITS)) if len(w) >= 4)
    added = 0
    for w, n in c.items():
        if n >= 3 and w not in TA and _ta_fix(w) == w:
            TA[w] = n; added += 1
    _ta_cache.clear()
    return added


DOMAIN_ADDED = _add_domain_words()


# --- Cross-book self-consistency -------------------------------------------
# If a word is unknown, and a rule-variant of it is much more common across all the Tamil books,
# the rare form is an OCR slip. Words that recur across independent books are accepted as real.
SOURCES = {'8_sci_ta': 'S8', '9_sci_ta': 'S9', '10_sci_ta': 'S10', '12_zoo_ta': 'Z12', '11_bot_ta': 'B11', '11_biobot_ta': 'B11',
           '11_zoo_ta': 'Z11', '11_biozoo_ta': 'Z11', '12_bot_ta': 'B12', '12_biobot_ta': 'B12',
           '3_sci_ta': 'T', '4_sci_ta': 'T', '5_sci_ta': 'T', '6_sci_ta': 'T', '7_sci_ta': 'T'}


def _rule_variants(w, depth=2):
    out, frontier = set(), {w}
    for _ in range(depth):
        nxt = set()
        for cur in frontier:
            for a, b, _m in TA_RULES:
                i = cur.find(a)
                while i >= 0:
                    v = cur[:i] + b + cur[i + len(a):]
                    if v not in out and v != w: out.add(v); nxt.add(v)
                    i = cur.find(a, i + 1)
        frontier = nxt
    return out


def _build_consistency():
    import json, collections
    C = collections.Counter(); src = collections.defaultdict(set)
    for bid, sname in SOURCES.items():
        f = '/home/claude/books/data/books/%s.json' % bid
        if not os.path.exists(f): continue
        for p in json.load(open(f, encoding='utf-8'))['pages']:
            for w in TA_WORD.findall(p['t'].translate(TA_DIGITS)):
                if len(w) >= 4: C[w] += 1; src[w].add(sname)
    for w, n in C.items():
        if w in TA: continue
        best = None
        for v in _rule_variants(w):
            cv = C.get(v, 0)
            if cv >= max(3, 3 * n) and len(src.get(v, ())) >= 1:
                if best is None or cv > best[1]: best = (v, cv)
        if best: TA_MAP[w] = best[0]
        elif len(src[w]) >= 2 or (n >= 4 and len(src[w]) >= 1 and 'T' in src[w]):
            DOMAIN[w] = n
    for w, n in DOMAIN.items():
        TA.setdefault(w, n)
    _ta_cache.clear()


_build_consistency()


LONE = re.compile(r'(?:(?<=\s)|^)[அ-ஹ][ா-்]?(?=[\s.,]|$)(?!\))', re.M)


def fix_tamil(text):
    text = text.translate(TA_DIGITS)
    text = re.sub('‌|‍', '', text)
    text = TA_WORD.sub(lambda m: _ta_fix(m.group(0)), text)
    out = []
    for line in text.split('\n'):
        if not line.strip():
            out.append(line); continue
        t = LONE.sub('', line)                                     # stray single letters from figure labels
        t = re.sub(r'[ \t]{2,}', ' ', t).strip()
        if not t or re.fullmatch(r'[ .,:;|\-]*\d?[ .,:;|\-]*', t):
            continue                                               # drop the whole line, so no false paragraph break
        out.append(t)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out))

# --- English -------------------------------------------------------------
import glob, json, collections
_corpus = collections.Counter()
for _f in glob.glob('/home/claude/books/data/books/*_en.json'):
    for _p in json.load(open(_f, encoding='utf-8'))['pages']:
        _corpus.update(w.lower() for w in re.findall(r'[A-Za-z]{3,}', _p['t']))
_SMALL = {'a', 'an', 'of', 'in', 'to', 'is', 'on', 'by', 'or', 'as', 'at', 'the', 'and', 'for', 'are', 'it', 'be', 'its', 'this', 'that', 'with', 'from'}
_SUFFIX = {'ly', 'ed', 'es', 's', 'ous', 'ic', 'us', 'os', 'al', 'ing', 'er', 'ers', 'ion', 'ions', 'ism', 'ist', 'ase', 'ose', 'ide', 'ate', 'oid', 'id', 'ia', 'ae', 'um', 'a'}


def _known(lw):
    # accepted if in the dictionary / typed textbooks, appears 3+ times in the books,
    # or is a regular form of a known word (British spelling, -ing/-ed/-s/-less/-ly, prefixes)
    if lw in EN or _corpus[lw] >= 3: return True
    for a, b in (('our', 'or'), ('ise', 'ize'), ('isation', 'ization'), ('yse', 'yze'), ('ae', 'e'), ('oe', 'e')):
        if a in lw and lw.replace(a, b) in EN: return True
    for suf in ('ing', 'ed', 'es', 's', 'ly', 'less', 'ness', 'ation', 'al', 'ic', 'er', 'ers', 'ity'):
        if lw.endswith(suf):
            st = lw[:-len(suf)]
            if st in EN or st + 'e' in EN or (len(st) > 3 and st[-1] == st[-2] and st[:-1] in EN): return True
    for pre in ('non', 'semi', 'ultra', 'micro', 'macro', 'hemi', 'photo', 'bio', 'sub', 'super', 'inter', 'intra', 'pre', 'post', 'multi', 'uni', 'mono', 'poly', 'endo', 'exo', 'ecto', 'meta', 'phyto', 'thermo', 'fore', 'land', 'night', 'self', 'over', 'under', 'out', 're', 'un', 'in', 'de', 'dis', 'co'):
        if lw.startswith(pre) and len(lw) - len(pre) >= 4 and _known(lw[len(pre):]): return True
    return False


START_SMALL = {'has', 'have', 'it', 'the', 'they', 'to', 'of', 'also', 'are', 'this', 'these', 'its', 'and', 'is', 'which', 'with', 'from', 'that', 'there', 'their'}
END_SMALL = {'and', 'are', 'the', 'of', 'to', 'was'}
FIRST_MAP = {'s': 'f', 'h': 'f', 'q': 'o', 'b': 'e', 'f': 's'}


EN_WORD = re.compile(r"\b[A-Za-z]{4,}\b")
_alpha = 'abcdefghijklmnopqrstuvwxyz'
_en_cache = {}


def _variant(a, b):
    # singular/plural or -al/-ar style variants are both valid; never swap them
    if a.rstrip('s') == b.rstrip('s'): return True
    for x, y in ((a, b), (b, a)):
        if x.startswith(y) and len(x) - len(y) <= 2: return True
    return False


def _en_fix(w):
    lw = w.lower()
    if lw in _en_cache: r = _en_cache[lw]
    else:
        r = None
        if not _known(lw):
            # 1) run-together with a small word: "Theyexhibit", "Antheridiaand", "toassociation"
            for i in range(2, len(lw) - 1):
                a, b = lw[:i], lw[i:]
                if (a in START_SMALL and ((len(b) >= 4 and _known(b)) or b in _SMALL)) or (b in END_SMALL and len(a) >= 4 and _known(a)):
                    r = a + ' ' + b; break
            # 2) first letter misread on capitalised words: Sungi -> Fungi, Hlagella -> Flagella, Quter -> Outer
            if r is None and w[0].isupper() and len(lw) >= 4 and lw[0] in FIRST_MAP:
                c = FIRST_MAP[lw[0]] + lw[1:]
                if c in EN_TEXT and _corpus[c] >= 2: r = c
            # 3) one-letter typo in a long lower-case word, into a word used in the typed textbooks
            if r is None and len(lw) >= 6 and w.islower() and _corpus[lw] <= 1:
                cands = set()
                for i in range(len(lw) + 1):
                    for c in _alpha:
                        cands.add(lw[:i] + c + lw[i + 1:]); cands.add(lw[:i] + c + lw[i:])
                    if i < len(lw): cands.add(lw[:i] + lw[i + 1:])
                good = sorted((c for c in cands if c in EN_TEXT and EN[c] >= 30 and c != lw and not _variant(c, lw)), key=lambda c: -EN[c])
                if good and (len(good) == 1 or EN[good[0]] >= 5 * EN[good[1]]): r = good[0]
        _en_cache[lw] = r
    if r is None: return w
    if w[0].isupper(): r = r[0].upper() + r[1:]
    return r


def _join_hyphen(m):
    a, b = m.group(1), m.group(2)
    j = (a + b).lower()
    return a + b if (j in EN or _corpus[j] >= 3) else a + '-' + b


def fix_english(text):
    text = re.sub(r'([A-Za-z]+)-\s*\n\s*([a-z]+)', _join_hyphen, text)      # word broken across lines
    text = re.sub(r'\b([A-Za-z]{2,})- ([a-z]{2,})\b', _join_hyphen, text)
    return EN_WORD.sub(lambda m: _en_fix(m.group(0)), text)


# OCR often puts a blank line inside a sentence (page layout, figures). Rejoin it when the line before
# does not end a sentence and the next line clearly continues it.
_JOIN = re.compile(r'([^\n]{15,}[^\s.?!:;)\]்])\n[ \t]*\n(?=[஀-௿a-z(])')


def fix(text, medium):
    text = fix_tamil(text) if medium == 'ta' else fix_english(text)
    for _ in range(2):
        text = _JOIN.sub(r'\1\n', text)
    return text
