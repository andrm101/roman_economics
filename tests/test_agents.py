"""WP11 harness tests: planted violations must be denied; legitimate actions must pass."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from romeco.agents import hooks, tasks
from romeco.agents.policy import load

ROOT = Path(__file__).resolve().parents[1]
P = str(ROOT)


def ev(tool, agent=None, **ti):
    e = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": ti, "cwd": P}
    if agent:
        e["agent_type"] = agent
    return e


def denied(e, branch="agent/T-WP11-001"):
    out = hooks.decide(e, project_dir=P, branch=branch)
    return bool(out) and out["hookSpecificOutput"]["permissionDecision"] == "deny"


# ------------------------------------------------------------------ planted violations (must be denied)
def test_unapproved_promotion_denied():
    assert denied(ev("Edit", "ag-cur", file_path=f"{P}/data/curated/context/manual_anchors.csv",
                     old_string="x,inspected", new_string="x,human_reviewed"))


def test_access_status_upgrade_denied():
    assert denied(ev("Edit", "ag-cur", file_path=f"{P}/registers/source_register.csv",
                     old_string="SRC-X,work,,,t,,,en,cited_only", new_string="SRC-X,work,,,t,,,en,inspected_full_text"))


def test_existing_inspected_rows_do_not_trigger_on_unrelated_write():
    # Write of the whole register with one new cited_only row: existing inspected rows are not "new text"
    text = (ROOT / "registers" / "source_register.csv").read_text(encoding="utf-8")
    new = text + "SRC-NEW-0001,work,A. Author,2020,T,,,en,cited_only,,,,\n"
    assert not denied(ev("Write", "ag-cur", file_path=f"{P}/registers/source_register.csv", content=new))


@pytest.mark.parametrize("path", ["config/parameters.yaml", "registers/decision_log.md", "registers/review_decisions.csv",
                                  "data/curated/semantic/questions.csv", ".claude/policy/roles.yaml", "ontology/shapes.ttl"])
@pytest.mark.parametrize("agent", ["ag-cur", "ag-mod", "ag-orch", "ag-scribe"])
def test_human_only_paths_denied_for_every_role(path, agent):
    assert denied(ev("Write", agent, file_path=f"{P}/{path}", content="x"))


def test_role_outside_grant_denied():
    assert denied(ev("Edit", "ag-parse", file_path=f"{P}/src/romeco/m0/fiscal.py", old_string="a", new_string="b"))
    assert denied(ev("Write", "Explore", file_path=f"{P}/docs/x.md", content="x"))   # unknown agent type


def test_heldout_peek_denied():
    assert denied(ev("Read", "ag-parse", file_path=f"{P}/benchmark/gold_heldout/G001.csv"))
    assert denied(ev("Grep", "ag-mod", pattern="x", path=f"{P}/benchmark/gold_heldout"))
    assert denied(ev("Bash", "ag-parse", command="cat benchmark/gold_heldout/*.csv"))
    assert not denied(ev("Read", "ag-aud", file_path=f"{P}/benchmark/gold_heldout/G001.csv"))


@pytest.mark.parametrize("cmd", ["git push --force origin main", "git push -f origin agent/x", "git push origin +agent/x",
                                 "git filter-branch --tree-filter x"])
def test_force_push_denied_for_everyone(cmd):
    assert denied(ev("Bash", None, command=cmd))
    assert denied(ev("Bash", "ag-orch", command=cmd))


@pytest.mark.parametrize("cmd", ["git push origin main", "git reset --hard HEAD~1", "git checkout main",
                                 "git merge agent/T-WP11-001", "rm -rf data", "git rebase main"])
def test_destructive_git_denied_for_subagents(cmd):
    assert denied(ev("Bash", "ag-cur", command=cmd))


def test_commit_on_main_denied_for_subagent():
    assert denied(ev("Bash", "ag-mod", command="git commit -m x"), branch="main")
    assert not denied(ev("Bash", "ag-mod", command="git commit -m x"), branch="agent/T-WP10-001")


def test_network_only_for_granted_roles():
    assert denied(ev("Bash", "ag-parse", command="curl -sL https://example.org/x.pdf -o x.pdf"))
    assert not denied(ev("Bash", "ag-acq", command="curl -sI https://example.org/robots.txt"))


def test_shell_write_to_human_only_path_denied():
    assert denied(ev("Bash", "ag-disc", command="sed -i 's/0.25/0.5/' config/parameters.yaml"))
    assert denied(ev("Bash", "ag-scribe", command="echo D099 >> registers/decision_log.md"))


# ------------------------------------------------------------------ legitimate actions (must pass)
def test_researcher_session_unrestricted_except_universal():
    assert not denied(ev("Write", None, file_path=f"{P}/config/parameters.yaml", content="x"))
    assert not denied(ev("Bash", None, command="git push origin main"))
    assert not denied(ev("Read", None, file_path=f"{P}/benchmark/gold_heldout/G001.csv"))


def test_role_inside_grant_allowed():
    assert not denied(ev("Write", "ag-rev", file_path=f"{P}/review_queue/EXT-1/packet.md", content="x"))
    assert not denied(ev("Edit", "ag-parse", file_path=f"{P}/src/romeco/corpus/extract.py", old_string="a", new_string="b"))
    assert not denied(ev("Bash", "ag-val", command="pytest -q"))
    assert not denied(ev("Bash", "ag-scribe", command="git push origin agent/T-WP11-001"))


def test_hook_cli_contract():
    e = ev("Write", "ag-scribe", file_path=f"{P}/config/parameters.yaml", content="x")
    env = {**os.environ, "CLAUDE_PROJECT_DIR": P, "PYTHONPATH": f"{P}/src"}
    r = subprocess.run([sys.executable, "-m", "romeco.agents.hooks", "pre-tool-use"], input=json.dumps(e),
                       capture_output=True, text=True, env=env, timeout=30)
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert out["hookSpecificOutput"]["permissionDecision"] == "deny"
    r = subprocess.run([sys.executable, "-m", "romeco.agents.hooks", "pre-tool-use"], input="not json",
                       capture_output=True, text=True, env=env, timeout=30)
    assert r.returncode == 0 and r.stdout == ""     # malformed input defers, never crashes


# ------------------------------------------------------------------ configuration consistency
def test_agents_check_passes():
    assert tasks.check_all() == []


def test_settings_hook_wired():
    s = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    cmds = [h["command"] for g in s["hooks"]["PreToolUse"] for h in g["hooks"]]
    assert any("romeco.agents.hooks pre-tool-use" in c for c in cmds)
    assert s["permissions"]["disableBypassPermissionsMode"] == "disable"


def test_task_contract_validation_catches_gaps():
    t = yaml.safe_load((ROOT / "tasks" / "TEMPLATE.yaml").read_text(encoding="utf-8"))
    t["task_id"] = "T-WP99-001"
    assert tasks.check_task(t) == []
    bad = dict(t, acceptance=[])
    assert any("acceptance" in e for e in tasks.check_task(bad))
    assert any("unknown role" in e for e in tasks.check_task(dict(t, role="ag-root")))
    assert any("report" in e for e in tasks.check_task(dict(t, status="done")))


def test_report_needs_not_checked():
    ok = "## Summary\nx\n## Files changed\nx\n## Checks run\nx\n## Not checked\npage images of p. 40\n## Escalations\nnone\n"
    assert tasks.check_report(ok) == []
    assert tasks.check_report(ok.replace("page images of p. 40", "")) != []


def test_review_decision_needs_known_human(tmp_path):
    f = tmp_path / "d.csv"
    f.write_text("decision_id,ext_id,decision,reviewer,date,claim_id,corrections,note\n"
                 "RVD-0001,EXT-1,accept,ag-cur,2026-10-25,,,\n", encoding="utf-8")
    errs = tasks.check_review_decisions(f)
    assert any("not in policy humans" in e for e in errs) and any("claim_id" in e for e in errs)


def test_every_role_has_agent_and_preloads_protocol():
    names = {p.stem for p in (ROOT / ".claude" / "agents").glob("*.md")}
    assert names == set(load().roles)


def test_review_packet_dry_run(tmp_path):
    from romeco.agents.review import make_packet
    out = make_packet("EXT-68c25790bd89-00053-001", out_root=tmp_path)
    text = (out / "packet.md").read_text(encoding="utf-8")
    assert "Candidate only (D024)" in text and "SRC-ADAMS-2007" in text
    raw = ROOT / "data" / "raw" / "corpus" / "68"
    if raw.exists():
        assert (out / "page.png").exists()
