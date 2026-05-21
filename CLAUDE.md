# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A curated collection of Claude Code skills (prompt-based tooling for Claude Code sessions). Each top-level directory is a standalone skill containing at minimum a `SKILL.md` file. The `superpowers/` directory is a git submodule.

## Skill Authorship

- `manuscript-review/` — authored by the repo owner (Michael Romano)
- `superpowers/` — git submodule from `github.com/obra/superpowers` (Jesse Vincent, MIT)
- Most others — authored by K-Dense Inc. (MIT or BSD-3-Clause)
- `boy-scout/`, `clean-*`, `python-clean-code/` — from `github.com/ertugrul-dmr/clean-code-skills` (MIT)

## Adding a New Skill

1. Create a directory named with the skill's kebab-case slug
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`, optionally `license`, `metadata.skill-author`, `allowed-tools`, `when_to_use`)
3. Optionally add `references/` and `scripts/` subdirectories
4. Update `README.md` — place it in the correct author section (Mine / Others / Submodules) and add a row to the summary table
5. Do NOT include proprietary/non-redistributable skills in this repo; reference them in the "Recommended Proprietary Skills" section instead

## README Style

The README is written in the voice of Napoleon Dynamite. Maintain that tone when adding entries.

## Repo Conventions

- No build system, no tests, no package manager (except `superpowers/` which has a `package.json` for versioning only)
- Skills are plain markdown; scripts are Python
- The `.gitmodules` file tracks the `superpowers` submodule
- Remote: `git@github.com:mfromano/great-skills.git`
