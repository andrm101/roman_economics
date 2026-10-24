"""WP4.5 Discovery by backward citation chaining (offline: Crossref/OpenAlex are not reachable here).

1. Detect bibliography pages by the density of entry-like lines (not by per-book rules).
2. Segment entries; fill '——' ditto authors; parse first author, year, title, container.
3. Cluster entries across citing documents (surname + year + title similarity) into candidate works.
4. Match candidates to ``registers/source_register.csv`` (rapidfuzz token-set similarity).
5. Resolve in-text author-date citations (romeco.corpus.extract.modern_cites) against each document's
   own bibliography: a citation-resolution rate per document.

Outputs (committed; bibliographic metadata only):
``registers/corpus/discovery_candidates.csv`` and ``data/derived/corpus/citation_resolution.csv``.
A discovered work is NOT acquired or read: state = discovered (screening is a human decision).
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict

from rapidfuzz import fuzz

from romeco.corpus import extract as E
from romeco.corpus import parse as P
from romeco.corpus import registry as R

DISCOVERY_VERSION = "0.1.0"
ENTRY_START = re.compile(
    r"^\s*(?:\d{1,3}\.\s+)?(?:(?P<ditto>[—–\-]{2,3})|(?P<sur>(?:(?:de|De|van|Van|von|di|Di|du|Du|le|Le|el|al-)\s)?"
    r"[A-ZÀ-Ý][A-Za-zà-ÿ'’\-]+(?:\s[A-ZÀ-Ý][A-Za-zà-ÿ'’\-]+)?),\s+(?:[A-ZÀ-Ý]\.|[A-ZÀ-Ý][a-zà-ÿ]+\b))")
YEAR = re.compile(r"(?<!\d)(1[5-9]\d\d|20[0-3]\d)(?P<suf>[a-z])?(?!\d)")
QUOTE = re.compile(r"[‘“'\"«](?P<t>[^’”'\"»]{5,250})[’”'\"»]")


def fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


def bib_units(units: list[dict]) -> list[int]:
    out = []
    for i, u in enumerate(units):
        lines = [l for l in u.get("text", "").splitlines() if l.strip()]
        if len(lines) < 5:
            continue
        starts = sum(bool(ENTRY_START.match(l)) for l in lines)
        years = sum(bool(YEAR.search(l)) for l in lines)
        if starts / len(lines) >= 0.22 and years / len(lines) >= 0.25:
            out.append(i)
    return out


def segment(text: str) -> list[str]:
    entries, cur = [], []
    for l in text.splitlines():
        if not l.strip():
            continue
        if ENTRY_START.match(l):
            if cur:
                entries.append(" ".join(cur))
            cur = [l.strip()]
        elif cur:
            cur.append(l.strip())
    if cur:
        entries.append(" ".join(cur))
    return [re.sub(r"\s+", " ", e) for e in entries]


_SUR = r"(?:(?:de|De|van|Van|von|di|Di|du|Du|le|Le|al-)\s)?[A-ZÀ-Ý][\wÀ-ÿ'’\-]+(?:\s[A-ZÀ-Ý][\wÀ-ÿ'’\-]+)?"
_INI = r"(?:[A-ZÀ-Ý][a-z]?\.\s?-?)+"
_CO = rf"(?:(?:,\s(?:and\s|e\s|&\s)?|\s?(?:and|e|&)\s)(?:{_INI}\s?{_SUR}|{_SUR},\s?{_INI}))"
AUTH_BLOCK = re.compile(rf"^(?P<a>{_SUR},\s{_INI}(?:{_CO})*)")


def parse_entry(e: str, prev_author: str) -> dict | None:
    """Two families: author-date ('Surname, I. (YYYY). Title...' / 'Surname, I. YYYY. Title...') and
    title-first ('Surname, I., Title (City, YYYY)' / 'Surname, I. Title. Journal 12, 3-4 (YYYY).')."""
    e = re.sub(r"^\d{1,3}\.\s+", "", e).strip()
    m = ENTRY_START.match(e)
    if not m:
        return None
    if m.group("ditto"):
        authors, rest = prev_author, e[m.end("ditto"):].strip(" .,")
    else:
        a = AUTH_BLOCK.match(e)
        authors = a.group("a").strip(" ,.") if a else m.group("sur")
        rest = e[a.end():] if a else e[m.end():]
    if not YEAR.search(e):
        return None
    rest = rest.lstrip(" .,")
    lead = re.match(r"^\(?(1[5-9]\d\d|20[0-3]\d)([a-z])?\)?[.,:]?\s*", rest)
    if lead:                                            # author-date family
        year = lead.group(1) + (lead.group(2) or "")
        body = rest[lead.end():]
    else:                                               # title-first family: year is the last one in the entry
        ys = list(YEAR.finditer(rest)) or list(YEAR.finditer(e))
        year = ys[-1].group(1) + (ys[-1].group("suf") or "")
        body = rest
    q = QUOTE.match(body.strip()) or (QUOTE.search(body) if body.strip()[:1] in "‘“'\"«" else None)
    if q:
        title = q.group("t")
    else:
        title = re.split(r"\.\s|\s\(|,\s(?=[A-Z][a-z]+\s\d)|\.$", body, maxsplit=1)[0]
    first = re.split(r",|\se\s|\sand\s|&", authors)[0].strip()
    return dict(first_author=first, authors=authors[:200], year=year, title=title.strip(" .,")[:300], raw=e[:500])


def discover() -> dict:
    src = R.sources()
    reg = [(sid, fold(r.get("creators", "")), r.get("year", ""), fold(r.get("title", ""))) for sid, r in src.items()]
    per_doc, entries = {}, []
    for it in R.read("items.csv"):
        if it["parse_route"] not in ("pdf_text_layer", "flattened_text"):
            continue
        us = [u for u in P.units(it["item_id"]) if u.get("route") != "pdf_ocr"]
        idx = bib_units(us)
        prev, n = "", 0
        for i in idx:
            for e in segment(us[i]["text"]):
                d = parse_entry(e, prev)
                if not d:
                    continue
                prev = d["authors"]
                d.update(cited_in=it["source_id"], unit=E.unit_ref(us[i]))
                entries.append(d)
                n += 1
        per_doc[it["source_id"]] = dict(bib_pages=len(idx), entries=n)
    # cluster across documents
    clusters: list[dict] = []
    for d in entries:
        key_s, key_t = fold(d["first_author"]), fold(d["title"])
        hit = next((c for c in clusters if c["sur"] == key_s and c["year"][:4] == d["year"][:4]
                    and fuzz.token_set_ratio(c["tit"], key_t) >= 85), None)
        if hit:
            hit["cited_in"].add(d["cited_in"])
            hit["n"] += 1
        else:
            clusters.append(dict(sur=key_s, year=d["year"], tit=key_t, d=d, cited_in={d["cited_in"]}, n=1))
    rows = []
    for k, c in enumerate(clusters):
        best, score = "", 0
        for sid, cre, yr, tit in reg:
            if yr and yr[:4] == c["year"][:4] and c["sur"] and c["sur"] in cre:
                s = fuzz.token_set_ratio(c["tit"], tit)
                if s > score:
                    best, score = sid, s
        matched = best if score >= 80 else ""
        rows.append(dict(cand_id=f"DSC-{k + 1:05d}", first_author=c["d"]["first_author"], authors=c["d"]["authors"],
                         year=c["year"], title=c["d"]["title"], cited_in="; ".join(sorted(c["cited_in"])),
                         n_citing_docs=len(c["cited_in"]), n_entries=c["n"], example_raw=c["d"]["raw"],
                         matched_source_id=matched, match_score=score if matched else "",
                         state="already_registered" if matched else "discovered", discovery_version=DISCOVERY_VERSION))
    R.write("discovery_candidates.csv", rows, list(rows[0]))
    # citation resolution: in-text author-date keys vs the same document's bibliography
    bykey = defaultdict(set)
    for d in entries:
        bykey[d["cited_in"]].add(f"{fold(d['first_author']).split()[-1]}:{d['year']}")
    res = []
    for r in csv.DictReader(open(E.OUT / "extractions.csv", encoding="utf-8")):
        if r["kind"] != "modern_cite" or r["source_id"] not in per_doc:
            continue
        sur, yr = r["norm_key"].rsplit(":", 1)
        res.append((r["source_id"], f"{fold(sur).split()[-1]}:{yr}" in bykey[r["source_id"]]))
    summ = []
    for sid, info in per_doc.items():
        rs = [ok for s, ok in res if s == sid]
        summ.append(dict(source_id=sid, bib_pages=info["bib_pages"], bib_entries=info["entries"],
                         intext_author_date=len(rs), resolved=sum(rs),
                         resolution_rate=round(sum(rs) / len(rs), 3) if rs else ""))
    with open(E.OUT / "citation_resolution.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summ[0]))
        w.writeheader()
        w.writerows(summ)
    return dict(entries=len(entries), candidates=len(rows), already_registered=sum(bool(r["matched_source_id"]) for r in rows),
                multi_cited=sum(r["n_citing_docs"] > 1 for r in rows), per_doc=summ)
