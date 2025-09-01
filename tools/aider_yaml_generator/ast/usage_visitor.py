import ast


class UsageVisitor(ast.NodeVisitor):
    def __init__(self, targets: set[str], type_aliases: set[str]) -> None:
        self.targets = targets
        self.type_aliases = type_aliases
        self.hit = False

    def visit_Name(self, node: ast.Name) -> None:
        if (self.targets and node.id in self.targets) or (self.type_aliases and node.id in self.type_aliases):
            self.hit = True
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        ann = getattr(node, "annotation", None)
        if isinstance(ann, ast.Name) and self.type_aliases and ann.id in self.type_aliases:
            self.hit = True
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg) -> None:
        ann = getattr(node, "annotation", None)
        if isinstance(ann, ast.Name) and self.type_aliases and ann.id in self.type_aliases:
            self.hit = True
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        ann = getattr(node, "returns", None)
        if isinstance(ann, ast.Name) and self.type_aliases and ann.id in self.type_aliases:
            self.hit = True
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        # string-annotations: Optional["MyAlias"]
        sl = getattr(node, "slice", None)
        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
            self.hit = True
        self.generic_visit(node)
