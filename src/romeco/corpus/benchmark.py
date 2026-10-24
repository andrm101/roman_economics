"""WP4.6 Stratified extraction benchmark (protocol: benchmark/PROTOCOL.md).

draw_sample()  -> benchmark/sample.csv           (seeded, frames as registered)
render(...)    -> page images for gold annotation (scratch; never committed)
score()        -> benchmark/results.csv + benchmark/results.json + benchmark/review_sheet.csv
"""

from __future__ import annotations

import csv
import json
import math
import random
import subprocess
from pathlib import Path

import yaml

from romeco.corpus import discover as D
from romeco.corpus import extract as E
from romeco.corpus import parse as P
from romeco.corpus import registry as R

BENCH = R.ROOT / "benchmark"
SEED = 20261025


def _item(source_id: str, suffix: str = "") -> dict:
    return next(i for i in R.read("items.csv") if i["source_id"] == source_id and i["locator"].endswith(suffix))


DEV_SIZES = dict(S1=6, S2=3, S4=5, S5=5, S6=8, S7=5, S8=2)
HELDOUT_SIZES = dict(S1=4, S2=2, S4=4, S5=4, S6=5, S7=3, S8=2)


def draw_sample(seed: int = SEED, sizes: dict | None = None, exclude: set | None = None,
                out: str = "sample.csv", fixed: bool = True) -> list[dict]:
    """Seeded stratified sample. ``exclude``: (stratum, unit_key) pairs already used (dev set)."""
    sizes = sizes or DEV_SIZES
    exclude = exclude or set()
    rng = random.Random(seed)
    rows = []

    def pick(stratum, frame, n):
        frame = [x for x in frame if (stratum, x) not in exclude]
        return rng.sample(frame, n)

    def add(stratum, item, unit_keys, fixed=()):
        for k in list(unit_keys) + list(fixed):
            rows.append(dict(stratum=stratum, item_id=item["item_id"], source_id=item["source_id"],
                             route={"S3": "pdf_ocr"}.get(stratum, item["parse_route"]), language=item["language"],
                             unit_key=k, fixed=k in fixed))

    adams = _item("SRC-ADAMS-2007")
    au = P.units(adams["item_id"])
    frame = [u["pdf_page"] for u in au if u.get("route") == "pdf_text_layer" and u.get("printed_page") and 3 <= u["printed_page"] <= 291]
    s1 = sorted(pick("S1", [f"pdf:{p}" for p in frame], sizes["S1"]), key=lambda k: int(k[4:]))
    s1 = [int(k[4:]) for k in s1]
    add("S1", adams, [f"pdf:{p}" for p in s1])
    itin = _item("SRC-ITINERE-PAPER-2025")
    add("S2", itin, sorted(pick("S2", [f"pdf:{p}" for p in range(1, 17)], sizes["S2"]), key=lambda k: int(k[4:])))
    add("S3", adams, [f"pdf:{p}" for p in s1])
    for st, sid, lo, hi in (("S4", "SRC-NAPPO-2018", 11, 180), ("S5", "SRC-BOWMAN-WILSON-2009", 3, 10_000)):
        it = _item(sid)
        us = P.units(it["item_id"])
        bib = set(D.bib_units(us))
        fr = [i for i, u in enumerate(us) if i not in bib and lo <= (u.get("page_low") or 0) <= hi]
        add(st, it, sorted(pick(st, [f"unit:{i}" for i in fr], sizes[st]), key=lambda k: int(k[5:])))
    pl = _item("SRC-PLINY-NH-MAYHOFF")
    fr = [u["locus"] for u in P.units(pl["item_id"]) if u["locus"].startswith("6.") and u["locus"] != "6.102"]
    add("S6", pl, sorted(pick("S6", fr, sizes["S6"])), fixed=["6.102"] if fixed else ())
    se = _item("SRC-STRABO-GEOG", "eng4.xml")
    fr = [u["cts_ref"] for u in P.units(se["item_id"]) if u["cts_ref"].startswith("17.")]
    add("S7", se, sorted(pick("S7", fr, sizes["S7"])))
    sg = _item("SRC-STRABO-GEOG", "grc2.xml")
    fr = [u["cts_ref"] for u in P.units(sg["item_id"]) if u["cts_ref"].startswith("17.1.")]
    add("S8", sg, sorted(pick("S8", fr, sizes["S8"])))
    if fixed:
        add("S8", _item("SRC-JOSEPHUS-BJ"), [], fixed=["2.387"])
    BENCH.mkdir(exist_ok=True)
    with open(BENCH / out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rows


def get_unit(item_id: str, key: str, route: str | None = None) -> dict:
    us = P.units(item_id)
    kind, val = key.split(":", 1) if ":" in key and key.split(":")[0] in ("pdf", "unit") else ("ref", key)
    if kind == "pdf":
        r = route or "pdf_text_layer"
        return next(u for u in us if u.get("pdf_page") == int(val) and u.get("route") == r)
    if kind == "unit":
        return [u for u in us if u.get("route") != "pdf_ocr"][int(val)]
    return next(u for u in us if (u.get("locus") or u.get("cts_ref")) == val)


def render(item_id: str, pdf_page: int, out_dir: Path, dpi: int = 110) -> Path:
    it = next(i for i in R.read("items.csv") if i["item_id"] == item_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / f"{item_id}_p{pdf_page:03d}"
    subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(pdf_page), "-l", str(pdf_page), "-png", "-singlefile",
                    str(R.ROOT / it["cache_path"]), str(stem)], check=True)
    return Path(f"{stem}.png")


# ---------------------------------------------------------------------------- scoring
def wilson(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def _match(gold: list, pred: list, keyf) -> tuple[int, int, int, list, list]:
    g = [keyf(x) for x in gold]
    p = [keyf(x) for x in pred]
    used, tp, fn_items = [False] * len(p), 0, []
    for gi, gk in enumerate(g):
        j = next((j for j, pk in enumerate(p) if not used[j] and pk == gk), None)
        if j is None:
            fn_items.append(gold[gi])
        else:
            used[j] = True
            tp += 1
    fp_items = [pred[j] for j, u in enumerate(used) if not u]
    return tp, len(fp_items), len(fn_items), fp_items, fn_items


def _qkey(x, strict=True):
    lo, hi = round(float(x["value_low"]), 6), round(float(x["value_high"]), 6)
    return (x["unit"], lo, hi) if strict else (lo, hi)


def score(tessdata: Path | None = None, sample_file: str = "sample.csv", gold_dir: str = "gold",
          suffix: str = "") -> dict:
    sample = list(csv.DictReader(open(BENCH / sample_file, encoding="utf-8")))
    gold = {}
    for f in sorted((BENCH / gold_dir).glob("*.yaml")):
        g = yaml.safe_load(f.read_text(encoding="utf-8"))
        gold[(g["stratum"], g["unit_key"])] = g
    agg: dict = {}
    review = []
    for s in sample:
        g = gold.get((s["stratum"], s["unit_key"]))
        if g is None:
            continue
        it = next(i for i in R.read("items.csv") if i["item_id"] == s["item_id"])
        if s["route"] == "pdf_ocr":
            page = int(s["unit_key"].split(":")[1])
            text, conf = P.ocr_page(R.ROOT / it["cache_path"], page, "eng", tessdata)
            u = dict(get_unit(s["item_id"], s["unit_key"]), text=text, ocr_mean_conf=conf)
        else:
            u = get_unit(s["item_id"], s["unit_key"])
        pred = E.extract_unit(u.get("text", ""), it["language"])
        pq = [c for c in pred if c["kind"] == "quantity"]
        pc = [c for c in pred if c["kind"] == "ancient_cite"]
        gq = g.get("quantities") or []
        gc = g.get("ancient_cites") or []
        a = agg.setdefault(s["stratum"], dict(units=0, q_tp=0, q_fp=0, q_fn=0, ql_tp=0, ql_fp=0, ql_fn=0,
                                              c_tp=0, c_fp=0, c_fn=0, page_ok=0, page_n=0, gold_q_word=0,
                                              gold_q_word_found=0, ocr_conf=[]))
        a["units"] += 1
        tp, fp, fn, fpi, fni = _match(gq, pq, _qkey)
        a["q_tp"] += tp; a["q_fp"] += fp; a["q_fn"] += fn
        tpl, fpl, fnl, _, _ = _match(gq, pq, lambda x: _qkey(x, strict=False))
        a["ql_tp"] += tpl; a["ql_fp"] += fpl; a["ql_fn"] += fnl
        a["gold_q_word"] += sum(1 for x in gq if x.get("numeral_form") == "word")
        a["gold_q_word_found"] += sum(1 for x in gq if x.get("numeral_form") == "word" and x not in fni)
        ctp, cfp, cfn, cfpi, cfni = _match(gc, pc, lambda x: x["norm_key"] if isinstance(x, dict) else x)
        a["c_tp"] += ctp; a["c_fp"] += cfp; a["c_fn"] += cfn
        if g.get("printed_page") is not None and s["route"] in ("pdf_text_layer", "pdf_ocr"):
            a["page_n"] += 1
            a["page_ok"] += int(u.get("printed_page") == g["printed_page"])
        if u.get("ocr_mean_conf") is not None:
            a["ocr_conf"].append(u["ocr_mean_conf"])
        for kind, items in (("quantity_FP", fpi), ("quantity_FN", fni), ("cite_FP", cfpi), ("cite_FN", cfni)):
            for x in items:
                review.append(dict(stratum=s["stratum"], unit_key=s["unit_key"], error=kind,
                                   item=json.dumps({k: x.get(k) for k in ("raw", "unit", "value_low", "value_high", "norm_key", "numeral_form", "note") if isinstance(x, dict) and x.get(k) is not None}, ensure_ascii=False) if isinstance(x, dict) else x,
                                   reviewer_verdict="", reviewer_note=""))
    rows = []
    for st, a in sorted(agg.items()):
        def prf(tp, fp, fn):
            p = tp / (tp + fp) if tp + fp else None
            r = tp / (tp + fn) if tp + fn else None
            f = 2 * p * r / (p + r) if p and r else (0.0 if p is not None and r is not None else None)
            return p, r, f
        qp, qr, qf = prf(a["q_tp"], a["q_fp"], a["q_fn"])
        lp, lr, lf = prf(a["ql_tp"], a["ql_fp"], a["ql_fn"])
        cp, cr, cf = prf(a["c_tp"], a["c_fp"], a["c_fn"])
        gq_n, gc_n = a["q_tp"] + a["q_fn"], a["c_tp"] + a["c_fn"]
        rows.append(dict(stratum=st, units=a["units"], gold_quantities=gq_n, q_precision=qp, q_recall=qr, q_f1=qf,
                         q_recall_ci=wilson(a["q_tp"], gq_n), q_precision_ci=wilson(a["q_tp"], a["q_tp"] + a["q_fp"]),
                         q_lenient_recall=lr, gold_word_numerals=a["gold_q_word"],
                         gold_cites=gc_n, c_precision=cp, c_recall=cr, c_f1=cf, c_recall_ci=wilson(a["c_tp"], gc_n),
                         page_label_acc=(a["page_ok"] / a["page_n"]) if a["page_n"] else None, page_n=a["page_n"],
                         ocr_mean_conf=round(sum(a["ocr_conf"]) / len(a["ocr_conf"]), 1) if a["ocr_conf"] else None,
                         indicative_only=(gq_n + gc_n) < 10))
    fmt = lambda v: round(v, 3) if isinstance(v, float) else v
    with open(BENCH / f"results{suffix}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows([{k: fmt(v) for k, v in r.items()} for r in rows])
    with open(BENCH / f"errors{suffix}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["stratum", "unit_key", "error", "item", "reviewer_verdict", "reviewer_note"])
        w.writeheader()
        w.writerows(review)
    pool = {k: sum(a[k] for st, a in agg.items() if st != "S3") for k in ("q_tp", "q_fp", "q_fn", "c_tp", "c_fp", "c_fn", "page_ok", "page_n")}
    pooled = dict(
        scope="all strata except S3 (S3 re-scores the S1 pages via OCR)",
        q_precision=fmt(pool["q_tp"] / (pool["q_tp"] + pool["q_fp"])) if pool["q_tp"] + pool["q_fp"] else None,
        q_precision_ci=wilson(pool["q_tp"], pool["q_tp"] + pool["q_fp"]),
        q_recall=fmt(pool["q_tp"] / (pool["q_tp"] + pool["q_fn"])) if pool["q_tp"] + pool["q_fn"] else None,
        q_recall_ci=wilson(pool["q_tp"], pool["q_tp"] + pool["q_fn"]), gold_quantities=pool["q_tp"] + pool["q_fn"],
        c_precision=fmt(pool["c_tp"] / (pool["c_tp"] + pool["c_fp"])) if pool["c_tp"] + pool["c_fp"] else None,
        c_precision_ci=wilson(pool["c_tp"], pool["c_tp"] + pool["c_fp"]),
        c_recall=fmt(pool["c_tp"] / (pool["c_tp"] + pool["c_fn"])) if pool["c_tp"] + pool["c_fn"] else None,
        c_recall_ci=wilson(pool["c_tp"], pool["c_tp"] + pool["c_fn"]), gold_cites=pool["c_tp"] + pool["c_fn"],
        page_label_acc=fmt(pool["page_ok"] / pool["page_n"]) if pool["page_n"] else None, page_n=pool["page_n"])
    out = dict(extractor_version=E.EXTRACTOR_VERSION, parser_version=P.PARSER_VERSION, seed=SEED, pooled=pooled,
               gold_status="assistant_annotated_pending_human_review", strata=[{k: fmt(v) for k, v in r.items()} for r in rows])
    out["sample_file"], out["gold_dir"] = sample_file, gold_dir
    (BENCH / f"results{suffix}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    return out


def gold_review_sheet() -> int:
    """One row per gold item (both splits) for the researcher's review (WP4 acceptance)."""
    rows = []
    for split, d in (("dev", "gold"), ("heldout", "gold_heldout")):
        for f in sorted((BENCH / d).glob("*.yaml")):
            g = yaml.safe_load(f.read_text(encoding="utf-8"))
            if g["stratum"] == "S3":          # same items as S1
                continue
            base = dict(split=split, stratum=g["stratum"], unit_key=g["unit_key"], source_id=g["source_id"],
                        annotated_from=g.get("annotated_from", ""), unit_notes=g.get("notes", ""))
            if g.get("printed_page") is not None:
                rows.append(dict(base, kind="page_label", raw="", unit="", value_low=g["printed_page"], value_high="", key="", item_note=""))
            for x in g.get("quantities") or []:
                rows.append(dict(base, kind="quantity", raw=x["raw"], unit=x["unit"], value_low=x["value_low"],
                                 value_high=x["value_high"], key="", item_note=x.get("note", "")))
            for x in g.get("ancient_cites") or []:
                rows.append(dict(base, kind="ancient_cite", raw=x["raw"], unit="", value_low="", value_high="",
                                 key=x["norm_key"], item_note=""))
            if not (g.get("quantities") or g.get("ancient_cites")):
                rows.append(dict(base, kind="no_items_claimed", raw="", unit="", value_low="", value_high="", key="", item_note=""))
    fields = ["split", "stratum", "unit_key", "source_id", "annotated_from", "kind", "raw", "unit", "value_low", "value_high",
              "key", "item_note", "unit_notes", "reviewer_verdict", "reviewer_correction", "reviewer"]
    with open(BENCH / "gold_review_sheet.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return len(rows)
