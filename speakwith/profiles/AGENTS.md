# Profiles Module

## Purpose

Loads user profile information from markdown files for personalized suggestions.

## Files

- `loader.py` - Profile loader

## Key Class

### ProfileLoader

```python
class ProfileLoader:
    def __init__(self, config: Config)
    def load(self) -> UserProfile
    def background_exists(self) -> bool
    def mood_board_exists(self) -> bool
```

## Files Read

From `user_data/` directory:

### background.md
Persistent user information:
- Name, age, location
- Interests and hobbies
- Communication preferences
- Important context

### mood_board.md
Daily/session information:
- Current mood
- Topics to discuss
- Topics to avoid
- Notes for today

## Output

```python
UserProfile(
    background: str,  # Contents of background.md
    mood_board: str   # Contents of mood_board.md
)
```

## Usage in Pipeline

1. Loaded once at startup by `PipelineCoordinator`
2. Stored in `SharedState.profile`
3. Included in `ConversationContext` for LLM calls
4. Affects suggestion tone and content

## Configuration

From `config.py`:
- `user_data_dir` (default: "user_data")

## Missing Files

If files don't exist, returns empty strings. App works without profile but suggestions are less personalized.
