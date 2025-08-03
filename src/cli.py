import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import logging
from .file_organizer import FileOrganizer

app = typer.Typer()
console = Console()

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('image_organizer.log'),
            logging.StreamHandler()
        ]
    )

@app.command()
def organize(
    source_dir: Path = typer.Argument(..., help="Source directory containing images"),
    dest_dir: Path = typer.Argument(..., help="Destination directory for organized images"),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run", help="Simulate the organization process"),
    use_ai: bool = typer.Option(False, "--use-ai", help="Enable AI-powered image tagging"),
    log_file: Optional[Path] = typer.Option(None, "--log", help="Path to save operations log")
):
    """
    Organize images based on their metadata (EXIF, date, location).
    """
    setup_logging()
    
    try:
        # Validate directories
        if not source_dir.exists():
            typer.echo(f"Error: Source directory {source_dir} does not exist")
            raise typer.Exit(1)
            
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize organizer
        organizer = FileOrganizer(source_dir, dest_dir, use_ai)
        
        # Show operation mode
        mode = "DRY RUN" if dry_run else "LIVE RUN"
        console.print(f"\n[bold yellow]{mode}[/bold yellow]")
        console.print(f"Source: {source_dir}")
        console.print(f"Destination: {dest_dir}")
        
        # Process images
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Organizing images...", total=None)
            stats = organizer.organize_images(dry_run=dry_run)
        
        # Display results
        table = Table(title="Organization Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right", style="green")
        
        table.add_row("Images Processed", str(stats['processed']))
        table.add_row("Images Moved", str(stats['moved']))
        if use_ai:
            table.add_row("Images Tagged", str(stats['tagged']))
        table.add_row("Errors", str(stats['errors']))
        
        console.print(table)
        
        # Save operations log
        if log_file:
            organizer.save_operations_log(log_file)
            console.print(f"\nOperations log saved to: {log_file}")
            
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        raise typer.Exit(1)

@app.command()
def undo(
    log_file: Path = typer.Argument(..., help="Path to the operations log file")
):
    """
    Undo the last organization operation using the operations log.
    """
    setup_logging()
    
    try:
        if not log_file.exists():
            typer.echo(f"Error: Log file {log_file} does not exist")
            raise typer.Exit(1)
            
        # Initialize organizer with dummy paths (will be overridden by the log)
        organizer = FileOrganizer(Path("."), Path("."))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Undoing operations...", total=None)
            organizer.undo_operations()
            
        console.print("[bold green]Successfully undone all operations![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        raise typer.Exit(1)

def main():
    app()
