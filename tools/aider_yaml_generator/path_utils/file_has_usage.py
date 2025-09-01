import ast
import pathlib
import re

from tools.aider_yaml_generator.ast.usage_visitor import UsageVisitor


def file_has_usage(py: pathlib.Path, targets: set[str], type_aliases: set[str], str_re: re.Pattern | None) -> bool:
    try:
        text = py.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    try:
        tree = ast.parse(text, filename=str(py))
        v = UsageVisitor(targets, type_aliases)
        v.visit(tree)
        if v.hit:
            return True
    except SyntaxError:
        pass
    return bool(str_re is not None and str_re.search(text))
