# 📋 Refinement Backlog: `prompt-architect`

This backlog tracks all documented issues and planned improvements for the `prompt-architect` documentation, as identified in the `DOCS_AUDIT.md`.

---

## 🚨 High Priority

### [RE-001] Create "Quick Start" / Usage Guide 🚨
* **Issue:** The current README ends after installation. There is no guidance on how to actually use the tool's core features.
* **Standard Violated:** `REFINEMENT_STANDARDS.md` - *Structural Requirements: Usage / Quick Start (Mandatory)*
* **Action Item:** Write a section demonstrating:
    1.  Defining a simple prompt template.
    2.  Running a basic evaluation (The "Golden Suite").
    3.  Committing a change via the `prompt-architect` CLI.
* **Status:** ✅ Completed

### [RE-002] Implement "Feature-to-Example" Mapping 🧪
* **Issue:** The "Solution" section promises powerful features (Versioning, Pydantic validation, etc.) but provides no command-line examples or code snippets.
* **Standard Violated:** `REFINEMENT_STANDARDS.md` - *Content & Examples: The "Copy-Paste" Test*
* **Action Item:** Add code blocks for each core feature listed in the "Core Features" section, showing the command used to trigger that feature.
* **Status:** ⏳ Pending

---

## ⚠️ Medium Priority

### [RE-003] Define System Prerequisites ⚙️
* **Issue:** The installation instructions do not explicitly state that `git` is a required system dependency.
* **Standard Violated:** `REFINEMENT_STANDARDS.md` - *Content & Examples: Pre-requisite Clarity*
* **Action Item:** Add a "Prerequisites" subsection before the Installation section, explicitly listing `git` and `python 3.12+`.
* **Status:** ✅ Completed

### [RE-004] Expand Roadmap Detail 🗺️
* **Issue:** The roadmap is currently a single, vague sentence.
* **SS Violated:** `REFINEMENT_STANDARDS.md` - *Structural Requirements: Logical Hierarchy*
* **Action Item:** Transform the Roadmap into a structured list of upcoming milestones (e.g., "Integration with OpenAI API," "Advanced Regex-based evaluation metrics").
* **Status:** ✅ Completed

---

## ✅ Completed
* [x] `DOCS_AUDIT.md` (Audit complete)
* [x] `REFINEMENT_STANDARDS.md` (Standards defined)
