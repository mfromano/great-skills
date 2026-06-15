#!/usr/bin/env python3
"""Regenerate README.md from all SKILL.md frontmatter in the skills directory."""

import os
import re
import sys

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(SKILLS_DIR, "README.md")

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(skill_md_path):
    try:
        with open(skill_md_path, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None

    m = FRONTMATTER_RE.match(content)
    if not m:
        return None

    block = m.group(1)
    data = {}

    # Parse name and description (simple key: value, handling multiline |)
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        kv = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if val == "|":
                # block scalar — collect indented lines
                parts = []
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or lines[i] == ""):
                    parts.append(lines[i])
                    i += 1
                data[key] = "\n".join(parts).strip()
                continue
            else:
                data[key] = val
        # nested metadata.skill-author
        nested = re.match(r"^\s+skill-author:\s*(.*)", line)
        if nested:
            data["skill-author"] = nested.group(1).strip()
        i += 1

    return data


def collect_skills():
    direct = []
    submodule = []

    for entry in sorted(os.listdir(SKILLS_DIR)):
        full_path = os.path.join(SKILLS_DIR, entry)
        skill_md = os.path.join(full_path, "SKILL.md")

        # Skip non-directories and entries without SKILL.md
        if not os.path.isdir(full_path):
            continue
        # Follow symlinks when checking for SKILL.md
        if not os.path.isfile(skill_md):
            continue
        # Skip submodule source dirs (lab-skills, superpowers) — they're not top-level skills
        if entry in ("superpowers", "lab-skills"):
            continue

        fm = parse_frontmatter(skill_md)
        if fm is None:
            continue

        name = fm.get("name", entry)
        description = fm.get("description", "")
        author = fm.get("skill-author", fm.get("metadata", {}) if isinstance(fm.get("metadata"), str) else "")
        if not author:
            author = "—"

        # Truncate description to first sentence for table readability
        short_desc = description.split("\n")[0]
        if len(short_desc) > 120:
            short_desc = short_desc[:117] + "..."

        row = {"name": name, "description": short_desc, "author": author}

        if os.path.islink(full_path):
            submodule.append(row)
        else:
            direct.append(row)

    return direct, submodule


def render_table(rows):
    if not rows:
        return "_None yet._\n"
    lines = ["| Skill | Description | Author |",
             "|-------|-------------|--------|"]
    for r in sorted(rows, key=lambda x: x["name"]):
        name = r["name"].replace("|", "\\|")
        desc = r["description"].replace("|", "\\|")
        author = r["author"].replace("|", "\\|")
        lines.append(f"| `{name}` | {desc} | {author} |")
    return "\n".join(lines) + "\n"


def main():
    direct, submodule = collect_skills()

    readme = """\
# Skills

```
        ___
       /   \\
      | o o |
      |  >  |
      | \\_/ |
       \\___/
      __|_|__
     /       \\
    | VOTE 4  |
    | PEDRO   |
     \\_______/
        | |
       /| |\\
      / | | \\
     /  | |  \\
    /   | |   \\
   /    | |    \\
  |_____|_|_____|
        | |
       _| |_
      |     |
      |     |
      |_____|
```

Gosh! This is like the best collection of Claude Code skills ever made. Probably the best anyone's ever seen. I'm not even joking. These skills have like incredible capabilities and stuff. If you don't use them you're basically an idiot.

---

## My Skills

These ones I made myself. With my own hands. Like a craft.

"""
    readme += render_table(direct)
    readme += """
---

## Submodule Skills

These came from other places. Like when you find a really good mix tape that isn't yours but you still listen to it.

"""
    readme += render_table(submodule)
    readme += "\n"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"README.md updated ({len(direct)} direct, {len(submodule)} submodule skills)")


if __name__ == "__main__":
    main()
