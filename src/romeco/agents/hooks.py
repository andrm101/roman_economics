"""WP11 PreToolUse hook: enforce .claude/policy/roles.yaml for project subagents.

Invoked by .claude/settings.json as
    python3 -m romeco.agents.hooks pre-tool-use      (JSON event on stdin)

Output follows the Claude Code hooks contract (code.claude.com/docs/en/hooks, read 2026-10-25):
exit 0 with hookSpecificOutput.permissionDecision = "deny" and a reason blocks the call;
exit 0 with no output defers to the normal permission flow.

``decide(event)`` is pure and unit-tested; it never allows anything the normal permission flow would
not, it only denies. Limits: Bash inspection is textual (a determined command can evade it), so the
deployment notes recommend running agents inside the sandbox / container as well.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

from romeco.agents.policy import load, relpath

WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
READ_TOOLS = {"Read", "Grep", "Glob"}

UNIVERSAL_BASH = [  # applies to everyone, including the researcher's session
    (r"\bgit\s+push\b[^;&|]*(\s--force\b|\s-f\b|\s--force-with-lease\b|\s\+\S)", "force-push rewrites shared history"),
    (r"\bgit\s+filter-(branch|repo)\b", "history rewriting"),
]
SUBAGENT_BASH = [
    (r"\bgit\s+reset\s+--hard\b", "discards work; subagents may not hard-reset"),
    (r"\bgit\s+(rebase|clean)\b", "rewrites or deletes work"),
    (r"\bgit\s+(checkout|switch)\s+(main|master)\b", "subagents work on agent/<task_id> branches only"),
    (r"\bgit\s+merge\b", "only the researcher merges"),
    (r"\bgit\s+branch\s+-[dD]\b", "branch deletion"),
    (r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b", "recursive forced delete"),
]
NETWORK_BASH = r"\b(curl|wget|aria2c|scp|rsync|ssh|nc|ncat)\b|requests\.(get|post)|urllib\.request|httpx\."
WRITE_OPS = r"(\bsed\s+-i\b|>>?|\btee\b|\bmv\b|\bcp\b|\brm\b|\btruncate\b|\bdd\b|write_text|open\([^)]*['\"][wa])"


def _deny(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": f"[romeco policy] {reason}"}}


def _current_branch(cwd: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True,
                              text=True, timeout=5).stdout.strip() or None
    except Exception:  # pragma: no cover - git missing
        return None


def decide(event: dict, project_dir: str | None = None, branch: str | None = None) -> dict | None:
    pol = load()
    tool = event.get("tool_name", "")
    ti = event.get("tool_input") or {}
    agent = event.get("agent_type")            # absent in the researcher's own session
    sub = agent is not None
    proj = project_dir or os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or "."

    if tool == "Bash":
        cmd = ti.get("command", "")
        for pat, why in UNIVERSAL_BASH:
            if re.search(pat, cmd):
                return _deny(f"blocked: {why}")
        if not sub:
            return None
        for pat, why in SUBAGENT_BASH:
            if re.search(pat, cmd):
                return _deny(f"blocked for subagent {agent}: {why}")
        m = re.search(r"\bgit\s+push\b(.*)", cmd)
        if m and not re.search(r"\bagent/[\w.-]+", m.group(1)):
            return _deny(f"subagent {agent} may push only agent/<task_id> branches")
        if re.search(r"\bgit\s+commit\b", cmd):
            b = branch if branch is not None else _current_branch(proj)
            if b in ("main", "master"):
                return _deny(f"subagent {agent} may not commit on {b}; use agent/<task_id>")
        if re.search(NETWORK_BASH, cmd) and not pol.network(agent):
            return _deny(f"{agent} has no network grant; discovery/acquisition roles fetch, others do not")
        for prefix, why in pol.sealed_prefixes(agent):
            if prefix and prefix in cmd:
                return _deny(f"sealed path {prefix}: {why}")
        if re.search(WRITE_OPS, cmd):
            for g in pol.raw.get("human_only_paths", []):
                stem = g.split("*")[0].rstrip("/")
                if stem and stem in cmd:
                    return _deny(f"shell write touching human-only path {stem}")
        return None

    if not sub:
        return None

    if tool in READ_TOOLS:
        target = ti.get("file_path") or ti.get("path") or ""
        if target:
            why = pol.sealed_for(agent, relpath(target, proj))
            if why:
                return _deny(f"{agent} may not read {target}: {why}")
        pat = ti.get("pattern", "") if tool == "Glob" else ""
        for prefix, why in pol.sealed_prefixes(agent):
            if prefix and prefix in pat:
                return _deny(f"sealed path {prefix}: {why}")
        return None

    if tool in WRITE_TOOLS:
        target = ti.get("file_path") or ti.get("notebook_path") or ""
        rel = relpath(target, proj)
        ok, why = pol.may_write(agent, rel)
        if not ok:
            return _deny(why)
        new = ti.get("content") if tool == "Write" else ti.get("new_string") or ti.get("new_source") or ""
        if tool == "MultiEdit":
            new = "\n".join(e.get("new_string", "") for e in ti.get("edits", []))
        if tool == "Write":                    # compare with the file on disk: only new lines count
            from pathlib import Path
            disk = Path(proj) / rel
            old = disk.read_text(encoding="utf-8", errors="replace") if disk.is_file() else ""
        else:
            old = ti.get("old_string", "")
        old_lines = set(old.splitlines())
        added = "\n".join(l for l in (new or "").splitlines() if l not in old_lines)
        why = pol.forbidden_text(rel, added)
        if why:
            return _deny(f"{agent} attempted a human-only change in {rel}: {why}")
        return None
    return None


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] != "pre-tool-use":
        print("usage: python -m romeco.agents.hooks pre-tool-use < event.json", file=sys.stderr)
        return 1
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0                                  # malformed input: defer, never crash the session
    out = decide(event)
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
