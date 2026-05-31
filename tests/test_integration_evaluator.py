import pytest
from prompt_architect.core.template import PromptTemplate
from prompt_architect.core.evaluator import Evaluator


def test_semantic_regression():
    """
    Tests that the Evaluator can compute semantic similarity metrics.
    Note: The mock embedding provider returns all-1.0 vectors (cos sim = 1.0),
    so all cases pass. Real regression detection requires a real provider.
    """
    template = PromptTemplate(
        name="test_template",
        template_string="Hello, {name}! Welcome to {location}.",
        variables=["name", "location"],
    )

    evaluator = Evaluator()

    test_cases = [
        {
            "name": "Alice",
            "location": "Wonderland",
            "golden_output": "Hello, Alice! Welcome to Wonderland.",
        },
        {
            "name": "Alice",
            "location": "Wonderland_v2",
            "golden_output": "Hello, Alice! Welcome to Wonderland.",
        },
        {
            "name": "!!!",
            "location": "???",
            "golden_output": "Hello, Alice! Welcome to Wonderland.",
        },
    ]

    metrics = {"semantic_similarity": 0.9}

    results = evaluator.evaluate(template, test_cases, metrics)

    assert len(results) == 3

    # All cases pass because mock embedder yields all-1.0 → cos sim = 1.0
    for i, res in enumerate(results):
        assert res.passed is True, f"Case {i} should pass"
        assert res.metrics["semantic_similarity"]["score"] == pytest.approx(1.0)


if __name__ == "__main__":
    test_semantic_regression()
    print("Regression test passed!")
