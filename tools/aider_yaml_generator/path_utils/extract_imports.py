import ast
import pathlib

from tools.aider_yaml_generator.path_utils.resolve_relative_import import resolve_relative_import
from tools.aider_yaml_generator.path_utils.to_module_name import to_module_name


def extract_imports(project_root: pathlib.Path, file_path: pathlib.Path, only_prefixes: list[str]) -> set[str]:
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return set()
    try:
        tree = ast.parse(text, filename=str(file_path))
    except SyntaxError:
        return set()

    result = set()
    curr_module = to_module_name(project_root, file_path) or ""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                if any(mod == p or mod.startswith(p + ".") for p in only_prefixes):
                    result.add(mod)
        elif isinstance(node, ast.ImportFrom):
            if node.level and curr_module:
                base = resolve_relative_import(curr_module, node.level, node.module)
            else:
                base = node.module or ""
            if not base:
                continue
            if any(base == p or base.startswith(p + ".") for p in only_prefixes):
                result.add(base)
            for alias in node.names:
                candidate = f"{base}.{alias.name}"
                if any(candidate == p or candidate.startswith(p + ".") for p in only_prefixes):
                    result.add(candidate)
    return result
