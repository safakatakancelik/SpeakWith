"""User profile loader from markdown files."""

from pathlib import Path

from speakwith.config import Config
from speakwith.models import UserProfile


class ProfileLoader:
    """Loads user profile from markdown files.

    Reads background.md and mood_board.md from the user_data directory.
    """

    def __init__(self, config: Config):
        self.user_data_dir = config.user_data_dir

    def load(self) -> UserProfile:
        """Load user profile from markdown files.

        Returns:
            UserProfile with background and mood board content.
            Returns empty strings if files don't exist.
        """
        background = self._read_file("background.md")
        mood_board = self._read_file("mood_board.md")

        return UserProfile(
            background=background,
            mood_board=mood_board,
        )

    def _read_file(self, filename: str) -> str:
        """Read a file from the user_data directory."""
        path = self.user_data_dir / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def background_exists(self) -> bool:
        """Check if background.md exists."""
        return (self.user_data_dir / "background.md").exists()

    def mood_board_exists(self) -> bool:
        """Check if mood_board.md exists."""
        return (self.user_data_dir / "mood_board.md").exists()
