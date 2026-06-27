---
name: zotero-enrich
description: Enrich Obsidian Zotero literature notes with PDF links, LLM summaries, and extracted figures. Run after adding new papers to Zotero so each note gets a clickable PDF link, a detailed summary, and embedded figure images with captions.
when_to_use: |
  Trigger on: "update obsidian zotero", "enrich zotero notes", "add summaries to papers", "new paper", "update literature notes", "sync zotero", "extract figures", or when the user says they've added papers to Zotero and wants their Obsidian notes updated. Also trigger when the user asks why a note is missing a PDF link, summary, or figures.
---

# Zotero-Obsidian Note Enrichment

When invoked, run the enrichment script that adds PDF links, Claude-generated summaries, and extracted figures to Obsidian literature notes imported from Zotero.

## What the script does

- **PDF links**: Queries the local Zotero SQLite DB to find each note's local PDF, then inserts a `[Open PDF](file://...)` link into the info callout.
- **LLM summaries**: Reads up to 15 pages of the actual PDF text, sends it to Claude via the UCSF Bedrock endpoint, and writes a 3-4 sentence summary into the `## Summary` section.
- **Figures**: Extracts raster figures from the PDF, pairs them with their captions from the text, saves them to `Papers/ad_dti_study/figures/{citekey}/`, and embeds them in a `## Figures` section in each note.
- **Fallback**: For papers without a local PDF, falls back to generating the summary from the abstract.
- **Idempotent**: Only touches notes that still have placeholder comments or are missing content. Notes you've manually edited are left alone.

## Setup

- Script: `~/research/obsidian-tools/enrich_obsidian_notes.py`
- Batch importer: `~/research/obsidian-tools/zotero_to_obsidian.py`
- Git repo: `~/research/obsidian-tools/` (track with git)
- Vault: `/Users/mromano/Obsidian/` (local disk; moved off the OneDrive-synced
  `~/Documents/Obsidian Vault` path, which caused cloud-only files to evict/hang)
  - Default collection folder: `Papers/ad_dti_study/`
  - Radiology collection folder: `Radiology/`
- Zotero DB: `~/Zotero/zotero.sqlite`
- Credentials: sourced automatically from `~/.config/settings.sh`

## Collections

Both scripts accept `--collection <name>` to target a Zotero group and its vault folder:

| `--collection` | Zotero source                          | Vault folder         |
|----------------|----------------------------------------|----------------------|
| `ad_dti_study` | ad_dti_study group                     | `Papers/ad_dti_study` (default) |
| `adstudy`      | ADstudy group                          | `Papers/adstudy`     |
| `gliosarcoma`  | gliosarcoma group                      | `Papers/gliosarcoma` |
| `radiology`    | "Radiology" collection in *My Library* | `Radiology`          |

Note: `radiology` is a **collection inside the personal "My Library"** (not a group library);
it filters by Zotero `collectionID`. To batch-import + enrich it:
```bash
python3 ~/research/obsidian-tools/zotero_to_obsidian.py --collection radiology
python3 ~/research/obsidian-tools/enrich_obsidian_notes.py --collection radiology
```
`enrich_obsidian_notes.py` also accepts `--notes-dir <path>` to target an arbitrary folder.

## Workflow

1. **Check for new notes**: Ask the user which papers were just added, or run in discovery mode to find all notes still missing content.

2. **Run the script**:
   ```bash
   python3 ~/research/obsidian-tools/enrich_obsidian_notes.py
   ```
   The script sources `~/.config/settings.sh` itself, so no manual export needed.

3. **Targeted single-paper run**:
   ```bash
   python3 ~/research/obsidian-tools/enrich_obsidian_notes.py --limit 1
   ```

4. **Dry run** to preview what would change without writing:
   ```bash
   python3 ~/research/obsidian-tools/enrich_obsidian_notes.py --dry-run
   ```

5. **Report back**: Tell the user how many notes were updated (PDF links, summaries, figures extracted) and mention any papers where the local PDF wasn't found.

## Failure modes to watch for

- **"X notes had no local PDF"**: The PDF may not be downloaded yet in Zotero. Ask the user to open the paper in Zotero, which triggers a download, then re-run.
- **API errors**: The UCSF Bedrock endpoint can occasionally return 503 — just re-run.
- **Zotero is open and DB is locked**: The script copies the DB before querying, so Zotero being open is fine.
- **No figures extracted**: Some papers use vector-only figures that cannot be extracted as raster images. This is expected.
- **Note not found at all**: Trigger a re-export from Zotero.

## Notes

- The model used is whatever `ANTHROPIC_MODEL` is set to in `~/.config/settings.sh` (currently `us.anthropic.claude-sonnet-4-6` via the UCSF Bedrock proxy).
- Figures are saved to `Papers/ad_dti_study/figures/{citekey}/fig{N}.png` and embedded as markdown images.
- Images are resized to max 1200px width to keep vault storage manageable.
- Small images (<10KB) are skipped as they are typically logos or decorative elements.
