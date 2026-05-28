---
name: zotero-enrich
description: Enrich Obsidian Zotero literature notes with PDF links and LLM summaries. Run after adding new papers to Zotero so each note gets a clickable link to open the PDF in your system viewer plus a detailed summary generated from the full PDF text.
when_to_use: |
  Trigger on: "update obsidian zotero", "enrich zotero notes", "add summaries to papers", "new paper", "update literature notes", "sync zotero", or when the user says they've added papers to Zotero and wants their Obsidian notes updated. Also trigger when the user asks why a note is missing a PDF link or summary.
---

# Zotero-Obsidian Note Enrichment

When invoked, run the enrichment script that adds PDF links and Claude-generated summaries to Obsidian literature notes imported from Zotero.

## What the script does

- **PDF links**: Queries the local Zotero SQLite DB to find each note's local PDF, then inserts a `[Open PDF](file://...)` link into the info callout. Clicking opens the PDF in your default system viewer (Preview on macOS).
- **LLM summaries**: Reads up to 15 pages of the actual PDF text, sends it to Claude via the UCSF Bedrock endpoint, and writes a 3-4 sentence summary (research question, methods, key findings) into the `## Summary` section.
- **Fallback**: For papers without a local PDF, falls back to generating the summary from the abstract already embedded in the note.
- **Idempotent**: Only touches notes that still have the placeholder comment or are missing a PDF link. Notes you've manually edited are left alone.

## Setup

- Script: `~/research/enrich_obsidian_notes.py`
- Vault: `/Users/mromano/Documents/Obsidian Vault/Papers/ad_dti_study/`
- Zotero DB: `~/Zotero/zotero.sqlite`
- Credentials: sourced automatically from `~/.config/settings.sh`

## Workflow

1. **Check for new notes**: Ask the user which papers were just added, or run in discovery mode to find all notes still missing a PDF link or summary.

2. **Run the script**:
   ```bash
   python3 ~/research/enrich_obsidian_notes.py
   ```
   The script sources `~/.config/settings.sh` itself, so no manual export needed.

3. **Targeted single-paper run**: If the user just added one paper, you can run with `--limit` after confirming the note exists:
   ```bash
   python3 ~/research/enrich_obsidian_notes.py --limit 1
   ```
   But since the script is idempotent and fast for already-processed notes, running it on all notes is usually fine.

4. **Dry run** to preview what would change without writing:
   ```bash
   python3 ~/research/enrich_obsidian_notes.py --dry-run
   ```

5. **Report back**: Tell the user how many notes were updated and mention any papers where the local PDF wasn't found (they may need to re-attach in Zotero).

## Failure modes to watch for

- **"X notes had no local PDF"**: The PDF may not be downloaded yet in Zotero. Ask the user to open the paper in Zotero, which triggers a download, then re-run.
- **API errors**: The UCSF Bedrock endpoint can occasionally return 503 — just re-run and the script will skip already-processed notes.
- **Zotero is open and DB is locked**: The script copies the DB before querying, so Zotero being open is fine.
- **Note not found at all**: The Zotero Better BibTeX plugin may not have exported the note yet. Ask the user to trigger a re-export from Zotero (right-click library → Export Library, or use the auto-export setting).

## Notes

- The model used is whatever `ANTHROPIC_MODEL` is set to in `~/.config/settings.sh` (currently `us.anthropic.claude-sonnet-4-6` via the UCSF Bedrock proxy).
- Summaries are written to the `## Summary` section only if it still contains the placeholder comment `<!-- 2-3 sentence summary ... -->`. Once you edit a summary manually, the script won't overwrite it.
- To regenerate a summary (e.g. you want a better one), replace the existing summary text with the original placeholder comment and re-run.
