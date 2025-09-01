import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class FileEntry:
    path: pathlib.Path
    depth: int  # 0 = seed; >=1 imports
