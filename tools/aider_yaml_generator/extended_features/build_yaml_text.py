import pathlib

from tools.aider_yaml_generator.extended_features.rel_or_abs import rel_or_abs


def build_yaml_text(
    model: str | None,
    *,
    add_gitignore: bool,
    rw_paths: list[pathlib.Path],
    ro_paths: list[pathlib.Path],
    meta: dict,
    root: pathlib.Path,
    path_mode: str,
) -> str:
    lines: list[str] = ["# авто-сгенерировано collect_rw_ro.py", f"# root: {root}"]
    ns = meta.get("namespace")
    if ns:
        lines.append(f"# namespace: {ns}")
    seeds = meta.get("seeds", [])
    if seeds:
        lines.append("# seeds:")
        lines.extend([f"#   - {s}" for s in seeds])
    lines.append(f"# max_depth: {meta.get('max_depth')}")
    mtm = meta.get("max_total_mib")
    mtb = meta.get("max_total_bytes")
    if mtm:
        lines.append(f"# max_total_mib: {mtm}")
    if mtb:
        lines.append(f"# max_total_bytes: {mtb}")
    lines.append(f"# add_gitignore_files: {add_gitignore}")

    if model:
        lines.append(f'\nmodel: "{model}"')
    lines.append(f"add-gitignore-files: {'true' if add_gitignore else 'false'}\n")

    # RW
    lines.append("file:  # READ-WRITE (RW)")
    if not rw_paths:
        lines.append("  []")
    else:
        lines.extend([f"  - {rel_or_abs(p, root, path_mode)}" for p in rw_paths])

    # RO
    lines.append("\nread:  # READ-ONLY (RO)")
    if not ro_paths:
        lines.append("  []")
    else:
        lines.extend([f"  - {rel_or_abs(p, root, path_mode)}" for p in ro_paths])

    return "\n".join(lines) + "\n"
