#!/usr/bin/env bash
set -o errexit \
    -o nounset \
    -o pipefail

# ====================================[НАСТРОЙКИ ДЛЯ БЫСТРОГО РЕДАКТИРОВАНИЯ]===========================================
TASK_NAME="added_pydantic_model"      # название текущей таски (папка внутри aider-template/tasks)

SEEDS=(
  "main_app/module_1/run__module_1.py"
)
VARS=(
  "authenticated_cookies"
  "authenticated_sessions"
)
TYPES=(
  "T_AUTHENTICATED_COOKIES"
  "T_AUTHENTICATED_SESSIONS"
)

# DRY RUN:
# true  — не записывать файл на диск, только вывести YAML в stdout
# false — записать YAML в EMIT_CONFIG
DRY_RUN=false
# ======================================================================================================================

# Корень проекта и namespace
ROOT="/home/dima/PycharmProjects/auto-bot"
NS="main_app"

# Относительная папка таски (относительно ROOT)
TASK_REL_DIR="aider-template/tasks/${TASK_NAME}"

# Путь для записи итогового aider-конфига (полный путь)
EMIT_CONFIG="$ROOT/${TASK_REL_DIR}/aider.conf.yaml"

# Модель для YAML (опционально):
# - Пусто => если файл EMIT_CONFIG уже есть, возьмём model из него; если нет — дефолт "ollama_chat/qwen3-coder:30b"
# - Укажи строку, чтобы перезаписать (пример: "ollama_chat/qwen3-coder:7b")
MODEL_FOR_YAML="ollama_chat/qwen3-coder:30b"

# Пути писать в YAML: "root" (относительно $ROOT) или "abs" (абсолютные)
USE_RELATIVE="root"

# Лимиты и диагностика
MAX_DEPTH=2
MAX_TOTAL_MIB=8          # 1 MiB = 1,048,576 байт
CHARS_PER_TOKEN=3.0
SHOW_SIZES=true          # печатать сводку объёмов/токенов
ADD_GITIGNORE_FILES=true # если true — добавим ключ add-gitignore-files: true

# Базовые сиды, переменные и тип-алиасы (массивы можно править)

# === ФАЙЛЫ ТЕКУЩЕЙ ТАСКИ (подставляются из TASK_NAME) ===
TASK="${TASK_REL_DIR}/task.md"
TODO="${TASK_REL_DIR}/AIDER_TODO.md"

# Всегда включаемые файлы (RO поверх лимита)
ALWAYS_INCLUDE=(
  "${TASK_REL_DIR}/aider.conf.yaml"
)

# Шорткаты (тоже попадают в RO поверх лимита)
CONVENTIONS="CONVENTIONS.md"
RULES="aider-template/tasks/AIDER_RULES.md"

# ======================================================================================================================
# ---------------------------------------------- НИЖЕ ЛУЧШЕ НЕ ТРОГАТЬ -------------------------------------------------
# ======================================================================================================================

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/collect_rw_ro.py"

ARGS=(
  --root "$ROOT"
  --namespace "$NS"
  --max-depth "$MAX_DEPTH"
  --max-total-mib "$MAX_TOTAL_MIB"
  --chars-per-token "$CHARS_PER_TOKEN"
  --use-relative "$USE_RELATIVE"
  --emit-config "$EMIT_CONFIG"
)

# Массивы в один флаг
(( ${#SEEDS[@]} )) && ARGS+=( --seed "${SEEDS[@]}" )
(( ${#VARS[@]}  )) && ARGS+=( --vars "${VARS[@]}" )
(( ${#TYPES[@]} )) && ARGS+=( --types "${TYPES[@]}" )

# always-include
(( ${#ALWAYS_INCLUDE[@]} )) && ARGS+=( --always-include "${ALWAYS_INCLUDE[@]}" )

# shortcuts
[[ -n "$CONVENTIONS" ]] && ARGS+=( --conventions "$CONVENTIONS" )
[[ -n "$RULES"       ]] && ARGS+=( --rules "$RULES" )
[[ -n "$TASK"        ]] && ARGS+=( --task "$TASK" )
[[ -n "$TODO"        ]] && ARGS+=( --todo "$TODO" )

# флаги
[[ "$SHOW_SIZES" == "true" ]] && ARGS+=( --show-sizes )
[[ "$ADD_GITIGNORE_FILES" == "true" ]] && ARGS+=( --add-gitignore-files )

# модель (опционально)
[[ -n "$MODEL_FOR_YAML" ]] && ARGS+=( --model "$MODEL_FOR_YAML" )

# dry-run
[[ "$DRY_RUN" == "true" ]] && ARGS+=( --dry-run )

echo "[gen_aider_config] TASK_NAME=${TASK_NAME}"
echo "[gen_aider_config] running:"
echo "python3 \"$PY\""
printf ' %q' "${ARGS[@]}"; echo
echo

python3 "$PY" "${ARGS[@]}"
