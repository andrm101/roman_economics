"""WP4.2 Acquisition queue (resumable, policy-gated, content-addressed).

Queue entries live in ``config/corpus_queue.yaml``. Each names a source_id and a
locator. Supported locator types and their policies:

* ``file``  a local file supplied by the researcher (attachment, project document, connected folder)
* ``git``   ``repo`` + pinned ``commit`` + ``path`` (the only network route open in this environment)
* ``http``  recorded but not fetched here: logged as ``blocked_by_environment``. Never used to get
            around access controls; the researcher supplies such files instead.

A file is cached once at ``data/raw/corpus/<sha256[:2]>/<sha256><ext>`` (git-ignored). Re-running
skips unchanged items (same source_id and sha256); a changed hash for the same locator is
logged and both items are kept. Failures are logged and do not stop the queue.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import yaml

from romeco.corpus import registry as R

CACHE = R.ROOT / "data" / "raw" / "corpus"
QUEUE = R.ROOT / "config" / "corpus_queue.yaml"


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _read_locator(loc: dict) -> bytes:
    t = loc["type"]
    if t == "file":
        return Path(loc["path"]).expanduser().read_bytes()
    if t == "git":
        from romeco.ingest.fetch import _ensure_clone, _git
        clone = _ensure_clone(loc["repo"], loc["commit"])
        return _git("show", f"{loc['commit']}:{loc['path']}", cwd=clone)
    if t == "http":
        raise PermissionError("http locators are not fetched from this environment (allow-list); supply the file")
    raise ValueError(f"unknown locator type {t}")


def locator_str(loc: dict) -> str:
    if loc["type"] == "git":
        return f"git:{loc['repo']}@{loc['commit'][:12]}:{loc['path']}"
    return f"{loc['type']}:{loc.get('path') or loc.get('url')}"


def run(queue_path: Path = QUEUE, only: list[str] | None = None) -> list[dict]:
    q = yaml.safe_load(queue_path.read_text(encoding="utf-8"))["items"]
    src = R.sources()
    items = R.read("items.csv")
    by_key = {(i["source_id"], i["sha256"]): i for i in items}
    report = []
    for e in q:
        sid = e["source_id"]
        if only and sid not in only:
            continue
        loc = e["locator"]
        ls = locator_str(loc)
        if sid not in src:
            R.append_log(sid, ls, "failed", "source_id not in source_register")
            report.append(dict(source_id=sid, outcome="failed"))
            continue
        rights_id = e.get("rights_id") or src[sid].get("rights_id") or "RGT-UNKNOWN"
        if e.get("permitted") is False:
            R.append_log(sid, ls, "not_permitted", e.get("reason", ""))
            R.set_state(sid, "unavailable", reason=e.get("reason", "not permitted"))
            report.append(dict(source_id=sid, outcome="not_permitted"))
            continue
        try:
            blob = _read_locator(loc)
        except PermissionError as ex:
            R.append_log(sid, ls, "blocked_by_environment", str(ex))
            report.append(dict(source_id=sid, outcome="blocked_by_environment"))
            continue
        except Exception as ex:  # noqa: BLE001 - logged, queue continues
            R.append_log(sid, ls, "failed", f"{type(ex).__name__}: {ex}")
            report.append(dict(source_id=sid, outcome="failed"))
            continue
        h = _sha256(blob)
        if (sid, h) in by_key:
            known = R.ROOT / by_key[(sid, h)]["cache_path"]
            outcome = "skipped_unchanged"
            if not known.exists():  # fresh clone or purged cache: same bytes, same item, restore the file
                known.parent.mkdir(parents=True, exist_ok=True)
                known.write_bytes(blob)
                outcome = "restored_cache"
            R.append_log(sid, ls, outcome, h[:12])
            report.append(dict(source_id=sid, outcome=outcome, sha256=h))
            continue
        ext = Path(loc.get("path", "")).suffix.lower() or e.get("ext", "")
        dest = CACHE / h[:2] / f"{h}{ext}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            dest.write_bytes(blob)
        prior = [i for i in items if i["source_id"] == sid and i["locator"] == ls]
        if prior:
            R.append_log(sid, ls, "content_changed", f"{prior[-1]['sha256'][:12]} -> {h[:12]}; both kept")
        item = dict(item_id=f"ITM-{h[:12]}", source_id=sid, origin_type=loc["type"], locator=ls,
                    media_type=e["media_type"], sha256=h, bytes=len(blob), acquired_on=R.today(),
                    cache_path=str(dest.relative_to(R.ROOT)), rights_id=rights_id,
                    redistribute_text="yes" if R.may_redistribute_text(rights_id) else "no",
                    language=e.get("language", ""), doc_type=e.get("doc_type", ""),
                    parse_route=e.get("parse_route", ""), note=e.get("note", ""))
        items.append(item)
        by_key[(sid, h)] = item
        R.set_state(sid, "acquired")
        R.append_log(sid, ls, "acquired", h[:12])
        report.append(dict(source_id=sid, outcome="acquired", sha256=h))
    R.write("items.csv", items, R.ITEM_FIELDS)
    return report


def cached(item: dict) -> Path:
    return R.ROOT / item["cache_path"]


def purge_cache() -> None:
    """Delete the local cache (re-acquire with run()). Not called automatically."""
    shutil.rmtree(CACHE, ignore_errors=True)
