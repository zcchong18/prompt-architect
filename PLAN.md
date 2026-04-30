# Project Plan: Prompt Architect 🏗️

## 🎯 Goal
A CLI tool to version-control, test, and evaluate LLM prompts using Git-inspired semantics and automated "Golden Prompt" test suites.

## 🚀 Core Features
- **Prompt Versioning:** Save, load, and track changes to prompt templates.
- **Schema Validation:** Use PydMT to ensure prompt inputs match expected types.
- **The "Golden Suite":** A testing framework to run a set of inputs against a prompt and evaluate outputs for consistency and quality.
- **Multi-Provider Support:** Seamlessly switch between local (Ollama) and cloud (OpenAI/Anthropic) backends.
- **Regression Testing:** Detect if a new prompt version "breaks" previously working use cases.

## 🛠️ Tech Stack
- **Language:** Python 3.12+
- **Data Modeling:** `pydantic`
- **Testing:** `pytest`
- **Git Integration:** `GitPython`
- **LLM Interface:** `langchain` or direct API calls via `httpx`

## 📅 Development Phases

### Phase 1: Foundation (Current)
- [ ] Setup project structure and environment.
- [ ] Implement basic Prompt Template class with Pydantic validation.
- [ ] Implement a simple filesystem-based storage mechanism.

### Phase 2: The Git Layer
- [ ] Implement the `commit` and `checkout` logic for prompts.
- [ ] Integrate `GitPython` to track changes in a hidden `.prompts` folder.

### Phase 3: The Evaluation Engine
- [ ] Implement the "Golden Suite" runner using `pytest`.
- [ ] Create a "Score" metric (e.g., string matching, semantic similarity via embeddings, or LLM-as-a-judge).

### Phase 4: CLI & UX
- [ ] Build a robust CLI using `typer` or `click`.
- [ ] Add support for different model backends (Ollama, OpenAI).

### Phase 5: Documentation & Showcase
- [ ] Write a professional `README.md`.
- [ ] Create a showcase of a "Prompt Regression" caught by the tool.

## 📂 Initial Structure
- `prompt_architect/` (Core package)
  - `core/` (Versioning and storage logic)
  template/ (Prompt storage)
  `tests/` (The Golden Suites)
- `pyproject.toml`
- `README.md`
- `PLAN.md`
