# obsidian — query router hub

A thin **router** skill. It does not search anything itself; it dispatches a generic
"search my Obsidian vault" ask to whichever of three systems fits, all of which index
the same vault (`~/Obsidian/Radiology`).

## Why this skill exists

Three query systems point at the same vault but live in different scopes:

- **obsidian-rag** — project-scoped to `~/obsidian-rag` (loads only inside that repo).
- **wiki-query** / **`llm-wiki`** / the `wiki-*` family — global (shipped by the
  `obsidian_wiki` pip package as symlinked skills).
- **qmd** — a global node CLI.

Nothing tied them together at the top level, so a plain "search my notes" request had no
obvious entry point. This hub is that entry point — the one skill that knows all three
exist and picks by question shape. See `SKILL.md` for the routing table.

## Design: hub-and-spoke, not nesting

Claude Code skill discovery is **flat** — a skill is a `SKILL.md` one level under a
skills root; deeper nesting is not walked (nested skills only surface via top-level
symlinks). So `obsidian-rag` **cannot** be a literal child of an `obsidian/` directory.

Instead this follows the existing **`llm-wiki` hub pattern**: `llm-wiki` is a "theory"
hub that ~31 `wiki-*` skills cite by relative path ("reference, don't duplicate"). The
`obsidian` hub does the same — it routes to `obsidian-rag/SKILL.md` and
`llm-wiki/SKILL.md` for the detailed workflows and never copies them.

## Routing, in one line each

| Question shape | Goes to | Entry point |
|---|---|---|
| Verbatim source text, protocols, paper figures, MRI protocol composition | **obsidian-rag** | `cd ~/obsidian-rag && uv run search.py "…"` |
| "What do I know about X", relationships, multi-hop, synthesis | **wiki-query** (GraphRAG) | the `wiki-query` skill |
| Fast concept-aware semantic scan of the raw vault | **qmd** | `qmd query "…"` |

Caveat baked into the routing: the compiled wiki is currently near-empty
(`index.md` → "No pages yet"), so prefer obsidian-rag or qmd for real answers until
sources are ingested via `wiki-ingest` / `wiki-capture`.

## Where things live

- This skill: `~/.claude/skills/obsidian/` — tracked in the **great-skills** repo
  (`git@github.com:mfromano/great-skills.git`).
- obsidian-rag skill + toolkit: `~/obsidian-rag/` (repo
  `git@github.com:mfromano/obsidian-rag.git`).
- wiki system: the `obsidian_wiki` package's bundled skills, symlinked into
  `~/.claude/skills/` (`llm-wiki`, `wiki-query`, `wiki-ingest`, …).
