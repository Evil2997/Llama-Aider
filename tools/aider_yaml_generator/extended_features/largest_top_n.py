import pathlib

from tools.aider_yaml_generator.extended_features.human_bytes import human_bytes
from tools.aider_yaml_generator.extended_features.read_text_bytes import read_text_bytes


def largest_top_n(all_paths: list[pathlib.Path], root: pathlib.Path) -> None:
    sizes = [(p, read_text_bytes(p)) for p in all_paths]
    sizes.sort(key=lambda t: t[1], reverse=True)
    top = sizes[:20]
    if top:
        print("\nTop largest files (up to 20):")
        for p, b in top:
            try:
                rel = str(p.relative_to(root))
            except Exception:
                rel = str(p)
            print(f"{rel:<100} {human_bytes(b)}")
