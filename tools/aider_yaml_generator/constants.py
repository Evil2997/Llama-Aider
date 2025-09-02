from __future__ import annotations

# === Общие константы проекта ===

# Модель по умолчанию, ранее была захардкожена в collect_rw_ro.py
DEFAULT_MODEL: str = "ollama_chat/qwen3-coder:30b"

# Базовые теги для поиска пометок в комментариях
DEFAULT_TODO_TAGS: tuple[str, str] = ("TODO", "FIXME")

# Базовые имена исключений для поиска в raise
DEFAULT_RAISE_NAMES: tuple[str, ...] = ("NotImplementedError",)

KIB = 1024
MIB = 1024 * KIB
GIB = 1024 * MIB
