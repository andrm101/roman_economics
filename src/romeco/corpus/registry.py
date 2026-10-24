"""WP4.1 Corpus registry: file copies, bibliographic relations and pipeline states.

Bibliographic entities (works, editions, chapters, datasets) stay in
``registers/source_register.csv``. This module adds:

* ``registers/corpus/items.csv``      one row per acquired file copy (item), keyed by content hash
* ``registers/corpus/relations.csv``  part_of / edition_of / translation_of / derived_from between source_ids
* ``registers/corpus/pipeline_state.csv``  the eight pipeline states, tracked independently per source_id
* ``registers/corpus/acquisition_log.csv`` append-only log of every acquisition attempt

Finding a citation (``discovered``) never implies ``acquired``; ``acquired`` never implies
``parsed`` or ``reviewed``. ``unavailable`` records an access limitation, with the reason.
"""

from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REG = ROOT / "registers" / "corpus"
STATES = ["discovered", "screened", "eligible", "acquired", "parsed", "extracted", "reviewed", "unavailable"]
RELATIONS = {"part_of", "edition_of", "translation_of", "derived_from", "same_work_as", "describes"}

ITEM_FIELDS = ["item_id", "source_id", "origin_type", "locator", "media_type", "sha256", "bytes",
               "acquired_on", "cache_path", "rights_id", "redistribute_text", "language", "doc_type",
               "parse_route", "note"]
STATE_FIELDS = ["source_id", *STATES, "unavailable_reason", "note"]
REL_FIELDS = ["subject_id", "relation", "object_id", "note"]
LOG_FIELDS = ["timestamp", "source_id", "locator", "outcome", "detail"]


def today() -> str:
    return dt.date.today().isoformat()


def read(name: str) -> list[dict]:
    p = REG / name
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def write(name: str, rows: list[dict], fields: list[str]) -> None:
    REG.mkdir(parents=True, exist_ok=True)
    with open(REG / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def append_log(source_id: str, locator: str, outcome: str, detail: str = "") -> None:
    p = REG / "acquisition_log.csv"
    new = not p.exists()
    REG.mkdir(parents=True, exist_ok=True)
    with open(p, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow(dict(timestamp=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                        source_id=source_id, locator=locator, outcome=outcome, detail=detail))


def set_state(source_id: str, state: str, on: str | None = None, reason: str = "") -> None:
    """Set one pipeline state (idempotent: an existing date is kept)."""
    if state not in STATES:
        raise ValueError(state)
    rows = read("pipeline_state.csv")
    row = next((r for r in rows if r["source_id"] == source_id), None)
    if row is None:
        row = {"source_id": source_id}
        rows.append(row)
    if not row.get(state):
        row[state] = on or today()
    if state == "unavailable" and reason:
        row["unavailable_reason"] = reason
    write("pipeline_state.csv", sorted(rows, key=lambda r: r["source_id"]), STATE_FIELDS)


def sources() -> dict[str, dict]:
    return {r["source_id"]: r for r in csv.DictReader(open(ROOT / "registers" / "source_register.csv", encoding="utf-8"))}


def rights() -> dict[str, dict]:
    return {r["rights_id"]: r for r in csv.DictReader(open(ROOT / "registers" / "rights_register.csv", encoding="utf-8"))}


def may_redistribute_text(rights_id: str) -> bool:
    r = rights().get(rights_id, {})
    return str(r.get("redistribute_full_text", "")).startswith("yes")


def validate() -> list[str]:
    """Referential and state-consistency checks; returns a list of problems (empty = valid)."""
    src = sources()
    probs = []
    for r in read("items.csv"):
        if r["source_id"] not in src:
            probs.append(f"item {r['item_id']}: unknown source {r['source_id']}")
        if r["rights_id"] not in rights():
            probs.append(f"item {r['item_id']}: unknown rights {r['rights_id']}")
    for r in read("relations.csv"):
        for k in ("subject_id", "object_id"):
            if r[k] not in src:
                probs.append(f"relation {r}: unknown {k} {r[k]}")
        if r["relation"] not in RELATIONS:
            probs.append(f"relation {r}: bad relation")
    acquired = {r["source_id"] for r in read("items.csv")}
    for r in read("pipeline_state.csv"):
        sid = r["source_id"]
        if sid not in src:
            probs.append(f"state: unknown source {sid}")
        for later in ("parsed", "extracted", "reviewed"):
            if r.get(later) and not r.get("acquired"):
                probs.append(f"state {sid}: {later} without acquired")
        if r.get("acquired") and sid not in acquired:
            probs.append(f"state {sid}: acquired but no item record")
        if r.get("unavailable") and not r.get("unavailable_reason"):
            probs.append(f"state {sid}: unavailable without reason")
    return probs
