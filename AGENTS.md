# AGENTS.md — Prompt Architect

Single-package Python CLI tool (`prompt_architect`) for version-controlling and regression-testing LLM prompts. Git-inspired workflow, Pydantic validation, provider-agnostic execution.

## Python env

- Python 3.12+. Always use `.venv/bin/python` (system `python3` also works; `python` does not exist).
- Activate: `source .venv/bin/activate` (preferred) or prefix every command with `.venv/bin/`.

## Commands

| Action | Command |
|---|---|
| All tests | `.venv/bin/python -m pytest tests/ -q` |
| Single test file | `.venv/bin/python -m pytest tests/test_template.py -q` |
| Single test | `.venv/bin/python -m pytest tests/test_template.py::test_prompt_template_render_success -q` |
| CLI entrypoint | `.venv/bin/python -m prompt_architect.core.cli prompt create/list/evaluate` |
| Regression demo | `.venv/bin/python scripts/demo_regression.py` |
| Create template | `python -m prompt_architect.core.cli prompt create "name" "Hello {var}!"` |
| Evaluate | `python -m prompt_architect.core.cli prompt evaluate "name" --test-cases-json '...'` |

## Architecture

```
src/prompt_architect/
  core/
    cli.py          — Typer CLI (entrypoint)
    template.py     — re-exports models.PromptTemplate
    evaluator.py    — exact-match / regex / semantic-similarity evaluation
    storage.py      — JSON file persistence in templates/
    git_manager.py  — GitPython wrapper for prompt versioning
  models.py         — PromptTemplate (Pydantic), render() uses {var}
  registry.py       — TemplateRegistry: in-memory cache + filesystem loader
  providers/
    base.py         — BaseLLMProvider ABC
    config.py       — Settings: env-based API keys, model defaults
    mock.py         — MockProvider: {{var}} syntax replacement
    factory.py      — ProviderFactory (only "mock" supported)
  embeddings/
    base.py         — BaseEmbeddingProvider ABC
    mock.py         — MockEmbeddingProvider: char-frequency vectors
  intelligence/
    similarity.py   — SimilarityEngine: cosine similarity
templates/          — default JSON storage dir (git-tracked)
tests/              — 58 tests, plain pytest (no test infra beyond pytest)
```

## Key quirks & gotchas

- **Two variable syntaxes**: `PromptTemplate.render()` uses `{var}` (Python `str.format`); `MockProvider.execute()` uses `{{var}}` (string replace). Tests exercise both.
- **Mock embedder returns all-1.0 vectors** — semantic similarity tests all score 1.0. Real regression detection needs a non-mock provider.
- **cli.py** computes `PROJECT_ROOT` as `../../` from its own dir — run commands from repo root or path resolution breaks.
- **No formatter/linter** configured. No pre-commit hooks. No CI.
- **Only `mock` provider** implemented. Real LLM providers (OpenAI, Anthropic, Ollama) are stubs.
- **Provider config via env vars**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OLLAMA_BASE_URL`, etc. See `providers/config.py`.

## Project conventions

- Update `PLAN.md` before significant changes. Update `CHANGELOG.md` (user-facing) and `DEV_LOG.md` (technical) after changes.
- Agent skill definitions live in `skills/*/SKILL.md`. Persona definitions in `agents/*.md`.
- Style follows existing test patterns: pytest functions, no test classes, descriptive function names with `snake_case`.
