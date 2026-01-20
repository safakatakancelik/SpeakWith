# Modes Module

## Purpose

Defines conversation modes that affect suggestion style.

## Files

- `conversation_modes.py` - Mode definitions

## Available Modes

### Friendly Mode
For casual conversations with friends, family, acquaintances.

- **Reactions**: emotional, expressive, warm
- **Follow-ups**: questions, sharing personal thoughts, empathy

### Shopping Mode
For transactional conversations in stores, restaurants, services.

- **Reactions**: confirmations, clarifications, practical
- **Follow-ups**: product questions, price inquiries, decisions

## Data Structures

```python
class ModeConfig:
    mode: ConversationMode        # Enum value
    display_name: str             # "Friendly Mode"
    description: str              # Shown in mode selection
    reaction_style: str           # Hint for LLM
    followup_style: str           # Hint for LLM
```

## Functions

```python
def get_mode_config(mode: ConversationMode) -> ModeConfig
def list_modes() -> list[ModeConfig]
```

## Adding New Mode

1. Add enum value in `models.py`:
   ```python
   class ConversationMode(Enum):
       FRIENDLY = "friendly"
       SHOPPING = "shopping"
       NEW_MODE = "new_mode"  # Add here
   ```

2. Add config in `conversation_modes.py`:
   ```python
   MODES[ConversationMode.NEW_MODE] = ModeConfig(
       mode=ConversationMode.NEW_MODE,
       display_name="New Mode",
       description="Description for selection",
       reaction_style="style hints for LLM",
       followup_style="style hints for LLM",
   )
   ```

## Usage

- Selected at app startup
- Stored in `SharedState.mode`
- Passed to LLM in prompt for style guidance
