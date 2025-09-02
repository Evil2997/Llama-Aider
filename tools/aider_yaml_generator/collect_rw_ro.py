#!/usr/bin/env python3

"""collect_rw_ro.py.

Собирает RW/RO файлы для Aider:
- RW: сиды + файлы, где замечено использование искомых var/type alias
- RO: импорт-зависимости по ограниченной глубине
- лимит суммарного объёма: --max-total-mib / --max-total-bytes
  (RW всегда включаются; RO добираются до лимита)
- "служебные" файлы (CONVENTIONS.md, AIDER_RULES.md, task.md, AIDER_TODO.md)
  добавляются в RO всегда, поверх лимита
- генерирует YAML-конфиг для Aider (печатает в stdout и пишет на диск по --emit-config).
"""

from __future__ import annotations

import pathlib
import re
import sys

from tools.aider_yaml_generator.cli import args_parser
from tools.aider_yaml_generator.constants import (
    DEFAULT_MODEL,
    MIB,
)
from tools.aider_yaml_generator.extended_features.build_yaml_text import build_yaml_text
from tools.aider_yaml_generator.extended_features.collect_with_depth import (
    collect_with_depth,
)
from tools.aider_yaml_generator.extended_features.ensure_list_unique_sorted import (
    ensure_list_unique_sorted,
)
from tools.aider_yaml_generator.extended_features.estimate_tokens import estimate_tokens
from tools.aider_yaml_generator.extended_features.file_entry import FileEntry
from tools.aider_yaml_generator.extended_features.human_bytes import human_bytes
from tools.aider_yaml_generator.extended_features.largest_top_n import largest_top_n
from tools.aider_yaml_generator.extended_features.load_existing_model_from_yaml import (
    load_existing_model_from_yaml,
)
from tools.aider_yaml_generator.extended_features.read_text_bytes import read_text_bytes
from tools.aider_yaml_generator.extended_features.rel_or_abs import rel_or_abs
from tools.aider_yaml_generator.path_utils.file_has_markers import file_marker_hits
from tools.aider_yaml_generator.path_utils.file_has_usage import file_has_usage
from tools.aider_yaml_generator.path_utils.iter_py import iter_py
from tools.aider_yaml_generator.path_utils.normalize_seed_to_path import (
    normalize_seed_to_path,
)


def main() -> None:
    args = args_parser()

    root = pathlib.Path(args.root).resolve()
    namespace = args.namespace
    ns_root = (root / namespace).resolve()

    if not ns_root.exists():
        print(f"[ERR] Namespace path not found: {ns_root}", file=sys.stderr)
        sys.exit(2)

    if not (args.seeds or args.vars or args.types):
        print(
            "[ERR] Provide at least one of: --seed, --vars, or --types", file=sys.stderr
        )
        sys.exit(2)

    # Seeds -> absolute paths
    seed_paths: list[pathlib.Path] = []
    for seed in args.seeds:
        p = normalize_seed_to_path(root, seed)
        if not p.exists():
            print(f"[ERR] Seed not found on disk: {p}", file=sys.stderr)
            sys.exit(2)
        seed_paths.append(p)

    # Usage scan inside namespace (по именам/типам)
    targets = set(args.vars or [])
    type_aliases = set(args.types or [])
    alt_tokens: set[str] = set()
    alt_tokens |= targets
    alt_tokens |= type_aliases
    str_re = (
        re.compile(r"\b(" + "|".join(map(re.escape, sorted(alt_tokens))) + r")\b")
        if alt_tokens
        else None
    )

    usage_files: list[pathlib.Path] = []
    if targets or type_aliases:
        usage_files.extend(
            [
                py
                for py in iter_py(ns_root)
                if file_has_usage(py, targets, type_aliases, str_re)
            ]
        )

    # AIDER_TODO.md — включаем как RW, если указан и существует
    todo_paths: list[pathlib.Path] = []
    if args.todo:
        todo_path = pathlib.Path(args.todo)
        todo_path = (
            (root / todo_path).resolve()
            if not todo_path.is_absolute()
            else todo_path.resolve()
        )
        if todo_path.exists():
            todo_paths.append(todo_path)
        else:
            print(f"[WARN] --todo not found on disk: {todo_path}", file=sys.stderr)

    # === Новый блок: авто-сиды по маркерам (raise + TO-DO/FIX-ME/etc.) ===
    auto_seed_paths: list[pathlib.Path] = []
    auto_raise_count = 0
    auto_tag_count = 0

    if args.scan_raises or args.scan_tags:
        raise_names = list(args.raise_names or [])
        tag_list = list(args.tag_list or [])

        for py in iter_py(ns_root):
            raise_hit, tag_hit = file_marker_hits(py, raise_names, tag_list)
            if raise_hit or tag_hit:
                auto_seed_paths.append(py)
                auto_raise_count += int(bool(raise_hit))
                auto_tag_count += int(bool(tag_hit))

    # RW = seeds + usage_hits + AIDER_TODO + auto-seeds
    combined_rw = ensure_list_unique_sorted(
        [*seed_paths, *todo_paths, *usage_files, *auto_seed_paths]
    )

    # Depth-limited import traversal:
    # ВАЖНО: передаём именно combined_rw как начальные точки (depth=0)
    rw_map, ro_map, unresolved = collect_with_depth(
        root, list(combined_rw), [namespace], args.max_depth
    )

    # Ensure usage_hits are RW (даже если не были сидом)
    for uf in usage_files:
        if uf not in rw_map:
            rw_map[uf] = FileEntry(uf, 0)

    # Ensure auto-seeds are RW (на всякий случай, если не попали)
    for ap in auto_seed_paths:
        if ap not in rw_map:
            rw_map[ap] = FileEntry(ap, 0)

    rw_set = set(rw_map.keys())
    ro_entries = list(ro_map.values())

    # Always-include paths (shortcuts included)
    always_raw = list(args.always_include or [])
    always_raw.extend([x for x in (args.conventions, args.rules, args.task) if x])

    # Normalize always-include under root (allow abs/rel)
    always_paths: list[pathlib.Path] = []
    for ap in always_raw:
        apath = pathlib.Path(ap)
        apath = (root / apath).resolve() if not apath.is_absolute() else apath.resolve()
        always_paths.append(apath)

    # Dedup and prefer existing files only (warn if missing)
    always_final: list[pathlib.Path] = []
    warned = set()
    for ap in ensure_list_unique_sorted(always_paths):
        if not ap.exists():
            if ap not in warned:
                print(f"[WARN] always-include missing on disk: {ap}", file=sys.stderr)
                warned.add(ap)
            continue
        always_final.append(ap)

    # Order RO: by depth then path
    ro_entries.sort(key=lambda fe: (fe.depth, str(fe.path)))
    ro_ordered = [fe.path for fe in ro_entries]

    # Remove any overlaps between RW and RO
    ro_ordered = [p for p in ro_ordered if p not in rw_set]

    # Base bytes = RW + always-include (они идут сверх лимита)
    base_paths = ensure_list_unique_sorted([*rw_set, *always_final])
    base_bytes = sum(read_text_bytes(p) for p in base_paths)

    # Convert MiB to bytes if provided
    max_total_bytes = int(args.max_total_bytes or 0)
    if args.max_total_mib and args.max_total_mib > 0:
        max_total_bytes = int(args.max_total_mib * MIB)

    # Select RO under limit (beyond base)
    selected_ro: list[pathlib.Path] = []
    cur = base_bytes
    if max_total_bytes and max_total_bytes > 0:
        for p in ro_ordered:
            b = read_text_bytes(p)
            if cur + b <= max_total_bytes:
                selected_ro.append(p)
                cur += b
            else:
                break
    else:
        selected_ro = ro_ordered[:]

    # Final RW/RO lists
    final_rw = ensure_list_unique_sorted(rw_set)

    # RO = always_final (above limit) + selected_ro (under limit), with dedup
    final_ro = ensure_list_unique_sorted([*always_final, *selected_ro])

    # ===== Console report =====
    sep = "=" * 72
    sub = "-" * 72

    print(sep)
    print("READ-WRITE (RW) — seeds + usage hits + auto-seeds (markers)")
    print(sub)
    if final_rw:
        for p in final_rw:
            print(str(p.relative_to(root)))
    else:
        print("(empty)")

    print("\n" + sep)
    print(
        "READ-ONLY (RO) — always-include (above limit) + import deps (depth-limited under limit)"
    )
    print(sub)
    if final_ro:
        for p in final_ro:
            try:
                print(str(p.relative_to(root)))
            except Exception:
                print(str(p))
    else:
        print("(empty)")

    # Доп. сводка по авто-сидáм
    if args.scan_raises or args.scan_tags:
        print("\n" + sep)
        print("AUTO-SEEDS — marker hits summary")
        print(sub)
        print(f"files with markers: {len(auto_seed_paths)}")
        if args.scan_raises:
            print(f"  raise-matches:    {auto_raise_count}")
        if args.scan_tags:
            print(f"  tag-matches:      {auto_tag_count}")

    # Sizes / tokens summary
    if args.show_sizes:
        all_paths = ensure_list_unique_sorted([*final_rw, *final_ro])
        total_bytes = sum(read_text_bytes(p) for p in all_paths)
        total_chars = total_bytes  # approx
        est_tokens = estimate_tokens(total_chars, args.chars_per_token)

        print("\n" + sep)
        print("SIZE SUMMARY")
        print(sub)
        print(
            f"RW files: {len(final_rw)}; RO files: {len(final_ro)}; TOTAL files: {len(all_paths)}"
        )
        print(f"Base (RW+always): {human_bytes(base_bytes)}")
        print(f"Total size:       {human_bytes(total_bytes)} ({total_bytes} bytes)")
        print(
            f"Est. tokens ~= total_chars / {args.chars_per_token:g} = ~{est_tokens:,}"
        )

        largest_top_n(
            all_paths=all_paths,
            root=root,
        )

    # Unresolved modules
    if unresolved:
        print("\n" + sep)
        print("UNRESOLVED MODULES — not under namespace or missing on disk")
        print(sub)
        for m in sorted(unresolved):
            print(m)

    # ===== YAML generation =====
    if args.model:
        model_to_write = args.model
    else:
        if args.emit_config:
            emit_path = pathlib.Path(args.emit_config).resolve()
            if emit_path.exists():
                prev = load_existing_model_from_yaml(emit_path)
                model_to_write = prev if prev else DEFAULT_MODEL
            else:
                model_to_write = DEFAULT_MODEL
        else:
            model_to_write = DEFAULT_MODEL

    yaml_meta = dict(
        namespace=namespace,
        seeds=[rel_or_abs(p, root, "root") for p in seed_paths],
        max_depth=args.max_depth,
        max_total_mib=args.max_total_mib if args.max_total_mib else None,
        max_total_bytes=args.max_total_bytes if args.max_total_bytes else None,
    )
    yaml_text = build_yaml_text(
        model=model_to_write,
        add_gitignore=bool(args.add_gitignore_files),
        rw_paths=final_rw,
        ro_paths=final_ro,
        meta=yaml_meta,
        root=root,
        path_mode=args.use_relative,
    )

    print("\n" + sep)
    print("AIDER YAML (to be written)")
    print(sub)
    print(yaml_text, end="")

    # Write file if requested and not dry-run
    if args.emit_config and not args.dry_run:
        out_path = pathlib.Path(args.emit_config).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(yaml_text, encoding="utf-8")
        print(f"[OK] Config written: {out_path}")

    print(sep)


if __name__ == "__main__":
    main()
