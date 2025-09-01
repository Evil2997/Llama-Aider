import argparse


def args_parser() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect RW/RO files and emit Aider YAML config.")
    p.add_argument(
        "--root",
        required=True,
        help="Project root (absolute path)",
    )
    p.add_argument(
        "--namespace",
        required=True,
        help="Top-level package (e.g., main_app)",
    )
    p.add_argument(
        "--seed",
        dest="seeds",
        nargs="*",
        default=[],
        help="Seed files at namespace (path or dotted module). Multiple allowed.",
    )
    p.add_argument(
        "--vars",
        dest="vars",
        nargs="*",
        default=[],
        help="Variable names to search",
    )
    p.add_argument(
        "--types",
        dest="types",
        nargs="*",
        default=[],
        help="Type alias names to search",
    )

    p.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Depth for following imports: 0=seeds only, N>=1 limited depth, -1=unlimited (default: 2)",
    )
    p.add_argument(
        "--show-sizes",
        action="store_true",
        help="Print per-file sizes and totals + rough tokens estimation",
    )
    p.add_argument(
        "--max-total-bytes",
        type=int,
        default=0,
        help="If >0: include all RW, then add RO until this byte budget is reached",
    )
    p.add_argument(
        "--max-total-mib",
        type=float,
        default=0.0,
        help="Same as --max-total-bytes, but in MiB (1 MiB = 1,048,576 bytes)",
    )
    p.add_argument(
        "--chars-per-token",
        type=float,
        default=3.0,
        help="Estimate tokens as total_chars / chars_per_token (default: 3.0)",
    )

    # Always-include and shortcuts (added to RO above the limit)
    p.add_argument(
        "--always-include",
        nargs="*",
        default=[],
        help="Paths to always include in RO regardless of size limit",
    )
    p.add_argument(
        "--conventions",
        default=None,
        help="Path to CONVENTIONS.md to always include in RO",
    )
    p.add_argument(
        "--rules",
        default=None,
        help="Path to AIDER_RULES.md to always include in RO",
    )
    p.add_argument(
        "--task",
        default=None,
        help="Path to task.md to always include in RO",
    )
    p.add_argument(
        "--todo",
        default=None,
        help="Path to AIDER_TODO.md to always include in **RW** (editable)",
    )

    # YAML emitting / formatting
    p.add_argument(
        "--emit-config",
        default=None,
        help="Path to write YAML config (aider.conf.yaml). Printed to stdout as well.",
    )
    p.add_argument(
        "--use-relative",
        choices=["root", "abs"],
        default="root",
        help="Write paths in YAML relative to --root (default) or absolute",
    )
    p.add_argument(
        "--add-gitignore-files",
        action="store_true",
        help="If present -> YAML key add-gitignore-files: true; else false",
    )
    p.add_argument(
        "--model",
        default=None,
        help="Optional model string to write into YAML. "
        "If omitted and --emit-config exists with model, reuse it; "
        "if omitted and file doesn't exist, use default 'ollama_chat/qwen3-coder:30b'.",
    )

    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show YAML in stdout but DO NOT write file",
    )
    return p.parse_args()
