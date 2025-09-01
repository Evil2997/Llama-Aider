# ========= ПЕРЕМЕННЫЕ =========
set shell := ["bash", "-euo", "pipefail", "-c"]

PY               := "3.12"
PROJECT_DIR      := env_var("HOME") + "/PycharmProjects/Llama_project"
VENV             := PROJECT_DIR + "/.venv"
MODELS_DIR       := PROJECT_DIR + "/models"

LLAMA_CUDA_INDEX := "https://abetlen.github.io/llama-cpp-python/whl/cu124"
export HF_HUB_ENABLE_HF_TRANSFER := "1"

MISTRAL_FILE     := "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MISTRAL_REPO     := "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"

DEEPSEEK_FILE    := "DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf"
DEEPSEEK_REPO    := "bartowski/DeepSeek-Coder-V2-Lite-Instruct-GGUF"
DEEPSEEK_HFNAME  := "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"

PHI_FILE         := "Phi-3.5-mini-instruct-Q4_K_M.gguf"
PHI_REPO         := "bartowski/Phi-3.5-mini-instruct-GGUF"

# ========= ЗАВИСИМОСТИ =========
deps:
    uv sync

setup-all: deps dl-mistral dl-deepseek dl-phi
	@echo "Setup complete."

# ========= ЗАГРУЗКА МОДЕЛЕЙ =========
dl-mistral:
	uv run --python "{{PY}}" \
	  huggingface-cli download "{{MISTRAL_REPO}}" "{{MISTRAL_FILE}}" \
	  --local-dir "{{MODELS_DIR}}" --local-dir-use-symlinks False
	ls -lh "{{MODELS_DIR}}/{{MISTRAL_FILE}}"

dl-deepseek:
	uv run --python "{{PY}}" \
	  huggingface-cli download "{{DEEPSEEK_REPO}}" "{{DEEPSEEK_FILE}}" \
	  --local-dir "{{MODELS_DIR}}" --local-dir-use-symlinks False
	ls -lh "{{MODELS_DIR}}/{{DEEPSEEK_FILE}}"

dl-phi:
	uv run --python "{{PY}}" \
	  huggingface-cli download "{{PHI_REPO}}" "{{PHI_FILE}}" \
	  --local-dir "{{MODELS_DIR}}" --local-dir-use-symlinks False
	ls -lh "{{MODELS_DIR}}/{{PHI_FILE}}"

# ========= ЗАПУСК СЕРВЕРА =========
# Переопределяй через env: PORT, ALIAS, N_CTX, N_BATCH, N_GPU_LAYERS

run-mistral:
	@if [[ ! -f "{{MODELS_DIR}}/{{MISTRAL_FILE}}" ]]; then just dl-mistral; fi
	uv run --python "{{PY}}" python -m llama_cpp.server \
	  --model "{{MODELS_DIR}}/{{MISTRAL_FILE}}" \
	  --model_alias "${ALIAS:-gpt-4o-mini}" \
	  --chat_format "mistral-instruct" \
	  --n_ctx "${N_CTX:-2048}" --n_batch "${N_BATCH:-512}" --n_gpu_layers "${N_GPU_LAYERS:--1}" \
	  --host "0.0.0.0" --port "${PORT:-8000}"

run-phi:
	@if [[ ! -f "{{MODELS_DIR}}/{{PHI_FILE}}" ]]; then just dl-phi; fi
	uv run --python "{{PY}}" python -m llama_cpp.server \
	  --model "{{MODELS_DIR}}/{{PHI_FILE}}" \
	  --model_alias "${ALIAS:-phi-3.5-mini}" \
	  --chat_format "phi-3" \
	  --n_ctx "${N_CTX:-2048}" --n_batch "${N_BATCH:-512}" --n_gpu_layers "${N_GPU_LAYERS:--1}" \
	  --host "0.0.0.0" --port "${PORT:-8001}"

run-deepseek:
	@if [[ ! -f "{{MODELS_DIR}}/{{DEEPSEEK_FILE}}" ]]; then just dl-deepseek; fi
	uv run --python "{{PY}}" python -m llama_cpp.server \
	  --model "{{MODELS_DIR}}/{{DEEPSEEK_FILE}}" \
	  --model_alias "${ALIAS:-deepseek-coder-v2-lite}" \
	  --chat_format "hf-autotokenizer" \
	  --hf_pretrained_model_name_or_path "{{DEEPSEEK_HFNAME}}" \
	  --n_ctx "${N_CTX:-4096}" --n_batch "${N_BATCH:-512}" --n_gpu_layers "${N_GPU_LAYERS:--1}" \
	  --host "0.0.0.0" --port "${PORT:-8002}"

# ========= УТИЛИТЫ =========
ls-models:
	@ls -lh "{{MODELS_DIR}}"/*.gguf 2>/dev/null || echo "No GGUF files yet."
