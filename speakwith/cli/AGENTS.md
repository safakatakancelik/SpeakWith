# CLI Module

## Purpose

Terminal user interface with async rendering and non-blocking input.

## Files

- `display.py` - Screen renderer using rich
- `input_handler.py` - Non-blocking input handler

## Components

### Display

```python
class Display:
    def __init__(self, state: SharedState)
    def render(self) -> None          # One-time render
    async def run(self) -> None       # Background render loop
    def stop(self) -> None
```

**Renders**:
- Header (mode, timer, status)
- Summary panel
- Recent transcripts
- User's last response
- Suggestions (reactions + follow-ups)

**Updates when**:
- `SharedState` changes (via `wait_for_change()`)

### InputHandler

```python
class InputHandler:
    def __init__(self, state: SharedState, on_response: Callable)
    async def run(self) -> None
    def stop(self) -> None
```

**Handles**:
- Numbers 1-3: Quick reactions
- Numbers 4-6: Follow-ups
- 'c': Custom response entry
- Other text: Direct response

## UI Layout

```
╔═══════════════════════════════════════════════════════╗
║  SPEAKWITH - Friendly Mode            [00:01:23]      ║
╠═══════════════════════════════════════════════════════╣
║  Summary                                              ║
║  (LLM-generated conversation summary)                 ║
╠═══════════════════════════════════════════════════════╣
║  Recent Transcript                                    ║
║  [00:00:40] "First transcript..."                     ║
║  [00:00:50] "Second transcript..."                    ║
╠═══════════════════════════════════════════════════════╣
║  Your Last Response                                   ║
║  "What you said last"                                 ║
╠═══════════════════════════════════════════════════════╣
║  Quick Reactions:                                     ║
║  [1] Yes    [2] No    [3] Tell me more               ║
║                                                       ║
║  Follow-ups:                                          ║
║  [4] First follow-up sentence.                        ║
║  [5] Second follow-up sentence.                       ║
║  [6] Third follow-up sentence.                        ║
║                                                       ║
║  [c] Custom response                                  ║
╚═══════════════════════════════════════════════════════╝
> _
```

## Dependencies

- `rich` for terminal rendering
- `aioconsole` for async input

## Status Indicators

- Recording: red
- Processing: yellow
- Ready: green

## Non-Blocking Pattern

Both display and input run as concurrent async tasks. Display waits for state changes, input waits for user keystroke. Neither blocks the other.
