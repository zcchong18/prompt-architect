import pytest
from prompt_architect.models import PromptTemplate
from prompt_architect.orchestration.chain import ChainStep, PromptChain, ChainResult


class TestChainStep:
    def test_chain_step_defaults(self):
        template = PromptTemplate(name="t", template_string="Hello {name}")
        step = ChainStep(template=template)
        assert step.provider_name == "mock"
        assert step.output_var == "previous_output"
        assert step.config == {}
        assert step.context_overrides == {}

    def test_chain_step_custom_values(self):
        template = PromptTemplate(name="t", template_string="Hello {name}")
        step = ChainStep(
            template=template,
            provider_name="openai",
            output_var="my_output",
            config={"api_key": "sk-test"},
            context_overrides={"name": "Override"},
        )
        assert step.provider_name == "openai"
        assert step.output_var == "my_output"
        assert step.config == {"api_key": "sk-test"}
        assert step.context_overrides == {"name": "Override"}


class TestPromptChain:
    def test_execute_single_step(self):
        template = PromptTemplate(
            name="t", template_string="Hello {{name}}", variables=["name"]
        )
        chain = PromptChain(steps=[ChainStep(template=template)])
        result = chain.execute({"name": "World"})

        assert isinstance(result, ChainResult)
        assert len(result.outputs) == 1
        assert "World" in result.outputs[0]
        assert result.full_context["previous_output"] == result.outputs[0]

    def test_execute_multi_step(self):
        step1 = ChainStep(
            template=PromptTemplate(
                name="s1", template_string="First: {{x}}", variables=["x"]
            ),
            output_var="step1_out",
        )
        step2 = ChainStep(
            template=PromptTemplate(
                name="s2",
                template_string="Second: {{step1_out}}",
                variables=["step1_out"],
            ),
            output_var="step2_out",
        )
        chain = PromptChain(steps=[step1, step2])
        result = chain.execute({"x": "hello"})

        assert len(result.outputs) == 2
        assert result.outputs[0] == "First: hello"
        assert result.outputs[1] == "Second: First: hello"
        assert result.full_context["step1_out"] == "First: hello"
        assert result.full_context["step2_out"] == "Second: First: hello"

    def test_context_overrides(self):
        template = PromptTemplate(
            name="t", template_string="{{a}} {{b}}", variables=["a", "b"]
        )
        step = ChainStep(
            template=template,
            context_overrides={"b": "overridden"},
        )
        chain = PromptChain(steps=[step])
        result = chain.execute({"a": "hello", "b": "original"})

        assert result.outputs[0] == "hello overridden"
        assert result.full_context["b"] == "original"

    def test_initial_context_preserved(self):
        template = PromptTemplate(name="t", template_string="{{a}}", variables=["a"])
        chain = PromptChain(steps=[ChainStep(template=template)])
        result = chain.execute({"a": "hello", "extra": "value"})

        assert result.outputs[0] == "hello"
        assert result.full_context["a"] == "hello"
        assert result.full_context["extra"] == "value"

    def test_add_step(self):
        chain = PromptChain()
        assert len(chain.steps) == 0
        template = PromptTemplate(name="t", template_string="test")
        chain.add_step(ChainStep(template=template))
        assert len(chain.steps) == 1
