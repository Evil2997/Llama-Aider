import pathlib
from collections.abc import Iterable


def ensure_list_unique_sorted(paths: Iterable[pathlib.Path]) -> list[pathlib.Path]:
    seen = set()
    out = []
    for p in paths:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(rp)
    out.sort(key=lambda x: str(x))
    return out
