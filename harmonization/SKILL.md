---
name: harmonization
description: "Use when implementing ComBat or scanner/site harmonization for neuroimaging data. Triggers on: multi-site batch correction, scanner effects, neuroCombat, neuroHarmonize, site harmonization, or when working with harmonize_tractography.py."
---

# Scanner/Site Harmonization (ComBat)

Reference for implementing ComBat batch-effect correction on neuroimaging metrics across acquisition sites or cohorts.

## Library: neuroCombat

```python
from neuroCombat import neuroCombat

result = neuroCombat(
    dat=data_matrix.T,          # features × samples (transposed from samples × features)
    covars=covars_df,           # samples × covariates (must include batch column)
    batch_col="site",           # column in covars_df defining batches
)
harmonized = result["data"].T  # back to samples × features
```

Install: `pip install neuroCombat`

## Two-Stage Harmonization Pattern

For multi-cohort studies (e.g., ADNI + NACC):

1. **Stage 1 — Within-cohort site harmonization**: Correct for scanner variability within each cohort independently. Batch = scanner site ID.
2. **Stage 2 — Cross-cohort harmonization**: Align distributions between cohorts. Batch = cohort label.

## Biological Covariates

Covariates to **preserve** (not remove) during harmonization:
- `age` (continuous)
- `sex` (binary: 0/1)
- `diagnosis` (categorical encoded as numeric: 1=CN, 2=MCI, 3=AD)

Do NOT include variables you intend to study as covariates (e.g., APOE4, education) — they would be regressed out.

## Handling Edge Cases

### Small sites (< 5 observations)
Pool into a composite "small_sites" batch before running ComBat:
```python
counts = site_ids.value_counts()
small = counts[counts < 5].index
site_ids[site_ids.isin(small)] = -1  # pooled batch
```

### NaN in features
neuroCombat does not handle NaN natively:
- Features with >20% NaN: **exclude** from ComBat, retain raw values
- Features with sparse NaN (<20%): impute with column mean, run ComBat, restore NaN positions after

```python
nan_positions = data.isna()
data_imputed = data.fillna(data.mean())
# ... run ComBat ...
harmonized[nan_positions] = np.nan  # restore
```

### Missing batch labels
Rows without a site assignment bypass ComBat entirely — their raw values pass through unchanged.

## Site Metadata Sources (This Project)

### ADNI
- **Primary**: `MRI3META_*.csv` → `SITEID` column (101 scanning sites)
  - Join on (PTID, closest EXAMDATE within 30 days of session date)
  - 23% of subjects scanned at multiple sites — per-session matching required
- **Fallback**: PTID prefix (first 3 digits = enrollment site, not scanning site)

### NACC
- `All_Subjects_Diffusion_MRI_Images_*.csv` → `dti_mfr`, site from NACCADC in investigator file
- 36 Alzheimer's Disease Centers

## Canonical Implementation

`fw_tau_cascade/harmonize_tractography.py` — ComBat harmonization of PyAFQ tract profiles.

Key functions:
- `run_combat(data, batch, covariates)` — wrapper handling NaN, small sites, transposition
- `match_site_from_mri3meta(sessions, mri3meta_path)` — per-session site assignment
- `pool_small_sites(site_ids, min_size=5)` — merge underpowered sites
- `load_covariates_for_combat(subjects, dates, config)` — load age/sex/dx

## Validation Checklist

After harmonization, verify:
1. **Site-mean variance decreased** — `raw_means_by_site.var()` > `harmonized_means_by_site.var()`
2. **Overall distribution preserved** — global mean and variance should be roughly stable
3. **Biological signal preserved** — group differences (CN vs AD) should persist or strengthen
4. **No artificial values** — check for negative values in metrics that should be non-negative (e.g., FW fraction)
