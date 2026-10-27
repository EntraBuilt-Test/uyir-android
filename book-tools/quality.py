"""Score text quality: share of words found in the Tamil / English lexicons.
usage: quality.py [data_dir]   (default /home/claude/books/data)
Writes a per-book summary to stdout and per-page scores to <data_dir>/../quality_pages.tsv
"""
import json, re, sys, glob, os

D = sys.argv[1] if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else '/home/claude/books/data'
TA = re.compile(r'[஀-௿]+')
EN = re.compile(r"[A-Za-z]{3,}")


def load(p, minc):
    s = set()
    with open(p, encoding='utf-8') as f:
        for line in f:
            w, c = line.rstrip('\n').split('\t')
            if int(c) >= minc: s.add(w)
    return s


TAL = load('/home/claude/lex/ta_freq.tsv', 3)
ENL = load('/home/claude/lex/en_freq.tsv', 1)


def score(text, med):
    if med == 'ta':
        ws = [w for w in TA.findall(text) if len(w) >= 3]
        ok = sum(1 for w in ws if w in TAL)
    else:
        ws = [w.lower() for w in EN.findall(text)]
        ok = sum(1 for w in ws if w in ENL)
    return ok, len(ws)


def main():
    rows = []
    out = []
    for f in sorted(glob.glob(D + '/books/*.json')):
        b = json.load(open(f, encoding='utf-8'))
        tok = tot = 0
        for p in b['pages']:
            ok, n = score(p['t'], b['medium'])
            tok += ok; tot += n
            if n >= 30: out.append((b['id'], p['n'], p.get('pg'), p['u'], round(ok / n, 3), n))
        rows.append((b['id'], tot and tok / tot, tot))
    for r in rows:
        print(f'{r[0]:14} {r[1]*100:5.1f}%  of {r[2]} words')
    with open(os.path.join(D, '..', 'quality_pages.tsv'), 'w') as o:
        o.write('book\tpdf_page\tprinted_page\tchapter\tscore\twords\n')
        for r in sorted(out, key=lambda x: x[4]):
            o.write('\t'.join(map(str, r)) + '\n')


if __name__ == "__main__":
    main()
