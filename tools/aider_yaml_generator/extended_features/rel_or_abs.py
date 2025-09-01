import pathlib


def rel_or_abs(p: pathlib.Path, root: pathlib.Path, mode: str) -> str:
    if mode == "abs":
        return str(p)
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)
