import json
import os
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from prompt_architect.core.evaluator import Evaluator
from prompt_architect.core.storage import Storage
from prompt_architect.core.template import PromptTemplate

app = typer.Typer(help="Prompt Architect CLI - Manage your LLM prompts like code.")
prompt_app = typer.Typer(help="Commands for managing prompts.")
app.add_typer(prompt_app, name="prompt")

console = Console()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
storage = Storage(storage_dir=os.path.join(PROJECT_ROOT, "templates"))


@prompt_app.command("create")
def prompt_create(
    name: str = typer.Argument(..., help="The name of the prompt template."),
    template_string: str = typer.Argument(..., help="The raw template string."),
    description: Optional[str] = typer.Option(
        "", help="A brief description of the prompt."
    ),
):
    """Create a new Prompt Template and save it to storage."""
    try:
        new_template = PromptTemplate(
            name=name,
            template_string=template_string,
            description=description,
        )
        storage.save(new_template)

        panel = Panel(
            f"Prompt template '[bold]{name}[/bold]' created and saved.",
            title="Success",
            border_style="green",
        )
        console.print(panel)

    except Exception as e:
        panel = Panel(str(e), title="Error", border_style="red")
        console.print(panel)
        raise typer.Exit(code=1)


@prompt_app.command("list")
def prompt_list():
    """List all saved prompt templates."""
    template_names = storage.list_all()
    if not template_names:
        console.print("[yellow]No templates found.[/yellow]")
        return

    table = Table(title="Available Prompt Templates")
    table.add_column("Name", style="bold cyan")
    table.add_column("Description")
    table.add_column("Version")
    table.add_column("Author")

    for name in template_names:
        try:
            template = storage.load(name)
            table.add_row(
                template.name,
                template.description or "",
                template.version,
                template.author or "",
            )
        except Exception as e:
            table.add_row(
                f"[red]{name}[/red]", f"[red]Error loading: {e}[/red]", "", ""
            )

    console.print(table)
    console.print(f"\n[dim]{len(template_names)} template(s) total[/dim]")


@prompt_app.command("evaluate")
def prompt_evaluate(
    template_name: str = typer.Argument(
        ..., help="The name of the template to evaluate."
    ),
    test_cases_json: str = typer.Option(
        ...,
        help="A JSON string containing test cases. "
        'Example: \'[{"name": "Alice", "golden_output": "Hello Alice"}]\'',
    ),
    similarity_threshold: Optional[float] = typer.Option(
        None, help="The semantic similarity threshold to enforce."
    ),
):
    """Run regression tests on a prompt template."""
    try:
        template = storage.load(template_name)
        test_cases = json.loads(test_cases_json)

        metrics = {}
        if similarity_threshold is not None:
            metrics["semantic_similarity"] = similarity_threshold

        evaluator = Evaluator(similarity_threshold=similarity_threshold)
        results = evaluator.evaluate(template, test_cases, metrics)

        table = Table(title=f"Evaluation Report: [bold]{template_name}[/bold]")
        table.add_column("#", style="dim")
        table.add_column("Result", no_wrap=True)
        table.add_column("Output")
        table.add_column("Metrics")

        passed_count = 0
        for i, res in enumerate(results):
            status = "[green]PASS[/green]" if res.passed else "[red]FAIL[/red]"
            if res.passed:
                passed_count += 1
            metrics_str = "; ".join(
                f"{k}={v.get('score', v) if isinstance(v, dict) else v}"
                for k, v in res.metrics.items()
            )
            output_display = (
                res.output if len(res.output) < 80 else res.output[:77] + "..."
            )
            table.add_row(str(i + 1), status, output_display, metrics_str)

        console.print()
        console.print(table)

        summary_style = "green" if passed_count == len(results) else "red"
        summary_title = (
            "All tests passed! No regressions detected."
            if passed_count == len(results)
            else "Some tests failed."
        )
        summary_panel = Panel(
            f"[bold]{passed_count}/{len(results)} tests passed[/bold]",
            title=summary_title,
            border_style=summary_style,
        )
        console.print(summary_panel)

        if passed_count < len(results):
            raise typer.Exit(code=1)

    except Exception as e:
        panel = Panel(str(e), title="Error", border_style="red")
        console.print(panel)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
