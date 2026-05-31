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
- **Multi-Provider Agnostic:** Switch seamlessly between local models (Ollama, llama.cpp) and cloud APIs (OpenAI, Anthropic, Gemini) without changing your core logic.

## 🚀 Core Features

### 🧬 Template Management
Create and manage your prompts with a simple CLI.
```bash
# Create a new template
python -m prompt_architect.core.cli prompt create "my_greeting" "Hello, {name}!"

# List all templates
python -m prompt_architect.core.cli prompt list
```

### 🧪 The Evaluation Engine
Run the "Golden Suite" to catch regressions before they hit production.
```bash
# Run a quick evaluation with test cases
python -m prompt_architect.core.cli prompt evaluate "my_greeting" --test-cases-json '[{"vars": {"name": "World"}, "expected": "Hello, World!"}]'

# Run the built-in regression demo
python scripts/demo_regression.py
```

### 🛡️ The Git Layer
Integrated `GitPython` tracking for a robust, versioned prompt store.

### 🛡️ Structural Integrity
Uses `Pydantic` to validate prompt inputs and template structure — balanced braces, valid variable names, duplicate detection, and more.

### 🔄 Regression Detection
Automatically detect when a change in a template breaks expected outputs (exact match, regex, semantic similarity).

### 🔌 Provider Ecosystem
Six supported providers — switch with a config change:
- **mock** — deterministic testing (no API needed)
- **ollama** — local LLMs via Ollama
- **llamacpp** — OpenAI-compatible local servers (llama.cpp, vLLM, TGI)
- **openai** — GPT-4o, GPT-4o-mini, etc.
- **anthropic** — Claude Sonnet 4, Opus 4, etc.
- **gemini** — Gemini 2.0 Flash, 2.5 Pro, etc.

### ⚙️ Centralized Configuration
Set API keys and model defaults via environment variables:
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza..."
export OLLAMA_BASE_URL="http://localhost:11434"
```

## 🛠️ Tech Stack
- **Core:** Python 3.12+
- **Data Modeling:** `Pydantic`
- **Testing:** `pytest`
- **CLI:** `Typer` + `rich`
- **Git Integration:** `GitPython`
- **HTTP:** `urllib.request` (no extra deps for cloud providers)

## 📋 Prerequisites
* Python 3.12+
* Git

## ⚙️ Installation
```bash
# Clone the repository
git clone https://github.com/zcchong18/prompt-architect.git
cd prompt-architect

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

## 🚀 Quick Start

### 1. Create your first template
Define a template with a name and a raw prompt string.
```bash
python -m prompt_architect.core.cli prompt create "my_greeting" "Hello, {name}!" --description "A simple greeting template"
```

### 2. List your templates
Verify that your template has been safely stored in the local repository.
```bash
python -m prompt_architect.core.cli prompt list
```

### 3. Run an Evaluation (The "Golden Suite")
Ensure your changes haven't broken your expected outputs by running the built-in regression demo.
```bash
python scripts/demo_regression.py
```

## 🗺️ Roadmap
- [x] Core Engine & Template Management
- [x] Evaluation Engine (Exact Match/Regex/Semantic)
- [x] Schema Validation (Pydantic)
- [x] CLI Polish (rich tables, panels)
- [x] Centralized Configuration (env-based)
- [x] Multi-Provider Support (mock, ollama, openai, anthropic, gemini, llamacpp)
- [x] Semantic Similarity Scoring (real embeddings)
- [x] LLM-as-a-Judge Evaluation
- [x] Prompt Chaining
- [x] Multi-agent Orchestration
- [x] Automated Prompt Optimization
- [ ] Semantic Regression Analysis (real, non-mock)

---
*Developed with ❤️ by [Zhi](https://github.com/zcchong18)*
