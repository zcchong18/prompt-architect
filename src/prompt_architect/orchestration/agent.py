from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.factory import ProviderFactory


@dataclass
class Agent:
    name: str
    template: PromptTemplate
    provider_name: str = "mock"
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentTask:
    agent_name: str
    context: Dict[str, Any]
    task_id: str = ""


@dataclass
class AgentResult:
    agent_name: str
    output: str
    task_id: str = ""


class AgentOrchestrator:
    def __init__(self, factory: Optional[ProviderFactory] = None):
        self._agents: Dict[str, Agent] = {}
        self._factory = factory or ProviderFactory()

    def register_agent(self, agent: Agent):
        if agent.name in self._agents:
            raise ValueError(f"Agent '{agent.name}' is already registered")
        self._agents[agent.name] = agent

    def get_agent(self, name: str) -> Agent:
        if name not in self._agents:
            raise ValueError(
                f"Unknown agent: '{name}'. Registered agents: {list(self._agents.keys())}"
            )
        return self._agents[name]

    def list_agents(self) -> List[str]:
        return list(self._agents.keys())

    def run(self, task: AgentTask) -> AgentResult:
        agent = self.get_agent(task.agent_name)
        provider = self._factory.get_provider(agent.provider_name, config=agent.config)
        output = provider.execute(agent.template, task.context)
        return AgentResult(
            agent_name=agent.name,
            output=output,
            task_id=task.task_id,
        )

    def handoff(
        self,
        from_task: AgentTask,
        from_result: AgentResult,
        to_agent_name: str,
        context_transform: Optional[callable] = None,
    ) -> AgentResult:
        next_context = dict(from_task.context)
        next_context["previous_agent"] = from_result.agent_name
        next_context["previous_output"] = from_result.output

        if context_transform:
            next_context = context_transform(next_context)

        next_task = AgentTask(
            agent_name=to_agent_name,
            context=next_context,
            task_id=from_task.task_id,
        )
        return self.run(next_task)
