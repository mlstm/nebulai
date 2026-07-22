#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""Validate an Agent Skill directory against the agentskills.io specification.

Usage:
    python3 validate.py <skill-dir>

Exits 0 if valid, 1 if any errors are found. Emits a JSON report to stdout.
"""
import json
import os
import re
import sys


def parse_frontmatter(text):
    """Return (frontmatter_dict, body) or raise ValueError. Minimal YAML subset."""
    if not text.startswith("---"):
        raise ValueError("SKILL.md must begin with a '---' frontmatter fence")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Frontmatter must be closed with a second '---' fence")
    raw, body = parts[1], parts[2]
    fm = {}
    key = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s+", line) and key is not None:
            continue  # nested mapping value; not validated here
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            val = m.group(2).strip().strip('"').strip("'")
            fm[key] = val
    return fm, body


def validate(skill_dir):
    errors = []
    warnings = []

    skill_dir = os.path.abspath(skill_dir.rstrip("/"))
    dir_name = os.path.basename(skill_dir)
    skill_md = os.path.join(skill_dir, "SKILL.md")

    if not os.path.isfile(skill_md):
        errors.append(f"Missing required file: {skill_md}")
        return errors, warnings

    with open(skill_md, encoding="utf-8") as f:
        text = f.read()

    try:
        fm, body = parse_frontmatter(text)
    except ValueError as e:
        errors.append(str(e))
        return errors, warnings

    # name
    name = fm.get("name")
    if not name:
        errors.append("Frontmatter missing required field: name")
    else:
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            errors.append(
                "name must be lowercase a-z/0-9/hyphens, no leading/trailing/"
                f"consecutive hyphens (got: {name!r})"
            )
        if not (1 <= len(name) <= 64):
            errors.append(f"name must be 1-64 chars (got {len(name)})")
        if name != dir_name:
            errors.append(
                f"name ({name!r}) must match parent directory name ({dir_name!r})"
            )

    # description
    desc = fm.get("description")
    if not desc:
        errors.append("Frontmatter missing required field: description")
    else:
        if len(desc) > 1024:
            errors.append(f"description must be <=1024 chars (got {len(desc)})")
        if len(desc) < 20:
            warnings.append("description is very short; state what it does AND when to use it")

    # compatibility length
    compat = fm.get("compatibility")
    if compat and len(compat) > 500:
        errors.append(f"compatibility must be <=500 chars (got {len(compat)})")

    # referenced relative files exist (skip globs and inline placeholders)
    seen = set()
    for ref in re.findall(r"`((?:scripts|references|assets)/[^`\s]+)`", body):
        if "*" in ref or "<" in ref or ref in seen:
            continue
        seen.add(ref)
        path = os.path.join(skill_dir, ref)
        if not os.path.exists(path):
            warnings.append(f"Referenced file not found: {ref}")

    # leanness
    lines = body.count("\n")
    if lines > 500:
        warnings.append(f"SKILL.md body is {lines} lines (>500); move detail to references/")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate.py <skill-dir>", file=sys.stderr)
        sys.exit(2)
    errors, warnings = validate(sys.argv[1])
    report = {"valid": not errors, "errors": errors, "warnings": warnings}
    print(json.dumps(report, indent=2))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
