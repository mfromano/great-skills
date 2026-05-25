---
name: r-statistical-modeling
description: Use R (mgcv, lme4, lmerTest, nlme, emmeans) instead of Python for all statistical modeling tasks. Triggers when fitting mixed models, GAMs, GLMMs, or any regression/ANOVA. Prefer R's mature ecosystem for inference, diagnostics, and publication-quality model summaries.
when_to_use: Any time a statistical model is being created, fitted, or analyzed — linear models, mixed effects, GAMs, GLMs/GLMMs, repeated measures, longitudinal analysis, or when model diagnostics/contrasts/post-hoc tests are needed.
license: MIT
metadata:
  skill-author: Michael Romano
---

# R-First Statistical Modeling

**When a statistical model is needed, use R — not Python.**

R's statistical ecosystem (mgcv, lme4, lmerTest, nlme, emmeans) is more mature, better tested, and produces publication-ready output for inference. Python tools (statsmodels, pingouin) are acceptable for simple descriptive statistics or quick t-tests, but for anything involving mixed effects, splines, GAMs, or complex random-effect structures, R is the correct tool.

## When This Skill Applies

- Fitting any regression model (linear, logistic, Poisson, etc.)
- Mixed-effects / multilevel models (random intercepts/slopes)
- Generalized additive models (GAMs, GAMMs)
- Repeated measures / longitudinal analysis
- ANOVA with post-hoc contrasts
- Model diagnostics (residuals, influence, overdispersion)
- Estimated marginal means and pairwise comparisons

## Core Packages

| Package | Purpose |
|---------|---------|
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

## r-btw MCP Server

The `r-btw` MCP server (`btw::btw_mcp_server()`) exposes R objects, data frames, and documentation directly to Claude without requiring file round-trips. Use it when it is available.

**When to use r-btw tools instead of `Rscript`:**
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
library(lme4)
library(lmerTest)
data(sleepstudy)
fit <- lmer(Reaction ~ Days + (Days | Subject), data=sleepstudy)
print(summary(fit))
'
```

For scripts that produce plots, save to file:

```r
library(ggplot2)
pdf("plot.pdf", width=8, height=6)
# ... plotting code ...
dev.off()
```

## Model Recipes

### Linear Mixed-Effects Model (lmer)

```r
library(lme4)
library(lmerTest)

fit <- lmer(outcome ~ fixed1 + fixed2 + (1 + fixed1 | subject), data=df)
summary(fit)           # Satterthwaite p-values
anova(fit, type=3)     # Type III ANOVA table
confint(fit)           # Profile confidence intervals
```

### Generalized Additive Model (mgcv)

```r
library(mgcv)

# Smooth nonlinear effects
fit <- gam(y ~ s(age) + s(time) + group + s(age, by=group), data=df)
summary(fit)
plot(fit, pages=1)

# With random effects (GAMM via re= or bs="re")
fit <- gam(y ~ s(age) + s(subject, bs="re"), data=df)

# Or use gamm() for nlme-style random effects
fit <- gamm(y ~ s(age), random=list(subject=~1), data=df)
```

### GAMM with large datasets (bam)

```r
library(mgcv)

# bam() is faster for large datasets, supports discrete=TRUE
fit <- bam(y ~ s(age) + s(subject, bs="re") + group,
           data=df, discrete=TRUE)
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

## Reading Data

```r
library(readr)

df <- read_csv("data.csv")

# Or for Excel
library(readxl)
df <- read_excel("data.xlsx", sheet=1)
```

## Reporting Results

Structure model output for manuscripts:

```r
library(broom.mixed)

# Tidy fixed effects table
tidy(fit, effects="fixed", conf.int=TRUE)

# Random effects
tidy(fit, effects="ran_pars")

# For APA-style: report F/t, df, p, effect size
# lmerTest provides Satterthwaite df in summary()
```

## When Python Is Acceptable

- Quick descriptive statistics (mean, SD, counts) — pandas is fine
- Simple t-tests or chi-square — scipy.stats is fine
- Machine learning / prediction (not inference) — scikit-learn is appropriate
- Data wrangling before modeling — pandas/polars, then pass CSV to R

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
