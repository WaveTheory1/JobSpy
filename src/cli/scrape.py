from __future__ import annotations

import csv
from datetime import date
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt, PromptBase
from rich.text import Text

from jobspy import scrape_jobs
from jobspy.model import Site

from .utils import generate_html_content

if TYPE_CHECKING:
    from pandas import DataFrame

app = typer.Typer()
console = Console(stderr=True)


class EnumPrompt(PromptBase[list[Enum]]):
    """A prompt that returns a list of Enums."""

    response_type = list[Enum]
    validate_error_message = "[prompt.invalid]Please enter a valid list"

    def process_response(self, value: str) -> list[Enum]:
        platforms = []
        for platform_name in value.split(","):
            try:
                platforms.append(Site[platform_name.strip().upper()])
            except KeyError:
                console.print(
                    f"[bold red]✗[/bold red] Invalid platform: [yellow]{platform_name}[/yellow]",
                    style="red",
                )
                raise typer.BadParameter(f"Invalid platform: {platform_name}.")
        return platforms


def print_welcome_message() -> None:
    """Format and print welcome message."""
    console.print()

    # Create welcome panel
    welcome_text = Text(justify="center")
    welcome_text.append("JOB SCRAPER", style="bold bright_cyan")

    panel = Panel(
        welcome_text,
        title="[bold bright_white]Welcome[/bold bright_white]",
        border_style="bright_cyan",
        padding=(1, 2),
    )
    console.print(panel)

    # Instructions
    console.print(
        "💡 [bright_yellow]Tip:[/bright_yellow] [white]Default values appear in [bright_cyan](brackets)[/bright_cyan][/white]",
        style="dim",
    )
    console.print(
        "   [white]Press [bright_green]ENTER[/bright_green] to accept the default value[/white]\n",
        style="dim",
    )


def print_goodbye_message(output_dir: str, num_results: int) -> None:
    """Format and print goodbye message."""
    console.print()

    text = Text()
    text.append("✅ ", style="bold bright_cyan")
    text.append(f"{num_results} found and saved.", style="bright_white")

    panel = Panel(
        text,
        subtitle=f"[dim white]📁 Results → {output_dir}[/dim white]",
        border_style="bright_green",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def collect_user_inputs() -> dict[str, Any]:
    """Collect user inputs for job scraping."""
    # Platforms
    available_platforms = ", ".join([s.name.capitalize() for s in Site])
    console.print(
        f"[dim]Available platforms: [bright_white]{available_platforms}[/bright_white][/dim]\n"
    )

    platforms = EnumPrompt.ask(
        "[bright_cyan]🖥️  Select platforms[/bright_cyan] [dim](comma-separated)[/dim]",
        default="Linkedin, Indeed",
        console=console,
    )

    # Search Query
    search_query = Prompt.ask(
        "[bright_cyan]🔍 Search query[/bright_cyan]",
        default='"Netsuite" consultant -oracle',
        console=console,
    )

    # Number of entries
    num_entries = Prompt.ask(
        "[bright_cyan]📊 Number of jobs[/bright_cyan] [dim](max 1000)[/dim]",
        default="1000",
        console=console,
    )
    try:
        num_entries = int(num_entries)
        if num_entries < 1 or num_entries > 1000:
            console.print(
                "[yellow]⚠[/yellow]  Using maximum of 1000 entries", style="dim"
            )
            num_entries = 1000
    except ValueError:
        console.print("[yellow]⚠[/yellow]  Invalid number. Using 1000", style="dim")
        num_entries = 1000

    # Hours
    hours_old = IntPrompt.ask(
        "[bright_cyan]⏰ Results age[/bright_cyan] [dim](hours)[/dim]",
        default="24",
        console=console,
    )

    # Region
    country = Prompt.ask(
        "[bright_cyan]🌍 Country[/bright_cyan]", default="USA", console=console
    )

    return {
        "site_name": platforms,
        "search_term": search_query,
        "results_wanted": num_entries,
        "hours_old": hours_old,
        "location": country,
        "country_indeed": country,
    }


def save_results(jobs: DataFrame, *, title: str, output_file: Path) -> None:
    """Save results as CSV and HTML."""
    jobs["emails"] = jobs["emails"].fillna("-")
    jobs.to_csv(
        f"{output_file}.csv",
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
        index=False,
    )

    html_content = generate_html_content(jobs, title=title)
    with Path(f"{output_file}.html").open("w", encoding="utf-8") as fp:
        fp.write(html_content)


@app.command()
def scrape() -> None:
    """Scrape job postings from multiple platforms with customizable filters."""
    print_welcome_message()

    inputs = collect_user_inputs()

    filename = Path(f"./data/{date.today()}/Jobs-{date.today()}")
    filename.parent.mkdir(parents=True, exist_ok=True)

    console.print("✨ ", style="bright_yellow")
    console.print("Scraping jobs... Please wait.", style="bright_white")

    jobs = scrape_jobs(**inputs, linkedin_fetch_description=True)
    save_results(jobs, title=inputs["search_term"], output_file=filename)

    print_goodbye_message(filename.parent.name, len(jobs))


if __name__ == "__main__":
    app()
