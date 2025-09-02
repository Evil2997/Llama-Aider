# AIDER RULES (Global)

---

The output should be:
```python
# file/path/file_name.py
<python file code write here!>
```

---

These rules apply to **all tasks** in the `tasks/` directory.
Every task folder contains:

- **`.aider.config.yaml`** — configuration file listing which files are RW/RO and the run command.
- **`task.md`** — description of the specific coding task (objective, requirements, scope).
- **`CONVENTIONS.md`** (at project root) — defines project-wide coding style and architecture rules.
- **`aider_TODO.md`** (per task) — file where Aider must record notes about changes blocked by RO files.

## File modes

- **RW (read–write):** You may read and modify these files.
- **RO (read-only):** You may read these files, but you MUST NOT modify them.
  The configuration enforces this — never try to bypass it.

## If a required change is in an RO file

- Do **not** modify the RO file directly.
- Instead, add an entry to the task’s `aider_TODO.md`.
- Each entry must include enough context so that a human developer can later apply the change.

**==============================================================================================**

# aider_TODO entry format

---

## TODO: <short title>

- File: \<path/to/file.py>
- Lines: \<line number(s) or "unknown">
- Problem: Why this change is required and why it cannot be applied (RO restriction).
- Intent: What should be changed (describe in words).
- Notes:
    ```python
    # (Optional) quoted snippet that illustrates the intended modification
    ```

**Context:** Why this change matters for completing the task.

---

## Usage of files

- **`.aider.config.yaml`**: Defines which files are RW/RO and enforces restrictions.
- **`task.md`**: Defines *what* must be done for this task.
- **`CONVENTIONS.md`**: Defines *how* code must be written (style, architecture).
- **`aider_TODO.md`**: The only place where Aider may record feedback about RO-blocked edits.

---

## Rules of work

1. Follow `task.md` for the task’s objective and scope.
2. Follow `CONVENTIONS.md` for coding style and architecture.
3. Only modify files listed as **RW** in `.aider.config.yaml`.
4. Never edit RO files — log required changes in `aider_TODO.md`.
5. Keep changes minimal, focused, and consistent with the existing project.
6. Always include type hints, docstrings, and meaningful descriptions in new code.
7. If new files are requested, create them exactly at the specified path.

---

## Deliverables

- Completed implementation in **RW** files.
- Detailed notes in **aider_TODO.md** for any RO-blocked changes.
- Code that respects project conventions and integrates cleanly.
