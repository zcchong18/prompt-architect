from enum import Enum
from typing import Any, Dict, List, Optional
import re
from pydantic import BaseModel
from prompt_architect.core.template import PromptTemplate

class MetricType(Enum):
    EXACT_MATCH = "exact_match"
    REGEX_MATCH = "regex_match"

class EvalResult(BaseModel):
    passed: bool
    metrics: Dict[str, Any]
    output: str

class Evaluator:
    """
    Evaluates prompt templates against a set of 'Golden' inputs.
    """

    def evaluate(
        self, 
        template: PromptTemplate, 
        test_cases: List[Dict[str, Any]], 
        metrics: Dict[str, Any]
    ) -> List[EvalResult]:
        """
        Runs the template against test cases and evaluates results.
        
        Args:
            template: The PromptTemplate to evaluate.
            test_cases: A list of dictionaries, where each dict is a set of inputs for the template.
            metrics: A dictionary mapping metric names to their expected values/patterns.
                Example: {"exact_match": "hello world", "regex_match": r"ID: \d+"}
        
        Returns:
            A list of EvalResult objects.
        """
        results = []
        
        for case in test_cases:
            try:
                # 1. Render the prompt with the provided inputs
                rendered_output = template.render(**case)
                
                # 2. Perform evaluations
                eval_metrics = {}
                all_passed = True
                
                # Exact Match Evaluation
                if "exact_match" in metrics:
                    expected = metrics["exact_match"]
                    passed = rendered_output.strip() == expected.strip()
                    eval_metrics["exact_match"] = {"passed": passed, "expected": expected, "actual": rendered_output.strip()}
                    if not passed:
                        all_passed = False
                
                # Regex Match Evaluation
                if "regex_match" in metrics:
                    pattern = metrics["regex_match"]
                    passed = bool(re.search(pattern, rendered_output))
                    eval_metrics["regex_match"] = {"passed": passed, "pattern": pattern}
                    if not passed:
                        all_passed = False

                results.append(EvalResult(
                    passed=all_passed,
                    metrics=eval_metrics,
                    output=rendered_output
                ))
                
            except Exception as e:
                # If rendering fails, we treat it as a failure
                results.append(EvalResult(
                    passed=False,
                    metrics={"error": str(e)},
                    output=""
                ))
                
        return results
