import re,unicodedata
C='க-ஹ'; V='ா-்'
def fix_visual(s):
    # vowel signs typed before their consonant (visual order) -> logical order
    s=re.sub('(?<![\u0B95-\u0BB9])\u0BC6([\u0B95-\u0BB9])\u0BBE','\\1\u0BCA',s)
    s=re.sub('(?<![\u0B95-\u0BB9])\u0BC7([\u0B95-\u0BB9])\u0BBE','\\1\u0BCB',s)
    s=re.sub('(?<![\u0B95-\u0BB9])\u0BC6([\u0B95-\u0BB9])\u0BD7','\\1\u0BCC',s)
    s=re.sub('(?<![\u0B95-\u0BB9])([\u0BC6\u0BC7\u0BC8])([\u0B95-\u0BB9])','\\2\\1',s)
    return s
def clean_ta(s):
    s=s.replace('‌','').replace('‍','')
    s=re.sub('�['+V+']','',s); s=s.replace('�','')
    s=re.sub('்்(['+C+'])\\1(?=['+V+'])','்\\1',s)
    s=re.sub('்+','்',s)
    s=fix_visual(s)
    return s
def clean_common(s):
    s=re.sub('[\x80-\x9f]','•',s); s=re.sub(r'¾¾\s*|^¾\s+','• ',s,flags=re.M)
    s=s.replace('\ufffd','')
    s=s.replace('\u00ad',''); s=re.sub('[\ue000-\uf8ff]','•',s)
    s=re.sub(r'[^\n]*\.indd[^\n]*','',s)
    s=re.sub(r'^\s*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\s+\d{1,2}[:.]\d{2}[:.]\d{2}.*$','',s,flags=re.M)
    s=re.sub(r'[ \t]+',' ',s)
    s=re.sub(r'\n{3,}','\n\n',s)
    return s.strip()
