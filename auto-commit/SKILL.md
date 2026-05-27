---
name: auto-commit
description: Commit and push changes to the current branch. Stages relevant files, drafts a commit message from the diff, and pushes to upstream.
when_to_use: |
  Trigger on: "commit", "commit and push", "save and push", "push this", "push it", or when the user asks to wrap up work and persist changes. Also trigger when the user says "done" or "ship it" in a context where uncommitted changes exist.
---

# Auto-Commit and Push

When invoked, perform a clean git commit and push workflow:

## Workflow

1. **Assess state**: Run `git status` and `git diff --stat` to understand what changed.

2. **Exclude artifacts**: Never stage these patterns:
   - `Rplots.pdf`, `*.pyc`, `__pycache__/`
   - `.env`, `credentials.json`, `*.key`
   - Large binary outputs (`*.pptx`, `*.pkl`) unless the user explicitly created them as deliverables
   - Generated figures in `output/` directories (they'll be regenerated)

3. **Stage files**: Add relevant source files by name (prefer explicit paths over `git add -A`).

4. **Draft commit message**: Analyze the staged diff and write a concise message:
   - One summary line (imperative mood, under 72 chars)
   - Optional body paragraph explaining "why" if not obvious
   - End with `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`

5. **Commit**: Use a HEREDOC for the message to preserve formatting.

6. **Push**: Push to the current branch's upstream (`git push origin <branch>`).

## Safeguards

- **Never force-push** (`--force`, `--force-with-lease`)
- **Never push to main/master** without explicit user confirmation
- **Never use `--no-verify`** — if hooks fail, fix the issue
- **Never stage `.env` or credential files** — warn the user if they ask
- If `git status` shows nothing to commit, say so and stop
- If there are merge conflicts, report them and stop

## Output

After pushing, report:
- The commit hash and message
- The branch and remote pushed to
- Any files intentionally excluded (so the user knows)
