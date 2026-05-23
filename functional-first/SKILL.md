---
name: functional-first
description: Use when writing, refactoring, or reviewing Python or R code. Enforces functional-first style — pure functions as default, classes only as configured namespaces. Triggers on class hierarchies, mutable state, R6/S4 usage, global assignment (<<-), or questions like "should this be a class".
---

# Functional-First Style

Pure functions are easier to debug, test, and audit. Default to functions; reach for classes only when they serve as configured namespaces (constructor stores config, methods use it read-only).

## Core Principle

| Default to | Reach for only when |
|------------|---------------------|
| Pure functions (inputs in, value out) | You need a shared config namespace |
| Composition (small functions piped) | A protocol/interface boundary requires dispatch |
| Explicit arguments | Closure state is genuinely simpler |

## Python

| Prefer | Avoid | Why |
|--------|-------|-----|
| `@dataclass(frozen=True)` for data | Mutable class attributes | Immutable = traceable |
| Functions that return values | Methods that mutate `self` | Call graphs capture data flow |
| Composition | Deep inheritance | Flat is debuggable |
| Type hints on signatures | Implicit contracts | Enables static checking |
| Module-level functions | Stateless `@staticmethod` classes | A module IS a namespace |

Acceptable class: constructor stores config, methods are pure given that config.

## R

| Prefer | Avoid | Why |
|--------|-------|-----|
| Standalone functions | R6/S4 classes | R's strength is functional |
| Pipe chains (`|>` or `%>%`) | Nested calls or temp variables | Left-to-right data flow |
| Explicit function arguments | Global variables, `attach()` | Reproducibility needs explicit inputs |
| Return values | `<<-` (global assignment) | Side effects hide data flow |
| Named lists for config | Environments as state bags | Lists are inspectable |

Acceptable OOP in R: S3 generics for method dispatch (`print.myclass`).

## When Classes Are Fine

- Configured namespace (dataclass/named-list + methods that read config only)
- Protocol boundary (ABC in Python, S3 generic in R)
- External API requirement (PyTorch `nn.Module`, R6 for Shiny)

## Relationship to Other Skills

- **code-audit**: Explains WHY functional style aids auditability
- **clean-functions**: Covers argument counts, single responsibility — complementary
- **clean-general**: Covers DRY, Law of Demeter — complementary
