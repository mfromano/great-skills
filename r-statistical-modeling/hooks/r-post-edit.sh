#!/bin/bash
# PostToolUse hook: after Edit/Write on .R files
# Parses the file for syntax errors and reports data frame objects
set -euo pipefail

FILE_PATH="${CLAUDE_FILE_PATH:-}"

# Only process .R files
if [[ ! "$FILE_PATH" =~ \.R$ ]]; then
  exit 0
fi

RSCRIPT="$(command -v Rscript 2>/dev/null || true)"
if [[ -z "$RSCRIPT" ]]; then
  exit 0
fi

# Step 1: Syntax check (fast, no side effects)
PARSE_RESULT=$($RSCRIPT --vanilla -e "tryCatch(parse(file='${FILE_PATH}'), error=function(e) cat('SYNTAX ERROR:', conditionMessage(e)))" 2>&1)

if echo "$PARSE_RESULT" | grep -q "SYNTAX ERROR"; then
  echo "=== R Syntax Error ==="
  echo "$PARSE_RESULT"
  exit 0
fi

# Step 2: Source in isolated session, report key objects
# Timeout after 8s to avoid blocking on long-running scripts
REPORT=$(timeout 8 $RSCRIPT --vanilla -e "
suppressPackageStartupMessages({
  tryCatch({
    source('${FILE_PATH}', local=TRUE)
    objs <- ls()
    if (length(objs) > 0) {
      cat('=== R Objects Created ===\n')
      for (obj in objs) {
        val <- get(obj)
        if (is.data.frame(val) || inherits(val, 'tbl_df')) {
          cat(sprintf('  %s: %d x %d data.frame [%s]\n', obj, nrow(val), ncol(val),
              paste(head(names(val), 5), collapse=', ')))
        } else if (inherits(val, c('lm', 'lmerMod', 'gam', 'glmerMod', 'glmmTMB'))) {
          cat(sprintf('  %s: %s model (%s)\n', obj, class(val)[1], deparse(formula(val), width.cutoff=60)))
        } else if (is.numeric(val) && length(val) == 1) {
          cat(sprintf('  %s: %s\n', obj, format(val, digits=4)))
        } else {
          cat(sprintf('  %s: %s [length %d]\n', obj, class(val)[1], length(val)))
        }
      }
    }
  }, error=function(e) {
    cat('=== R Runtime Error ===\n')
    cat(conditionMessage(e), '\n')
  })
})
" 2>&1 | grep -v "^Warning\|^Attaching\|^The following\|^package\|^Loading\|^Registered\|^$\|^    ")

if [[ -n "$REPORT" ]]; then
  echo "$REPORT"
fi
