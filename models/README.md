# Каталог `models/`

Здесь хранятся локальные LLM-модели в формате **GGUF** (например: `mistral-7b-instruct-v0.2.Q4_K_M.gguf`).

## Правила и `.gitignore`
- В репозиторий **не коммитим** сами `.gguf` (большие файлы).
- В этой папке разрешены только два файла: `.gitignore` и `README.md`.


```bash

# Скачать конкретную модель
just dl-mistral
just dl-deepseek
just dl-phi

# Посмотреть, что скачано
just ls
````

## Альтернатива (без `just`)

```bash

# Mistral 7B Instruct v0.2 (Q4_K_M)
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
  mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  --local-dir . --local-dir-use-symlinks False

# DeepSeek Coder V2 Lite Instruct (Q4_K_M)
huggingface-cli download bartowski/DeepSeek-Coder-V2-Lite-Instruct-GGUF \
  DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf \
  --local-dir . --local-dir-use-symlinks False

# Phi-3.5 mini instruct (Q4_K_M)
huggingface-cli download bartowski/Phi-3.5-mini-instruct-GGUF \
  Phi-3.5-mini-instruct-Q4_K_M.gguf \
  --local-dir . --local-dir-use-symlinks False
```

## Быстрый запуск локального сервера (опционально)

```bash

python3 -m llama_cpp.server \
  --model ./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  --model_alias gpt-4o-mini \
  --chat_format mistral-instruct \
  --n_ctx 4096 --n_batch 512 --n_gpu_layers -1 \
  --host 0.0.0.0 --port 8000
```
> Подсказка: для быстрых загрузок можно включить `HF_HUB_ENABLE_HF_TRANSFER=1`.

