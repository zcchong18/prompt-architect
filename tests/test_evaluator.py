import pytest
from prompt_architect.core.template import PromptTemplate
from prompt_architect.core.evaluator import Evaluator

def test_evaluator_exact_match():
    """Test that exact match metric works correctly."""
    template = PromptTemplate(
        name="Greeting",
        template_string="Hello, {name}!",
    )
    
    evaluator = Evaluator()
    test_cases = [{"name": "Alice"}, {"name": "Bob"}]
    metrics = {"exact_match": "Hello, Alice!"}
    
    results = evaluator.evaluate(template, test_cases, metrics)
    
    assert len(results) == 2
    # First case should pass
    assert results[0].passed is True
    # Second case should fail because it doesn't match "Hello, Alice!"
    assert results[1].passed is False
    assert results[1].metrics["exact_match"]["actual"] == "Hello, Bob!"

def test_evaluator_regex_match():
    """Test that regex match metric works correctly."""
    template = PromptTemplate(
        name="ID Generator",
        template_string="User ID: {user_id}",
    )
    
    evaluator = Evaluator()
    test_cases = [{"user_id": "123"}, {"user_id": "abc"}]
    # Expecting a digit pattern
    metrics = {"regex_match": r"ID: \d+"}
    
    results = evaluator.evaluate(template, test_cases, metrics)
    
    assert len(results) == 2
    assert results[0].passed is True
    assert results[1].passed is False

def test_evaluator_error_handling():
    """Test that evaluator handles rendering errors gracefully."""
    template = PromptTemplate(
        name="Broken",
        template_string="Missing: {missing_key}",
    )
    
    evaluator = Evaluator()
    # Providing incomplete inputs to trigger a KeyError during rendering
    test_cases = [{"existing_key": "val"}]
    metrics = {}
    
    results = evaluator.evaluate(template, test_cases, metrics)
    
    assert len(results) == 1
    assert results[0].passed is False
    assert "error" in results[0].metrics
