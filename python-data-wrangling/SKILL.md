---
name: python-data-wrangling
description: Use when writing Python code to assemble, collate, merge, or prepare datasets that will be consumed by R for statistical analysis. Triggers on ETL pipelines, data extraction, parquet assembly, merging multiple data sources, or any Python data prep that feeds into R scripts.
---

# Python Data Wrangling for R Analysis

**Python prepares the data. R does the statistics.**

This skill governs Python code whose purpose is to collate, merge, clean, and export datasets that will be consumed by R scripts for statistical modeling. The goal is a single, comprehensive, well-documented parquet file that R can load without further wrangling.

## Core Principles

1. **One comprehensive parquet file per analysis suite** — not multiple CSVs, not analysis-specific subsets
2. **Wide format by default** — preserves subjects/observations with partial missingness across domains
3. **Pandas first** — use pandas where tractable; only reach for polars when pandas is genuinely too slow
4. **Log everything** — every merge, filter, and missing-data pattern goes to a log file

## Output Format

- Export as `.parquet` (pyarrow engine, default compression)
- Wide format: one row per subject/observation unit (or subject × timepoint if longitudinal)
- Include all variables needed across the full R analysis suite: outcomes, predictors, covariates, grouping variables, IDs, dates
- Name descriptively: `longitudinal_metrics.parquet`, not `data_final_v2.parquet`
- Include metadata columns (IDs, session/visit, date, group, demographics) even if not all R models use them

```python
df.to_parquet("longitudinal_metrics.parquet", engine="pyarrow", index=False)
```

## Wide Format Preference

**Default to wide format** so that observations with missing data in one domain are preserved rather than dropped by an implicit inner join or `dropna` in long format.

- One row per unit (cross-sectional) or unit × timepoint (longitudinal)
- Columns for each measure: `domain1_var1`, `domain1_var2`, ..., `domain2_var1`, ...
- NaN in a column means that domain/variable is missing for that row — the row is still kept
- Only pivot to long format inside R when a specific model requires it

```python
# Wide merge preserving all observations
df = (
    observations
    .merge(domain_a, on=["id", "visit"], how="left")
    .merge(domain_b, on=["id", "visit"], how="left")
    .merge(domain_c, on=["id", "visit"], how="left")
)
```

## Logging Requirements

Every script must produce a `.log` file with timestamped, human-readable messages describing each data manipulation step.

### Setup

```python
import logging
from pathlib import Path

log_path = Path(__file__).with_suffix(".log")
logging.basicConfig(
    filename=log_path,
    filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
```

### What to log

Log after **every** operation that changes the shape or content of the data frame:

| Operation | Log must include |
|-----------|-----------------|
| Load | Rows × cols, source file |
| Filter | Rows before → after, rows dropped, reason |
| Merge/join | Rows before → after, join type, keys, new NAs introduced |
| Drop duplicates | Rows before → after, dedup keys |
| Pivot | Old shape → new shape |
| Column creation | Name, basic stats (mean/SD or value_counts for categorical) |
| Missing data | Count and percentage of NaN per column (or per domain) |
| Outlier removal | How many values affected, threshold used |
| Export | Final shape, output path |

### Missing data logging

**Any time missing data exists after a merge or at export, log it explicitly:**

```python
# After every merge
missing = df.isna().sum()
missing_cols = missing[missing > 0]
if not missing_cols.empty:
    log.info("Missing data after merge:")
    for col, n in missing_cols.items():
        log.info(f"  {col}: {n}/{len(df)} ({100*n/len(df):.1f}%) missing")

# At export — full missingness report
log.info("Final missingness summary:")
for col in df.columns:
    n_miss = df[col].isna().sum()
    if n_miss > 0:
        log.info(f"  {col}: {n_miss}/{len(df)} ({100*n_miss/len(df):.1f}%)")
```

### Example log output

```
[09:14:01] Loaded visits: 4,231 rows × 8 cols from visits.csv
[09:14:01] Filtered to eligible participants: 4,231 → 2,847 rows (1,384 dropped)
[09:14:02] Merged domain A (left join on [id, visit]): 2,847 → 2,847 rows
[09:14:02] Missing data after merge:
[09:14:02]   domain_a_var1: 312/2847 (11.0%) missing
[09:14:02]   domain_a_var2: 312/2847 (11.0%) missing
[09:14:03] Merged domain B (left join on [id, visit]): 2,847 → 2,847 rows
[09:14:03] Missing data after merge:
[09:14:03]   domain_b_var1: 89/2847 (3.1%) missing
[09:14:04] Final shape: 2,847 rows × 54 cols
[09:14:04] Final missingness summary:
[09:14:04]   domain_a_var1: 312/2847 (11.0%)
[09:14:04]   domain_a_var2: 312/2847 (11.0%)
[09:14:04]   domain_b_var1: 89/2847 (3.1%)
[09:14:04]   score_x: 23/2847 (0.8%)
[09:14:04] Exported: longitudinal_metrics.parquet
```

## Pandas Conventions

- **Prefer pandas** for all operations unless the dataset is genuinely too large (>10M rows or memory-constrained)
- Use method chaining with `.pipe()`, `.assign()`, `.query()` for readability
- Use `.merge()` with explicit `how=` and `on=` — never rely on index alignment
- Always specify `how="left"` for merges to preserve the primary table's rows
- Use categorical dtypes for group/factor columns to save memory and signal intent
- Avoid inplace operations (`inplace=True`) — always reassign

```python
df = (
    pd.read_csv("observations.csv")
    .query("age >= 18")
    .assign(
        age_centered=lambda x: x["age"] - x["age"].mean(),
        group=lambda x: pd.Categorical(x["group"], categories=["Control", "Treatment"]),
    )
    .merge(measurements, on=["id", "visit"], how="left")
)
```

## Merge Strategy

- **Left joins by default** — the primary observations table defines the rows; ancillary data is joined in
- Never use inner joins unless explicitly reducing the sample (and log why)
- After every merge, check for unexpected row duplication:

```python
n_before = len(df)
df = df.merge(other, on=keys, how="left")
assert len(df) == n_before, f"Merge duplicated rows: {n_before} → {len(df)}"
log.info(f"Merged {other_name} (left join on {keys}): {n_before} → {len(df)} rows")
```

## File and Script Naming

- Scripts: `00_assemble_dataset.py`, `01_extract_features.py` — zero-padded numeric prefix
- Output: descriptive name reflecting content, not pipeline step (`longitudinal_metrics.parquet`, not `step3_output.parquet`)
- Log files: same name as script with `.log` extension (automatic from setup above)

## Simplify Workflow

**When `/simplify` is invoked on Python data-wrangling code, follow this three-step regression-tested workflow:**

1. **Baseline capture** — Run all Python scripts in the project sequentially (ordered by numeric prefix: `00_*.py`, `01_*.py`, etc.). Capture all output artifacts: parquet files, log files, any intermediate outputs. This is the ground truth.

2. **Simplify** — Refactor code to be as concise and human-auditable as possible. Goals:
   - Eliminate unnecessary intermediate variables
   - Collapse redundant logic
   - Shorten function bodies without obscuring intent
   - Remove dead code paths
   - Prefer idiomatic pandas method chains over verbose step-by-step
   - Keep every function short enough to audit in a single screen (~30 lines max)

3. **Regression verification** — Rerun all Python scripts in the same sequential order. Compare all output artifacts to the baseline. Every parquet file must be **identical** (same schema, same values, same row order). Log files must report the same counts and missingness. If any output differs, revert the offending change and retry.

**The simplify is only complete when step 3 confirms identical output.** Do not report success without running the full regression pass.

## What NOT to Do

- Do not export multiple analysis-specific files — one comprehensive parquet
- Do not drop rows with partial missingness — keep them in wide format, let R handle per-model
- Do not convert to long format in Python — R will pivot as needed per model
- Do not compute statistics or fit models — that belongs in R
- Do not use `df.dropna()` without logging exactly what was lost
- Do not use polars unless pandas is demonstrably too slow for the dataset size
