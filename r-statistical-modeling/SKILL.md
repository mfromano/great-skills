---
name: r-statistical-modeling
description: Use R (mgcv, lme4, lmerTest, nlme, emmeans) instead of Python for all statistical modeling tasks. Triggers when fitting mixed models, GAMs, GLMMs, or any regression/ANOVA. Prefer R's mature ecosystem for inference, diagnostics, and publication-quality model summaries.
when_to_use: Any time a statistical model is being created, fitted, or analyzed — linear models, mixed effects, GAMs, GLMs/GLMMs, repeated measures, longitudinal analysis, or when model diagnostics/contrasts/post-hoc tests are needed.
license: MIT
metadata:
  skill-author: Michael Romano
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "hooks/r-post-edit.sh"
          timeout: 10000
  PreToolUse:
    - matcher: "mcp__r-btw"
      hooks:
        - type: command
          command: "hooks/r-session-summary.sh"
          timeout: 6000
---

# R-First Statistical Modeling

**When a statistical model is needed, use R — not Python.**

R's statistical ecosystem (mgcv, lme4, lmerTest, nlme, emmeans) is more mature, better tested, and produces publication-ready output for inference. Python tools (statsmodels, pingouin) are acceptable for simple descriptive statistics or quick t-tests, but for anything involving mixed effects, splines, GAMs, or complex random-effect structures, R is the correct tool.

## Model Specification Workflow

**Before writing any model code, propose the formula and ask for modifications.**

When a statistical analysis is requested:
1. State the recommended model formula in R syntax (e.g., `outcome ~ s(age, by = group) + covariate + (1 | subject)`)
2. Explain briefly why this specification is appropriate (family, link, random effects structure, smooth terms)
3. Ask the user whether they want any modifications before proceeding

Do not fit the model until the user confirms or adjusts the specification. This prevents wasted iterations on the wrong model structure.

## Consistency Within Analysis Folders

**All statistical models within a single folder/script suite must be harmonized.**

- Use the same input dataset across all models in the folder (load once, subset as needed)
- Use consistent random-effects structures (e.g., if one model has `(1 | subject)`, all models in the suite should unless there is a specific reason to differ)
- Use the same covariates / confound adjustment strategy across models
- Use the same filtering criteria (inclusion/exclusion) so sample sizes are comparable
- Use the same variable transformations (centering, scaling, factor coding)

When adding a new model to an existing analysis folder, first read the other scripts in the folder to identify the established conventions and match them.

## Data Preparation — Single Comprehensive CSV

**When curating data in Python for R analysis, compile a single comprehensive CSV rather than multiple analysis-specific files.**

- One CSV should contain all variables needed across the full analysis suite (outcomes, predictors, covariates, grouping variables, IDs)
- R scripts then `select()` or `filter()` from this master file as needed
- This ensures consistent sample definitions across analyses and avoids version drift between files
- Name the file descriptively (e.g., `lobar_metrics_long.csv` not `data_for_gam1.csv`)
- Include all relevant metadata columns (subject ID, session, group, demographics) even if not all models use them

Only create separate CSVs when data genuinely come from different sources or pipelines that cannot be meaningfully joined.

## When This Skill Applies

- Fitting any regression model (linear, logistic, Poisson, etc.)
- Mixed-effects / multilevel models (random intercepts/slopes)
- Generalized additive models (GAMs, GAMMs)
- Repeated measures / longitudinal analysis
- ANOVA with post-hoc contrasts
- Model diagnostics (residuals, influence, overdispersion)
- Estimated marginal means and pairwise comparisons

## Core Packages

### Data Manipulation — tidyverse first

**Always use tidyverse for data manipulation.** Prefer `dplyr`, `tidyr`, `purrr`, `stringr`, and `forcats` over base R equivalents. This means:

- `dplyr::filter()`, `mutate()`, `select()`, `group_by()`, `summarise()` — not `subset()`, `transform()`, `aggregate()`
- `tidyr::pivot_longer()`, `pivot_wider()`, `separate()`, `nest()` — not `reshape()`, `melt()`/`dcast()`
- `purrr::map()`, `map_dfr()`, `walk()` — not `lapply()`, `sapply()`, `do.call(rbind, ...)`
- `stringr::str_detect()`, `str_replace()` — not `grep()`, `gsub()`
- `forcats::fct_relevel()`, `fct_reorder()` — not manual `factor(levels=...)`
- `readr::read_csv()` — not `read.csv()`
- Pipe-based workflows with `|>` or `%>%`

Load `library(tidyverse)` at the top of every script. For scripts that only need one or two tidyverse packages, loading the full tidyverse is still preferred for consistency.

| Package | Purpose |
|---------|---------|
| `tidyverse` | Core data manipulation, reading, and visualization (dplyr, tidyr, ggplot2, readr, purrr, stringr, forcats, tibble) |
| `lme4` | Linear and generalized linear mixed-effects models |
| `lmerTest` | Satterthwaite/Kenward-Roger df and p-values for lmer |
| `mgcv` | GAMs, GAMMs, tensor interactions, penalized regression |
| `nlme` | Mixed models with complex correlation/variance structures |
| `emmeans` | Estimated marginal means, contrasts, post-hoc tests |
| `car` | Type II/III ANOVA tables, diagnostic tests |
| `MuMIn` | Model selection (AICc, dredge, model averaging) |
| `performance` | Model diagnostics (check_model, R², ICC) |
| `DHARMa` | Residual diagnostics for GLMMs via simulation |
| `glmmTMB` | Zero-inflated, hurdle, and complex GLMMs |
| `broom.mixed` | Tidy model output for mixed models |
| `gt` | Publication-quality tables for model results and diagnostics |
| `gtsummary` | Model summary tables (tbl_regression, tbl_merge) |

## r-btw MCP Server

The `r-btw` MCP server (`btw::btw_mcp_server()`) exposes R objects, data frames, and documentation directly to Claude without requiring file round-trips. Use it when it is available.

### Installation

If the `r-btw` MCP server is not connected or the `btw` package is missing, install it:

```r
install.packages("btw", repos="https://cran.r-project.org")
```

Then add to `.mcp.json` (project-level) or `~/.claude/settings.json` (global):

```json
{
  "mcpServers": {
    "r-btw": {
      "command": "Rscript",
      "args": ["-e", "btw::btw_mcp_server()"]
    }
  }
}
```

Reload/restart Claude Code after adding the entry. The `-32000` error on connection means the server process failed to start — most often because `btw` is not installed.

**When to use r-btw tools instead of `Rscript`:**
- **R documentation lookups** — Always use r-btw to look up R function signatures, package documentation, argument defaults, and style guide references. Prefer r-btw over web searches for any R/tidyverse/stats documentation question.
- Inspecting a data frame's structure, column types, or summary stats before fitting a model
- Checking a fitted model object (coefficients, random effects, convergence warnings) after fitting
- Looking up R function or package documentation mid-task
- Iterating on model specification when you need to examine intermediate objects

**Typical workflow with r-btw:**
1. Use r-btw tools to explore the data (column names, N, distributions, missing values)
2. Write and run the model script with `Rscript`
3. Use r-btw tools to inspect the fitted object or load diagnostics back into context
4. Refine as needed

If r-btw tools are not responding or the server is not connected, fall back to `Rscript` with `print()`/`summary()` and capture output directly.

## Running R Code

Use `Rscript -e '...'` for single expressions, or write to a `.R` file and run with `Rscript file.R`. For multi-line scripts:

```bash
Rscript -e '
library(tidyverse)
library(lme4)
library(lmerTest)

sleepstudy |>
  mutate(Days_z = scale(Days)[, 1]) |>
  lmer(Reaction ~ Days_z + (Days_z | Subject), data = _) |>
  summary() |>
  print()
'
```

For scripts that produce plots, save to file:

```r
library(tidyverse)

p <- df |>
  ggplot(aes(x = age, y = outcome, color = group)) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "gam") +
  theme_minimal()

ggsave("plot.pdf", p, width = 8, height = 6)
```

## Model Recipes

### Linear Mixed-Effects Model (lmer)

```r
library(tidyverse)
library(lme4)
library(lmerTest)

df_model <- df |>
  filter(!is.na(outcome), !is.na(fixed1)) |>
  mutate(fixed1_z = scale(fixed1)[, 1])

fit <- lmer(outcome ~ fixed1_z + fixed2 + (1 + fixed1_z | subject), data = df_model)
summary(fit)           # Satterthwaite p-values
anova(fit, type = 3)   # Type III ANOVA table
confint(fit)           # Profile confidence intervals
```

### Generalized Additive Model (mgcv)

```r
library(tidyverse)
library(mgcv)

df_gam <- df |>
  filter(!is.na(y), !is.na(age)) |>
  mutate(group = factor(group))

# Smooth nonlinear effects
fit <- gam(y ~ s(age) + s(time) + group + s(age, by = group), data = df_gam)
summary(fit)
plot(fit, pages = 1)

# With random effects (GAMM via re= or bs="re")
fit <- gam(y ~ s(age) + s(subject, bs = "re"), data = df_gam)

# Or use gamm() for nlme-style random effects
fit <- gamm(y ~ s(age), random = list(subject = ~1), data = df_gam)
```

### GAMM with large datasets (bam)

```r
library(tidyverse)
library(mgcv)

# bam() is faster for large datasets, supports discrete=TRUE
fit <- bam(y ~ s(age) + s(subject, bs = "re") + group,
           data = df_gam, discrete = TRUE)
```

### Generalized Linear Mixed Model

```r
library(lme4)

# Logistic
fit <- glmer(binary_outcome ~ x1 + x2 + (1 | subject),
             data=df, family=binomial)

# Poisson
fit <- glmer(count ~ x1 + (1 | subject),
             data=df, family=poisson)
```

### Zero-Inflated / Hurdle Models (glmmTMB)

```r
library(glmmTMB)

fit <- glmmTMB(count ~ x1 + x2 + (1 | subject),
               ziformula = ~ x1,
               family = nbinom2, data=df)
summary(fit)
```

### Estimated Marginal Means and Contrasts

```r
library(emmeans)

emm <- emmeans(fit, ~ group)
print(emm)
pairs(emm, adjust="tukey")       # pairwise comparisons
contrast(emm, method="trt.vs.ctrl")  # vs control
```

### Model Comparison

```r
library(MuMIn)

fit_full <- lmer(y ~ x1 + x2 + (1|subj), data=df, REML=FALSE)
fit_reduced <- lmer(y ~ x1 + (1|subj), data=df, REML=FALSE)

anova(fit_reduced, fit_full)   # likelihood ratio test
AICc(fit_full, fit_reduced)    # corrected AIC
```

## Visualization and Reporting Requirements

**Every statistical analysis must produce two plots AND gt tables:**

1. **Raw data plot** — Show the raw data going into the analysis. This means the actual observed values, plotted in a way that conveys the structure of the data (e.g., scatter plots, spaghetti plots for longitudinal data, jittered points by group). No model fits, no smoothers — just the data.

2. **Result overlay plot** — Show the analysis result (fitted values, smooth curves, predicted means, confidence bands) overlaid on top of the same raw data. The reader should be able to see both what the data look like and what the model estimates.

3. **gt tables** — Model statistics (fixed effects, smooth terms) and diagnostics (R², AIC, ICC) presented as publication-quality `gt` tables saved as `.pdf` and `.png`. See the "Reporting Results — gt Tables" section for details.

Both plots should use the same axis scales and structure so they are directly comparable. Save them as separate files or as panels in a combined figure when appropriate. Tables are saved to the same output directory as figures.

### Plot style — keep it simple

**Default to the simplest plot that communicates the result.** Prefer:

- **Scatter plot + regression line** for continuous × continuous relationships
- **Box-and-whisker plot** (or violin + jitter) for group comparisons
- **Point + error bar** for estimated means / contrasts
- **Scatter + smooth line** (`geom_smooth`) for nonlinear trends

**Avoid** unless the data genuinely requires it:
- Spaghetti plots (use only for longitudinal data where individual trajectories matter)
- Faceted multi-panel grids (use only when comparing across >2 grouping variables)
- Density ridgelines or complex geoms
- Heavy annotation, arrows, or text labels on plots
- **Heatmaps** — almost never use heatmaps. Instead, produce a figure or table that displays raw data (if possible) or raw data + model estimate with effect sizes. The only acceptable use of a heatmap is for extremely low-count categorical data (e.g., a small contingency table), and in that case the precise count must be annotated on top of each cell (`geom_text()`). For continuous outcomes across many regions/variables, prefer dot plots, forest plots, or `gt` tables with effect sizes.

**Guiding principles:**
- One geom layer for data, one for the model fit. Two layers is usually enough.
- Let the data speak — if a scatter + `geom_smooth(method="lm")` tells the story, don't add confidence ribbons, rug plots, and marginal densities.
- Use `alpha` for overplotting, `color` or `shape` for groups — not both simultaneously.
- `theme_minimal()` or `theme_classic()` as default. No grey backgrounds.
- Label axes clearly with units. No title unless the figure appears without a caption.

**Preferred patterns by analysis type:**

- **Continuous predictor (lm, GAM)**: `geom_point(alpha=0.4) + geom_smooth(method=...)` — scatter with fitted line/curve.
- **Group comparison (ANOVA, t-test)**: `geom_boxplot() + geom_jitter(width=0.2, alpha=0.3)` — boxes show distribution, jitter shows individual observations.
- **Interaction (2 groups × continuous)**: `geom_point(aes(color=group)) + geom_smooth(aes(color=group), method="lm")` — one regression line per group.
- **Longitudinal (mixed model)**: `geom_point(alpha=0.3) + geom_smooth(aes(group=subject), se=FALSE, alpha=0.2) + geom_smooth(aes(color=group), linewidth=1.2)` — only if individual trajectories are informative; otherwise just group-level fit over points.
- **Post-hoc contrasts**: `geom_pointrange(aes(y=estimate, ymin=conf.low, ymax=conf.high))` — point + CI bars, nothing else.

**Figure naming convention:** Figures must be labeled relative to the R script that generates them. A script with numeric prefix `NN` (e.g., `01_lobar_gam.R`, `03-cognitive.Rmd`) produces figures labeled `NNa`, `NNb`, `NNc`, etc. in order. For example:
- `01_lobar_gam.R` → `fig_01a_raw_lobar.pdf`, `fig_01b_gam_lobar.pdf`, `fig_01c_lobar_diffs.pdf`
- `03-cognitive.Rmd` → `fig_03a_cognitive_raw.pdf`, `fig_03b_cognitive_model.pdf`

This keeps figures traceable to their source script and orders them consistently across the manuscript.

## Model Diagnostics

### For lmer/glmer models

```r
library(performance)

check_model(fit)           # visual diagnostic panel
r2(fit)                    # marginal and conditional R²
icc(fit)                   # intraclass correlation
check_collinearity(fit)    # VIF for fixed effects
```

### For GLMMs (simulation-based residuals)

```r
library(DHARMa)

sim_res <- simulateResiduals(fit)
plot(sim_res)
testDispersion(sim_res)
testZeroInflation(sim_res)
```

### For GAMs

```r
gam.check(fit)    # residual plots + basis dimension checks
concurvity(fit)   # analogue of collinearity for smooth terms
```

## Reading and Preparing Data

```r
library(tidyverse)

df <- read_csv("data.csv") |>
  janitor::clean_names() |>
  mutate(
    group = factor(group),
    age_centered = age - mean(age, na.rm = TRUE)
  ) |>
  filter(!is.na(outcome))

# Reshaping for longitudinal/repeated measures
df_long <- df |>
  pivot_longer(
    cols = starts_with("score_"),
    names_to = "timepoint",
    values_to = "score"
  )

# Nested operations per group
df_summary <- df |>
  group_by(group, region) |>
  summarise(
    n = n(),
    mean_val = mean(value, na.rm = TRUE),
    se_val = sd(value, na.rm = TRUE) / sqrt(n()),
    .groups = "drop"
  )

# For Excel
library(readxl)
df <- read_excel("data.xlsx", sheet = 1)
```

## Reporting Results — gt Tables

**Every model must produce gt tables for statistics and diagnostics, saved alongside figures.**

After fitting any linear model (lm, lmer, gam, glmer, etc.), produce publication-quality tables using `gt` and save them as both `.pdf` and `.png` files. Tables follow the same naming convention as figures.

**Table naming convention:** Same as figures — a script `NN_*.R` produces tables labeled `tbl_NNa`, `tbl_NNb`, etc. For example:
- `01_lobar_gam.R` → `tbl_01a_fixed_effects.pdf`, `tbl_01b_model_diagnostics.pdf`
- `03_cognitive_gam.R` → `tbl_03a_smooth_terms.pdf`, `tbl_03b_pairwise.pdf`

Save tables to the same output directory as figures (e.g., `output/`).

### Required tables after model fitting

1. **Fixed effects / coefficients table** — estimates, CIs, test statistics, p-values
2. **Model diagnostics table** — R², AIC/BIC, sample size, random effects variance (as applicable)
3. **Post-hoc / contrasts table** (when applicable) — pairwise comparisons with adjusted p-values

### Fixed effects table (lmer / lm)

```r
library(tidyverse)
library(broom.mixed)
library(gt)

tbl_fixed <- tidy(fit, effects = "fixed", conf.int = TRUE) |>
  mutate(
    across(c(estimate, conf.low, conf.high, statistic), \(x) round(x, 3)),
    p.value = scales::pvalue(p.value)
  ) |>
  select(Term = term, Estimate = estimate, `95% CI Low` = conf.low,
         `95% CI High` = conf.high, `t / z` = statistic, `p` = p.value) |>
  gt() |>
  tab_header(title = "Fixed Effects") |>
  tab_options(table.font.size = px(12))

gtsave(tbl_fixed, "output/tbl_01a_fixed_effects.pdf")
gtsave(tbl_fixed, "output/tbl_01a_fixed_effects.png", vwidth = 800)
```

### GAM smooth terms table

```r
tbl_smooth <- tidy(fit, parametric = FALSE) |>
  mutate(
    across(c(edf, ref.df, statistic), \(x) round(x, 2)),
    p.value = scales::pvalue(p.value)
  ) |>
  select(Term = term, EDF = edf, `Ref. df` = ref.df,
         F = statistic, `p` = p.value) |>
  gt() |>
  tab_header(title = "Smooth Terms")

gtsave(tbl_smooth, "output/tbl_01b_smooth_terms.pdf")
gtsave(tbl_smooth, "output/tbl_01b_smooth_terms.png", vwidth = 800)
```

### Model diagnostics table

```r
library(performance)

diag_df <- tibble(
  Metric = c("R² (marginal)", "R² (conditional)", "AIC", "BIC", "ICC", "N obs", "N groups"),
  Value = c(
    round(r2(fit)$R2_marginal, 3),
    round(r2(fit)$R2_conditional, 3),
    round(AIC(fit), 1),
    round(BIC(fit), 1),
    round(icc(fit)$ICC_adjusted, 3),
    nobs(fit),
    ngrps(fit)
  )
)

tbl_diag <- diag_df |>
  gt() |>
  tab_header(title = "Model Diagnostics")

gtsave(tbl_diag, "output/tbl_01c_diagnostics.pdf")
gtsave(tbl_diag, "output/tbl_01c_diagnostics.png", vwidth = 600)
```

### Post-hoc contrasts table

```r
library(emmeans)

tbl_contrasts <- pairs(emmeans(fit, ~ group), adjust = "tukey") |>
  as_tibble() |>
  mutate(
    across(c(estimate, SE, t.ratio), \(x) round(x, 3)),
    p.value = scales::pvalue(p.value)
  ) |>
  gt() |>
  tab_header(title = "Pairwise Comparisons (Tukey-adjusted)")

gtsave(tbl_contrasts, "output/tbl_01d_pairwise.pdf")
gtsave(tbl_contrasts, "output/tbl_01d_pairwise.png", vwidth = 800)
```

### Using gtsummary for quick model tables

```r
library(gtsummary)

# One-line model summary table
tbl_regression(fit, exponentiate = FALSE) |>
  bold_p() |>
  as_gt() |>
  gtsave("output/tbl_01a_regression.pdf")
```

### gt formatting conventions

- Use `tab_header()` with a descriptive title
- Use `tab_options(table.font.size = px(12))` for readable PDF output
- Use `fmt_number(decimals = 3)` for numeric columns when not pre-rounded
- Use `tab_footnote()` for method details (e.g., "Satterthwaite degrees of freedom")
- Save both `.pdf` (for manuscript/LaTeX) and `.png` (for quick preview / slides)
- Set `vwidth = 600–1000` in `gtsave(..., .png)` to control table width

## Code Style — Tidyverse Style Guide

**All R code must conform to the [Tidyverse Style Guide](https://style.tidyverse.org/).**

### Naming
- **Files:** lowercase, use `_` or `-` as separators, `.R` extension. Zero-pad numeric prefixes (`01_`, `02_`). No spaces or special characters.
- **Objects:** `snake_case` only. Variables are nouns, functions are verbs. Never use `.` in names (reserved for S3 dispatch). Never shadow base functions (`c`, `mean`, `T`, `F`).

### Spacing and Operators
- Space after commas, never before: `x[, 1]`
- Spaces around infix operators (`<-`, `==`, `+`, `|>`), except `::`, `$`, `@`, `[`, `[[`, `^`, unary `-`/`+`
- No spaces inside parentheses: `mean(x, na.rm = TRUE)`
- Space before `(` for control flow: `if (x > 0) {`
- Use `<-` for assignment, never `=`

### Line Length and Indentation
- Maximum 80 characters per line
- Indent with 2 spaces (never tabs)
- If function arguments don't fit on one line, put each on its own line, indented:
  ```r
  fit <- gam(
    y ~ s(age, by = group) + s(subject, bs = "re"),
    data = df_model,
    method = "REML"
  )
  ```

### Pipes
- Use base pipe `|>` (not `%>%`)
- `|>` has a space before it and is followed by a newline
- Each step indented 2 spaces:
  ```r
  df |>
    filter(!is.na(outcome)) |>
    mutate(age_z = scale(age)[, 1]) |>
    group_by(group) |>
    summarise(mean_val = mean(outcome), .groups = "drop")
  ```

### Braces and Control Flow
- `{` is always the last character on its line
- `}` is always the first character on its line
- Contents indented 2 spaces
- `else` on same line as closing `}`: `} else {`
- Loop/if bodies always use braces (even one-liners)
- Use `&&`/`||` in `if` conditions (never `&`/`|`)

### Functions
- Only use `return()` for early returns; rely on implicit last-expression return
- Multi-line definitions: arguments each on own line, indented 2 spaces
- Use `\(x)` lambda for short anonymous functions; `function(x)` for multi-line

### ggplot2
- `+` has a space before and is followed by a newline
- Layers indented 2 spaces below `ggplot()`:
  ```r
  df |>
    ggplot(aes(x = age, y = value, color = group)) +
    geom_point(alpha = 0.4) +
    geom_smooth(method = "gam") +
    theme_minimal()
  ```
- Do not manipulate data inside `ggplot()` — do it in the pipe before

### Comments
- `# ` (hash + space) to start
- Explain "why", not "what"
- Use `# Section name ----` for file sections

### Strings and Literals
- Double quotes `"` for strings
- `TRUE`/`FALSE`, never `T`/`F`

### Tooling
- Use `styler` for automated reformatting and `lintr` for style checking

## When Python Is Acceptable

- Machine learning / prediction (not inference) — scikit-learn is appropriate
- Data pipelines that feed into R (e.g., SuStaIn output, NIfTI extraction) — pandas/polars for ETL, then pass CSV to R

**Do NOT use Python for:**
- Descriptive statistics, summaries, or counts — use `dplyr::summarise()`
- Data reshaping or pivoting — use `tidyr::pivot_longer()` / `pivot_wider()`
- String manipulation on data columns — use `stringr`
- Any data wrangling that precedes or follows a model — keep it all in R/tidyverse

## Package Installation

If a package is missing:

```r
install.packages("package_name", repos="https://cloud.r-project.org")
```

If HTTPS fails (SSL issues), fall back to:

```r
options(repos = c(CRAN = "http://cran.r-project.org"))
options(download.file.method = "wget")
install.packages("package_name", method="wget")
```
