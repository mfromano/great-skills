---
name: obsidian
description: >
  Router hub for querying the user's Obsidian vault when it is unclear which search
  system to use. Triggers on generic vault intents like "search my obsidian vault",
  "search my notes", "find in my vault", "what do I know about X", "look this up in my
  notes". Dispatches to one of three systems that all index the same vault: obsidian-rag
  (exact verbatim source retrieval + MRI protocol composition), wiki-query (GraphRAG
  synthesis over the compiled wiki), and qmd (fast semantic scan). This is a thin router
  — it points at the right system; the detailed docs live in each spoke skill.
---

# Obsidian — Query Router

Three separate systems query the **same** Obsidian vault, each answering a different
kind of question. They are scattered across scopes (obsidian-rag is project-scoped to
`~/obsidian-rag`; the `wiki-*` family and `qmd` are global), so this hub is the single
entry point that knows all three exist. **Pick by what the user is asking for**, then
follow the linked spoke skill for the full workflow.

## Routing table

| Question shape | System | Entry point | Full docs |
|---|---|---|---|
| "What does the source *say*?" — protocols, verbatim policy/guide text, paper summaries, figures; also **composing** MRI protocols | **obsidian-rag** (sqlite + ollama, verbatim units, collection-scoped, source back-links) | `cd ~/obsidian-rag && uv run search.py "…"` | `obsidian-rag/SKILL.md` (loads inside `~/obsidian-rag`) |
| "What do I *know* about X?", relationship / multi-hop ("how is X connected to Y?"), synthesis, gap questions | **obsidian-wiki** GraphRAG over the *compiled* wiki | the **`wiki-query`** skill (`obsidian-wiki graph-query "$VAULT" "…" --pretty`) | `wiki-query/SKILL.md`, hub `llm-wiki/SKILL.md` |
| Fast concept-aware semantic scan of the raw vault when terms may not appear verbatim | **qmd** (FTS5 + EmbeddingGemma + Qwen3 reranker) | `qmd query "…"` (also `qmd search` BM25, `qmd vsearch` vectors, `qmd get <file>`) | `qmd --help`; collections `radiology`, `papers` |

## Rules of thumb

- **Default to obsidian-rag** for the radiology use cases — verbatim source text,
  protocols, paper figures, protocol composition. Its collections are `mri-protocols`,
  `fellowship`, `textbooks`, `papers`, `papers-fulltext`. The *toolkit* runs from any
  directory via `uv run` (the command above); the *skill* with full docs only loads
  when working inside `~/obsidian-rag`. Never invent content — it returns source text.
- **wiki-query** for synthesized / relational / "what do I know" questions. Read-only.
  **Note:** the compiled wiki is currently near-empty (`index.md` → "No pages yet"), so
  GraphRAG has little to return until sources are ingested via `wiki-ingest` /
  `wiki-capture`. Until then, prefer obsidian-rag or qmd for real answers.
- **qmd** overlaps obsidian-rag's semantic mode; prefer obsidian-rag when you need
  collection scoping, verbatim units, figures, or the composer, and qmd/wiki-query for
  fuzzy concept lookup and synthesis.

## Reference, don't duplicate

This hub only routes. The authoritative detailed skills are `obsidian-rag/SKILL.md`
(query/add/compose over collections) and `llm-wiki/SKILL.md` (the wiki system's theory
hub that the `wiki-*` family cites). Do not copy their workflows here — follow the
chosen spoke.
