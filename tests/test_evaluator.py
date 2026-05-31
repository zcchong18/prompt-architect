import json
from unittest.mock import MagicMock, patch

import pytest
from prompt_architect.core.template import PromptTemplate
from prompt_architect.core.evaluator import Evaluator
from prompt_architect.embeddings.mock import MockEmbeddingProvider
from prompt_architect.intelligence.similarity import SimilarityEngine


class TestEvaluatorBasics:
    def test_exact_match(self):
        template = PromptTemplate(
            name="Greeting",
            template_string="Hello, {name}!",
        )

        evaluator = Evaluator()
        test_cases = [{"name": "Alice"}, {"name": "Bob"}]
        metrics = {"exact_match": "Hello, Alice!"}

        results = evaluator.evaluate(template, test_cases, metrics)

        assert len(results) == 2
        assert results[0].passed is True
        assert results[1].passed is False
        assert results[1].metrics["exact_match"]["actual"] == "Hello, Bob!"

    def test_regex_match(self):
        template = PromptTemplate(
            name="ID Generator",
            template_string="User ID: {user_id}",
        )

        evaluator = Evaluator()
        test_cases = [{"user_id": "123"}, {"user_id": "abc"}]
        metrics = {"regex_match": r"ID: \d+"}

        results = evaluator.evaluate(template, test_cases, metrics)

        assert len(results) == 2
        assert results[0].passed is True
        assert results[1].passed is False

    def test_error_handling(self):
        template = PromptTemplate(
            name="Broken",
            template_string="Missing: {missing_key}",
        )

        evaluator = Evaluator()
        test_cases = [{"existing_key": "val"}]
        metrics = {}

        results = evaluator.evaluate(template, test_cases, metrics)

        assert len(results) == 1
        assert results[0].passed is False
        assert "error" in results[0].metrics

    def test_injectable_similarity_engine(self):
        class IdentityEngine:
            def calculate_similarity(self, a, b):
                return 1.0

        template = PromptTemplate(
            name="Test",
            template_string="Hello {name}",
        )

        evaluator = Evaluator(similarity_engine=IdentityEngine())
        test_cases = [
            {"name": "World", "golden_output": "Hello World"},
        ]
        metrics = {"semantic_similarity": 0.5}

        results = evaluator.evaluate(template, test_cases, metrics)

        assert results[0].passed is True
        assert results[0].metrics["semantic_similarity"]["score"] == 1.0


class TestEvaluatorLLMJudge:
    def test_llm_judge_passes_with_mock(self):
        template = PromptTemplate(
            name="Test",
            template_string="Hello {name}",
        )

        evaluator = Evaluator(judge_provider_name="mock")
        test_cases = [{"name": "World"}]
        metrics = {"llm_judge": "Should be a greeting"}

        results = evaluator.evaluate(template, test_cases, metrics)

        assert len(results) == 1
        assert "llm_judge" in results[0].metrics
        assert "passed" in results[0].metrics["llm_judge"]

    def test_parse_judge_response_json(self):
        evaluator = Evaluator()
        raw = json.dumps({"passed": True, "score": 8, "reasoning": "Good"})
        result = evaluator._parse_judge_response(raw)
        assert result["passed"] is True
        assert result["score"] == 8
        assert result["reasoning"] == "Good"

    def test_parse_judge_response_with_code_fence(self):
        evaluator = Evaluator()
        raw = '```json\n{"passed": false, "score": 3, "reasoning": "Poor"}\n```'
        result = evaluator._parse_judge_response(raw)
        assert result["passed"] is False
        assert result["score"] == 3

    def test_parse_judge_response_malformed(self):
        evaluator = Evaluator()
        raw = "not json at all"
        result = evaluator._parse_judge_response(raw)
        assert result["passed"] is False
        assert "Failed to parse" in result["reasoning"]

    @patch("prompt_architect.providers.factory.ProviderFactory.get_provider")
    def test_llm_judge_calls_provider(self, mock_get_provider):
        mock_provider = MagicMock()
        mock_provider.execute.return_value = json.dumps(
            {"passed": True, "score": 10, "reasoning": "Perfect"}
        )
        mock_get_provider.return_value = mock_provider

        template = PromptTemplate(
            name="Test",
            template_string="Hello {name}",
        )

        evaluator = Evaluator(
            judge_provider_name="openai", judge_config={"api_key": "sk-test"}
        )
        test_cases = [{"name": "World"}]
        metrics = {"llm_judge": "Should be a greeting"}

        results = evaluator.evaluate(template, test_cases, metrics)

        assert results[0].passed is True
        mock_get_provider.assert_called_once_with(
            "openai", config={"api_key": "sk-test"}
        )
        assert mock_provider.execute.called
