# Claude Code deployment of the agent harness (WP11, Part 2)

**Status (2026-10-25):** configuration and enforcement code are implemented and unit-tested (`tests/test_agents.py`, 52 tests). **Not yet live-tested:** no Claude Code session has run these subagents and hooks end to end. The first live run is task `T-WP11-001` (proposed). The format was checked against code.claude.com/docs (sub-agents, hooks, skills, permissions) on 2026-10-25. Re-check those pages before deploying, because fields change between versions.

## 1. What is where

| Piece | Path | Role |
|---|---|---|
| Policy (single source of truth) | `.claude/policy/roles.yaml` | per-role write grants, human-only paths, sealed paths, forbidden text, network grants, human reviewer IDs |
| Enforcement | `src/romeco/agents/hooks.py` | PreToolUse hook. Denies (never allows) based on the policy and the hook's `agent_type` field |
| Hook wiring and permissions | `.claude/settings.json` | one PreToolUse hook on Bash/Edit/Write/NotebookEdit/MultiEdit/Read/Grep/Glob; deny rules for force-push and history rewrite; `disableBypassPermissionsMode: "disable"` |
| Subagents | `.claude/agents/ag-*.md` | 11 roles (AG-ORCH … AG-SCRIBE), explicit tools allowlists, `maxTurns`, preloaded skills |
| Skills | `.claude/skills/{task-protocol, rights-check, review-packet, register-source, audit-result}/SKILL.md` | procedures shared across roles |
| Task contracts | `tasks/T-WPnn-nnn.yaml` (+ `TEMPLATE.yaml`), reports in `tasks/reports/` | the unit of work |
| Human decision records | `registers/review_decisions.csv`, `registers/decision_log.md`, `data/curated/semantic/questions.csv`, `config/parameters.yaml` | writable only outside subagents |
| Proposals by agents | `registers/rights_proposals.csv`, `review_queue/` (git-ignored) | inputs to human decisions |
| Checks | `python -m romeco.cli agents-check` | agent definitions ↔ policy, skills, task contracts, reports, review decisions |

## 2. How enforcement works

- **Who is restricted.**
  - Hook events from a subagent carry `agent_type`, and the hook polices only those events.
  - The researcher's own session (no `agent_type`) is restricted only by the universal rules: no force-push, no history rewriting.
  - An unknown agent type, such as the built-in `Explore`, gets no write grant at all.
- **Denials.** The hook prints `hookSpecificOutput.permissionDecision = "deny"` with a reason and exits 0. Anything it does not deny goes through Claude Code's normal permission flow, so the hook can only tighten.
- **Text-level rules.** A subagent cannot add new lines that contain:
  - `human_reviewed` (in data or registers);
  - `inspected_*` in `source_register.csv`;
  - `resolved_working` (in curated data or registers).

  For `Write`, the hook compares the new content against the file on disk, so rewriting an existing file does not trip on old rows.
- **Held-out evidence.** `benchmark/gold_heldout/**` is unreadable except to ag-val and ag-aud. This is enforced for Read, Grep and Glob, and for Bash commands that name the path.
- **Git.** Subagents:
  - commit only on `agent/<task_id>`;
  - push only `agent/*` branches;
  - cannot reset --hard, rebase, merge, clean, delete branches, or check out `main`.

## 3. Known limits (and what covers them)

| Limit | Consequence | Mitigation |
|---|---|---|
| Bash inspection is textual (documented as fragile by Claude Code itself) | A deliberately obfuscated command, e.g. `sh -c` with built strings or Python that writes files, can evade the path checks | Run agents in the sandbox or a container. Agents have no reason to obfuscate, and ag-val plus the tests catch the effects (rights, register integrity). Treat the hook as a guardrail, not a security boundary |
| Hooks in project settings only run after the folder is trusted | On an untrusted checkout nothing is enforced | First-run checklist (§5) |
| `permissionMode` in a subagent is overridden when the main session is in `bypassPermissions`, `acceptEdits` or `auto` | Approval prompts could disappear | `disableBypassPermissionsMode` is set. Run the orchestrator in `default` mode; `agents-check` rejects agents that declare permissive modes |
| `Agent(ag-…)` restriction in ag-orch applies only when it runs as the main thread (`claude --agent ag-orch`) | If invoked as a subagent, it could spawn others | Run the orchestrator only as the main thread |
| Experiment manifest-before-run is a skill rule plus audit, not a hook | A run could precede its manifest | ag-aud checks commit order. A hook-level check is a WP11 follow-up |
| Hook needs `python3` with pyyaml on PATH | If missing, the hook errors non-blockingly and the action proceeds | First-run checklist runs `pytest tests/test_agents.py` |

## 4. Running it

Interactive (the researcher present):

```bash
cd roman_economics
claude --agent ag-orch          # orchestrator as main thread, default permission mode
# then: "Show proposed tasks", approve one by editing tasks/T-…yaml (status: approved, approved_by: andrei),
# "Run T-WP11-001"
```

Unattended batches (discovery sweeps, parsing, nightly validation) use a scheduled task that runs the orchestrator with one approved task per run. Runs stop at the first human gate, and the digest in `tasks/reports/DIGEST-<date>.md` lists what awaits approval.

## 5. First-run checklist

1. `pip install -e .[dev]` and `pytest -q`. All tests pass, including `tests/test_agents.py`.
2. `python -m romeco.cli agents-check` prints `OK`.
3. Open the folder in Claude Code and accept the trust prompt.
4. Confirm that the subagents are listed (`/agents`) and the hook is active (`/hooks`).
5. **Live smoke test.** Ask ag-scribe to write `config/parameters.yaml`. Expect a deny with `[romeco policy]`. Then ask ag-mod to read `benchmark/gold_heldout/`. Expect a deny.
6. Approve and run `T-WP11-001`. Accept it only if every CQ10 candidate for ANC-PLINY-DESERT has a packet and `registers/review_decisions.csv` is unchanged.

## 6. Changing the policy

`roles.yaml` is human-only. A new module, such as `src/romeco/time.py` for T-WP10-001, needs its path added to the right role's `write` list by the researcher before the task is approved. After any policy change, run `pytest tests/test_agents.py` and `agents-check`.
