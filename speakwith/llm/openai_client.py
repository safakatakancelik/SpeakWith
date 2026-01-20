"""OpenAI implementation of the LLM client."""

import json
from typing import Any

from openai import AsyncOpenAI

from speakwith.config import Config
from speakwith.llm.base import BaseLLMClient
from speakwith.models import ConversationContext, Suggestions


class OpenAIClient(BaseLLMClient):
    """OpenAI API client for generating suggestions and summaries."""

    def __init__(self, config: Config):
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.model = config.llm_model
        self.temperature = config.llm_temperature

    async def generate(self, prompt: str, system: str = "") -> str:
        """Generate a text response using OpenAI."""
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )

        return response.choices[0].message.content or ""

    async def generate_suggestions(self, context: ConversationContext) -> Suggestions:
        """Generate response suggestions based on conversation context."""
        system_prompt = self._build_system_prompt(context)
        user_prompt = self._build_user_prompt(context)

        response = await self.generate(user_prompt, system_prompt)

        return self._parse_suggestions(response)

    async def generate_summary(self, transcripts: list[str], previous_summary: str) -> str:
        """Generate or update a conversation summary."""
        system = (
            "You are a helpful assistant that summarizes conversations. "
            "Keep summaries concise (2-3 sentences max). Focus on key topics "
            "and the flow of conversation."
        )

        transcript_text = "\n".join(f"- {t}" for t in transcripts)
        prompt = f"""Update this conversation summary with the new transcripts.

Previous summary: {previous_summary or "(No previous summary)"}

New transcripts:
{transcript_text}

Provide an updated summary in 2-3 sentences."""

        return await self.generate(prompt, system)

    def _build_system_prompt(self, context: ConversationContext) -> str:
        """Build the system prompt for suggestion generation."""
        return f"""You are helping a person who cannot speak communicate in a conversation.

USER BACKGROUND:
{context.profile.background or "(No background provided)"}

TODAY'S MOOD:
{context.profile.mood_board or "(No mood board provided)"}

MODE: {context.mode.value}

Generate natural, contextually appropriate responses the user might want to say.
- Quick reactions should be 1-5 words (emotional for friendly mode, practical for shopping)
- Follow-ups should be complete sentences that continue the conversation naturally

Always respond in valid JSON format."""

    def _build_user_prompt(self, context: ConversationContext) -> str:
        """Build the user prompt with conversation context."""
        transcript_lines = []
        for t in context.recent_transcripts:
            transcript_lines.append(f"- [Other person]: \"{t.text}\"")

        transcripts_text = "\n".join(transcript_lines) or "(No transcripts yet)"

        user_response = context.user_last_response or "(No response yet)"

        return f"""CONVERSATION SO FAR:
Summary: {context.summary or "(Conversation just started)"}

Recent exchanges:
{transcripts_text}

User's last response: "{user_response}"

Based on what was just said, suggest responses the user might want to say next.
Consider the flow of conversation and what would be natural to say.

Respond in JSON format:
{{
  "reactions": ["reaction1", "reaction2", "reaction3"],
  "followups": ["followup1", "followup2", "followup3"]
}}"""

    def _parse_suggestions(self, response: str) -> Suggestions:
        """Parse LLM response into Suggestions object."""
        try:
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith("```"):
                # Handle markdown code blocks
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])

            data = json.loads(response)
            return Suggestions(
                reactions=data.get("reactions", [])[:3],
                followups=data.get("followups", [])[:3],
            )
        except (json.JSONDecodeError, KeyError):
            # Return defaults if parsing fails
            return Suggestions.default()
