"""SpeakWith entry point."""

import asyncio
import sys

from rich.console import Console
from rich.prompt import Prompt

from speakwith.config import init_config
from speakwith.models import ConversationMode
from speakwith.modes import list_modes
from speakwith.pipeline import PipelineCoordinator


console = Console()


def select_mode() -> ConversationMode:
    """Prompt user to select a conversation mode."""
    modes = list_modes()

    console.print("\n[bold]Select conversation mode:[/bold]")
    for i, mode_config in enumerate(modes, 1):
        console.print(f"  [{i}] {mode_config.display_name}")
        console.print(f"      [dim]{mode_config.description}[/dim]")

    while True:
        choice = Prompt.ask("\nEnter choice", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(modes):
                return modes[idx].mode
        except ValueError:
            pass
        console.print("[red]Invalid choice. Please enter a number.[/red]")


async def async_main() -> None:
    """Async entry point."""
    console.print("[bold cyan]Welcome to SpeakWith[/bold cyan]")
    console.print("Communication assistant for people who cannot speak\n")

    # Load configuration
    try:
        console.print("Loading configuration... ", end="")
        config = init_config()
        console.print("[green]Done[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("\nPlease create a .env file with your OPENAI_API_KEY")
        sys.exit(1)

    # Select mode
    mode = select_mode()

    # Initialize pipeline
    console.print(f"\nStarting {mode.value} conversation mode...")
    console.print("Initializing Whisper model... ", end="")

    coordinator = PipelineCoordinator(config, mode)
    await coordinator.initialize()
    console.print("[green]Done[/green]")

    console.print("\n[bold green]Listening...[/bold green] (Press Ctrl+C to exit)\n")

    try:
        await coordinator.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping...[/yellow]")
        await coordinator.stop()

    console.print("[bold cyan]Goodbye![/bold cyan]")


def main() -> None:
    """CLI entry point."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
