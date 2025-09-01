import pathlib

from tools.aider_yaml_generator.extended_features.file_entry import FileEntry
from tools.aider_yaml_generator.path_utils.extract_imports import extract_imports
from tools.aider_yaml_generator.path_utils.resolve_module_to_path import resolve_module_to_path


def collect_with_depth(
    project_root: pathlib.Path,
    seeds: list[pathlib.Path],
    prefixes: list[str],
    max_depth: int,
) -> tuple[dict[pathlib.Path, FileEntry], dict[pathlib.Path, FileEntry], set[str]]:
    rw_map: dict[pathlib.Path, FileEntry] = {}
    ro_map: dict[pathlib.Path, FileEntry] = {}
    unresolved: set[str] = set()
    visited: set[pathlib.Path] = set()

    def visit_file(fp: pathlib.Path, depth: int) -> None:
        if fp in visited:
            return
        visited.add(fp)

        if max_depth == 0 and depth > 0:
            return
        if 0 <= max_depth < depth:
            return

        imports = extract_imports(project_root, fp, prefixes)
        for mod in imports:
            p = resolve_module_to_path(project_root, mod)
            base = mod.rsplit(".", 1)[0] if "." in mod else mod
            pb = resolve_module_to_path(project_root, base)

            if pb is None and p is None:
                unresolved.add(base)
                continue

            next_depth = depth + 1

            # if alias refers to symbol -> fallback to base
            target = p or pb
            if target is None:
                continue

            if target not in rw_map and target not in ro_map:
                ro_map[target] = FileEntry(target, next_depth)
                visit_file(target, next_depth)

    for s in seeds:
        rw_map[s] = FileEntry(s, 0)
        visit_file(s, 0)

    return rw_map, ro_map, unresolved
