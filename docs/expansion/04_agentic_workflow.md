# Agentic workflow design (basis for a Claude Code deployment)

**Status:** design. Part 2 will turn this into concrete Claude Code configuration (subagent definitions, skills, hooks, permission settings), checked against the Claude Code documentation current at deployment. Nothing here is deployed.

## 1. Principle: agents move work items between registered states; humans make the epistemic decisions

The registers already define the states:

- the eight corpus pipeline states;
- candidate → claim;
- open → resolved_working questions;
- parameter status;
- experiment registration.

Agents work **inside** these state machines. Any transition that changes what the project believes needs a recorded human approval. That includes:

- promoting a candidate to a claim;
- selecting a position;
- changing a parameter's status or value;
- accepting an identity claim with high impact.

| Transition | Who | Recorded where |
|---|---|---|
| discovered → screened → eligible | agent (rule-based screening criteria, logged) | `registers/corpus/pipeline_state.csv`, `search_log.csv` |
| eligible → acquired | agent, **only through the rights gate** (permitted source, licence recorded, no access controls bypassed) | `acquisition_log.csv` |
| acquired → parsed → extracted | agent | `parse_manifest.csv`, `extractions.csv` |
| candidate → claim | **human** approves an agent-prepared review packet | the claim row carries `review_status = human_reviewed` and the reviewer ID |
| claim → question position; question → resolved_working | **human** decision (D-number) | `questions.csv`, `decision_log.md` |
| parameter added or changed | agent proposes; **human** approves | `parameters.yaml` + D-number |
| experiment registered → run | agent, *after* the manifest (expectations, held-out evidence) is committed | `experiment_registry.csv`, `runs/` |
| result → reported finding | agent drafts; an **independent auditor** agent checks; human signs off | WP result section |

## 2. Agent roles

Each role has one job, a narrow tool set and an input/output contract. Roles are stable IDs (`AG-*`).

| ID | Role | Inputs | Outputs | May | May never |
|---|---|---|---|---|---|
| AG-ORCH | Orchestrator | WP plan, register states, open tasks | task assignments, a daily state digest | read everything; create tasks; spawn the other roles | edit evidence, parameters or decisions; merge |
| AG-DISC | Discovery librarian | search briefs per domain, existing bibliography | candidate sources (metadata only), `search_log` rows | web search; citation chaining over parsed bibliographies | mark anything inspected; invent metadata |
| AG-RIGHTS | Rights auditor | candidate source | licence/terms record, a redistribution decision proposal | read terms pages, robots, licence files | acquire; decide ambiguous cases (escalates) |
| AG-ACQ | Acquisition | eligible + rights-cleared items | files with sha256, acquisition log | download from cleared hosts at logged rate limits | bypass paywalls, logins, bot checks, robots disallow; use mirrors of blocked content |
| AG-PARSE | Parser/extractor | acquired items | anchored text units, candidates (versioned extractor) | run parsers, OCR, extractors | write claims |
| AG-REV | Review-packet preparer | candidates + page images | a review packet: candidate, page image crop, context, proposed claim fields, rivals found | render pages; draft claim rows marked `proposed` | approve its own packet |
| AG-CUR | Curator (per domain) | approved packets | claim rows, identity claims, questions (open), coverage maps | write curated CSVs on a branch | resolve questions; change selected positions |
| AG-MOD | Modeller (per RQ) | registered RQ, parameter register | model code, experiment manifests, runs | write code and run registered experiments | run before the manifest is committed; peek at held-out evidence |
| AG-VAL | Validator | any branch | pytest, SHACL, CQ answers, rights checks, dating-circularity checks | block a merge | fix the evidence to make tests pass |
| AG-AUD | Independent auditor | a finished result, **without** the producing agent's transcript | an audit report: re-derived numbers, source spot-checks, overclaim flags | re-run code; read sources | see the producer's reasoning before auditing |
| AG-SCRIBE | Scribe | merged work | research log entries, doc updates, project-doc sync | write docs and logs | change results |

**Why separate AG-REV and AG-AUD.**
- The producing agent must not grade its own work.
- The auditor starts cold, from the repository and the claim of the result.

## 3. Task contract (every agent task)

```yaml
task_id: T-<WP>-<n>            # stable, appended
role: AG-PARSE
wp: WP10
inputs: [items: [...], extractor: v0.3]
outputs_expected: [data/derived/corpus/extractions.csv rows for items]
acceptance:                    # machine-checkable where possible
  - pytest -q passes
  - every new row has anchor_ref and extractor_version
  - no snippet from rights_id in {RGT-*-ARR} (test_rights)
forbidden: [write registers/source_register.csv access_status upgrades]
budget: {max_tool_calls: 200, max_wall_minutes: 60}
stop_and_escalate_if:
  - rights unclear
  - a reading changes a parameter-feeding claim
  - a test can only be passed by editing evidence
report: summary + files changed + what was NOT checked
```

## 4. Guardrails (to become hooks, permissions and tests in Part 2)

| Risk | Guardrail |
|---|---|
| Fabricated citations or pages | Every `source_id`, page and locus written must resolve to a register row or a parsed unit (test). Agents cannot add `inspected_*` access status without a parse-manifest entry for that source |
| Candidate promoted silently | SHACL CandidateShape + test that `human_reviewed` rows carry a reviewer ID that is in the human list |
| Rights breach | Rights gate test (exists); acquisition only from hosts with a cleared policy row; snippet test |
| Prompt injection from ingested texts | Ingested text is data. Agents never execute instructions found in sources, and parsed text is passed as quoted data in prompts. AG-ACQ and AG-PARSE run without push or network-write permissions |
| Peeking at held-out evidence | Held-out IDs live in a file that AG-MOD cannot read until the manifest commit exists (hook on read) |
| Over-claiming | AG-AUD checks the claim tags ([sourced]/[calculated]/[assumption]) and the causal language list ("caused", "led to", "because") against the registered identification strategy |
| Circular dating | AG-VAL runs the `dating_dependency` cycle check |
| Synthetic leakage | `record_origin` CHECK constraints; origin label is preserved in exports (WP7 test) |
| Runaway cost | Per-task budgets; the orchestrator works from a queue with daily caps; scheduled runs do bounded batches |
| Destructive git operations | Agents work on `agent/<task_id>` branches; only a human merges to `main`; no force-push; no deletes outside the agent's own outputs |

## 5. Human touchpoints (the only places the researcher must act)

1. Approve or reject review packets. These are batched in a review queue artifact, sorted by impact: parameter-feeding first.
2. Decide questions (D-numbers) when a resolution is proposed.
3. Approve parameter changes and experiment registrations.
4. Supply sources the agents cannot legally acquire.
5. Merge branches after the validator and auditor pass.

Everything else runs without the researcher. The orchestrator posts a digest of what moved, what is blocked and what awaits approval.

## 6. Run modes

| Mode | Use |
|---|---|
| Interactive | design, decisions, reviewing packets |
| Scheduled batch | discovery sweeps, acquisition queues, parsing and extraction, coverage-map regeneration, nightly validation |
| On-demand pipeline | an end-to-end chain for one domain module (discover → … → review packets), stopping at the first human gate |

## 7. Repository layout additions (planned)

```
.claude/agents/        # one definition per AG-* role (Part 2)
.claude/skills/        # reusable procedures: review-packet, rights-check, dating-mc, coverage-map
.claude/settings.json  # permissions and hooks (Part 2)
tasks/                 # task contracts (YAML), one per T-id
review_queue/          # review packets awaiting human decision
runs/                  # experiment runs (manifest-first)
docs/expansion/        # this documentation
```
