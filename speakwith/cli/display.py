"""Async screen renderer using rich."""

import asyncio
from typing import Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from speakwith.models import ConversationMode, PipelineStatus, SharedState
from speakwith.modes import get_mode_config


class Display:
    """Async screen renderer that updates when state changes.

    Uses rich library for beautiful terminal rendering.
    Redraws automatically when SharedState changes.
    """

    def __init__(self, state: SharedState):
        self.state = state
        self.console = Console()
        self._running = False

    def _build_header(self) -> Panel:
        """Build the header panel with mode and timer."""
        mode_config = get_mode_config(self.state.mode)
        status_icon = self._get_status_icon()

        header_text = Text()
        header_text.append("SPEAKWITH", style="bold cyan")
        header_text.append(f" - {mode_config.display_name}", style="white")
        header_text.append(f"  [{self.state.elapsed_formatted}]", style="dim")
        header_text.append(f"  {status_icon}", style="bold")

        return Panel(header_text, style="cyan")

    def _get_status_icon(self) -> str:
        """Get status indicator icon."""
        status_icons = {
            PipelineStatus.IDLE: "[green]Ready[/green]",
            PipelineStatus.RECORDING: "[red]Recording...[/red]",
            PipelineStatus.TRANSCRIBING: "[yellow]Processing...[/yellow]",
            PipelineStatus.GENERATING: "[yellow]Thinking...[/yellow]",
        }
        return status_icons.get(self.state.status, "")

    def _build_summary(self) -> Panel:
        """Build the summary panel."""
        summary = self.state.summary or "(Listening for conversation...)"
        return Panel(summary, title="Summary", border_style="blue")

    def _build_transcripts(self) -> Panel:
        """Build the recent transcripts panel."""
        if not self.state.transcripts:
            content = "(No transcripts yet - listening...)"
        else:
            lines = []
            for t in self.state.transcripts:
                # Format timestamp as MM:SS
                minutes = int(t.timestamp) // 60
                seconds = int(t.timestamp) % 60
                time_str = f"[{minutes:02d}:{seconds:02d}]"
                lines.append(f"{time_str} \"{t.text}\"")
            content = "\n\n".join(lines)

        return Panel(content, title="Recent Transcript", border_style="green")

    def _build_last_response(self) -> Panel:
        """Build the user's last response panel."""
        response = self.state.user_response or "(No response yet)"
        return Panel(f'"{response}"', title="Your Last Response", border_style="magenta")

    def _build_suggestions(self) -> Panel:
        """Build the suggestions panel."""
        suggestions = self.state.suggestions

        # Build reactions row
        reactions_text = Text()
        reactions_text.append("Quick Reactions:\n", style="bold yellow")
        for i, reaction in enumerate(suggestions.reactions, 1):
            reactions_text.append(f"  [{i}] {reaction}", style="white")
            if i < len(suggestions.reactions):
                reactions_text.append("    ")

        # Build follow-ups
        followups_text = Text()
        followups_text.append("\n\nFollow-ups:\n", style="bold cyan")
        for i, followup in enumerate(suggestions.followups, 4):
            followups_text.append(f"  [{i}] {followup}\n", style="white")

        # Custom option
        custom_text = Text()
        custom_text.append("\n  [c] Custom response", style="dim")

        combined = Text()
        combined.append_text(reactions_text)
        combined.append_text(followups_text)
        combined.append_text(custom_text)

        return Panel(combined, title="Suggestions", border_style="yellow")

    def render(self) -> None:
        """Render the current state to the console."""
        self.console.clear()

        # Build layout
        self.console.print(self._build_header())
        self.console.print(self._build_summary())
        self.console.print(self._build_transcripts())
        self.console.print(self._build_last_response())
        self.console.print(self._build_suggestions())
        self.console.print("\n> ", end="")

    async def run(self) -> None:
        """Background task that re-renders on state changes."""
        self._running = True
        try:
            while self._running:
                self.render()
                await self.state.wait_for_change()
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False

    def stop(self) -> None:
        """Stop the display task."""
        self._running = False
