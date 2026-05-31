from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.factory import ProviderFactory
from prompt_architect.core.storage import Storage


@dataclass
class ChainStep:
    template: PromptTemplate
    provider_name: str = "mock"
    output_var: str = "previous_output"
    config: Dict[str, Any] = field(default_factory=dict)
    context_overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChainResult:
    outputs: List[str]
    full_context: Dict[str, Any]


class PromptChain:
    def __init__(
        self,
        steps: Optional[List[ChainStep]] = None,
        factory: Optional[ProviderFactory] = None,
    ):
        self.steps = steps or []
        self._factory = factory or ProviderFactory()

    def add_step(self, step: ChainStep):
        self.steps.append(step)

    def execute(self, initial_context: Dict[str, Any]) -> ChainResult:
        context = dict(initial_context)
        outputs = []

        for step in self.steps:
            merged_context = {**context, **step.context_overrides}
            provider = self._factory.get_provider(
                step.provider_name, config=step.config
            )
            result = provider.execute(step.template, merged_context)
            outputs.append(result)
            context[step.output_var] = result

        return ChainResult(outputs=outputs, full_context=context)

    @classmethod
    def from_template_names(
        cls,
        template_names: List[str],
        provider_name: str = "mock",
        output_var_template: str = "step_{i}_output",
    ) -> "PromptChain":
        storage = Storage()
        steps = []
        for i, name in enumerate(template_names):
            template = storage.load(name)
            step = ChainStep(
                template=template,
                provider_name=provider_name,
                output_var=output_var_template.replace("{i}", str(i)),
            )
            steps.append(step)
        return cls(steps=steps)
