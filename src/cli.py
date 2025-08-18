import typer
from pathlib import Path
from typing import Optional, List, Dict
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.panel import Panel
import logging
from .file_organizer import FileOrganizer

app = typer.Typer(
    help="Smart Image Organizer - Automatically organize images using metadata and AI",
    add_completion=False,
)
console = Console()


class CLIError(Exception):
    """Custom exception for CLI errors with user-friendly messages."""

    pass


def setup_logging(log_file: str = "image_organizer.log"):
    """Setup logging with file and console output."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )


def validate_source_dir(source_dir: Path) -> List[Path]:
    """Validate source directory and return list of image files."""
    if not source_dir.exists():
        raise CLIError(f"Source directory does not exist: {source_dir}")

    if not source_dir.is_dir():
        raise CLIError(f"Source path is not a directory: {source_dir}")

    image_files = list(source_dir.rglob("*"))
    image_files = [
        f
        for f in image_files
        if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
    ]

    if not image_files:
        raise CLIError(f"No image files found in {source_dir}")

    return image_files


def create_progress() -> Progress:
    """Create a progress bar with multiple columns."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    )


def display_results(stats: Dict, use_ai: bool = False):
    """Display organization results in a table."""
    table = Table(title="Organization Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right", style="green")

    table.add_row("Images Processed", str(stats["processed"]))
    table.add_row("Images Moved", str(stats["moved"]))
    if use_ai:
        table.add_row("Images Tagged", str(stats["tagged"]))
    table.add_row("Errors", str(stats["errors"]))

    console.print(table)


@app.command()
def preview(
    source_dir: Path = typer.Argument(..., help="Source directory containing images"),
    dest_dir: Path = typer.Argument(
        ..., help="Destination directory for organized images"
    ),
    use_ai: bool = typer.Option(
        False, "--use-ai", help="Enable AI-powered image tagging"
    ),
):
    """Preview how images would be organized without making any changes."""
    try:
        image_files = validate_source_dir(source_dir)
        organizer = FileOrganizer(source_dir, dest_dir, use_ai)

        console.print("\n[bold yellow]PREVIEW MODE[/bold yellow]")
        console.print(f"Found {len(image_files)} images to organize\n")

        with create_progress() as progress:
            task = progress.add_task("Analyzing images...", total=len(image_files))
            stats = organizer.organize_images(dry_run=True)
            progress.update(task, advance=len(image_files))

        # Show sample of planned operations
        operations = organizer.operations_log[:5]
        if operations:
            console.print("\n[bold]Sample of planned operations:[/bold]")
            for op in operations:
                console.print(f"• Move {op['source']} → {op['destination']}")
            if len(organizer.operations_log) > 5:
                console.print(f"...and {len(organizer.operations_log) - 5} more files")

        display_results(stats, use_ai)

    except CLIError as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {str(e)}[/bold red]")
        logging.exception("Unexpected error during preview")
        raise typer.Exit(1)


@app.command()
def organize(
    source_dir: Path = typer.Argument(..., help="Source directory containing images"),
    dest_dir: Path = typer.Argument(
        ..., help="Destination directory for organized images"
    ),
    dry_run: bool = typer.Option(
        True, "--dry-run/--no-dry-run", help="Simulate the organization process"
    ),
    use_ai: bool = typer.Option(
        False, "--use-ai", help="Enable AI-powered image tagging"
    ),
    log_file: Optional[Path] = typer.Option(
        None, "--log", help="Path to save operations log"
    ),
):
    """Organize images based on their metadata (EXIF, date, location)."""
    try:
        setup_logging()
        image_files = validate_source_dir(source_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Initialize organizer
        organizer = FileOrganizer(source_dir, dest_dir, use_ai)

        # Show operation mode and summary
        mode = "DRY RUN" if dry_run else "LIVE RUN"
        console.print(
            Panel.fit(
                f"{mode}\nSource: {source_dir}\nDestination: {dest_dir}\n"
                f"Found {len(image_files)} images to process"
            )
        )

        # Process images with progress bar
        with create_progress() as progress:
            task = progress.add_task("Organizing images...", total=len(image_files))
            stats = organizer.organize_images(dry_run=dry_run)
            progress.update(task, advance=len(image_files))

        # Display results and save log
        display_results(stats, use_ai)

        if log_file:
            organizer.save_operations_log(log_file)
            console.print(f"\nOperations log saved to: {log_file}")

    except CLIError as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {str(e)}[/bold red]")
        logging.exception("Unexpected error during organization")
        raise typer.Exit(1)


@app.command()
def undo(log_file: Path = typer.Argument(..., help="Path to the operations log file")):
    """Undo the last organization operation using the operations log."""
    try:
        setup_logging()

        if not log_file.exists():
            raise CLIError(f"Log file not found: {log_file}")

        # Load and validate log file
        import json

        try:
            with open(log_file) as f:
                operations = json.load(f)
            if not isinstance(operations, list) or not operations:
                raise CLIError("Invalid or empty operations log")
        except json.JSONDecodeError:
            raise CLIError("Invalid JSON format in operations log")

        # Initialize organizer
        organizer = FileOrganizer(Path("."), Path("."))
        organizer.operations_log = operations

        # Show summary of operations to undo
        console.print("\n[bold yellow]UNDO OPERATIONS[/bold yellow]")
        console.print(f"Found {len(operations)} operations to undo")

        # Sample of operations to undo
        for op in operations[:3]:
            console.print(f"• Move back: {op['destination']} → {op['source']}")
        if len(operations) > 3:
            console.print(f"...and {len(operations) - 3} more files")

        # Confirm with user
        if not typer.confirm("\nDo you want to proceed with the undo operation?"):
            console.print("Operation aborted by user")
            return

        # Perform undo with progress bar
        with create_progress() as progress:
            task = progress.add_task("Undoing operations...", total=len(operations))
            organizer.undo_operations()
            progress.update(task, completed=len(operations))

        console.print("[bold green]Successfully undone all operations![/bold green]")

    except CLIError as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {str(e)}[/bold red]")
        logging.exception("Unexpected error during undo")
        raise typer.Exit(1)


def main():
    app()
