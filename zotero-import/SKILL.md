---
name: zotero-import
description: Use when adding a paper to Zotero by DOI or from a recently downloaded PDF. Triggers on "import paper", "add to zotero", "I just downloaded a paper", "add this DOI", or when user provides a DOI/PDF and wants it in their library.
---

# Import Paper to Zotero

Add a paper to a Zotero library (personal or group) by DOI or PDF, create an Obsidian literature note, and run enrichment (summary, figures, citations).

## Script

```bash
python3 ~/research/obsidian-tools/import_paper.py [OPTIONS]
```

## Usage

**By DOI (default → ad_dti_study group):**
```bash
python3 ~/research/obsidian-tools/import_paper.py --doi 10.xxxx/yyyy
```

**By PDF (extracts DOI automatically from first pages):**
```bash
python3 ~/research/obsidian-tools/import_paper.py --pdf              # most recent in ~/Downloads
python3 ~/research/obsidian-tools/import_paper.py --pdf /path/to.pdf # explicit path
```

**Choose library:**
```bash
--library personal       # user's personal Zotero library
--library ad_dti_study   # default group → vault folder Papers/ad_dti_study
--library gliosarcoma    # → vault folder Papers/gliosarcoma
--library adstudy        # → vault folder Papers/adstudy
```

Each library writes its note into its own vault folder and tags it with the
collection name.

**Radiology note:** the "Radiology" set is a *collection inside My Library*, not a group
library, so single-paper `import_paper.py` (which adds to a Zotero library, not a specific
collection) does not target it directly. Use the batch importer to (re)populate the
`Radiology/` vault folder from that collection:
```bash
python3 ~/research/obsidian-tools/zotero_to_obsidian.py --collection radiology
python3 ~/research/obsidian-tools/enrich_obsidian_notes.py --collection radiology
```

**Other flags:**
- `--no-enrich` — skip LLM summary/figures/citations
- `--no-zotero` — skip Zotero API call (note only)
- `--force` — overwrite if already in vault
- `--dry-run` — preview without writing

## Workflow

1. Ask user for DOI or PDF (if not obvious from their message).
2. Ask which library (default: ad_dti_study). If user says "my library" or "personal", use `--library personal`.
3. Source credentials: `source ~/.config/settings.sh`
4. Run the command.
5. Report: title, citekey, library destination, whether PDF/summary/figures/citations succeeded.

## Credentials

Sourced from `~/.config/settings.sh`:
- `ZOTERO_API_KEY` — required
- `ZOTERO_USER_ID` — required only for `--library personal`
- `AWS_ACCESS_KEY_ID` + `ANTHROPIC_BEDROCK_BASE_URL` — for enrichment via UCSF proxy

## Failure modes

- **DOI not found in CrossRef or OpenAlex**: Double-check DOI format. Some preprints use non-standard DOIs.
- **Cannot extract DOI from PDF**: Ask user to provide DOI explicitly with `--doi`.
- **Already in vault (exit 2)**: Paper exists. Use `--force` to re-import, or tell user it's already there.
- **ZOTERO_USER_ID not set**: Needed for personal library. User must add it to `~/.config/settings.sh` (find at zotero.org/settings/keys).
- **403 from Zotero API**: API key lacks write permission for that library.
