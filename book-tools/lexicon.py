"""Build Tamil + English word-frequency lexicons for OCR scoring and correction.

Tamil sources: Tamil Wikipedia + Project Madurai text (open-tamil), open-tamil word lists,
and the clean (text-layer) Std 3-7 Tamil textbooks.
English sources: open-tamil English dictionary words + clean English textbooks (text layer).
Output: lex/ta_freq.tsv, lex/en_freq.tsv  (word<TAB>count)
"""
import re, collections, glob, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from clean import clean_ta, clean_common

L = '/home/claude/lex'
OT = '/home/claude/ext/ot'
TXT = '/home/claude/books/txt'
TA = re.compile(r'[஀-௿]+')
EN = re.compile(r"[A-Za-z][a-z]+")


def ta_tokens(s):
    return [w for w in TA.findall(s) if len(w) >= 2]


ta = collections.Counter()
for f in glob.glob(L + '/TaWiktionary/*/*.txt'):
    with open(f, encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            ta.update(ta_tokens(line))
for f in [OT + '/examples/speller/out-tamil-words.txt', OT + '/solthiruthi/data/tamilvu_dictionary_words.txt']:
    for w in open(f, encoding='utf-8', errors='ignore').read().split():
        for t in ta_tokens(w):
            ta[t] += 1
# clean textbooks count a lot: they are the exact register we need
for f in glob.glob(TXT + '/Class_[3-7]_*Tamil*.txt'):
    for t in ta_tokens(clean_ta(open(f, encoding='utf-8', errors='replace').read())):
        ta[t] += 20

en = collections.Counter()
for w in open(OT + '/solthiruthi/data/english_dictionary_words.txt', encoding='utf-8', errors='ignore').read().split():
    if w.isalpha(): en[w.lower()] += 1
for f in glob.glob(TXT + '/*English*.txt'):
    if os.path.getsize(f) < 20000: continue   # scanned books have no text layer
    for t in EN.findall(open(f, encoding='utf-8', errors='replace').read()):
        en[t.lower()] += 20

with open(L + '/ta_freq.tsv', 'w', encoding='utf-8') as o:
    for w, c in ta.most_common():
        if c >= 2: o.write(f'{w}\t{c}\n')
with open(L + '/en_freq.tsv', 'w', encoding='utf-8') as o:
    for w, c in en.most_common():
        o.write(f'{w}\t{c}\n')
print('tamil words', sum(1 for w, c in ta.items() if c >= 2), 'english words', len(en))
