"""WP4.3 Parsing into page- or locus-anchored units.

Every unit records where it is in the source:

* PDFs (``pdf_text_layer``): one unit per PDF page; ``printed_page`` from running heads/folios with a
  fitted constant offset; ``label_method`` = detected | inferred_from_offset | none.
* OCR (``pdf_ocr``): same anchors, text from tesseract on a 300-dpi rasterisation, with mean word
  confidence (parser confidence, NOT evidence reliability).
* Flattened text (``flattened_text``): pages recovered from the longest monotone chain of folio
  lines; folio placement (closes vs opens a page) chosen by agreement with the printed contents list,
  and the agreement rate is reported as the page-anchor validation.
* TEI (``tei_cts`` / ``tei_milestone``): one unit per canonical locus (e.g. Plin. NH 6.102), apparatus
  (``<note>``) kept separate from the text, print-edition page breaks (``<pb>``) recorded.
* EpiDoc (``epidoc``): one unit per text line (side.column.line).

Output: ``data/interim/corpus/<item_id>/units.jsonl`` + ``manifest.json`` (git-ignored: may contain
non-redistributable text). The committed summary is ``registers/corpus/parse_manifest.csv``.
"""

from __future__ import annotations

import collections
import json
import re
import statistics
import subprocess
import tempfile
from pathlib import Path

from lxml import etree

from romeco.corpus import registry as R

INTERIM = R.ROOT / "data" / "interim" / "corpus"
PARSER_VERSION = "0.2.0"   # 0.2.0: TEI overline numerals kept as \u203e...\u203e
TOOLS = {"pdftotext": "poppler 24.02.0", "tesseract": "5.3.4", "tessdata": "tessdata_fast@87416418"}
TESSDATA = Path(__file__).resolve().parents[3] / ".." / "tessdata"   # overridden by env/arg in ocr_page
ROMAN = re.compile(r"^(?=[ivxlc]+$)c{0,3}(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$")


# ----------------------------------------------------------------------------- PDF
def pdf_pages(path: Path) -> list[str]:
    out = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout
    pages = out.split("\f")
    return pages[:-1] if pages and not pages[-1].strip() else pages


FOLIO_PATTERNS = [re.compile(r"^\s*(\d{1,4})\s{2,}\S"), re.compile(r"\S\s{2,}(\d{1,4})\s*$"),
                  re.compile(r"^\s*(\d{1,4})\s*$")]


def detect_folio(text: str) -> int | None:
    lines = [l for l in text.splitlines() if l.strip()]
    for cand in lines[:2] + lines[-2:]:
        for p in FOLIO_PATTERNS:
            m = p.search(cand)
            if m:
                return int(m.group(1))
    return None


def label_pdf_pages(pages: list[str]) -> tuple[list[dict], dict]:
    det = [detect_folio(p) for p in pages]
    offs = collections.Counter(d - (i + 1) for i, d in enumerate(det) if d is not None)
    if not offs:
        return [dict(pdf_page=i + 1, printed_page=None, label_method="none") for i in range(len(pages))], {}
    off, support = offs.most_common(1)[0]
    agree = [i for i, d in enumerate(det) if d is not None and d - (i + 1) == off]
    lo, hi = min(agree), max(agree)
    out = []
    for i, d in enumerate(det):
        pp = i + 1 + off
        if d is not None and d == pp:
            m = "detected"
        elif lo <= i <= hi and pp > 0:
            m = "inferred_from_offset"
        else:
            m, pp = "none", None
        out.append(dict(pdf_page=i + 1, printed_page=pp, label_method=m))
    stats = dict(offset=off, offset_support=support, pages_with_folio=sum(d is not None for d in det),
                 detected=len(agree), contradicting=sum(1 for i, d in enumerate(det) if d is not None and d - (i + 1) != off))
    return out, stats


def ocr_page(pdf: Path, page: int, lang: str, tessdata: Path, dpi: int = 300) -> tuple[str, float]:
    with tempfile.TemporaryDirectory() as td:
        stem = Path(td) / "p"
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-png", "-singlefile",
                        str(pdf), str(stem)], check=True, capture_output=True)
        img = f"{stem}.png"
        base = ["tesseract", img, "stdout", "-l", lang, "--tessdata-dir", str(tessdata)]
        text = subprocess.run(base, capture_output=True, text=True, check=True).stdout
        tsv = subprocess.run(base + ["-c", "tessedit_create_tsv=1"], capture_output=True, text=True, check=True).stdout
    confs = [float(r.split("\t")[10]) for r in tsv.splitlines()[1:] if len(r.split("\t")) > 11 and r.split("\t")[11].strip()]
    confs = [c for c in confs if c >= 0]
    return text, (statistics.mean(confs) if confs else float("nan"))


# ----------------------------------------------------------------------------- flattened text
FLAT_FOLIO = [re.compile(r"^\s*(\d{1,3})\s*$"), re.compile(r"^\s*(\d{1,3}) [A-Z][^.]{2,70}$"),
              re.compile(r"^[A-Z][^.]{2,80}? (\d{1,3})\s*$")]


def folio_candidates(lines: list[str]) -> list[tuple[int, int]]:
    out = []
    for i, l in enumerate(lines):
        for p in FLAT_FOLIO:
            m = p.match(l)
            if m:
                out.append((i, int(m.group(1))))
                break
    return out


def folio_chain(cands: list[tuple[int, int]], max_step: int = 6, min_lines: int = 8) -> list[tuple[int, int]]:
    """Longest chain with strictly increasing folio (step 1..max_step) and line gaps >= min_lines*step."""
    n = len(cands)
    best = [1] * n
    prev = [-1] * n
    for j in range(n):
        lj, vj = cands[j]
        for i in range(max(0, j - 60), j):
            li, vi = cands[i]
            step = vj - vi
            if 1 <= step <= max_step and lj - li >= min_lines * step and best[i] + 1 > best[j]:
                best[j], prev[j] = best[i] + 1, i
    if not n:
        return []
    j = max(range(n), key=lambda k: best[k])
    chain = []
    while j != -1:
        chain.append(cands[j])
        j = prev[j]
    return chain[::-1]


def toc_entries(lines: list[str], scan: int = 600) -> list[tuple[str, int, int]]:
    """(title without chapter numbering, page, line index) from the printed contents list."""
    out = []
    for i, l in enumerate(lines[:scan]):
        m = re.match(r"^(.{8,120}?)[\s.]+(\d{1,3})\s*$", l.strip())
        if m and not re.fullmatch(r"[\d ]+", m.group(1).strip()):
            title = re.sub(r"^(\d+|[IVX]+)\.\s*", "", m.group(1).strip())
            if len(title) >= 8:
                out.append((title, int(m.group(2)), i))
    return out


def split_flattened(text: str) -> tuple[list[dict], dict]:
    lines = text.replace("\r\n", "\n").split("\n")
    chain = folio_chain(folio_candidates(lines))
    body_start = chain[0][0] if chain else 0

    def assign(position: str) -> list[dict]:
        """Units between folio lines. A jump in folio numbers (unnumbered chapter openers, plates)
        makes the unit's page uncertain: it is anchored to the range [page_low, page_high]."""
        units = []
        for k, (li, v) in enumerate(chain):
            if position == "closes":                     # folio at the foot: text above it ends page v
                a = chain[k - 1][0] + 1 if k else 0
                b = li
                low, high = (chain[k - 1][1] + 1 if k else v), v
            else:                                        # folio at the head: text below it starts page v
                a = li + 1
                b = chain[k + 1][0] if k + 1 < len(chain) else len(lines)
                low, high = v, (chain[k + 1][1] - 1 if k + 1 < len(chain) else v)
            units.append(dict(printed_page=v if low == high else None, page_low=low, page_high=high,
                              line_from=a, line_to=b, text="\n".join(lines[a:b])))
        return units

    def norm(x: str) -> str:
        return re.sub(r"^[\dIVX]+(\.\d+)*\.?\s+", "", x.strip()).lower()

    toc = toc_entries(lines)
    toc_end = max((i for _, _, i in toc), default=0)
    scores = {}
    for pos in ("closes", "opens"):
        us = assign(pos)
        exact = within = tot = 0
        cursor = max(toc_end, body_start)
        for title, pg, _ in toc:
            key = norm(title)
            bare = re.sub(r"^[\dIVX]+(\.\d+)*\.?\s+", "", title.strip())
            if len(key) < 12 or not bare[:1].isupper():   # wrapped fragments ('di Myos Hormos') are not headings
                continue
            # heading-like line: the title starts the line and the line is not much longer than the title
            loc = next((i for i in range(cursor + 1, len(lines))
                        if norm(lines[i]).startswith(key[:30]) and len(norm(lines[i])) <= len(key) + 15), None)
            if loc is None:
                continue
            cursor = loc                                    # contents entries occur in reading order
            u = next((u for u in us if u["line_from"] <= loc < u["line_to"]), None)
            if u is None:
                continue
            tot += 1
            if u["page_low"] <= pg <= u["page_high"]:
                within += 1
                exact += u["printed_page"] == pg
        scores[pos] = (within, exact, tot)
    pos = max(scores, key=lambda p: (scores[p][0], scores[p][1]))
    units = assign(pos)
    within, exact, tot = scores[pos]
    stats = dict(folio_position=pos, folios_in_chain=len(chain), toc_entries=len(toc), toc_located=tot,
                 toc_within_range=within, toc_exact=exact,
                 toc_within_rate=within / tot if tot else None, toc_exact_rate=exact / tot if tot else None,
                 alt_position_within=scores["opens" if pos == "closes" else "closes"][0],
                 units_with_page_range=sum(u["printed_page"] is None for u in units),
                 page_range=[units[0]["page_low"], units[-1]["page_high"]] if units else None)
    return units, stats


# ----------------------------------------------------------------------------- TEI / EpiDoc
def _txt(e) -> str:
    return re.sub(r"\s+", " ", "".join(e.itertext())).strip()


def tei_units(path: Path, unit_milestone: str | None = None) -> tuple[list[dict], dict]:
    """Walk TEI textparts (div/@n with type textpart or div1/@n) and milestones; notes -> apparatus."""
    parser = etree.XMLParser(recover=True, resolve_entities=False)
    root = etree.parse(str(path), parser).getroot()
    body = next(root.iter("{*}body"), root)
    units: dict[str, dict] = {}
    order: list[str] = []
    state = {"path": [], "ms": None, "pb": None}

    def key() -> str:
        parts = [p for p in state["path"]]
        if state["ms"]:
            parts = parts + [state["ms"]]
        return ".".join(parts)

    def add(text: str, note: bool = False):
        if not text or not text.strip():
            return
        k = key()
        if not k:
            return
        if k not in units:
            units[k] = dict(cts_ref=k, text="", apparatus=[], print_pages=[])
            order.append(k)
        u = units[k]
        if note:
            u["apparatus"].append(text.strip())
        else:
            u["text"] += text
        if state["pb"] and (not u["print_pages"] or u["print_pages"][-1] != state["pb"]):
            u["print_pages"].append(state["pb"])

    def walk(e):
        tag = etree.QName(e).localname if isinstance(e.tag, str) else ""
        pushed = False
        if tag in ("div", "div1", "div2", "div3") and e.get("n") and (e.get("type") in ("textpart", "book", "chapter", "section") or tag != "div") \
                and not str(e.get("n")).startswith("urn:"):
            state["path"].append(e.get("n"))
            state["ms"] = None
            pushed = True
        if tag == "milestone" and (unit_milestone is None or e.get("unit") == unit_milestone):
            if e.get("unit") in ("section", "chapter") or e.get("unit") == unit_milestone:
                state["ms"] = e.get("n")
        if tag == "pb":
            state["pb"] = e.get("{http://www.w3.org/XML/1998/namespace}id") or e.get("n")
        if tag == "note":
            add(_txt(e), note=True)
            if e.tail:
                add(e.tail)
            return
        if tag in ("head",):
            if e.tail:
                add(e.tail)
            return
        if tag == "hi" and e.get("rend") == "overline":
            # Overlined numerals multiply by 1,000 (Mayhoff: CCCVIIII with overline = 309 milia passuum).
            # Keep the mark so extraction can distinguish passus from milia passuum.
            add("\u203e" + _txt(e) + "\u203e")
            if e.tail:
                add(e.tail)
            return
        if e.text:
            add(e.text)
        for c in e:
            walk(c)
        if pushed:
            state["path"].pop()
            state["ms"] = None
        if e.tail:
            add(e.tail)

    walk(body)
    out = []
    for k in order:
        u = units[k]
        u["text"] = re.sub(r"\s+", " ", u["text"]).strip()
        if u["text"] or u["apparatus"]:
            out.append(u)
    return out, dict(units=len(out), with_apparatus=sum(bool(u["apparatus"]) for u in out),
                     with_print_page=sum(bool(u["print_pages"]) for u in out))


def epidoc_units(path: Path) -> tuple[list[dict], dict]:
    from romeco.ingest.epidoc import read_lines
    lines = read_lines(path)
    out = [dict(cts_ref=ln.locus, text=ln.text, apparatus=[], print_pages=[]) for ln in lines]
    return out, dict(units=len(out))


# ----------------------------------------------------------------------------- driver
def parse_item(item: dict, ocr_pages: list[int] | None = None, tessdata: Path | None = None) -> dict:
    src = R.ROOT / item["cache_path"]
    route = item["parse_route"]
    units, stats = [], {}
    if route == "pdf_text_layer":
        pages = pdf_pages(src)
        labels, stats = label_pdf_pages(pages)
        units = [dict(**lab, text=t, route="pdf_text_layer") for lab, t in zip(labels, pages)]
        if ocr_pages:
            lang = {"en": "eng", "it": "ita", "la": "lat", "grc": "grc", "de": "deu"}.get(item["language"], "eng")
            for p in ocr_pages:
                t, conf = ocr_page(src, p, lang, tessdata)
                lab = labels[p - 1]
                units.append(dict(**lab, text=t, route="pdf_ocr", ocr_mean_conf=conf))
    elif route == "flattened_text":
        raw, stats = split_flattened(src.read_text(encoding="utf-8"))
        units = [dict(pdf_page=None, printed_page=u["printed_page"], page_low=u["page_low"], page_high=u["page_high"],
                      label_method="folio_chain" if u["printed_page"] is not None else "folio_chain_range",
                      line_from=u["line_from"], line_to=u["line_to"], text=u["text"], route=route) for u in raw]
    elif route in ("tei_cts", "tei_milestone"):
        raw, stats = tei_units(src, unit_milestone="section" if item["source_id"] == "SRC-PLINY-NH-MAYHOFF"
                               else ("chapter" if route == "tei_milestone" else None))
        cite = (lambda r: ".".join([r.split(".")[0], r.split(".")[-1]])) if item["source_id"] == "SRC-PLINY-NH-MAYHOFF" else (lambda r: r)
        units = [dict(route=route, locus=cite(u["cts_ref"]), **u) for u in raw]   # Pliny is cited book.section
    elif route == "epidoc":
        raw, stats = epidoc_units(src)
        units = [dict(route=route, **u) for u in raw]
    else:
        return dict(item_id=item["item_id"], source_id=item["source_id"], route=route, status="not_text_parsed_elsewhere", units=0)
    outdir = INTERIM / item["item_id"]
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "units.jsonl", "w", encoding="utf-8") as fh:
        for u in units:
            fh.write(json.dumps(u, ensure_ascii=False) + "\n")
    man = dict(item_id=item["item_id"], source_id=item["source_id"], sha256=item["sha256"], route=route,
               parser_version=PARSER_VERSION, tools=TOOLS, units=len(units), stats=stats)
    (outdir / "manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False))
    R.set_state(item["source_id"], "parsed")
    return dict(item_id=item["item_id"], source_id=item["source_id"], route=route, status="parsed",
                units=len(units), stats=json.dumps(stats, ensure_ascii=False))


MANIFEST_FIELDS = ["item_id", "source_id", "route", "status", "units", "parser_version", "stats"]


def parse_all(only: list[str] | None = None) -> list[dict]:
    """Parse every acquired item; write registers/corpus/parse_manifest.csv (committed summary)."""
    rows = []
    for it in R.read("items.csv"):
        if only and it["source_id"] not in only:
            continue
        r = parse_item(it)
        r["parser_version"] = PARSER_VERSION
        rows.append(r)
    keep = [r for r in R.read("parse_manifest.csv") if only and r["source_id"] not in only]
    R.write("parse_manifest.csv", keep + rows, MANIFEST_FIELDS)
    return rows


def units(item_id: str) -> list[dict]:
    return [json.loads(l) for l in open(INTERIM / item_id / "units.jsonl", encoding="utf-8")]
