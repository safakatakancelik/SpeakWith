"""Configuration management for SpeakWith."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration loaded from environment."""

    # OpenAI
    openai_api_key: str

    # Whisper
    whisper_model: str = "base"

    # Audio
    sample_rate: int = 16000
    chunk_duration: float = 10.0

    # Paths
    user_data_dir: Path = Path("user_data")

    # LLM
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.7

    # Memory
    max_transcripts: int = 3
    summary_update_interval: int = 3  # Update summary every N transcripts

    @classmethod
    def load(cls, env_file: Optional[Path] = None) -> "Config":
        """Load configuration from environment variables."""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return cls(
            openai_api_key=openai_key,
            whisper_model=os.getenv("WHISPER_MODEL", "base"),
            sample_rate=int(os.getenv("SAMPLE_RATE", "16000")),
            chunk_duration=float(os.getenv("CHUNK_DURATION", "10.0")),
            user_data_dir=Path(os.getenv("USER_DATA_DIR", "user_data")),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_transcripts=int(os.getenv("MAX_TRANSCRIPTS", "3")),
            summary_update_interval=int(os.getenv("SUMMARY_UPDATE_INTERVAL", "3")),
        )


# Global config instance (initialized on first access)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def init_config(env_file: Optional[Path] = None) -> Config:
    """Initialize global config from specified env file."""
    global _config
    _config = Config.load(env_file)
    return _config
