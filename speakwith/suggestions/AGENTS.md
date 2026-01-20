# Suggestions Module

## Purpose

Generates contextual response suggestions based on conversation state.

## Files

- `generator.py` - Suggestion generator

## Key Class

### SuggestionGenerator

```python
class SuggestionGenerator:
    def __init__(self, config: Config, llm: BaseLLMClient, state: SharedState)
    async def generate(self) -> Suggestions
    async def run(self) -> None  # Background task
    def stop(self) -> None
```

## Data Flow

```
SharedState changes → detect new transcript → generate() → new Suggestions → SharedState
```

## Output Format

```python
Suggestions(
    reactions=["Yes", "No", "Tell me more"],  # 3 quick reactions (1-5 words)
    followups=["Full sentence 1.", "Full sentence 2.", "Full sentence 3."]  # 3 longer responses
)
```

## Generation Triggers

The background task (`run()`) generates new suggestions when:
1. New transcript arrives
2. User selects a response (triggered by coordinator)

## Dependencies

- `BaseLLMClient` for generation
- `SharedState` for context and storage
- `ConversationContext` bundled from state

## Mode-Aware Generation

Suggestions adapt to conversation mode:

**Friendly Mode**:
- Reactions: emotional, expressive ("That's wonderful!", "Oh no!")
- Follow-ups: questions, sharing, empathy

**Shopping Mode**:
- Reactions: practical ("Yes", "No thanks", "How much?")
- Follow-ups: product questions, decisions

## Error Handling

If LLM call fails, keeps previous suggestions and continues.

## Performance

- Generation happens in background
- Status indicator shows "Thinking..." during generation
- Previous suggestions remain usable while generating
