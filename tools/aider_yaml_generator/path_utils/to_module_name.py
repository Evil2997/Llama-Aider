import pathlib


def to_module_name(project_root: pathlib.Path, file_path: pathlib.Path) -> str | None:
    try:
        rel = file_path.relative_to(project_root)
    except ValueError:
        return None
    rel = rel.parent if rel.name == "__init__.py" else rel.with_suffix("")
    return ".".join(rel.parts)
