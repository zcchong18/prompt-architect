import pytest
from prompt_architect.models import PromptTemplate
from prompt_architect.orchestration.agent import (
    Agent,
    AgentOrchestrator,
    AgentTask,
    AgentResult,
)


class TestAgent:
    def test_agent_defaults(self):
        template = PromptTemplate(name="t", template_string="Hello {name}")
        agent = Agent(name="test_agent", template=template)
        assert agent.name == "test_agent"
        assert agent.provider_name == "mock"
        assert agent.description == ""
        assert agent.config == {}


class TestAgentOrchestrator:
    def test_register_and_list_agents(self):
        orchestrator = AgentOrchestrator()
        assert orchestrator.list_agents() == []

        template = PromptTemplate(name="t", template_string="Hello {name}")
        orchestrator.register_agent(Agent(name="agent_a", template=template))
        assert orchestrator.list_agents() == ["agent_a"]

    def test_register_duplicate_raises_error(self):
        orchestrator = AgentOrchestrator()
        template = PromptTemplate(name="t", template_string="test")
        orchestrator.register_agent(Agent(name="dup", template=template))
        with pytest.raises(ValueError, match="already registered"):
            orchestrator.register_agent(Agent(name="dup", template=template))

    def test_get_agent_returns_agent(self):
        orchestrator = AgentOrchestrator()
        template = PromptTemplate(name="t", template_string="Hello {name}")
        orchestrator.register_agent(Agent(name="greeter", template=template))
        agent = orchestrator.get_agent("greeter")
        assert agent.name == "greeter"

    def test_get_unknown_agent_raises_error(self):
        orchestrator = AgentOrchestrator()
        with pytest.raises(ValueError, match="Unknown agent"):
            orchestrator.get_agent("nonexistent")

    def test_run_with_mock_provider(self):
        orchestrator = AgentOrchestrator()
        template = PromptTemplate(
            name="t", template_string="Hello {{name}}", variables=["name"]
        )
        orchestrator.register_agent(Agent(name="greeter", template=template))

        task = AgentTask(agent_name="greeter", context={"name": "World"})
        result = orchestrator.run(task)

        assert isinstance(result, AgentResult)
        assert result.agent_name == "greeter"
        assert result.output == "Hello World"

    def test_handoff_between_agents(self):
        orchestrator = AgentOrchestrator()

        agent_a = Agent(
            name="extractor",
            template=PromptTemplate(
                name="a", template_string="Extracted: {{input}}", variables=["input"]
            ),
        )
        agent_b = Agent(
            name="formatter",
            template=PromptTemplate(
                name="b",
                template_string="Formatted: {{previous_output}}",
                variables=["previous_output"],
            ),
        )
        orchestrator.register_agent(agent_a)
        orchestrator.register_agent(agent_b)

        task = AgentTask(agent_name="extractor", context={"input": "data"})
        result_a = orchestrator.run(task)
        result_b = orchestrator.handoff(task, result_a, "formatter")

        assert result_b.agent_name == "formatter"
        assert "Extracted: data" in result_b.output

    def test_handoff_with_context_transform(self):
        orchestrator = AgentOrchestrator()
        agent_a = Agent(
            name="producer",
            template=PromptTemplate(
                name="a", template_string="Output: {{x}}", variables=["x"]
            ),
        )
        agent_b = Agent(
            name="consumer",
            template=PromptTemplate(
                name="b",
                template_string="Got: {{custom}}",
                variables=["custom"],
            ),
        )
        orchestrator.register_agent(agent_a)
        orchestrator.register_agent(agent_b)

        task = AgentTask(agent_name="producer", context={"x": "hello"})
        result_a = orchestrator.run(task)

        def transform(ctx):
            ctx["custom"] = ctx["previous_output"]
            return ctx

        result_b = orchestrator.handoff(
            task, result_a, "consumer", context_transform=transform
        )
        assert result_b.output == "Got: Output: hello"
