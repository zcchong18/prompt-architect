import typer
from typing import Optional
from rich import print as rprint
from prompt_architect.core.template import PromptTemplate
from prompt_architect.core.storage import Storage

app = typer.Typer(help="Prompt Architect CLI - Manage your LLM prompts like code.")
prompt_app = typer.Typer(help="Commands for managing prompts.")
app.add_typer(prompt_app, name="prompt")

storage = Storage(storage_dir="templates")

@prompt_app.command("create")
def prompt_create(
    name: str = typer.Argument(..., help="The name of the prompt template."),
    template_string: str = typer.Argument(..., help="The raw template string."),
    description: Optional[str] = typer.Option("", help="A brief description of the prompt.")
):
    """
    Create a new Prompt Template and save it to storage.
    """
    try:
        # 1. Validate with Pydantic
        new_template = PromptTemplate(
            name=name,
            template_string=template_string,
            description=description
        )
        
        # 2. Save to storage
        storage.save(new_template)
        
        rprint(f"[bold green]✅ Success![/bold green] Prompt template '[bold]{name}[/bold]' created and saved.")
        
    except Exception as e:
        rprint(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@prompt_app.command("list")
def prompt_list():
    """
    List all saved prompt templates.
    """
    template_names = storage.list_all()
    if not template_names:
        rprint("[yellow]No templates found.[/yellow]")
        return

    rprint("[bold blue]Available Prompt Templates:[/bold blue]")
    for name in template_names:
        try:
            template = storage.load(name)
            rprint(f"- [bold]{template.name}[/bold]: {template.description}")
        except Exception as e:
            rprint(f"- [red]{name}[/red] (Error loading: {e})")

if __name__ == "__main__":
    app()
