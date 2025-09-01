import pathlib
from collections.abc import Iterable


def iter_py(ns_root: pathlib.Path) -> Iterable[pathlib.Path]:
    yield from ns_root.rglob("*.py")
