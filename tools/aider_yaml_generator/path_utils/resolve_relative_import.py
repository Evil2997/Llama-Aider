def resolve_relative_import(curr_module: str, level: int, module: str | None) -> str:
    parts = curr_module.split(".")
    base = parts[:-1] if parts and parts[-1] != "__init__" else parts[:]
    up = max(0, level - 1)
    if up:
        base = base[:-up]
    if module:
        base += module.split(".")
    return ".".join(p for p in base if p).strip(".")
