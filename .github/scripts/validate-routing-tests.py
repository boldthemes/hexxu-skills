#!/usr/bin/env python3
# validate-routing-tests.py — schema check for SKILL.tests.md routing test files.
#
# This is the always-runs portion of the routing-margin gate. It enforces the
# YAML frontmatter shape defined in docs/routing-tests.md without invoking any
# external model. It runs on every PR that touches skills/**.
#
# The oracle portion (sending positives/negatives through a model and asserting
# routing margins) requires an ANTHROPIC_API_KEY repo secret and is gated in
# the workflow. See docs/routing-tests.md "What the CI gate does".
#
# Usage:
#   validate-routing-tests.py <SKILL.tests.md> [<SKILL.tests.md> ...]
#
# Exit codes:
#   0 — all files valid
#   1 — at least one file failed validation (annotations printed)
#   2 — invocation error (missing file, bad arg)

import os
import re
import sys
from pathlib import Path

try:
    import yaml  # pyyaml; preinstalled on ubuntu-latest GH runners
except ImportError:
    print("::error::pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


SCHEMA_VERSION = "hexxu-routing-test/v1"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class V:
    """Validation error accumulator with file/line annotation support."""

    def __init__(self, path: Path):
        self.path = path
        self.errors: list[str] = []

    def err(self, msg: str, line: int = 1) -> None:
        # GH Actions annotation format; surfaces in PR diff view.
        print(f"::error file={self.path},line={line}::{msg}")
        self.errors.append(msg)

    def ok(self) -> bool:
        return not self.errors


def load_frontmatter(path: Path, v: V) -> dict | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        v.err(f"cannot read file: {e}")
        return None

    m = FRONTMATTER_RE.match(content)
    if not m:
        v.err("file must start with YAML frontmatter (--- ... ---)")
        return None

    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        v.err(f"invalid YAML in frontmatter: {e}")
        return None

    if not isinstance(data, dict):
        v.err("frontmatter must parse to a YAML mapping")
        return None
    return data


def load_skill_non_goals(skill_dir: Path) -> list[str]:
    """Return the non_goals list from the sibling SKILL.md, or [] on any failure."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return []
    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError:
        return []
    m = FRONTMATTER_RE.match(content)
    if not m:
        return []
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return []
    if not isinstance(data, dict):
        return []
    ng = data.get("non_goals")
    return ng if isinstance(ng, list) else []


def normalize(s: str) -> str:
    """Whitespace-collapse + casefold for non_goals substring matching."""
    return re.sub(r"\s+", " ", s).strip().casefold()


def validate_file(path: Path) -> bool:
    v = V(path)
    data = load_frontmatter(path, v)
    if data is None:
        return v.ok()

    # schema
    schema = data.get("schema")
    if schema != SCHEMA_VERSION:
        v.err(f"schema must be '{SCHEMA_VERSION}' (got {schema!r})")

    # margin
    margin = data.get("margin")
    if not isinstance(margin, (int, float)) or not (0.0 <= float(margin) <= 1.0):
        v.err(f"margin must be a number in [0.0, 1.0] (got {margin!r})")

    # positive_prompts
    pos = data.get("positive_prompts")
    if not isinstance(pos, list) or not (3 <= len(pos) <= 10):
        v.err(f"positive_prompts must be a list of 3-10 strings (got {type(pos).__name__})")
    else:
        for i, p in enumerate(pos):
            if not isinstance(p, str) or len(p.strip()) < 10:
                v.err(f"positive_prompts[{i}] must be a non-empty string >= 10 chars")
        if len(set(pos)) != len(pos):
            v.err("positive_prompts must be unique")

    # negative_prompts
    neg = data.get("negative_prompts")
    skill_dir = path.parent
    skill_name = skill_dir.name
    non_goals_norm = [normalize(g) for g in load_skill_non_goals(skill_dir)]

    if not isinstance(neg, list) or not (2 <= len(neg) <= 8):
        v.err(f"negative_prompts must be a list of 2-8 objects (got {type(neg).__name__})")
    else:
        seen_prompts = set()
        for i, item in enumerate(neg):
            if not isinstance(item, dict):
                v.err(f"negative_prompts[{i}] must be a mapping with prompt/why/must_not_route_to")
                continue
            p = item.get("prompt")
            why = item.get("why")
            mnrt = item.get("must_not_route_to")

            if not isinstance(p, str) or len(p.strip()) < 10:
                v.err(f"negative_prompts[{i}].prompt must be a non-empty string >= 10 chars")
            elif p in seen_prompts:
                v.err(f"negative_prompts[{i}].prompt is duplicated")
            else:
                seen_prompts.add(p)

            if not isinstance(why, str) or len(why.strip()) < 10:
                v.err(f"negative_prompts[{i}].why must be a non-empty string >= 10 chars")
            elif non_goals_norm and normalize(why) not in non_goals_norm:
                v.err(
                    f"negative_prompts[{i}].why must verbatim-cite a non_goals entry "
                    f"from the sibling SKILL.md. Got {why!r}; "
                    f"non_goals are {[g for g in load_skill_non_goals(skill_dir)]}"
                )

            if not isinstance(mnrt, list) or not mnrt:
                v.err(f"negative_prompts[{i}].must_not_route_to must be a non-empty list of skill names")
            else:
                for j, n in enumerate(mnrt):
                    if not isinstance(n, str) or not NAME_RE.match(n):
                        v.err(
                            f"negative_prompts[{i}].must_not_route_to[{j}] must be a valid skill name "
                            f"(lowercase + hyphens). Got {n!r}"
                        )
                # The skill itself MUST appear in its own negatives' must_not_route_to.
                # That's the whole point — we are asserting "not me".
                if skill_name not in mnrt:
                    v.err(
                        f"negative_prompts[{i}].must_not_route_to must include this skill's own name "
                        f"({skill_name!r}). The negative is asserting routing AWAY from this skill."
                    )

    return v.ok()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate-routing-tests.py <SKILL.tests.md> [...]", file=sys.stderr)
        return 2

    failures = 0
    for arg in argv[1:]:
        path = Path(arg)
        if not path.is_file():
            print(f"::error::file not found: {path}")
            failures += 1
            continue
        if not validate_file(path):
            failures += 1

    if failures:
        print(f"\n{failures} file(s) failed routing-test schema validation.")
        print("See docs/routing-tests.md for the spec.")
        return 1
    print(f"All {len(argv) - 1} routing test file(s) pass schema validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
