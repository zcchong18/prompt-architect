import pytest
from prompt_architect.core.template import PromptTemplate
from prompt_architect.core.evaluator import Evaluator
from prompt_architect.core.storage import Storage

@pytest.fixture
def test_storage(tmp_path):
    """Fixture to provide a clean storage directory for each test."""
    storage_dir = tmp_path / "templates"
    storage_dir.mkdir()
    return Storage(storage_dir=str(storage_dir))

def test_prompt_regression_detection(test_storage):
    """
    Integration test: Ensures that the Evaluator correctly detects 
    a regression between a 'gold' template and a 'broken' template.
    """
    evaluator = Evaluator()
    
    # 1. Define the Gold Standard
    gold_str = "Hello {name}, welcome to the world of {topic}!"
    gold_template = PromptTemplate(name="gold_standard", template_string=gold_str)
    test_storage.save(gold_template)
    
    # 2. Define the Broken Version (Regression: missing space after comma)
    broken_str = "Hello {name},welcome to the world of {topic}!"
    broken_template = PromptTemplate(name="broken_version", template_string=broken_str)
    test_storage.save(broken_template)
    
    # 3. Define the Test Case
    test_case = {"name": "Alice", "topic": "AI"}
    expected_output = "Hello Alice, welcome to the world of AI!"
    metrics = {"exact_match": expected_output}
    
    # 4. Run Evaluation
    gold_results = evaluator.evaluate(gold_template, [test_case], metrics)
    broken_results = evaluator.evaluate(broken_template, [test_case], metrics)
    
    # 5. Assertions
    assert len(gold_results) == 1
    assert gold_results[0].passed is True, f"Gold template failed! Output: {gold_results[0].output}"
    
    assert len(broken_results) == 1
    assert broken_results[0].passed is False, "Broken template was NOT detected as a failure!"
    assert broken_results[0].output == "Hello Alice,welcome to the world of AI!"
