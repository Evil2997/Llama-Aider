from __future__ import annotations

import ast
import pathlib
import re
from typing import Iterable

from tools.aider_yaml_generator.ast.marker_visitor import MarkerVisitor


def _compile_tag_regex(tags: Iterable[str]) -> re.Pattern | None:
    clean = [t.strip() for t in tags if t and t.strip()]
    if not clean:
        return None
    pattern = r"#\s*(?:" + "|".join(map(re.escape, clean)) + r")\b"
    return re.compile(pattern)


def file_marker_hits(
    py: pathlib.Path,
    raise_names: Iterable[str],
    tags: Iterable[str],
) -> tuple[bool, bool]:
    """
    Возвращает кортеж (raise_hit, tag_hit) для данного .py файла.
    - raise_hit: найден ли raise из raise_names по AST
    - tag_hit:   найден ли тег из tags в комментариях (по regexp)
    """
    try:
        text = py.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False, False

    # --- Теги в комментариях ---
    tag_re = _compile_tag_regex(tags)
    tag_hit = bool(tag_re and tag_re.search(text))

    # --- Raise по AST ---
    try:
        tree = ast.parse(text, filename=str(py))
    except SyntaxError:
        # Если синтаксис битый — тег по тексту всё равно мог сработать
        return False, tag_hit

    mv = MarkerVisitor(set(raise_names))
    mv.visit(tree)
    return mv.raise_hit, tag_hit
