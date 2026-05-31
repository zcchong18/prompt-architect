import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.factory import ProviderFactory
from prompt_architect.core.evaluator import Evaluator


_OPTIMIZER_PROMPT = """You are a prompt engineering expert.
Given the following prompt template and its evaluation results,
generate an improved version of the template.

== Current Template ==
{current_template}

== Evaluation Results ==
{evaluation_summary}

== Instructions ==
- Fix the specific issues identified in the evaluation.
- Keep the same {{variable}} placeholders.
- Return ONLY the new template text, nothing else.

Improved template:"""


@dataclass
class OptimizationResult:
    best_template: str
    best_score: float
    history: List[Dict[str, Any]] = field(default_factory=list)


class PromptOptimizer:
    def __init__(
        self,
        factory: Optional[ProviderFactory] = None,
        evaluator: Optional[Evaluator] = None,
        optimizer_provider: str = "mock",
        optimizer_config: Optional[Dict[str, Any]] = None,
        max_iterations: int = 5,
    ):
        self._factory = factory or ProviderFactory()
        self._evaluator = evaluator or Evaluator()
        self._optimizer_provider = optimizer_provider
        self._optimizer_config = optimizer_config or {}
        self.max_iterations = max_iterations

    def optimize(
        self,
        template: PromptTemplate,
        test_cases: List[Dict[str, Any]],
        metrics: Dict[str, Any],
    ) -> OptimizationResult:
        current_template = template.template_string
        best_template = current_template
        best_score = self._score(template, test_cases, metrics)
        history = [
            {
                "iteration": 0,
                "template": current_template,
                "score": best_score,
            }
        ]

        for iteration in range(1, self.max_iterations + 1):
            new_template_str = self._generate_variant(current_template, history)

            if (
                not new_template_str
                or new_template_str.strip() == current_template.strip()
            ):
                continue

            new_template = PromptTemplate(
                name=f"{template.name}_iter_{iteration}",
                template_string=new_template_str,
                variables=template.variables,
            )

            score = self._score(new_template, test_cases, metrics)
            history.append(
                {
                    "iteration": iteration,
                    "template": new_template_str,
                    "score": score,
                }
            )

            if score > best_score:
                best_template = new_template_str
                best_score = score
                current_template = new_template_str

        return OptimizationResult(
            best_template=best_template,
            best_score=best_score,
            history=history,
        )

    def _score(
        self,
        template: PromptTemplate,
        test_cases: List[Dict[str, Any]],
        metrics: Dict[str, Any],
    ) -> float:
        results = self._evaluator.evaluate(template, test_cases, metrics)
        if not results:
            return 0.0
        passed = sum(1 for r in results if r.passed)
        return passed / len(results)

    def _generate_variant(
        self,
        current_template: str,
        history: List[Dict[str, Any]],
    ) -> str:
        latest = history[-1] if history else {}
        summary = json.dumps(
            {
                "current_score": latest.get("score", 0),
                "total_iterations": len(history),
            }
        )

        prompt_text = _OPTIMIZER_PROMPT.format(
            current_template=current_template,
            evaluation_summary=summary,
        )

        judge_template = PromptTemplate(
            name="__optimizer__",
            template_string=prompt_text,
        )

        provider = self._factory.get_provider(
            self._optimizer_provider,
            config=self._optimizer_config,
        )
        return provider.execute(judge_template, {}).strip()
