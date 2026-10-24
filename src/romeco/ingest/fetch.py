"""Fetch pinned context datasets from git repositories (the only route open here).

Partial clones (no blobs) are kept in a cache; only the listed files are
materialised with ``git show <commit>:<path>``. Checksums go to
config/datasets.lock.yaml so later runs can detect upstream drift.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
CACHE = Path(os.environ.get("ROMECO_GIT_CACHE", Path.home() / ".cache" / "romeco-git"))


def _git(*args: str, cwd: Path | None = None) -> bytes:
    env = {**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"}
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=True, capture_output=True).stdout


def _ensure_clone(repo: str, commit: str) -> Path:
    dest = CACHE / repo.rstrip("/").split("github.com/")[-1].replace("/", "__")
    if not (dest / ".git").exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        _git("clone", "--filter=blob:none", "--no-checkout", "--depth", "1", repo, str(dest))
    try:
        _git("cat-file", "-e", f"{commit}^{{commit}}", cwd=dest)
    except subprocess.CalledProcessError:
        _git("fetch", "--depth", "1", "--filter=blob:none", "origin", commit, cwd=dest)
    return dest


def fetch_all(config: Path | None = None, only: list[str] | None = None) -> dict:
    config = config or ROOT / "config" / "datasets.yaml"
    spec = yaml.safe_load(config.read_text(encoding="utf-8"))["datasets"]
    lock_path = ROOT / "config" / "datasets.lock.yaml"
    lock = yaml.safe_load(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}
    lock = lock or {}
    for name, d in spec.items():
        if only and name not in only:
            continue
        if d["route"] != "git":
            lock.setdefault(name, {"route": d["route"], "status": "manual_download_required"})
            continue
        clone = _ensure_clone(d["repo"], d["commit"])
        outdir = ROOT / "data" / "raw" / "context" / name / d["commit"]
        entry = {"route": "git", "repo": d["repo"], "commit": d["commit"], "files": {}}
        for f in d["files"]:
            blob = _git("show", f"{d['commit']}:{f}", cwd=clone)
            target = outdir / f
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
            entry["files"][f] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
        prev = lock.get(name, {}).get("files", {})
        drift = [f for f, v in entry["files"].items() if f in prev and prev[f]["sha256"] != v["sha256"]]
        if drift:
            raise RuntimeError(f"{name}: checksum drift at pinned commit for {drift}")
        lock[name] = entry
    lock_path.write_text(yaml.safe_dump(lock, sort_keys=True, allow_unicode=True), encoding="utf-8")
    return lock


def raw_path(name: str, relpath: str) -> Path:
    spec = yaml.safe_load((ROOT / "config" / "datasets.yaml").read_text(encoding="utf-8"))["datasets"][name]
    return ROOT / "data" / "raw" / "context" / name / spec["commit"] / relpath
