---
name: code-audit
description: Interactive, deterministic code audit. Walks through a Python file function-by-function using AST-derived call graphs, with parallel specialist agents providing findings anchored to exact line numbers. Use when auditing code for bugs, reviewing Claude-generated code, or performing a thorough code walkthrough.
license: MIT
metadata:
  skill-author: Michael Romano
---

# Code Audit Skill

An interactive, multi-agent audit pipeline that walks through Python code deterministically — no hallucinated code, no skipped sections.

## Invocation

Triggered by requests like:
- "Audit `src/data_loader.py`"
- "Walk me through this file for bugs"
- "Review this module step by step"

## Architecture: Three Layers

| Layer | Source | Hallucination risk |
|-------|--------|-------------------|
| Code & structure | `audit_call_graph.py` + Read tool | None — deterministic |
| Agent findings | 4 specialist LLM agents | Labeled as commentary |
| Navigation | User controls | None |

## Workflow

### Step 1: Build the Call Graph

Run the AST analysis script on the target file:

```bash
python3 ~/.claude/skills/code-audit/audit_call_graph.py <target-file>
```

Parse the JSON output. This gives you:
- All functions with exact line ranges
- The call graph (who calls whom)
- Entry points (functions not called by others)
- Execution order (topological sort)
- Cyclomatic complexity per function
- Cycle detection

### Step 2: Dispatch Specialist Agents

Launch **4 agents in parallel** using the Agent tool. Each agent receives:
1. The full file content (line-numbered, via Read tool output)
2. The call graph JSON (for execution context)
3. Their specialist prompt (see `agent-prompts.md`)

Agent types:
- **Logic** — correctness, edge cases, off-by-one, missing checks
- **Design** — coupling, cohesion, naming, complexity, dead code
- **Security** — injection, path traversal, unsafe operations, data exposure
- **Performance** — O(n²) patterns, redundant I/O, unnecessary copies

Each agent MUST return findings as a JSON array:
```json
[
  {
    "function": "function_name",
    "lines": [42, 45],
    "severity": "critical|important|minor",
    "category": "logic|design|security|performance",
    "finding": "Brief description of the issue"
  }
]
```

### Step 3: Present the Call Graph Tree

Show the user the navigable tree with finding counts:

```
Entry points:
├── main (L10-25) [3 findings]
│   ├── process_data (L28-45) [1 finding]
│   │   └── validate_input (L48-55) [0 findings]
│   └── format_output (L58-62) [2 findings]
├── DataProcessor.run (L70-85) [1 finding]
│   ├── DataProcessor._transform (L88-100) [4 findings]
│   └── DataProcessor._format (L103-110) [0 findings]
...

Navigate: [function name] to inspect, [done] to finish
```

### Step 4: Interactive Walkthrough

When the user selects a function:

1. **Show verbatim source code** — use the Read tool with exact line range from the call graph. NEVER paraphrase, summarize, or regenerate the code.

2. **Show agent findings** — display all findings for that function, grouped by severity:
   ```
   ## `process_data` (L28-45)

   [source code displayed here via Read tool]

   ### Findings
   **[CRITICAL | Logic]** L32: Division by zero when items list is empty...
   **[IMPORTANT | Security]** L40: User input passed to eval() without sanitization...
   **[MINOR | Design]** L35: Variable 'x' could be more descriptive...
   ```

3. **Offer navigation**:
   ```
   [next] → format_output | [into] validate_input | [back] → main | [skip] | [done]
   ```

### Step 5: Persist Findings

Create `audits/YYYY-MM-DD-<filename>.md` in the project directory with:

```markdown
# Code Audit: <filename>
Date: YYYY-MM-DD
Auditor: <user> (assisted by Claude Code)

## Summary
- Functions audited: X/Y
- Critical findings: N
- Important findings: N
- Minor findings: N

## Findings by Function

### `function_name` (L##-##)
**[SEVERITY | Category]** L##: Description...
```

## Writing Auditable Code

Patterns that make code easier to audit with this tool (and in general):

| Prefer | Avoid | Why |
|--------|-------|-----|
| Pure functions (explicit inputs → outputs) | Methods mutating `self.x` across calls | Call graph captures calls, not shared-state dependencies |
| Flat class hierarchies ("configured namespace") | Deep inheritance chains | Inherited methods are non-local — call graph can't resolve `super()` dispatch |
| One responsibility per function | Multi-purpose functions | Keeps cyclomatic complexity low, findings map cleanly to behavior |
| Return values | Side-effect chains (A mutates state B reads) | The call graph tells the truth about data flow |
| Small functions (< 30 lines) | Long functions with many branches | Agent findings stay anchored to specific behavior |

A class like `AWSDataLoader` (constructor stores config, methods use it read-only) is fine — it's essentially a function namespace with shared configuration. What hurts auditability is methods that mutate instance state that other methods implicitly depend on.

## Critical Rules

1. **NEVER regenerate or paraphrase code.** Always use the Read tool to show exact file content.
2. **NEVER claim a finding without a line number.** Every finding must reference specific lines.
3. **The call graph is ground truth.** If the AST script says function X is at lines 42-58, that's where it is.
4. **Agent findings are opinions.** Always present them as labeled commentary, never as fact.
5. **User controls navigation.** Never auto-advance. Wait for the user to choose where to go.
6. **Determinism is non-negotiable.** The structural analysis produces identical output every time.
