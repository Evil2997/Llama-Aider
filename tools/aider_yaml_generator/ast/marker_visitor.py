from __future__ import annotations

import ast


class MarkerVisitor(ast.NodeVisitor):
    """
    Ищет raise с указанными именами (NotImplementedError и др.).
    Отмечает срабатывание флагом self.raise_hit.
    """

    def __init__(self, raise_names: set[str]) -> None:
        self.raise_names = {rn.strip() for rn in raise_names if rn and rn.strip()}
        self.raise_hit = False

    def visit_Raise(self, node: ast.Raise) -> None:
        exc = getattr(node, "exc", None)
        # raise NotImplementedError
        if isinstance(exc, ast.Name):
            if exc.id in self.raise_names:
                self.raise_hit = True

        # raise NotImplementedError("msg") / SomeError(...)
        elif isinstance(exc, ast.Call):
            func = getattr(exc, "func", None)
            # Name(...)
            if isinstance(func, ast.Name) and func.id in self.raise_names:
                self.raise_hit = True
            # SomeModule.SomeError(...)
            elif isinstance(func, ast.Attribute):
                # Берём правую часть chain.attr (напр. SomeError)
                if func.attr in self.raise_names:
                    self.raise_hit = True

        # На всякий случай продолжаем обход
        self.generic_visit(node)
