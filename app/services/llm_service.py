"""LLM Service using Groq SDK for prompt-cached agricultural advisory.

Uses the Groq Python SDK directly (not LangChain) to enable
automatic prompt caching with cache hit rate tracking.

Prompt caching is automatic on Groq for supported models.
Static prefixes (system prompt + history) are cached across requests.
50% cost discount on cached tokens.
"""

import json
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from flask import current_app

import groq

from app.config import AppConfig
from app.services.prompt_manager import PromptManager

logger = logging.getLogger(__name__)


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from LLM output.

    Strips bold (**), italic (*), headers (#), backticks, etc.
    This is a safety net in case the model ignores the prompt instruction.
    """
    if not text:
        return text

    # Remove bold: **text** → text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove italic: *text* → text
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
    # Remove underscores: _text_ → text
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'\1', text)
    # Remove headers: ### text → text
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove backticks: `text` → text
    text = re.sub(r'`([^`\n]+)`', r'\1', text)
    # Remove triple backtick blocks
    text = re.sub(r'```[\s\S]*?```', '', text)

    return text.strip()


@dataclass
class LLMResult:
    """Response wrapper including cache metrics."""
    text: str
    prompt_tokens: int = 0
    cached_tokens: int = 0
    completion_tokens: int = 0

    @property
    def cache_hit_rate(self) -> float:
        """Percentage of prompt tokens served from cache."""
        if self.prompt_tokens == 0:
            return 0.0
        return (self.cached_tokens / self.prompt_tokens) * 100


class LLMService:
    """Service for LLM interaction via Groq SDK with prompt caching.

    Prompt caching works automatically when the static prefix
    (system prompt + conversation history) is consistent across requests.
    Only the new user query changes, maximizing cache hits.
    """

    def __init__(self) -> None:
        """Initialize the LLM service."""
        self.config = AppConfig
        self.prompt_manager = PromptManager()
        self._client = self._create_client()
        logger.info("LLM Service initialized (model: %s)", self.config.LLM_MODEL)

    def _create_client(self) -> Optional[groq.Groq]:
        """Create the Groq client."""
        api_key = self.config.GROQ_API_KEY
        if not api_key:
            logger.warning("GROQ_API_KEY not set. LLM unavailable.")
            return None
        return groq.Groq(api_key=api_key)

    def generate(
        self,
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None,
    ) -> LLMResult:
        """Generate a response with cache hit tracking.

        Args:
            user_query: The farmer's input message.
            conversation_history: Prior messages from memory.
            session_id: Session ID for logging.

        Returns:
            LLMResult with text and cache metrics.
        """
        if self._client is None:
            return LLMResult(text="LLM not configured. Set GROQ_API_KEY in .env.")

        try:
            messages = self.prompt_manager.build_messages(
                user_query=user_query,
                conversation_history=conversation_history,
            )

            logger.debug("LLM call [session: %s], messages=%d",
                         session_id, len(messages))

            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get current weather and 7-day forecast for a city. Use this when the user asks about the weather, or asks farming questions that depend on weather (e.g., irrigation, pesticide spraying).",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {
                                    "type": "string",
                                    "description": "The name of the city, e.g., Bangalore, Delhi"
                                }
                            },
                            "required": ["city"]
                        }
                    }
                }
            ]

            response = self._client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=messages,
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=self.config.LLM_MAX_TOKENS,
                tools=tools,
                tool_choice="auto"
            )

            # Extract cache metrics from usage
            usage = response.usage
            total_prompt = getattr(usage, 'prompt_tokens', 0)
            total_completion = getattr(usage, 'completion_tokens', 0)

            details = getattr(usage, 'prompt_tokens_details', None)
            total_cached = 0
            if details and isinstance(details, dict):
                total_cached = details.get('cached_tokens', 0)
            elif details:
                total_cached = getattr(details, 'cached_tokens', 0)

            response_message = response.choices[0].message
            tool_calls = getattr(response_message, 'tool_calls', None)

            if tool_calls:
                logger.info("LLM requested tool call(s) [session: %s]", session_id)
                messages.append(response_message)
                
                for tool_call in tool_calls:
                    if tool_call.function.name == "get_weather":
                        try:
                            args = json.loads(tool_call.function.arguments)
                            city = args.get("city")
                            weather_data = current_app.weather_service.get_weather_for_city(city)
                            content_str = json.dumps(weather_data)
                        except Exception as e:
                            logger.error("Error executing tool %s: %s", tool_call.function.name, e)
                            content_str = json.dumps({"error": str(e)})
                            
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": "get_weather",
                            "content": content_str
                        })
                
                # Second call with tool output
                second_response = self._client.chat.completions.create(
                    model=self.config.LLM_MODEL,
                    messages=messages,
                    temperature=self.config.LLM_TEMPERATURE,
                    max_tokens=self.config.LLM_MAX_TOKENS,
                )
                
                response_message = second_response.choices[0].message
                second_usage = second_response.usage
                total_prompt += getattr(second_usage, 'prompt_tokens', 0)
                total_completion += getattr(second_usage, 'completion_tokens', 0)
                
                sec_details = getattr(second_usage, 'prompt_tokens_details', None)
                if sec_details and isinstance(sec_details, dict):
                    total_cached += sec_details.get('cached_tokens', 0)
                elif sec_details:
                    total_cached += getattr(sec_details, 'cached_tokens', 0)

            final_text = response_message.content.strip() if response_message.content else ""
            result = LLMResult(
                text=strip_markdown(final_text),
                prompt_tokens=total_prompt,
                cached_tokens=total_cached,
                completion_tokens=total_completion,
            )

            logger.info(
                "LLM response [session: %s] — "
                "prompt: %d tokens, cached: %d (%.0f%% hit), "
                "completion: %d tokens",
                session_id,
                result.prompt_tokens,
                result.cached_tokens,
                result.cache_hit_rate,
                result.completion_tokens,
            )

            return result

        except Exception as exc:
            logger.error("LLM generation failed [session: %s]: %s",
                         session_id, exc)
            return LLMResult(
                text="I apologize, but I'm experiencing a temporary issue. "
                     "Please try again in a moment."
            )

    @property
    def client(self):
        """Access the underlying Groq client."""
        return self._client

    def generate_with_image(
        self,
        user_query: str,
        image_base64: str,
        image_mime: str = "image/jpeg",
        session_id: Optional[str] = None,
    ) -> LLMResult:
        """Generate a response analyzing an image with the vision model.

        Uses meta-llama/llama-4-scout-17b-16e-instruct for multimodal input.
        The image is passed as base64 data URL.

        Args:
            user_query: The farmer's question about the image.
            image_base64: Base64 encoded image data.
            image_mime: MIME type (image/jpeg, image/png, etc).
            session_id: Session ID for logging.

        Returns:
            LLMResult with text and cache metrics.
        """
        if self._client is None:
            return LLMResult(text="LLM not configured. Set GROQ_API_KEY in .env.")

        try:
            system_prompt = self.prompt_manager.get_system_prompt()

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_query},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_mime};base64,{image_base64}"
                            },
                        },
                    ],
                },
            ]

            logger.debug("Vision LLM call [session: %s]", session_id)

            response = self._client.chat.completions.create(
                model=self.config.LLM_VISION_MODEL,
                messages=messages,
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=self.config.LLM_MAX_TOKENS,
            )

            usage = response.usage
            cached_tokens = 0
            prompt_tokens = getattr(usage, 'prompt_tokens', 0)

            details = getattr(usage, 'prompt_tokens_details', None)
            if details and isinstance(details, dict):
                cached_tokens = details.get('cached_tokens', 0)
            elif details:
                cached_tokens = getattr(details, 'cached_tokens', 0)

            result = LLMResult(
                text=strip_markdown(response.choices[0].message.content.strip()),
                prompt_tokens=prompt_tokens,
                cached_tokens=cached_tokens,
                completion_tokens=getattr(usage, 'completion_tokens', 0),
            )

            logger.info(
                "Vision response [session: %s] — prompt: %d, cached: %d (%.0f%%)",
                session_id, result.prompt_tokens,
                result.cached_tokens, result.cache_hit_rate,
            )

            return result

        except Exception as exc:
            logger.error("Vision LLM failed [session: %s]: %s", session_id, exc)
            return LLMResult(
                text="I could not analyze the image. Please try again."
            )