# Prompt Architect 🏗️

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: MIT](httpshttps://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.to/badge/status-production--ready-successgreen)](#)

**Prompt Architect** is a CLI tool designed to bring the power of Git-style version control, testing, and automated evaluation to the world of LLM prompt engineering. 

Stop guessing if your new prompt is better. **Prove it.** 🧪

## 🎯 The Problem
Prompt engineering is often a chaotic process of trial and error. A minor change in a prompt can lead to unexpected regressions, breaking previously working use cases. Traditional version control (Git) is great for code, but it doesn't understand the semantic nuances of prompt templates or the requirement for "Golden Suite" evaluations.

## ✨ The Solution: Git-Inspired Prompt Engineering
Prompt Architect introduces several key concepts:
- **Prompt Versioning:** Track evolution of templates with `commit` and `checkout` semantics.
- **The "Golden Suite":** Automated regression testing. Run a set of standard inputs against a prompt and ensure the output quality remains consistent.
- **Structural Integrity:** Uses Pydenc to validate prompt inputs and template structure.
- **Multi-Provider Agnostic:** Switch seamlessly between local models (Ollama) and cloud giants (OpenAI, Anthropic) without changing your core logic.

## 🚀 Core Features

### 🧬 Template Management
Create and manage your prompts with a simple CLI.
```bash
# Create a new template
python -m prompt_architect.core.cli prompt create "my_greeting" "Hello, {name}!"

# List all templates
python -m prompt_architect.cli prompt list
```

### 🧪 The Evaluation Engine
Run the "Golden Suite" to catch regressions before they hit production.
```bash
# Run the built-in regression demo
python scripts/demo_regression.py
```

### 🛡️ The Git Layer
Integrated `GitPython` tracking for a robust, versioned prompt store.
```bash
# (Note: Git operations are currently managed internally via GitManager 
# and can be extended via the CLI in future releases.)
```

### 🛡️ Structural Integrity
Uses `Pydantic` to validate prompt inputs and template structure.

### 🔄 Regression Detection
Automatically detect when a change in a template breaks expected outputs.

## 🛠️ Tech Stack
- **Core:** Python 3.12+
- **Data Modeling:** `Pydantic`
- **Testing:** `pytest`
- **CLI:** `Typer`
- **Git Integration:** `GitPython`

## 📋 Prerequisites
* Python 3.12+
* Git

## ⚙️ Installation
```bash
# Clone the repository
git clone https://github.com/zcchong18/prompt-architect.git
cd prompt-architect

# Create and activate a virtual environment
python -m v5env venv
source venv/bin/activate

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
- [x] Evaluation Engine (Exact Match/Regex)
- [ ] Advanced Multi-Provider Support (OpenAI, Anthropic)
- [ ] Multi-agent Orchestration Capabilities
- [ ] Advanced Metrics (Semantic Similarity)

---
*Developed with ❤️ by [Zhi](https://github.com/zc/chong18)*
