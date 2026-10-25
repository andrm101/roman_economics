"""WP11 task contracts, task reports, review decisions and agent-definition checks.

``check_all()`` returns a list of problems (empty = OK); ``romeco agents-check`` prints them.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import yaml

from romeco.agents.policy import ROOT, load

TASKS = ROOT / "tasks"
AGENTS = ROOT / ".claude" / "agents"
SKILLS = ROOT / ".claude" / "skills"
DECISIONS = ROOT / "registers" / "review_decisions.csv"

TASK_REQUIRED = ["task_id", "role", "wp", "status", "goal", "inputs", "outputs_expected", "acceptance",
                 "forbidden", "stop_and_escalate_if", "budget"]
TASK_STATUS = {"proposed", "approved", "in_progress", "blocked", "done", "rejected"}
REPORT_SECTIONS = ["## Summary", "## Files changed", "## Checks run", "## Not checked", "## Escalations"]
REVIEW_FIELDS = ["decision_id", "ext_id", "decision", "reviewer", "date", "claim_id", "corrections", "note"]
REVIEW_DECISIONS = {"accept", "accept_corrected", "reject", "defer"}
FORBIDDEN_MODES = {"bypassPermissions", "dontAsk", "auto", "acceptEdits"}


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: frontmatter must open on line 1")
    _, fm, body = text.split("---\n", 2)
    return yaml.safe_load(fm) or {}, body


def check_task(t: dict, where: str = "") -> list[str]:
    errs = [f"{where}: missing {k}" for k in TASK_REQUIRED if k not in t]
    if errs:
        return errs
    if not re.fullmatch(r"T-WP\d+-\d{3}", str(t["task_id"])):
        errs.append(f"{where}: task_id {t['task_id']!r} must look like T-WP10-001")
    if t["role"] not in load().roles:
        errs.append(f"{where}: unknown role {t['role']!r}")
    if t["status"] not in TASK_STATUS:
        errs.append(f"{where}: status {t['status']!r} not in {sorted(TASK_STATUS)}")
    if not t["acceptance"]:
        errs.append(f"{where}: acceptance must list at least one check")
    if not t["stop_and_escalate_if"]:
        errs.append(f"{where}: stop_and_escalate_if must not be empty")
    b = t["budget"] or {}
    if not {"max_turns", "max_wall_minutes"} <= set(b):
        errs.append(f"{where}: budget needs max_turns and max_wall_minutes")
    if t["status"] == "done":
        rep = TASKS / "reports" / f"{t['task_id']}.md"
        if not rep.exists():
            errs.append(f"{where}: done but no report {rep.relative_to(ROOT)}")
        else:
            errs += check_report(rep.read_text(encoding="utf-8"), str(rep.relative_to(ROOT)))
    return errs


def check_report(text: str, where: str = "") -> list[str]:
    errs = [f"{where}: report lacks section {s!r}" for s in REPORT_SECTIONS if s not in text]
    m = re.search(r"^## Not checked[ \t]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if m and not m.group(1).strip():
        errs.append(f"{where}: 'Not checked' must say what was not checked (or 'nothing, because …')")
    return errs


def check_tasks() -> list[str]:
    errs, seen = [], set()
    for p in sorted(TASKS.glob("T-*.yaml")):
        t = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        errs += check_task(t, str(p.relative_to(ROOT)))
        if t.get("task_id") in seen:
            errs.append(f"{p.name}: duplicate task_id")
        seen.add(t.get("task_id"))
        if t.get("task_id") and p.stem != t["task_id"]:
            errs.append(f"{p.name}: file name must equal task_id")
    return errs


def check_review_decisions(path: Path = DECISIONS) -> list[str]:
    if not path.exists():
        return []
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    errs = []
    humans = set(load().humans)
    for i, r in enumerate(rows, 2):
        if list(r.keys()) != REVIEW_FIELDS:
            return [f"{path.name}: header must be {','.join(REVIEW_FIELDS)}"]
        if r["reviewer"] not in humans:
            errs.append(f"{path.name}:{i}: reviewer {r['reviewer']!r} is not in policy humans")
        if r["decision"] not in REVIEW_DECISIONS:
            errs.append(f"{path.name}:{i}: decision {r['decision']!r}")
        if r["decision"].startswith("accept") and not r["claim_id"]:
            errs.append(f"{path.name}:{i}: an accepted candidate needs the claim_id it becomes")
    return errs


def check_agent_definitions() -> list[str]:
    pol = load()
    errs, names = [], set()
    for p in sorted(AGENTS.glob("*.md")):
        fm, body = frontmatter(p)
        name = fm.get("name")
        names.add(name)
        if name != p.stem:
            errs.append(f"{p.name}: name {name!r} must equal file stem")
        if name not in pol.roles:
            errs.append(f"{p.name}: no role {name!r} in policy")
        if not fm.get("description"):
            errs.append(f"{p.name}: description required")
        if fm.get("permissionMode") in FORBIDDEN_MODES:
            errs.append(f"{p.name}: permissionMode {fm['permissionMode']} weakens human gates")
        tools = [t.strip() for t in (fm.get("tools") or "").split(",") if t.strip()] if isinstance(fm.get("tools"), str) else list(fm.get("tools") or [])
        if not tools:
            errs.append(f"{p.name}: explicit tools allowlist required")
        net_tools = {"WebFetch", "WebSearch"} & set(tools)
        if net_tools and not pol.network(name):
            errs.append(f"{p.name}: {sorted(net_tools)} granted but policy has network: false")
        if not pol.roles.get(name, {}).get("write") and {"Write", "Edit"} & set(tools):
            errs.append(f"{p.name}: write tools granted but policy grants no write paths")
        for sk in fm.get("skills") or []:
            if not (SKILLS / sk / "SKILL.md").exists():
                errs.append(f"{p.name}: preloads missing skill {sk!r}")
        if "task-protocol" not in (fm.get("skills") or []):
            errs.append(f"{p.name}: must preload task-protocol")
    missing = set(pol.roles) - names
    if missing:
        errs.append(f"roles without agent definitions: {sorted(missing)}")
    return errs


def check_skills() -> list[str]:
    errs = []
    for p in sorted(SKILLS.glob("*/SKILL.md")):
        fm, _ = frontmatter(p)
        if fm.get("name") != p.parent.name:
            errs.append(f"{p}: name must equal folder")
        if not fm.get("description"):
            errs.append(f"{p}: description required")
    return errs


def check_all() -> list[str]:
    return check_agent_definitions() + check_skills() + check_tasks() + check_review_decisions()
