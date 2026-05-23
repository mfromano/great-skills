#!/usr/bin/env python3
"""Static call-graph analysis using Python's ast module.

Produces a deterministic JSON representation of a module's function index,
call graph, entry points, and execution order. No external dependencies.
"""

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path


def compute_complexity(node):
    """Cyclomatic complexity: count decision points + 1."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, (ast.IfExp, ast.comprehension)):
            complexity += 1
    return complexity


def extract_functions(tree, source_lines):
    """Extract all function/method definitions with metadata."""
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    name = f"{class_name}.{item.name}"
                    functions.append(_function_info(item, name, source_lines))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not _is_method(node, tree):
                functions.append(_function_info(node, node.name, source_lines))

    return functions


def _is_method(node, tree):
    """Check if a function node is a method inside a class."""
    for cls in ast.walk(tree):
        if isinstance(cls, ast.ClassDef):
            for item in cls.body:
                if item is node:
                    return True
    return False


def _function_info(node, name, source_lines):
    """Build metadata dict for a single function."""
    line_end = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else node.lineno
    for child in ast.walk(node):
        if hasattr(child, "lineno"):
            line_end = max(line_end, getattr(child, "end_lineno", child.lineno))

    args = []
    for arg in node.args.args:
        if arg.arg != "self" and arg.arg != "cls":
            args.append(arg.arg)

    decorators = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            decorators.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            decorators.append(ast.unparse(dec))
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Name):
                decorators.append(dec.func.id)
            elif isinstance(dec.func, ast.Attribute):
                decorators.append(ast.unparse(dec.func))

    return {
        "name": name,
        "line_start": node.lineno,
        "line_end": line_end,
        "args": args,
        "decorators": decorators,
        "complexity": compute_complexity(node),
        "is_async": isinstance(node, ast.AsyncFunctionDef),
    }


def build_call_graph(tree, functions):
    """Map each function to the functions it calls (within the module)."""
    known_names = {f["name"] for f in functions}
    short_names = {}
    for name in known_names:
        short = name.split(".")[-1] if "." in name else name
        short_names[short] = name

    call_graph = defaultdict(list)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    caller = f"{class_name}.{item.name}"
                    _collect_calls(item, caller, known_names, short_names, call_graph, class_name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not _is_method(node, tree):
                _collect_calls(node, node.name, known_names, short_names, call_graph, None)

    return dict(call_graph)


def _collect_calls(func_node, caller_name, known_names, short_names, call_graph, class_context):
    """Walk a function body and record calls to known functions."""
    for child in ast.walk(func_node):
        if isinstance(child, ast.Call):
            callee = _resolve_call_target(child, class_context)
            if callee is None:
                continue
            if callee in known_names:
                if callee not in call_graph[caller_name]:
                    call_graph[caller_name].append(callee)
            elif callee in short_names:
                resolved = short_names[callee]
                if resolved not in call_graph[caller_name]:
                    call_graph[caller_name].append(resolved)


def _resolve_call_target(call_node, class_context):
    """Extract the callable name from a Call node.

    Resolves self.method() and cls.method() to ClassName.method when inside a class.
    """
    func = call_node.func
    if isinstance(func, ast.Name):
        return func.id
    elif isinstance(func, ast.Attribute):
        if isinstance(func.value, ast.Name):
            if func.value.id in ("self", "cls") and class_context:
                return f"{class_context}.{func.attr}"
            return f"{func.value.id}.{func.attr}"
        return func.attr
    return None


def find_entry_points(functions, call_graph):
    """Functions not called by any other function in the module.

    Self-recursive calls don't disqualify a function from being an entry point.
    """
    all_callees = set()
    for caller, callees in call_graph.items():
        for callee in callees:
            if callee != caller:
                all_callees.add(callee)

    entry_points = []
    for f in functions:
        if f["name"] not in all_callees:
            entry_points.append(f["name"])

    return entry_points


def compute_execution_order(call_graph, entry_points, functions):
    """Topological sort from entry points through the call graph.

    Handles cycles by detecting and flagging them without crashing.
    """
    all_names = {f["name"] for f in functions}
    visited = set()
    order = []
    in_stack = set()
    cycles = []

    def dfs(name):
        if name in visited:
            return
        if name in in_stack:
            cycles.append(name)
            return
        in_stack.add(name)
        for callee in call_graph.get(name, []):
            if callee in all_names:
                dfs(callee)
        in_stack.discard(name)
        visited.add(name)
        order.append(name)

    for ep in entry_points:
        dfs(ep)

    for f in functions:
        if f["name"] not in visited:
            dfs(f["name"])

    order.reverse()
    return order, cycles


def parse_file(path):
    """Main entry point: parse a Python file and return the full analysis."""
    source = Path(path).read_text(encoding="utf-8")
    source_lines = source.splitlines()
    tree = ast.parse(source, filename=path)

    functions = extract_functions(tree, source_lines)
    call_graph = build_call_graph(tree, functions)
    entry_points = find_entry_points(functions, call_graph)
    execution_order, cycles = compute_execution_order(call_graph, entry_points, functions)

    for f in functions:
        f["calls"] = call_graph.get(f["name"], [])
        all_callees = set()
        for callees in call_graph.values():
            all_callees.update(callees)
        f["called_by"] = [
            caller for caller, callees in call_graph.items() if f["name"] in callees
        ]
        f["is_entry_point"] = f["name"] in entry_points

    return {
        "file": str(Path(path).name),
        "file_path": str(Path(path).resolve()),
        "total_lines": len(source_lines),
        "functions": functions,
        "call_graph": call_graph,
        "entry_points": entry_points,
        "execution_order": execution_order,
        "cycles": cycles,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: audit_call_graph.py <file.py> [file2.py ...]", file=sys.stderr)
        sys.exit(1)

    results = []
    for path in sys.argv[1:]:
        results.append(parse_file(path))

    output = results[0] if len(results) == 1 else results
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
