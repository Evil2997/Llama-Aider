import pathlib


def resolve_module_to_path(project_root: pathlib.Path, module: str) -> pathlib.Path | None:
    p = project_root.joinpath(*module.split("."))
    if p.with_suffix(".py").exists():
        return p.with_suffix(".py")
    if p.joinpath("__init__.py").exists():
        return p.joinpath("__init__.py")
    return None
