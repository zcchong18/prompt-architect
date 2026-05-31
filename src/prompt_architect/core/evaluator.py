import json
import re
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from prompt_architect.core.template import PromptTemplate
from prompt_architect.intelligence.similarity import SimilarityEngine
from prompt_architect.providers.factory import ProviderFactory


_JUDGE_PROMPT_TEMPLATE = """You are an expert evaluator of LLM outputs.
Evaluate the following output against the criteria below.

== Criteria ==
{rubric}

== Input ==
{input}

== Output to Evaluate ==
{output}

Respond with a JSON object (no markdown, no code fences):
{{"passed": true_or_false, "score": 0_to_10, "reasoning": "brief explanation"}}"""


class MetricType(Enum):
    EXACT_MATCH = "exact_match"
    REGEX_MATCH = "regex_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    LLM_JUDGE = "llm_judge"


class EvalResult(BaseModel):
    passed: bool
    metrics: Dict[str, Any]
    output: str


class Evaluator:
    def __init__(
        self,
        similarity_threshold: Optional[float] = None,
        similarity_engine: Optional[SimilarityEngine] = None,
        judge_provider_name: Optional[str] = None,
        judge_config: Optional[Dict[str, Any]] = None,
    ):
        self.similarity_threshold = similarity_threshold
        if similarity_engine is not None:
            self.engine = similarity_engine
        else:
            from prompt_architect.embeddings.mock import MockEmbeddingProvider

            self.engine = SimilarityEngine(MockEmbeddingProvider())

        self._judge_provider_name = judge_provider_name or "mock"
        self._judge_config = judge_config or {}
        self._factory = ProviderFactory()

    def evaluate(
        self,
        template: PromptTemplate,
        test_cases: List[Dict[str, Any]],
        metrics: Dict[str, Any],
    ) -> List[EvalResult]:
        results = []

        for case in test_cases:
            try:
                rendered_output = template.render(**case)
                eval_metrics = {}
                all_passed = True

                if "exact_match" in metrics:
                    expected = metrics["exact_match"]
                    passed = rendered_output.strip() == expected.strip()
                    eval_metrics["exact_match"] = {
                        "passed": passed,
                        "expected": expected,
                        "actual": rendered_output.strip(),
                    }
                    if not passed:
                        all_passed = False

                if "regex_match" in metrics:
                    pattern = metrics["regex_match"]
                    passed = bool(re.search(pattern, rendered_output))
                    eval_metrics["regex_match"] = {
                        "passed": passed,
                        "pattern": pattern,
                    }
                    if not passed:
                        all_passed = False

                if "semantic_similarity" in metrics and "golden_output" in case:
                    threshold = metrics["semantic_similarity"]
                    golden = case["golden_output"]
                    similarity = self.engine.calculate_similarity(
                        rendered_output, golden
                    )
                    passed = similarity >= threshold
                    eval_metrics["semantic_similarity"] = {
                        "passed": passed,
                        "score": similarity,
                        "threshold": threshold,
                    }
                    if not passed:
                        all_passed = False

                if "llm_judge" in metrics:
                    rubric = metrics["llm_judge"]
                    result = self._judge(rendered_output, case, rubric)
                    eval_metrics["llm_judge"] = result
                    if not result.get("passed", False):
                        all_passed = False

                results.append(
                    EvalResult(
                        passed=all_passed,
                        metrics=eval_metrics,
                        output=rendered_output,
                    )
                )

            except Exception as e:
                results.append(
                    EvalResult(
                        passed=False,
                        metrics={"error": str(e)},
                        output="",
                    )
                )

        return results

    def _judge(
        self,
        rendered_output: str,
        case: Dict[str, Any],
        rubric: str,
    ) -> Dict[str, Any]:
        prompt_text = _JUDGE_PROMPT_TEMPLATE.format(
            rubric=rubric,
            input=json.dumps(case),
            output=rendered_output,
        )

        judge_template = PromptTemplate(
            name="__judge__",
            template_string=prompt_text,
        )

        provider = self._factory.get_provider(
            self._judge_provider_name,
            config=self._judge_config,
        )
        raw = provider.execute(judge_template, {})

        return self._parse_judge_response(raw)

    def _parse_judge_response(self, raw: str) -> Dict[str, Any]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.removeprefix("```json").strip()
            cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "passed": False,
                "score": 0,
                "reasoning": f"Failed to parse judge response: {raw[:200]}",
            }

        return {
            "passed": bool(parsed.get("passed", False)),
            "score": int(parsed.get("score", 0)),
            "reasoning": parsed.get("reasoning", ""),
        }
