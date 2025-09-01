# Project Code Conventions

## Extra

- Use the latest Python features (e.g., f-strings, type hints).
- Type annotations are required.
- Enforce strict linting and formatting
  rules ([ruff](https://docs.astral.sh/ruff/), [mypy](https://mypy.readthedocs.io/en/stable/)).
  Use [pre-commit](https://pre-commit.com/) for this.
- Use [uv](https://docs.astral.sh/uv/) for dependency management and virtual environments.
- Prefer [pydantic v2](https://docs.pydantic.dev/latest/) for classes, data validation, etc.
- Use asynchronous programming where applicable (`httpx` for HTTP, `aiofiles` for file operations).
- Use `pathlib` for all path manipulations.
- Use [typer](https://typer.tiangolo.com/) for CLI commands.
- If needed, use in-function logger (with external import of the library) or something similar.
- Allow use of "grouping" for arguments by "#". Don't use docstring with arguments if annotations are enough.
- Always use our SeverityLevel + SeverityScoreRange system (from severity_level.py and severity_score.py) — wherever
  severity is referenced, specify both level and score, and never create alternative scales.
- "try except" should only be used when strictly necessary.

---

## Function Structure (Modules Only)

> These rules apply **only to modular packages**: `module_1/`, `module_2/`, …

- One file = one **main** function (entry) per module.
- Supporting functions live in their own package (a directory with `__init__.py`) **inside the corresponding stage**.
- A function used only once stays in its **stage package**.
- Anything reused in ≥2 different places is placed in `multiple_uses/` (at the module root, **outside** `stage_1`).
- If a group of helpers is reused across the project, extract a dedicated package with a clear name (e.g., `utils/`,
  `config/`).

## Architecture (Modules Only)

> The staged architecture is enforced **exclusively inside module directories**:
> `main_app/module_1/`, `main_app/module_2/`, …

- Execution is split into stages:
  `FUNC_NAME__stage_1 → FUNC_NAME__stage_2 → …` with a nested folder structure.
- `stage_1` **always** exists and is **single**.
- `stage_2+` may have multiple branches. **Branches at the same level live in the same folder and run sequentially.**
- Repeated code lives **outside** a stage (e.g., `multiple_uses/` or thematic `utils/` at the module root).

## Non-Module Code (Free-Form Area)

> Everything **outside** `main_app/module_*/` is **not considered a module** under these rules and may follow a free,
> logical structure.

- Typical layout: `main_app/<python_package>/...` with descriptive package/file names.
- Allowed: any thematic packages (`core/`, `severity/`, `external_tools/`, `web_interface/`, etc.) **without staged
  hierarchy**.
- For shared utilities/config, use clear names and a flat, maintainable structure.

## Notes

- Module numbering: `module_1/`, `module_2/`, … — each module is independent and follows the rules above.
- Outside modules, it is **forbidden** to imitate staged hierarchy (`__stage_N`).
  Stages belong only inside modules.
- Code reuse rules:
    - within a module → `module_X/multiple_uses/` or local `utils/`;
    - project-wide → move to shared packages outside `module_*` (e.g., `main_app/core/`, `main_app/utils/`).

[### Module Structure Schema

```
module_1/
├── __init__.py
├── scan_host.py                          # main function (entry for module_1)
├── scan_host__stage_1/
│   ├── __init__.py
│   ├── authenticate_host.py
│   ├── detect_technology_stack.py
│   ├── run_ai_tests.py
│   ├── authenticate_host__stage_2/
│   │   ├── __init__.py
│   │   └── authenticate_host.py          # def authenticate_host(...)
│   ├── detect_technology_stack__stage_2/
│   │   ├── __init__.py
│   │   └── detect_technology_stack.py    # def detect_technology_stack(...)
│   └── run_ai_tests__stage_2/
│       ├── __init__.py
│       ├── test_ai_driven_vulnerabilities__stage_3/
│       │   ├── __init__.py
│       │   └── test_ai_driven_vulnerabilities.py   # def test_ai_driven_vulnerabilities(...)
│       └── test_xvwa_direct_vulnerabilities__stage_3/
│           ├── __init__.py
│           └── test_xvwa_direct_vulnerabilities.py # def test_xvwa_direct_vulnerabilities(...)
├── multiple_uses/                         # reused (≥2) helpers
│   ├── __init__.py
│   ├── url_utils.py                       # def normalize_url(...)
│   └── payload_builder.py                 # def build_payload(...)
├── utils/                                 # тематические группы (альтернатива multiple_uses)
│   └── __init__.py
└── config/                                # конфиг-загрузчики, валидаторы и пр.
    └── __init__.py
```
]()
## Constants

- Stored inside `constants` in the appropriate file.
- Module-specific constants live in the module folder.
- Common constants are stored in the constants core.

## Core

- Shared functions and utilities used outside modules or in more than one module.
