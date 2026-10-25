"""WP11 agent policy: load .claude/policy/roles.yaml and answer path/role questions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath

import yaml

ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / ".claude" / "policy" / "roles.yaml"


@dataclass(frozen=True)
class Policy:
    raw: dict

    @property
    def humans(self) -> list[str]:
        return list(self.raw.get("humans", []))

    @property
    def roles(self) -> dict[str, dict]:
        return self.raw.get("roles", {})

    def role(self, agent_type: str | None) -> dict | None:
        return self.roles.get(agent_type or "")

    # ------------------------------------------------------------- paths
    @staticmethod
    def match(rel: str, glob: str) -> bool:
        p = PurePosixPath(rel)
        return p.full_match(glob) or (glob.endswith("/**") and rel == glob[:-3])

    def human_only(self, rel: str) -> bool:
        return any(self.match(rel, g) for g in self.raw.get("human_only_paths", []))

    def may_write(self, agent_type: str | None, rel: str) -> tuple[bool, str]:
        if self.human_only(rel):
            return False, f"{rel} is human-only (epistemic decisions, policy and ontology stay with the researcher)"
        r = self.role(agent_type)
        if r is None:
            return False, f"agent type {agent_type!r} has no write grant in .claude/policy/roles.yaml"
        if any(self.match(rel, g) for g in r.get("write", [])):
            return True, ""
        return False, f"{agent_type} may not write {rel} (allowed: {', '.join(r.get('write', []))})"

    def sealed_for(self, agent_type: str | None, rel: str) -> str | None:
        for s in self.raw.get("sealed_paths", []):
            if self.match(rel, s["glob"]) and agent_type not in s.get("readers", []):
                return s.get("reason", "sealed path")
        return None

    def sealed_prefixes(self, agent_type: str | None) -> list[tuple[str, str]]:
        out = []
        for s in self.raw.get("sealed_paths", []):
            if agent_type not in s.get("readers", []):
                out.append((s["glob"].split("*")[0].rstrip("/"), s.get("reason", "sealed path")))
        return out

    def forbidden_text(self, rel: str, text: str) -> str | None:
        for rule in self.raw.get("forbidden_new_text", []):
            files = rule.get("files")
            if files and not any(self.match(rel, f) for f in files):
                continue
            if re.search(rule["pattern"], text or ""):
                return rule["reason"]
        return None

    def network(self, agent_type: str | None) -> bool:
        r = self.role(agent_type)
        return bool(r and r.get("network"))


@lru_cache(maxsize=4)
def load(path: str | None = None) -> Policy:
    return Policy(yaml.safe_load(Path(path or POLICY_PATH).read_text(encoding="utf-8")))


def relpath(file_path: str, project_dir: str | Path) -> str:
    p = Path(file_path)
    base = Path(project_dir).resolve()
    if not p.is_absolute():
        p = base / p
    try:
        return p.resolve().relative_to(base).as_posix()
    except ValueError:
        return "/" + p.resolve().as_posix().lstrip("/")   # outside the project: never matches a grant
