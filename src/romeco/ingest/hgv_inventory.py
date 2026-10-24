"""Inventory of Eastern Desert documents in the HGV metadata (papyri.info idp.data, CC BY 3.0).

Purpose (WP2 follow-up, D022): establish what a documentary traffic or seasonality
count could be built from. HGV metadata gives provenance, date (with precision),
publication series and subject keywords. It is NOT a traffic count: survival,
excavation and publication fractions are unknown, so any count is a lower bound
on attested activity.

Usage:
    python -m romeco.ingest.hgv_inventory /path/to/idp.data   # writes data/derived/context/
"""

from __future__ import annotations

import collections
import csv
import re
import subprocess
import sys
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
NS = {"t": "http://www.tei-c.org/ns/1.0"}
# Site classes by HGV origPlace (anchored to avoid Diospolis / Krokodilopolis false matches)
SITES = [
    ("Mons Claudianus", r"Claudian"), ("Mons Porphyrites", r"Porphyr"),
    ("route_to_Koptos", r"bzw\. Koptos"),                       # Nikanor archive labels ('Berenike bzw. Koptos')
    ("Berenike", r"^Berenike( \(\?\))?$"), ("Myos Hormos", r"^Myos Hormos( \(\?\))?$"),
    ("Didymoi", r"^Didymoi"), ("Krokodilo", r"^Krokodilo$"), ("Xeron Pelagos", r"Xeron"),
    ("Maximianon", r"Maximian"), ("Dios", r"^Dios$|Fundort: Dios"), ("Abu Shaar", r"Abu Sha"),
    ("Koptos", r"^Koptos( \(\?\))?$"),
]
TRANSPORT_KW = re.compile(r"Passierschein|Dekania|Kamel|Lieferung|Transport|Wasser|Zoll|Karawane", re.I)


def site_of(place: str) -> str | None:
    for name, rx in SITES:
        if re.search(rx, place):
            return name
    return None


def date_info(x) -> tuple[str, float | None]:
    """(precision, mid-year). precision: 'month' if a single date has YYYY-MM, 'year', 'range' or 'none'."""
    prec, ys = "none", []
    for e in x.iterfind(".//t:origDate", NS):
        w, nb, na = e.get("when"), e.get("notBefore"), e.get("notAfter")
        single = w or (nb if nb and nb == na else None)
        if single and re.match(r"-?\d{4}-\d{2}", single):
            prec = "month"
        elif single and prec != "month":
            prec = "year"
        elif (nb or na) and prec == "none":
            prec = "range"
        ys += [int(re.match(r"(-?\d+)", v).group(1)) for v in (w, nb, na) if v]
    return prec, (sum(ys) / len(ys) if ys else None)


def scan(idp_root: Path) -> list[dict]:
    rows = []
    for f in sorted((idp_root / "HGV_meta_EpiDoc").glob("HGV*/*.xml")):
        try:
            x = etree.parse(str(f))
        except etree.XMLSyntaxError:
            continue
        place = " | ".join(" ".join(e.itertext()).strip() for e in x.iterfind(".//t:origPlace", NS))
        s = site_of(place)
        if not s:
            continue
        prec, mid = date_info(x)
        ddb = [e.text for e in x.iterfind('.//t:idno[@type="ddb-hybrid"]', NS)]
        kws = [" ".join(e.itertext()).strip() for e in x.iterfind(".//t:keywords/t:term", NS)]
        rows.append(dict(hgv_file=f.name, ddb=ddb[0] if ddb else "", series=ddb[0].split(";")[0] if ddb else "",
                         site=s, orig_place=place, date_precision=prec,
                         date_mid=None if mid is None else round(mid, 1),
                         transport_related=bool(TRANSPORT_KW.search(" ".join(kws))), keywords="; ".join(kws)))
    return rows


def summarise(rows: list[dict]) -> list[dict]:
    out = []
    by = collections.defaultdict(list)
    for r in rows:
        by[r["site"]].append(r)
    for s, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        c = collections.Counter(r["date_precision"] for r in rs)
        w2 = [r for r in rs if r["date_mid"] is not None and 100 <= r["date_mid"] <= 200]
        ser = collections.Counter(r["series"] for r in rs).most_common(3)
        out.append(dict(site=s, documents=len(rs), month_precise=c["month"], year_precise=c["year"],
                        range_only=c["range"], undated=c["none"], mid_in_100_200=len(w2),
                        month_precise_in_100_200=sum(r["date_precision"] == "month" for r in w2),
                        transport_related=sum(r["transport_related"] for r in rs),
                        top_series="; ".join(f"{k} ({v})" for k, v in ser)))
    return out


def main(idp_root: str) -> None:
    root = Path(idp_root)
    commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rows = scan(root)
    outdir = ROOT / "data" / "derived" / "context"
    for name, data in (("eastern_desert_documents.csv", rows), ("eastern_desert_documents_summary.csv", summarise(rows))):
        with open(outdir / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    (outdir / "eastern_desert_documents.SOURCE.txt").write_text(
        f"HGV metadata from papyri/idp.data commit {commit} (CC BY 3.0; attribution: Heidelberger Gesamtverzeichnis "
        f"der griechischen Papyrusurkunden Ägyptens / papyri.info). Generated by romeco.ingest.hgv_inventory.\n")
    print(f"{len(rows)} documents; commit {commit}")


if __name__ == "__main__":
    main(sys.argv[1])
