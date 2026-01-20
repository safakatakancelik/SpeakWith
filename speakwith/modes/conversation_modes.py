"""Conversation mode definitions and configurations."""

from dataclasses import dataclass

from speakwith.models import ConversationMode


@dataclass
class ModeConfig:
    """Configuration for a conversation mode."""

    mode: ConversationMode
    display_name: str
    description: str
    reaction_style: str
    followup_style: str


# Mode configurations
MODES: dict[ConversationMode, ModeConfig] = {
    ConversationMode.FRIENDLY: ModeConfig(
        mode=ConversationMode.FRIENDLY,
        display_name="Friendly Mode",
        description="Casual conversation with friends, family, or acquaintances",
        reaction_style="emotional, expressive, warm",
        followup_style="questions, sharing personal thoughts, showing empathy",
    ),
    ConversationMode.SHOPPING: ModeConfig(
        mode=ConversationMode.SHOPPING,
        display_name="Shopping Mode",
        description="Transactional conversations in stores, restaurants, or services",
        reaction_style="confirmations, clarifications, practical responses",
        followup_style="product questions, price inquiries, decision-making",
    ),
}


def get_mode_config(mode: ConversationMode) -> ModeConfig:
    """Get configuration for a conversation mode."""
    return MODES[mode]


def list_modes() -> list[ModeConfig]:
    """List all available conversation modes."""
    return list(MODES.values())
