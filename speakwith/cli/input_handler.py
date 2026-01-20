"""Non-blocking user input handler."""

import asyncio
from typing import Callable, Optional, Awaitable

from aioconsole import ainput

from speakwith.models import SharedState, Suggestions


class InputHandler:
    """Non-blocking input handler for user responses.

    Handles:
    - Number selection (1-6) for suggestions
    - 'c' for custom response
    - Graceful cancellation
    """

    def __init__(self, state: SharedState, on_response: Optional[Callable[[str], Awaitable[None]]] = None):
        self.state = state
        self.on_response = on_response
        self._running = False

    async def _handle_input(self, user_input: str) -> Optional[str]:
        """Process user input and return the selected response."""
        user_input = user_input.strip().lower()

        if not user_input:
            return None

        suggestions = self.state.suggestions

        # Handle number selection
        if user_input.isdigit():
            num = int(user_input)
            if 1 <= num <= 3 and num <= len(suggestions.reactions):
                return suggestions.reactions[num - 1]
            elif 4 <= num <= 6 and (num - 4) < len(suggestions.followups):
                return suggestions.followups[num - 4]

        # Handle custom response
        if user_input == "c":
            try:
                custom = await ainput("Your response: ")
                return custom.strip() if custom.strip() else None
            except (EOFError, asyncio.CancelledError):
                return None

        # Treat any other input as a direct response
        return user_input if len(user_input) > 1 else None

    async def run(self) -> None:
        """Background task that listens for user input."""
        self._running = True
        try:
            while self._running:
                try:
                    user_input = await ainput("")
                    response = await self._handle_input(user_input)

                    if response:
                        await self.state.set_user_response(response)
                        if self.on_response:
                            await self.on_response(response)

                except EOFError:
                    break
                except asyncio.CancelledError:
                    break

        finally:
            self._running = False

    def stop(self) -> None:
        """Stop the input handler."""
        self._running = False
