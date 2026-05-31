import pytest
from prompt_architect.intelligence.analyzer import PromptAnalyzer


class DiffProvider:
    def __init__(self, vectors):
        self._vectors = vectors
        self._call_count = 0

    def embed_text(self, text):
        idx = self._call_count
        self._call_count += 1
        return self._vectors[idx % len(self._vectors)]


class TestPromptAnalyzer:
    def test_identical_templates_no_regression(self):
        class IdentityProvider:
            def embed_text(self, text):
                return [1.0, 0.0]

        engine = type("Engine", (), {"calculate_similarity": lambda self, a, b: 1.0})()
        analyzer = PromptAnalyzer(engine, threshold=0.9)
        result = analyzer.analyze("Hello {name}", "Hello {name}")

        assert result.overall_similarity == 1.0
        assert result.is_regression is False
        assert result.changes == []

    def test_different_templates_detects_changes(self):
        class OneIfHelloEngine:
            def calculate_similarity(self, a, b):
                return 0.0

        engine = OneIfHelloEngine()
        analyzer = PromptAnalyzer(engine, threshold=0.9)
        result = analyzer.analyze("Hello {name}", "Goodbye {name}")

        assert result.is_regression is True
        assert len(result.changes) >= 1

    def test_changes_identified_correctly(self):
        class ZeroEngine:
            def calculate_similarity(self, a, b):
                return 0.5

        engine = ZeroEngine()
        analyzer = PromptAnalyzer(engine, threshold=0.9)
        result = analyzer.analyze(
            "Instructions: Do X\nContext: Y\nOutput: Z",
            "Instructions: Do Y\nContext: Y\nOutput: Z",
        )

        assert len(result.changes) >= 1
        assert any("Instructions" in c.old_text for c in result.changes)

    def test_remove_segment_static(self):
        result = PromptAnalyzer._remove_segment("Hello World Foo", "World")
        assert result == "Hello  Foo"

    def test_most_disruptive_change_identified(self):
        call_log = []

        class TrackEngine:
            def calculate_similarity(self, a, b):
                call_log.append((a[:20], b[:20]))
                if "Instructions: Be concise" in a and "Instructions: Be verbose" in b:
                    return 0.8
                if a.strip() == b.strip():
                    return 1.0
                return 0.3

        engine = TrackEngine()
        analyzer = PromptAnalyzer(engine, threshold=0.9)
        result = analyzer.analyze(
            "Instructions: Be concise\nOutput: result",
            "Instructions: Be verbose\nOutput: result",
        )

        assert result.most_disruptive_change is not None
