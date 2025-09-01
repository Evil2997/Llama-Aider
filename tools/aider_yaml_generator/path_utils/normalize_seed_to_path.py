import pathlib


def normalize_seed_to_path(root: pathlib.Path, seed: str) -> pathlib.Path:
    s = seed.strip()
    if "." in s and "/" not in s and "\\" not in s:
        parts = s.split(".")
        p = root.joinpath(*parts)
        if p.suffix != ".py":
            p = p.with_suffix(".py")
        return p.resolve()
    return (root / s).resolve()
