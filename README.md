# Prompt Architect 🏗️

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/status-production--ready-successgreen)](#)

**Prompt Architect** is a CLI tool designed to bring the power of Git-style version control, testing, and automated evaluation to the world of LLM prompt engineering. 

Stop guessing if your new prompt is better. **Prove it.** 🧪

## 🎯 The Problem
Prompt engineering is often a chaotic process of trial and error. A minor change in a prompt can lead to unexpected regressions, breaking previously working use cases. Traditional version control (Git) is great for code, but it doesn't understand the semantic nuances of prompt templates or the requirement for "Golden Suite" evaluations.

## ✨ The Solution: Git-Inspired Prompt Engineering
Prompt Architect introduces several key concepts:
- **Prompt Versioning:** Track evolution of templates with `commit` and `checkout` semantics.
- **The "Golden Suite":** Automated regression testing. Run a set of standard inputs against a prompt and ensure the output quality remains consistent.
- **Structural Integrity:** Uses Pydantic to validate prompt inputs and template structure.
- **Multi-Provider Agnostic:** Switch seamlessly between local models (Ollama) and cloud giants (OpenAI, Anthropic) without changing your core logic.

## 🚀 Core Features
- [x] **Template Management:** Create, save, and load versioned prompt templates.
- [x] **The Evaluation Engine:** A `pytest`-powered runner to execute the "Golden Suite" and calculate performance metrics (exact match, regex, etc.).
- [x] **The Git Layer:** Integrated `GitPython` tracking for a robust, versioned prompt store.
- [x] **CLI Interface:** A user-friendly, robust interface powered by `Typer`.
- [x] **Regression Detection:** Automatically detect when a change in a template breaks expected outputs.

## 🛠️ Tech Stack
- **Core:** Python 3.12+
- **Data Modeling:** `Pydantic`
- **Testing:** `pytest`
- **CLI:** `Typer`
- **Git Integration:** `GitPython`

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/zcchong18/prompt-architect.git
cd prompt-architect

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

## 🗺️ Roadmap
We have completed the core engine and are currently focusing on expanding the evaluation metrics and advanced multi-agent orchestration capabilities.

---
*Developed with ❤️ by [Zhi](https://github.com/zcchong18)*
