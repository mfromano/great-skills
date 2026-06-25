# Zotero → Obsidian → RAG

This skill imports papers into Zotero/Obsidian. It works alongside the
`zotero-enrich` skill and the scripts in `~/research/obsidian-tools/`. This
README documents two workflows added on 2026-06-25: populating a **Radiology**
folder from a Zotero collection, and using the Obsidian vault as a **RAG**.

## Vault & Zotero facts

- **Active vault:** `/Users/mromano/Documents/Obsidian Vault` (same files as the
  `…/OneDrive-UCSF/Documents/Obsidian Vault` path). The Obsidian **MCP** server
  is connected to a *different* vault (`~/research/fw-tau-cascade`) — not this one.
- **Group library vs. collection:** a Zotero *group library* (own libraryID,
  has a group_id) is not the same as a *collection* inside the personal
  "My Library" (libraryID 1, filtered by collectionID). The user's **Radiology**
  is a My-Library collection (collectionID 82), not the unrelated
  `adrd_radiology` group.

## Part A — Radiology → Obsidian

The `~/research/obsidian-tools/` scripts are **collection-aware** via a
`COLLECTIONS` table mapping each source to its vault folder, tag, and Zotero IDs.

| `--collection` | Zotero source                          | Vault folder         |
|----------------|----------------------------------------|----------------------|
| `ad_dti_study` | ad_dti_study group                     | `Papers/ad_dti_study` (default) |
| `adstudy`      | ADstudy group                          | `Papers/adstudy`     |
| `gliosarcoma`  | gliosarcoma group                      | `Papers/gliosarcoma` |
| `radiology`    | "Radiology" collection in *My Library* | `Radiology`          |

Populate (and enrich) the `Radiology/` folder:

```bash
source ~/.config/settings.sh
python3 ~/research/obsidian-tools/zotero_to_obsidian.py --collection radiology
python3 ~/research/obsidian-tools/enrich_obsidian_notes.py --collection radiology
```

Notes are tagged `[literature-note, radiology]` with
`zotero://select/library/items/...` links. Enrichment adds PDF links, LLM
summaries, and extracted figures (`Radiology/figures/{citekey}/`). Items missing
author metadata in Zotero get `unknown<TitleWord>` citekeys — that's a Zotero
data issue, not a script bug.

To add a single new paper to a **group** library, use the import script with
`--library` (see SKILL.md). The `radiology` collection is populated via the
batch importer above rather than single-paper import.

## Part B — Obsidian vault as a RAG

The `neuro-lecture-catalog` project (`~/research/neuro-lecture-catalog`) builds a
**local, offline** retrieval-augmented index over the Obsidian vault notes
**plus** the lecture transcripts, queryable from its CLI.

- Embeddings: local `sentence-transformers` (`BAAI/bge-small-en-v1.5`) — no API,
  no data leaves the machine.
- Store: a numpy flat index persisted under `output/rag_index/`.
- Config: the `[rag]` section in `config.toml`
  (`vault_root`, `vault_subdirs`, `embedding_model`, `chunk_size`, `top_k`, …).

```bash
cd ~/research/neuro-lecture-catalog
uv sync                                          # installs sentence-transformers
nlc rag build                                    # index notes + transcripts
nlc rag ask "white matter integrity in AD DTI" --no-llm   # offline retrieval-only
nlc rag ask "Summarize glioma imaging findings" --top-k 6 # cited answer via Claude
```

Re-run `nlc rag build` after enriching new notes so their summaries get indexed.
Set `HF_HUB_OFFLINE=1` to force fully-offline embedding once the model is cached.

## Related files

- `~/research/obsidian-tools/{zotero_to_obsidian,enrich_obsidian_notes,import_paper}.py`
- `~/research/neuro-lecture-catalog/src/neuro_catalog/rag/`
- `zotero-enrich` skill (companion enrichment workflow)
