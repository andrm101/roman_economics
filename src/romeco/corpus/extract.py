"""WP4.4 Candidate extraction (rule-based, deterministic, versioned).

Three extractors, each producing *candidates* (review_status = unreviewed):

* ``quantity``       number (arabic or Roman) + unit, incl. ranges and 'HS n million'
* ``ancient_cite``   literary loci (Plin. NH 6.102, Strabo 17.1.45, PME 49) and documentary
                     sigla (P.Oxy. XXXI 2766, O.Claud. II 245, BGU III 921, OGIS 674, ILS 2288)
* ``modern_cite``    author-date references (Rathbone 2009, 304; Cuvigny et al. 2011, p. 20)

Every candidate carries its anchor (pdf_page / printed page or page range / canonical locus),
character offsets within the unit, the extractor version, and a rule confidence. Rule
confidence is a property of the extraction, NOT of the evidence. Committed output
(``data/derived/corpus/extractions.csv``) includes a context snippet only when the rights
register permits redistribution of the text; otherwise it stores a hash of the snippet.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from romeco.corpus import parse as P
from romeco.corpus import registry as R

EXTRACTOR_VERSION = "0.2.0"   # see CHANGES in benchmark/README.md
OUT = R.ROOT / "data" / "derived" / "corpus"

# ---------------------------------------------------------------------------- numbers
NUM = r"(?:\d{1,3}(?:[,   ]\d{3})+|\d+)(?:[.,]\d+)?(?:\s?(?:¼|½|¾|1/4|1/2|3/4|1/3|2/3))?"
RANGE = rf"(?P<n1>{NUM})(?:\s?(?:[–\-—]|to|a|or|o|and|e)\s?(?P<n2>{NUM}))?"
FRAC = {"¼": .25, "½": .5, "¾": .75, "1/4": .25, "1/2": .5, "3/4": .75, "1/3": 1 / 3, "2/3": 2 / 3}


def to_number(s: str, lang: str) -> float | None:
    s = s.strip()
    frac = 0.0
    for k, v in FRAC.items():
        if s.endswith(k):
            frac, s = v, s[: -len(k)].strip()
            break
    s = s.replace(" ", "").replace(" ", "")
    if re.fullmatch(r"\d{1,3}(?:[ ,.]\d{3})+", s) and not re.fullmatch(r"\d{1,3}[.,]\d{1,2}", s):
        s = re.sub(r"[ ,.]", "", s)                       # thousands separators (1,200 / 1.200 / 1 200)
    elif lang == "it":
        s = s.replace(",", ".")                           # Italian decimal comma
    else:
        s = s.replace(",", "")
    try:
        return float(s) + frac
    except ValueError:
        return None


ROMAN_VAL = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman(s: str) -> int | None:
    s = s.upper()
    if not s or not re.fullmatch(r"M{0,3}(CM|CD|D?C{0,4})(XC|XL|L?X{0,4})(IX|IV|V?I{0,4})", s):
        return None
    tot = 0
    for a, b in zip(s, s[1:] + " "):
        v = ROMAN_VAL[a]
        tot += -v if b != " " and ROMAN_VAL.get(b, 0) > v else v
    return tot or None


# ---------------------------------------------------------------------------- units lexicon
UNITS = [  # (canonical unit, regex for the unit token following the number)
    ("km", r"km|kilomet(?:re|er)s?|chilometri|chilometro"),
    ("m3", r"m3|m³|cubic met(?:re|er)s?|metri cubi"),
    ("kg", r"kg|kilograms?|chilogrammi|chili"),
    ("tonne", r"tonnes?|tons?|tonnellate"),
    ("libra_roman", r"Roman (?:lbs?|pounds)|librae|libbre romane"),
    ("lb", r"lbs?\.?|pounds|libbre"),
    ("artaba", r"artabas?|artabai|artabe|artabe?"),
    ("drachma", r"drachmas?|drachmai|drachmae|dracme|dr\.?(?=\s|$|[,;)])"),
    ("obol", r"obols?|oboli"),
    ("talent", r"talents?|talenti"),
    ("mina", r"minae|minas|mine|mnai"),
    ("sestertius", r"sesterces|sestertii|sesterzi|sesterces"),
    ("denarius", r"denarii|denari|denarius"),
    ("day", r"days?|giorni|giorno|diebus|die"),
    ("month", r"months?|mesi|mese"),
    ("mile_roman", r"Roman miles|miglia romane|m\.p\.|mp|milia passuum|miglia|miles"),
    ("stade", r"stades|stadia|stadi"),
    ("camel", r"camels?|cammelli|cammello"),
    ("camel_load", r"camel[- ]loads?|carichi di cammello"),
    ("ship", r"ships|navi|vessels|nave"),
    ("legion", r"legions|legioni"),
    ("soldier", r"soldiers|soldati|men(?= )|uomini"),
    ("percent", r"%|per ?cent|percent|per cento"),
    ("hectare", r"ha\b|hectares|ettari"),
    ("keramion", r"keramia|keramion"),
    ("metretes", r"metretai|metretes"),
]
UNIT_RX = "|".join(f"(?P<u_{name}>{rx})" for name, rx in UNITS)
QTY = re.compile(rf"(?<![\w/])(?<!\d[.,]){RANGE}\s?(?:(?P<mult>million|milioni|m\b|thousand|mila)\s)?(?:{UNIT_RX})(?![\w])", re.I)
HS = re.compile(rf"(?<![\w])(?:HS|sesterces)\s?(?P<n1>{NUM})(?:\s?(?P<mult>million|milioni|m\b|bn|billion))?", re.I)
LAT_ROMAN_QTY = re.compile(r"(?<![\w])(?P<ov>\u203e)?(?P<r>[IVXLCDM]{1,})(?P=ov)?\s?(?P<u>p\.|passuum|diebus|die|stadia|naves)", re.U)
MULT = {"million": 1e6, "milioni": 1e6, "m": 1e6, "thousand": 1e3, "mila": 1e3, "bn": 1e9, "billion": 1e9}
LAT_UNIT = {"p.": "mile_roman", "passuum": "mile_roman", "diebus": "day", "die": "day", "stadia": "stade", "naves": "ship"}


EN_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
            "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
            "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000}
IT_WORDS = {"due": 2, "tre": 3, "quattro": 4, "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "nove": 9, "dieci": 10,
            "dodici": 12, "venti": 20, "trenta": 30, "cento": 100, "mille": 1000}
GRC_WORDS = {"δύο": 2, "τρεῖς": 3, "τρία": 3, "τριῶν": 3, "τέσσαρες": 4, "τέτταρες": 4, "τέσσαρα": 4, "πέντε": 5, "ἕξ": 6,
             "ἑπτά": 7, "ὀκτώ": 8, "ἐννέα": 9, "δέκα": 10, "δώδεκα": 12, "εἴκοσι": 20, "τριάκοντα": 30, "ἑκατόν": 100,
             "χίλιοι": 1000, "χίλια": 1000, "ἐννέα": 9}
GRC_UNITS = [("legion", r"τάγματ\w*|ταγμάτ\w*|τάγμα"), ("stade", r"στάδι\w*|σταδί\w*"), ("day", r"ἡμέρ\w*|ἡμερ\w*"),
             ("talent", r"τάλαντ\w*|ταλάντ\w*"), ("drachma", r"δραχμ\w*"), ("artaba", r"ἀρτάβ\w*"),
             ("camel", r"κάμηλ\w*|καμήλ\w*"), ("ship", r"πλοῖ\w*|πλοί\w*|ναῦς|νῆες|νεῶν")]
_EN_NUM = r"(?:(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[- ](?:one|two|three|four|five|six|seven|eight|nine))?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|(?:a |one )?hundred|(?:a |one )?thousand)"
WORD_QTY_EN = re.compile(rf"(?<![\w-])(?P<w1>{_EN_NUM})(?:\s(?:or|to|and)\s(?P<w2>{_EN_NUM}))?\s(?:{UNIT_RX})(?:['’]s?)?(?![\w])", re.I)
WORD_QTY_IT = re.compile(rf"(?<![\w])(?P<w1>{'|'.join(IT_WORDS)})(?:\s(?:o|e|a)\s(?P<w2>{'|'.join(IT_WORDS)}))?\s(?:{UNIT_RX})(?![\w])", re.I)
GRC_QTY = re.compile(rf"(?<![\w])(?P<w>{'|'.join(GRC_WORDS)})(?P<gap>(?:\s+\S+){{0,4}}?)\s+(?:{'|'.join(f'(?P<g_{k}>{rx})' for k, rx in GRC_UNITS)})")


def _en_word(w: str) -> float | None:
    w = w.lower().replace("a ", "").replace("one hundred", "hundred").replace("one thousand", "thousand")
    parts = re.split(r"[- ]", w)
    tot = 0
    for p_ in parts:
        if p_ not in EN_WORDS:
            return None
        tot += EN_WORDS[p_]
    return float(tot)


def quantities(text: str, lang: str) -> list[dict]:
    out = []
    word_rx = {"en": WORD_QTY_EN, "it": WORD_QTY_IT}.get(lang)
    if word_rx is not None:
        conv = _en_word if lang == "en" else (lambda w: float(IT_WORDS[w.lower()]) if w.lower() in IT_WORDS else None)
        for m in word_rx.finditer(text):
            unit = next(k[2:] for k, v in m.groupdict().items() if k.startswith("u_") and v)
            v1 = conv(m.group("w1"))
            v2 = conv(m.group("w2")) if m.group("w2") else None
            if v1 is None or unit in ("soldier",):          # 'two men' is too ambiguous in prose
                continue
            out.append(dict(kind="quantity", start=m.start(), end=m.end(), raw=m.group(0), unit=unit,
                            value_low=v1, value_high=v2 if v2 is not None else v1, rule="WORD", conf=0.6))
    if lang == "grc":
        for m in GRC_QTY.finditer(text):
            unit = next(k[2:] for k, v in m.groupdict().items() if k.startswith("g_") and v)
            v = float(GRC_WORDS[m.group("w")])
            out.append(dict(kind="quantity", start=m.start(), end=m.end(), raw=m.group(0), unit=unit,
                            value_low=v, value_high=v, rule="GRC_WORD", conf=0.5))
    for m in QTY.finditer(text):
        unit = next(k[2:] for k, v in m.groupdict().items() if k.startswith("u_") and v)
        v1 = to_number(m.group("n1"), lang)
        v2 = to_number(m.group("n2"), lang) if m.group("n2") else None
        mult = MULT.get((m.group("mult") or "").lower(), 1)
        if v1 is None or (unit in ("day", "month") and v1 > 3000):
            continue
        conf = 0.9 if unit not in ("soldier", "day", "drachma") else 0.7
        out.append(dict(kind="quantity", start=m.start(), end=m.end(), raw=m.group(0), unit=unit,
                        value_low=v1 * mult, value_high=(v2 if v2 is not None else v1) * mult, rule="QTY", conf=conf))
    for m in HS.finditer(text):
        v = to_number(m.group("n1"), lang)
        if v is None:
            continue
        mult = MULT.get((m.group("mult") or "").lower(), 1)
        out.append(dict(kind="quantity", start=m.start(), end=m.end(), raw=m.group(0), unit="sestertius",
                        value_low=v * mult, value_high=v * mult, rule="HS", conf=0.9))
    if lang == "la":
        for m in LAT_ROMAN_QTY.finditer(text):
            v = roman(m.group("r"))
            if not v or (len(m.group("r")) == 1 and m.group("r") not in "IVX"):
                continue
            unit = LAT_UNIT[m.group("u")]
            rule, conf = "LAT_ROMAN", 0.8
            if unit == "mile_roman" and m.group("u") == "p.":
                # Pliny's geographical books give distances in milia passuum ('N p.'). The Perseus TEI marks
                # overlines inconsistently, so: overlined -> milia passuum; plain M-built numeral ('MM p.')
                # -> passus (/1000); other plain numerals -> milia passuum (default), flagged for review.
                if not m.group("ov") and "M" in m.group("r"):
                    v, rule = v / 1000, "LAT_ROMAN_PASSUS"
                elif not m.group("ov"):
                    rule, conf = "LAT_ROMAN_MP_DEFAULT", 0.6
            out.append(dict(kind="quantity", start=m.start(), end=m.end(), raw=m.group(0),
                            unit=unit, value_low=v, value_high=v, rule=rule, conf=conf))
    # de-duplicate overlaps (keep longest)
    out.sort(key=lambda d: (d["start"], -(d["end"] - d["start"])))
    keep, last_end = [], -1
    for d in out:
        if d["start"] >= last_end:
            keep.append(d)
            last_end = d["end"]
    return keep


# ---------------------------------------------------------------------------- ancient citations
AUTHORS = [  # (canonical key, regex for author/work prefix)
    ("plin.nh", r"(?:Plin(?:y|io)?\.?(?: the Elder| il Vecchio)?|Plinio)\s*,?\s*(?:N\.?\s?H\.?|H\.?\s?N\.?|Nat\.?\s?Hist\.?|Naturalis Historia)"),
    ("strabo", r"Strab(?:o|one|\s?\.)|Str\s?\."),
    ("pme", r"PME|Peripl(?:us|\.)(?: Maris Erythraei| M\. Rubr\.)?"),
    ("joseph.bj", r"Joseph(?:us|\.)\s*,?\s*(?:BJ|B\.J\.|Bell\.\s?Iud\.)"),
    ("joseph.aj", r"Joseph(?:us|\.)\s*,?\s*(?:AJ|A\.J\.|Ant\.)"),
    ("tac.ann", r"Tac(?:itus|\.)\s*,?\s*Ann\.?"),
    ("tac.hist", r"Tac(?:itus|\.)\s*,?\s*Hist\.?"),
    ("dio", r"(?:Cass(?:ius|\.)\s)?Dio"),
    ("diod", r"Diod(?:orus|\.)(?: Sic(?:ulus|\.))?"),
    ("ptol.geog", r"(?:Ptol(?:emy|emaeus|em\.|\.)|Tolomeo)\s*,?\s*Geog(?:raphy|\.)?"),
    ("gaius.inst", r"Gaius\s*,?\s*Inst\.?"),
    ("dig", r"Dig\.|Digest"),
    ("philostr.vs", r"Philostr(?:atus|\.)\s*,?\s*VS"),
    ("ael.arist", r"Ael\.\s?Arist\.?(?:\s*,?\s*Aeg\.?)?"),
    ("aelian.ha", r"Aelian\s*,?\s*HA"),
    ("veg", r"Veg(?:etius|\.)"),
    ("ed.diocl", r"Ed(?:ict(?:um)?)?\.?\s?Diocl\.?"),
]
LOCUS = r"(?P<book>[IVXLC]+|\d{1,3})(?:\s?[.,]\s?(?P<c>\d{1,3}[a-z]?))?(?:\s?[.,]\s?(?P<s>\d{1,3}[a-z]?))?"
ANC = re.compile("|".join(f"(?P<a_{k.replace('.', '_')}>{rx})\\s*,?\\s*{LOCUS.replace('?P<', f'?P<{k.replace(chr(46), chr(95))}_')}"
                          for k, rx in AUTHORS))
DOC_SERIES = r"(?:P\.\s?(?:Oxy|Vindob\.\s?G|Lond|Mich|Giss|Fay|Grenf|Heid|Wisc|Customs|Yale|Ryl|Tebt|Amh|Cair\.\s?Zen|Ross\.\s?Georg|Hamb|Quseir|Kron|Petrie|Hib|Mil\.\s?Vogl|Bingen|Sijp|Princ|Col|Cair\.\s?Masp|Lips|Strasb|Flor|Brem|Bad)\.?|PSI|Chr(?:est)?\.\s?W\.|W\.\s?Chr(?:est)?\.|O\.\s?(?:Claud|Ber(?:enike)?|Petr(?:\.\s?Mus)?|Did|Krok|Max|Flor|Bodl|Wilck|Stras|Amst|Blemmyes)\.?|SB|BGU|ILS|CIL|OGIS|I\.\s?Portes|I\.\s?Pan|I\.\s?Koptos|AE|SEG|IGRR|W\.\s?Chr\.|M\.\s?Chr\.|WO|Sel\.\s?Pap\.)"
DOC = re.compile(rf"(?<![\w])(?P<series>{DOC_SERIES})\s?(?P<vol>[IVXL]+(?=,?\s\d)|\d{{1,4}}(?=[.]\d|\s\d))?(?:,|\.)?\s?(?P<num>\d{{1,6}})(?:\s?(?P<suf>[a-z]|recto|verso|r|v)\b)?")


def _norm_series(s: str) -> str:
    k = re.sub(r"[\s.]", "", s).lower()
    return {"chrestw": "wchr", "chrw": "wchr", "wchrest": "wchr"}.get(k, k)


def ancient_cites(text: str) -> list[dict]:
    out = []
    for m in ANC.finditer(text):
        gd = m.groupdict()
        key = next(k[2:] for k, v in gd.items() if k.startswith("a_") and v)
        b, c, s = gd.get(f"{key}_book"), gd.get(f"{key}_c"), gd.get(f"{key}_s")
        if b is None:
            continue
        book = str(roman(b) or b) if re.fullmatch(r"[IVXLC]+", b) else b
        locus = ".".join(x for x in (book, c, s) if x)
        if key == "dio" and not c:            # bare 'Dio 55' is too ambiguous
            continue
        out.append(dict(kind="ancient_cite", start=m.start(), end=m.end(), raw=m.group(0),
                        norm_key=f"{key.replace('_', '.')}:{locus}", rule="ANC", conf=0.85))
    CONT = re.compile(r"\s?(?:,|;|and|e|et)\s(?P<b>\d{1,3})\s?[.,]\s?(?P<c>\d{1,3})(?:\s?[.,]\s?(?P<s>\d{1,3}))?")
    for prev in list(out):
        m2 = CONT.match(text, prev["end"])
        if m2 and prev["norm_key"].split(":")[0] in ("strabo", "plin.nh", "pme", "joseph.bj", "tac.ann", "dio", "diod"):
            loc = ".".join(x for x in (m2.group("b"), m2.group("c"), m2.group("s")) if x)
            out.append(dict(kind="ancient_cite", start=m2.start(), end=m2.end(), raw=m2.group(0).strip(),
                            norm_key=f"{prev['norm_key'].split(':')[0]}:{loc}", rule="ANC_CONT", conf=0.6))
    for m in DOC.finditer(text):
        vol = m.group("vol")
        volv = str(roman(vol)) if vol and re.fullmatch(r"[IVXL]+", vol) else (vol or "")
        key = f"{_norm_series(m.group('series'))}:{volv + ':' if volv else ''}{m.group('num')}"
        out.append(dict(kind="ancient_cite", start=m.start(), end=m.end(), raw=m.group(0), norm_key=key,
                        rule="DOC", conf=0.85 if vol or m.group("series").startswith(("P.", "O.")) else 0.7))
    return out


# ---------------------------------------------------------------------------- modern author-date citations
SURNAME = r"(?:[A-Z][a-zà-ÿ'’\-]+(?:\s(?:de|De|van|Van|von|der|Der|di|Di)\s[A-Z][a-zà-ÿ'’\-]+)?|[A-Z][a-z]+\s[A-Z][a-z]+)"
MODERN = re.compile(rf"(?<![\w])(?P<auth>{SURNAME}(?:\s(?:et al\.|e|and|&)\s?{SURNAME}?)?)\s\(?(?P<year>1[89]\d\d|20[0-3]\d)(?P<suf>[a-z])?\)?(?:\s?[,:]\s?(?:p{{1,2}}\.\s?)?(?P<pages>\d{{1,4}}(?:\s?[–\-]\s?\d{{1,4}})?))?")
STOP_AUTH = {"In", "The", "See", "Cfr", "AD", "Ad", "BC", "Fig", "Table", "Nel", "Dal", "Sul", "Nella", "Anno", "Nero",
             "Per", "Tra", "Dopo", "Prima", "Since", "From", "In the", "After", "Before", "Until"}


def modern_cites(text: str) -> list[dict]:
    out = []
    for m in MODERN.finditer(text):
        a = m.group("auth").strip()
        if a.split()[0] in STOP_AUTH:
            continue
        surname = re.sub(r"\s(?:et al\.|e|and|&).*$", "", a)
        out.append(dict(kind="modern_cite", start=m.start(), end=m.end(), raw=m.group(0),
                        norm_key=f"{surname.lower()}:{m.group('year')}{m.group('suf') or ''}",
                        pages=m.group("pages") or "", rule="AUTHDATE", conf=0.6))
    return out


# ---------------------------------------------------------------------------- driver
FIELDS = ["ext_id", "item_id", "source_id", "unit_ref", "pdf_page", "printed_page", "page_low", "page_high",
          "locus", "route", "kind", "rule", "raw", "unit", "value_low", "value_high", "norm_key", "pages",
          "start", "end", "snippet", "snippet_sha1", "conf", "extractor_version", "review_status"]


def unit_ref(u: dict) -> str:
    if u.get("locus") or u.get("cts_ref"):
        return u.get("locus") or u["cts_ref"]
    if u.get("pdf_page"):
        return f"pdf:{u['pdf_page']}"
    return f"p:{u.get('page_low')}-{u.get('page_high')}" if u.get("printed_page") is None else f"p:{u['printed_page']}"


def extract_unit(text: str, lang: str) -> list[dict]:
    return quantities(text, lang) + ancient_cites(text) + modern_cites(text)


def extract_item(item: dict) -> list[dict]:
    redistribute = item["redistribute_text"] == "yes"
    rows = []
    for k, u in enumerate(P.units(item["item_id"])):
        if u.get("route") == "pdf_ocr":
            continue                                   # OCR units are for the benchmark only
        text = u.get("text", "")
        for j, c in enumerate(extract_unit(text, item["language"])):
            snip = text[max(0, c["start"] - 60): c["end"] + 60].replace("\n", " ")
            rows.append(dict(
                ext_id=f"EXT-{item['item_id'][4:]}-{k:05d}-{j:03d}", item_id=item["item_id"], source_id=item["source_id"],
                unit_ref=unit_ref(u), pdf_page=u.get("pdf_page") or "", printed_page=u.get("printed_page") or "",
                page_low=u.get("page_low") or "", page_high=u.get("page_high") or "", locus=u.get("locus") or u.get("cts_ref") or "",
                route=u.get("route", ""), kind=c["kind"], rule=c["rule"], raw=c["raw"], unit=c.get("unit", ""),
                value_low=c.get("value_low", ""), value_high=c.get("value_high", ""), norm_key=c.get("norm_key", ""),
                pages=c.get("pages", ""), start=c["start"], end=c["end"],
                snippet=snip if redistribute else "", snippet_sha1=hashlib.sha1(snip.encode()).hexdigest(),
                conf=c["conf"], extractor_version=EXTRACTOR_VERSION, review_status="unreviewed"))
    return rows


def extract_all(only: list[str] | None = None) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    allrows, summary = [], []
    for it in R.read("items.csv"):
        if only and it["source_id"] not in only:
            continue
        if not (P.INTERIM / it["item_id"] / "units.jsonl").exists():
            continue
        rows = extract_item(it)
        allrows += rows
        R.set_state(it["source_id"], "extracted")
        kinds = {k: sum(r["kind"] == k for r in rows) for k in ("quantity", "ancient_cite", "modern_cite")}
        summary.append(dict(item_id=it["item_id"], source_id=it["source_id"], route=it["parse_route"], **kinds))
    with open(OUT / "extractions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(allrows)
    with open(OUT / "extraction_summary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    return dict(rows=len(allrows), items=len(summary))
