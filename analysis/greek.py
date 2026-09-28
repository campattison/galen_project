"""Greek word-form utilities for the corrected rarity measure.

Diorisis stores each word form in Beta Code (<word form="...">) and its lemma in
Unicode (<lemma entry="...">). To look up a form from Galen in Diorisis, both sides
are converted to one canonical Beta Code: lower case, grave accent written as acute,
diacritics in a fixed order after their letter, final/lunate sigma and capitals
normalised. A second, "bare" key (letters and apostrophe only) is the fallback.

Nothing here is random, and no step depends on set or dict iteration order.
"""
import csv
import unicodedata

LETTERS = {'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'h', 'θ': 'q',
           'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'c', 'ο': 'o', 'π': 'p',
           'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'u', 'φ': 'f', 'χ': 'x', 'ψ': 'y',
           'ω': 'w', 'ϲ': 's', 'ϝ': 'v', 'ϐ': 'b', 'ϑ': 'q', 'ϕ': 'f', 'ϖ': 'p', 'ϛ': 's'}
COMBINING = {'̓': ')', '̔': '(', '́': '/', '̀': '/', '͂': '=',
             'ͅ': '|', '̈': '+', '̓': ')'}
APOSTROPHES = {'’', "'", 'ʼ', '᾽', '᾿'}
# Greek numeral sign, tonos, modifier prime, acute: used both as the numeral keraia
# (ι΄ = 10) and, after an accented word, as an elision mark (ὑπ΄ = ὑπ’).
KERAIA = 'ʹ΄ʹ´'
DIACRITIC_ORDER = ')(/=|+'

# Weight and measure abbreviations in Comp., expanded to their lemma.
ABBREVIATIONS = {'δραχ': 'δραχμή', 'δρ': 'δραχμή', 'ξε': 'ξέστης', 'οὐγγ': 'οὐγγία',
                 'λίτρ': 'λίτρα', 'κοτ': 'κοτύλη'}

RHO_PSILI, RHO_DASIA = 'ῤ', 'ῥ'   # ῤ ῥ (Kühn's spelling of -ρρ-)


def to_beta(token):
    """Unicode Greek -> Beta Code (letters, diacritics, apostrophe; keraia -> '#')."""
    out = []
    for ch in unicodedata.normalize('NFD', token.lower()):
        if ch in LETTERS:
            out.append(LETTERS[ch])
        elif ch in COMBINING:
            out.append(COMBINING[ch])
        elif ch in APOSTROPHES:
            out.append("'")
        elif ch in KERAIA:
            out.append('#')
    return ''.join(out)


def canon_beta(s):
    """Canonical Beta Code: lower case, grave -> acute, diacritics sorted per letter.
    Accepts Diorisis Beta Code ('*' marks a capital, digits mark sigma variants)."""
    s = s.replace('\\', '/')
    letters, pending, i = [], None, 0
    while i < len(s):
        c = s[i]
        if c == '*':
            pending = set()
            i += 1
            continue
        if c in DIACRITIC_ORDER:
            if pending is not None:
                pending.add(c)
            elif letters:
                letters[-1][1].add(c)
            i += 1
            continue
        if c.isalpha():
            c = c.lower()
            letters.append([c, pending if pending is not None else set()])
            pending = None
            i += 1
            if c == 's' and i < len(s) and s[i].isdigit():
                i += 1
            continue
        if c in "'#":
            letters.append([c, set()])
        i += 1
    return ''.join(l + ''.join(sorted(d, key=DIACRITIC_ORDER.index)) for l, d in letters)


def bare(c):
    """Letters and apostrophe only (drops accents and breathings)."""
    return ''.join(ch for ch in c if ch.isalpha() or ch == "'")


def norm_lemma(x):
    """Lemma key for exact-but-forgiving matching: grave -> acute, NFC, lower case."""
    x = unicodedata.normalize('NFD', x).replace('̀', '́')
    return unicodedata.normalize('NFC', x).lower()


def has_greek_letter(w):
    return any(unicodedata.category(ch).startswith('L') and
               ('Ͱ' <= ch <= 'Ͽ' or 'ἀ' <= ch <= '῿') for ch in w)


def classify(word):
    """symbol (no Greek letter, e.g. Latin numerals or a stray ano teleia),
    numeral (letters + keraia, no accents: ι΄, ιβ΄), abbreviation, or word."""
    if not has_greek_letter(word):
        return 'symbol'
    core = word.rstrip(KERAIA)
    if core != word and len(core) <= 4 and all(
            unicodedata.category(c) != 'Mn' for c in unicodedata.normalize('NFD', core)):
        return 'numeral'
    if word in ABBREVIATIONS:
        return 'abbreviation'
    return 'word'


def lookup_key(word):
    """Canonical Beta Code used to look a word up in Diorisis. A keraia after an
    accented word is an elision mark, so ὑπ΄ is looked up as ὑπ’."""
    if word and word[-1] in KERAIA:
        word = word.rstrip(KERAIA) + '’'
    return canon_beta(to_beta(word))


def read_stanza_tokens(path, merge=True):
    """Tokens counted in the original measure (Stanza UPOS != PUNCT), in file order.
    With merge=True, Stanza's ῤ|ῥ splits are re-joined (αἱμοῤ + ῥοΐδας -> αἱμοῤῥοΐδας);
    merge=False returns the tokens exactly as the original measure counted them.

    Returns a list of dicts: text, chunk, word_index, word, upos, stanza_lemma,
    stanza_freq, kind, merged (bool).
    """
    with open(path, encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh))
    counted = [r for r in rows if r['counted_in_metric'] == 'True']
    out, skip = [], set()
    for k, r in enumerate(counted):
        if k in skip:
            continue
        tok = dict(text=r['text'], chunk=int(r['chunk']), word_index=int(r['word_index']),
                   word=r['word'], upos=r['upos'], stanza_lemma=r['lemma'],
                   stanza_freq=int(r['diorisis_freq']), merged=False)
        nxt = counted[k + 1] if k + 1 < len(counted) else None
        if (merge and nxt is not None and nxt['text'] == r['text'] and nxt['chunk'] == r['chunk']
                and int(nxt['word_index']) == tok['word_index'] + 1
                and unicodedata.normalize('NFC', r['word']).endswith(RHO_PSILI)
                and unicodedata.normalize('NFC', nxt['word']).startswith(RHO_DASIA)):
            tok['word'] = r['word'] + nxt['word']
            tok['stanza_lemma'] = r['lemma'] + '+' + nxt['lemma']
            tok['stanza_freq'] = 0          # the halves' lemmas are artefacts of the split
            tok['merged'] = True
            skip.add(k + 1)
        tok['kind'] = classify(tok['word'])
        out.append(tok)
    return out


def needed_keys(tokens):
    """Canonical and bare lookup keys for every word token (sorted, deterministic)."""
    full = sorted({lookup_key(t['word']) for t in tokens if t['kind'] == 'word'})
    return full, sorted({bare(c) for c in full})
