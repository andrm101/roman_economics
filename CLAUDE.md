# Working conventions for AI-assisted sessions

- Read `docs/research_design.md`, `registers/decision_log.md` and `registers/research_log.md` before proposing new work.
- Keep stage IDs stable: WP0–WP8, RQ1–RQ3, H1a/H1b…, K1…, D001…, E000…. Never renumber; append.
- Never invent bibliographic data, page numbers, readings or access claims. Register every new source in `registers/source_register.csv` with an honest `access_status`.
- A claim read only through a summary or abstract is `machine_summary_only`, never "inspected".
- New parameters go in `config/parameters.yaml` with status, bounds and evidence IDs that resolve (`pytest` checks this).
- New conversions go in `romeco.units.RULES` with scope, source and status.
- Tag claims in research outputs as [sourced], [calculated], or [assumption].
- Run `pytest` before committing. Append a dated entry to `registers/research_log.md` each session.

## Agent harness (WP11)
- Subagents (`.claude/agents/ag-*`) are bound by `.claude/policy/roles.yaml`, enforced by the PreToolUse hook `romeco.agents.hooks`. See `docs/expansion/06_claude_code_deployment.md`.
- Every agent task has a contract in `tasks/` and a report in `tasks/reports/` (skill `task-protocol`).
- Only the researcher writes decisions, review decisions, questions, parameters, ontology and policy. Agents propose.
- Run `python -m romeco.cli agents-check` after changing agents, skills, tasks or policy.
