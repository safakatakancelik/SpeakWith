# LLM Module

## Purpose

Abstraction layer for LLM providers. Generates response suggestions and conversation summaries.

## Files

- `base.py` - Abstract interface (`BaseLLMClient`)
- `openai_client.py` - OpenAI implementation

## Interface

### BaseLLMClient (Abstract)

```python
class BaseLLMClient(ABC):
    async def generate(self, prompt: str, system: str = "") -> str
    async def generate_suggestions(self, context: ConversationContext) -> Suggestions
    async def generate_summary(self, transcripts: list[str], previous_summary: str) -> str
```

## OpenAI Implementation

Uses `AsyncOpenAI` client for non-blocking calls.

### Prompt Structure

System prompt includes:
- User background (from profile)
- Today's mood (from mood board)
- Conversation mode (friendly/shopping)

User prompt includes:
- Conversation summary
- Recent transcripts (last 3)
- User's last response

### Response Parsing

LLM returns JSON:
```json
{
  "reactions": ["Yes", "Tell me more", "Really?"],
  "followups": ["That's interesting!", "I'd like to know more.", "How about you?"]
}
```

Fallback to defaults if parsing fails.

## Adding New Provider

1. Create `new_provider.py`
2. Implement `BaseLLMClient`
3. Handle async properly (use executor if needed)
4. Update `pipeline/coordinator.py` to use it

## Configuration

From `config.py`:
- `openai_api_key` (required)
- `llm_model` (default: gpt-4o-mini)
- `llm_temperature` (default: 0.7)

## Consumes

- `ConversationContext` (from `models.py`)

## Produces

- `Suggestions` (reactions + followups)
- Summary strings

## Error Handling

- Parse errors: Return default suggestions
- API errors: Let caller handle (suggestions module)
