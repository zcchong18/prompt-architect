import difflib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from prompt_architect.intelligence.similarity import SimilarityEngine


@dataclass
class Segment:
    text: str
    start: int
    end: int


@dataclass
class Change:
    segment: Segment
    old_text: str
    new_text: str


@dataclass
class AnalysisResult:
    overall_similarity: float
    is_regression: bool
    changes: List[Change] = field(default_factory=list)
    change_impacts: List[Dict[str, Any]] = field(default_factory=list)
    most_disruptive_change: Optional[str] = None


class PromptAnalyzer:
    def __init__(self, engine: SimilarityEngine, threshold: float = 0.9):
        self.engine = engine
        self.threshold = threshold

    def analyze(
        self,
        old_template: str,
        new_template: str,
    ) -> AnalysisResult:
        old_lines = old_template.splitlines(keepends=True)
        new_lines = new_template.splitlines(keepends=True)

        overall_similarity = self.engine.calculate_similarity(
            old_template, new_template
        )
        is_regression = overall_similarity < self.threshold

        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        changes = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ("replace", "delete", "insert"):
                old_text = "".join(old_lines[i1:i2])
                new_text = "".join(new_lines[j1:j2])
                changes.append(
                    Change(
                        segment=Segment(
                            text=(old_text or new_text).strip(),
                            start=i1,
                            end=i2,
                        ),
                        old_text=old_text,
                        new_text=new_text,
                    )
                )

        change_impacts = []
        most_disruptive = None
        max_impact = -1.0

        for change in changes:
            old_without = self._remove_segment(old_template, change.old_text)
            new_without = self._remove_segment(new_template, change.new_text)

            sim_without = self.engine.calculate_similarity(old_without, new_without)
            impact = overall_similarity - sim_without
            change_impacts.append(
                {
                    "change": change.old_text.strip() or change.new_text.strip(),
                    "similarity_without_change": sim_without,
                    "impact": impact,
                }
            )

            if impact > max_impact:
                max_impact = impact
                most_disruptive = change.old_text.strip() or change.new_text.strip()

        return AnalysisResult(
            overall_similarity=overall_similarity,
            is_regression=is_regression,
            changes=changes,
            change_impacts=change_impacts,
            most_disruptive_change=most_disruptive,
        )

    @staticmethod
    def _remove_segment(text: str, segment: str) -> str:
        return text.replace(segment, "").strip()
