#!/bin/bash
# PreToolUse hook: before r-btw MCP calls or Rscript commands
# Reports what's available in the current R workspace (.RData or renv)
set -euo pipefail

RSCRIPT="/data/romano1/miniconda3/bin/Rscript"
if [[ ! -x "$RSCRIPT" ]]; then
  RSCRIPT="Rscript"
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Check if there's a saved workspace or recently-sourced .R files
RDATA_FILE=""
if [[ -f "$PROJECT_DIR/.RData" ]]; then
  RDATA_FILE="$PROJECT_DIR/.RData"
elif [[ -f "$PROJECT_DIR/r_analysis/.RData" ]]; then
  RDATA_FILE="$PROJECT_DIR/r_analysis/.RData"
fi

if [[ -n "$RDATA_FILE" ]]; then
  REPORT=$(timeout 5 $RSCRIPT --vanilla -e "
  suppressPackageStartupMessages({
    load('${RDATA_FILE}')
    objs <- ls()
    if (length(objs) > 0) {
      cat('=== R Workspace (${RDATA_FILE}) ===\n')
      for (obj in head(objs, 20)) {
        val <- get(obj)
        if (is.data.frame(val) || inherits(val, 'tbl_df')) {
          cat(sprintf('  %s: %d x %d [%s]\n', obj, nrow(val), ncol(val),
              paste(head(names(val), 4), collapse=', ')))
        } else if (inherits(val, c('lm', 'lmerMod', 'gam', 'glmerMod'))) {
          cat(sprintf('  %s: %s\n', obj, class(val)[1]))
        }
      }
      if (length(objs) > 20) cat(sprintf('  ... and %d more objects\n', length(objs) - 20))
    }
  })
  " 2>&1 | grep -v "^Warning\|^Attaching\|^The following\|^$")

  if [[ -n "$REPORT" ]]; then
    echo "$REPORT"
  fi
else
  # No workspace file; report available CSV data files instead
  CSV_COUNT=$(find "$PROJECT_DIR/r_analysis" "$PROJECT_DIR/cascade_model" -name "*.csv" 2>/dev/null | wc -l)
  if [[ "$CSV_COUNT" -gt 0 ]]; then
    echo "=== Available Data Files ==="
    find "$PROJECT_DIR/r_analysis" "$PROJECT_DIR/cascade_model" -name "*.csv" 2>/dev/null | head -10 | while read f; do
      ROWS=$(wc -l < "$f" 2>/dev/null || echo "?")
      echo "  $(basename "$f"): ${ROWS} rows"
    done
    REMAINING=$((CSV_COUNT - 10))
    if [[ "$REMAINING" -gt 0 ]]; then
      echo "  ... and $REMAINING more CSV files"
    fi
  fi
fi
