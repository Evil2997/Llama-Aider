import pathlib


def read_text_bytes(p: pathlib.Path) -> int:
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
        return len(text.encode("utf-8"))
    except Exception:
        try:
            return p.stat().st_size
        except Exception:
            return 0
