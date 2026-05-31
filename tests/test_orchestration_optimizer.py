import pytest
from prompt_architect.models import PromptTemplate
from prompt_architect.orchestration.optimizer import (
    PromptOptimizer,
    OptimizationResult,
)


class TestOptimizationResult:
    def test_default_history(self):
        result = OptimizationResult(best_template="hello", best_score=1.0)
        assert result.best_template == "hello"
        assert result.best_score == 1.0
        assert result.history == []


class TestPromptOptimizer:
    def test_score_all_pass(self):
        template = PromptTemplate(name="t", template_string="Hello {name}")
        optimizer = PromptOptimizer(max_iterations=1)
        test_cases = [{"name": "World"}]
        metrics = {"exact_match": "Hello World"}

        score = optimizer._score(template, test_cases, metrics)
        assert score == 1.0

    def test_score_none_pass(self):
        template = PromptTemplate(name="t", template_string="Hello {name}")
        optimizer = PromptOptimizer(max_iterations=1)
        test_cases = [{"name": "World"}]
        metrics = {"exact_match": "Wrong"}

        score = optimizer._score(template, test_cases, metrics)
        assert score == 0.0

    def test_score_mixed(self):
        template = PromptTemplate(name="t", template_string="Hello {name}")
        optimizer = PromptOptimizer(max_iterations=1)
        test_cases = [
            {"name": "World"},
            {"name": "Alice"},
        ]
        metrics = {"exact_match": "Hello World"}

        score = optimizer._score(template, test_cases, metrics)
        assert score == 0.5

    def test_optimize_returns_result(self):
        template = PromptTemplate(name="t", template_string="Hello {name}")
        optimizer = PromptOptimizer(max_iterations=1)
        test_cases = [{"name": "World"}]
        metrics = {"exact_match": "Hello World"}

        result = optimizer.optimize(template, test_cases, metrics)
        assert isinstance(result, OptimizationResult)
        assert result.best_template == "Hello {name}"
        assert result.best_score == 1.0
        assert len(result.history) >= 1

    def test_history_tracks_iterations(self):
        template = PromptTemplate(name="t", template_string="Hi {name}")
        optimizer = PromptOptimizer(max_iterations=3)
        test_cases = [{"name": "World"}]
        metrics = {"exact_match": "Hi World"}

        result = optimizer.optimize(template, test_cases, metrics)
        assert result.history[0]["iteration"] == 0
        assert result.history[0]["score"] == 1.0
        assert result.history[0]["template"] == "Hi {name}"
