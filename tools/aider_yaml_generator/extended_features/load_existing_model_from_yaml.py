import pathlib
import re


def load_existing_model_from_yaml(path: pathlib.Path) -> str | None:
    """Минимальный парсер model: "...", без зависимости от PyYAML."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    # Ищем строку вида: model: "..."   или model: '...'   или model: name
    m = re.search(r"^\s*model\s*:\s*(.+)$", text, flags=re.MULTILINE)
    if not m:
        return None
    raw = m.group(1).strip()
    raw = raw.split("#", 1)[0].strip()

    if (raw.startswith('"') and '"' in raw[1:]) or (raw.startswith("'") and "'" in raw[1:]):
        q = raw[0]
        try:
            end = raw.index(q, 1)
            return raw[1:end]
        except ValueError:
            return raw.strip(q)
    return raw.strip().rstrip(",")
