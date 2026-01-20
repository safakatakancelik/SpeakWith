# SpeakWith - Project Guide

## Overview

SpeakWith is a communication assistant for people who cannot speak but can read. It listens to environmental audio, transcribes speech, and suggests contextual responses (quick reactions and longer follow-ups) that the user can select to communicate.

This project is the **brain only** - a prototype of core functionality that can later be integrated into various applications or hardware.

## Core Functionality

1. **Audio Capture**: Record environment audio in 10-second batches
2. **Transcription**: Process audio using local Whisper model
3. **Response Generation**: Use LLM to suggest contextual responses
4. **Memory Management**: Maintain conversation context via summary + recent transcripts

## Architecture

```
speakwith/
├── main.py                 # Entry point, async event loop
├── cli/
│   ├── display.py          # Async screen renderer
│   └── input_handler.py    # Non-blocking user input
├── config.py               # Configuration and constants
├── audio/
│   └── recorder.py         # Async 10-second batch audio recording
├── transcription/
│   └── whisper_client.py   # Local Whisper transcription
├── llm/
│   ├── base.py             # Abstract LLM interface
│   └── openai_client.py    # OpenAI implementation
├── memory/
│   └── conversation.py     # Summary + last 3 transcripts management
├── suggestions/
│   └── generator.py        # Response suggestion logic
├── profiles/
│   └── loader.py           # Load user background & mood board
├── modes/
│   └── conversation_modes.py  # Friendly / Shopping mode definitions
└── pipeline/
    └── coordinator.py      # Async pipeline orchestration

user_data/
├── background.md           # User background info
└── mood_board.md           # Daily mood/context
```

## Technical Stack

- **Language**: Python 3.10+
- **Audio**: `sounddevice` or `pyaudio` for recording
- **Transcription**: `openai-whisper` (local, not API)
- **LLM**: OpenAI API (with abstraction layer for future providers)
- **Interface**: CLI (rich or simple print statements)

## Key Design Decisions

### Audio Processing (Fully Async)
- Record in **10-second batches**
- Pipeline runs continuously in background:
  ```
  [Recording Batch N] → [Transcribing N-1] → [Generating Suggestions N-2]
  ```
- Every 10 seconds: new transcription appears, memory updates, suggestions refresh
- User can select a response at ANY time (non-blocking input)
- All UI updates happen asynchronously without interrupting user input

### Memory System
- **Summary**: LLM-generated summary of conversation so far (updated periodically)
- **Recent transcripts**: Exact text of last 3 transcription batches (circular buffer)
- **User's last response**: Track what the user selected/typed
- Summary should be concise (2-3 sentences max)

### Async Pipeline Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ASYNC EVENT LOOP                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│   │   RECORDER   │───▶│ TRANSCRIBER  │───▶│  SUGGESTION  │         │
│   │   (10 sec)   │    │   (Whisper)  │    │  GENERATOR   │         │
│   └──────────────┘    └──────────────┘    └──────────────┘         │
│          │                   │                   │                  │
│          ▼                   ▼                   ▼                  │
│   ┌─────────────────────────────────────────────────────┐          │
│   │              SHARED STATE (Thread-safe)             │          │
│   │  - transcripts[]    - summary    - suggestions      │          │
│   │  - user_response    - is_recording    - timestamp   │          │
│   └─────────────────────────────────────────────────────┘          │
│                              │                                      │
│          ┌───────────────────┼───────────────────┐                 │
│          ▼                   ▼                   ▼                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│   │   DISPLAY    │    │    INPUT     │    │   MEMORY     │         │
│   │  (renders)   │    │  (non-block) │    │  (summarize) │         │
│   └──────────────┘    └──────────────┘    └──────────────┘         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Key async tasks:**
1. `record_audio_task`: Continuous 10-sec recordings, queues audio buffers
2. `transcribe_task`: Pulls from audio queue, transcribes, updates state
3. `suggestion_task`: Watches for new transcripts, generates suggestions
4. `display_task`: Re-renders screen when state changes
5. `input_task`: Listens for user input, updates user_response
6. `summary_task`: Periodically updates conversation summary

### LLM Abstraction
```python
# Base interface all LLM clients must implement
class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    async def generate_suggestions(self, context: ConversationContext) -> Suggestions:
        pass
```

### Response Format
Each suggestion cycle produces:
- **3 Quick Reactions**: Short phrases (1-5 words) like "Yes", "Tell me more", "I disagree"
- **3 Follow-up Phrases**: Complete sentences relevant to conversation
- **Custom Entry**: User can always type their own response

### Conversation Modes
Selected at app start, affects suggestion style:

1. **Friendly Mode**: Casual conversation
   - Reactions: emotional, expressive
   - Follow-ups: questions, sharing, empathy
   
2. **Shopping Mode**: Transactional conversation
   - Reactions: confirmations, clarifications
   - Follow-ups: product questions, price inquiries, decisions

### User Profile (Markdown Files)

**background.md** example:
```markdown
# About Me

## Basic Info
- Name: Alex
- Age: 34
- Location: Seattle

## About Me
I work as a graphic designer. I love coffee, hiking, and sci-fi movies.

## Communication Preferences
I prefer direct answers. I have a dry sense of humor.
```

**mood_board.md** example:
```markdown
# Today's Mood

## How I'm Feeling
Tired but optimistic. Had a good morning.

## Topics I'd Like to Discuss
- Weekend plans
- The new movie I watched

## Topics to Avoid
- Work stress
```

## CLI Interface Flow

```
$ python main.py

Welcome to SpeakWith
Loading user profile... ✓
Initializing Whisper... ✓

Select conversation mode:
[1] Friendly conversation
[2] Shopping conversation
> 1

Starting friendly conversation mode.
Listening... (Press Ctrl+C to exit)

╔══════════════════════════════════════════════════════════════════╗
║  SPEAKWITH - Friendly Mode                          [00:01:23]   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📝 SUMMARY                                                      ║
║  Friend greeted me after not seeing me for a while. They asked   ║
║  about my weekend and mentioned they tried a new coffee shop.    ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🎙️ RECENT TRANSCRIPT                                            ║
║  ┌────────────────────────────────────────────────────────────┐  ║
║  │ [00:00:40] "Hey, how are you doing? Haven't seen you in    │  ║
║  │            a while!"                                       │  ║
║  ├────────────────────────────────────────────────────────────┤  ║
║  │ [00:00:50] "I was wondering if you had any plans this      │  ║
║  │            weekend. We should hang out!"                   │  ║
║  ├────────────────────────────────────────────────────────────┤  ║
║  │ [00:01:00] "Oh by the way, I tried that new coffee shop    │  ║
║  │            downtown. It was amazing!"                      │  ║
║  └────────────────────────────────────────────────────────────┘  ║
║                                                                  ║
║  💬 YOUR LAST RESPONSE                                           ║
║  "I've been doing well! Good to see you too."                    ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ⚡ QUICK REACTIONS                                               ║
║  [1] That sounds great!    [2] Really?    [3] Tell me more       ║
║                                                                  ║
║  💭 FOLLOW-UPS                                                    ║
║  [4] I'd love to check out that coffee shop! Where is it?        ║
║  [5] This weekend works for me. What did you have in mind?       ║
║  [6] I've been meaning to explore downtown more lately.          ║
║                                                                  ║
║  [c] Custom response                                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

> _
```

### Async CLI Behavior

- **Screen redraws every 10 seconds** as new transcription comes in
- **User input is non-blocking**: can type/select at any time
- When user selects a response:
  - "Your Last Response" updates immediately
  - Response is logged to conversation memory
  - Suggestions regenerate considering the user's response
- **Visual indicators** for state:
  - 🔴 Recording...
  - ⏳ Processing...
  - ✓ Ready

## Implementation Order

1. **Phase 1**: Basic structure
   - Project setup, dependencies
   - Config management
   - User profile loader

2. **Phase 2**: Audio pipeline
   - Async audio recorder (10-sec batches)
   - Whisper transcription integration
   - Test: continuously print transcriptions

3. **Phase 3**: LLM integration
   - Abstract LLM interface
   - OpenAI async client implementation
   - Suggestion generator with mode support

4. **Phase 4**: Memory system
   - Transcript history (last 3, circular buffer)
   - Summary generation and periodic updates
   - User response tracking

5. **Phase 5**: Async CLI interface
   - Screen renderer (redraws on state change)
   - Non-blocking input handler
   - State management for display elements

6. **Phase 6**: Pipeline coordinator
   - Orchestrate all async tasks
   - Handle timing (10-sec cycles)
   - Manage state transitions

## Dependencies

```
openai-whisper
openai
sounddevice
numpy
python-dotenv
asyncio          # Built-in, but noting for clarity
aioconsole       # Async non-blocking input
rich             # Beautiful terminal rendering
```

## Environment Variables

```
OPENAI_API_KEY=your_key_here
WHISPER_MODEL=base  # tiny, base, small, medium, large
```

## Prompt Engineering Notes

The LLM prompt for generating suggestions should include:
1. System context (what SpeakWith is, the user's situation)
2. User background (from background.md)
3. Today's mood (from mood_board.md)
4. Conversation mode (friendly/shopping)
5. Conversation summary
6. Last 3 exact transcripts
7. User's last response (what they said/selected)
8. Clear output format instructions (JSON for parsing)

Example prompt structure:
```
You are helping a person who cannot speak communicate in a conversation.

USER BACKGROUND:
{background_md_content}

TODAY'S MOOD:
{mood_board_md_content}

MODE: {friendly|shopping}

CONVERSATION SO FAR:
Summary: {summary}

Recent exchanges:
- [Other person]: {transcript_1}
- [Other person]: {transcript_2}  
- [Other person]: {transcript_3}

User's last response: "{user_last_response}"

Based on what was just said, suggest responses the user might want to say next.
Consider the flow of conversation and what would be natural to say.

Respond in JSON format:
{
  "reactions": ["...", "...", "..."],
  "followups": ["...", "...", "..."]
}
```

## Testing Approach

- Unit tests for individual modules
- Integration test with pre-recorded audio files
- Manual CLI testing for full flow

## Future Considerations (Out of Scope for MVP)

- Multiple LLM provider support
- Voice output of selected responses
- Screen display integration
- Learning from user selections
- More conversation modes
- Multilingual support
