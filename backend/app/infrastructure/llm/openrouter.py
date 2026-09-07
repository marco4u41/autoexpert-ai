import asyncio
import json
import logging
from collections.abc import AsyncIterator

import httpx

from app.config import settings
from app.domain.exceptions import LLMProviderError, LLMRateLimitError
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.models.message import Message

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 5


class OpenRouterProvider(LLMProvider):
    def __init__(self) -> None:
        self._api_key = settings.openrouter_api_key
        self._model = settings.openrouter_model
        self._base_url = settings.openrouter_base_url

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://autoexpert.local",
            "X-Title": "AutoExpert AI — Asistente Automotriz",
        }

    def _build_messages(
        self, messages: list[Message], system_prompt: str
    ) -> list[dict[str, str]]:
        api_messages: list[dict[str, str]] = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        for msg in messages:
            api_messages.append({"role": msg.role.value, "content": msg.content})
        return api_messages

    async def _request_with_retry(
        self,
        client: httpx.AsyncClient,
        payload: dict,
    ) -> httpx.Response:
        last_error: LLMRateLimitError | None = None

        for attempt in range(_MAX_RETRIES):
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers=self._build_headers(),
                json=payload,
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get("retry-after", str(_RETRY_BASE_DELAY)))
                delay = min(retry_after, 30)
                last_error = LLMRateLimitError("openrouter", retry_after=retry_after)
                logger.warning(
                    "Rate limited (attempt %d/%d). Retrying in %ds...",
                    attempt + 1,
                    _MAX_RETRIES,
                    delay,
                )
                await asyncio.sleep(delay)
                continue

            if response.status_code != 200:
                raise LLMProviderError(
                    "openrouter", f"HTTP {response.status_code}: {response.text}"
                )

            return response

        raise last_error or LLMProviderError("openrouter", "Max retries exceeded")

    async def stream_chat(
        self,
        messages: list[Message],
        system_prompt: str = "",
    ) -> AsyncIterator[str]:
        if not self._api_key:
            raise LLMProviderError("openrouter", "API key not configured")

        payload = {
            "model": self._model,
            "messages": self._build_messages(messages, system_prompt),
            "stream": True,
        }

        for attempt in range(_MAX_RETRIES):
            async with httpx.AsyncClient(timeout=120.0) as client:
                try:
                    async with client.stream(
                        "POST",
                        f"{self._base_url}/chat/completions",
                        headers=self._build_headers(),
                        json=payload,
                    ) as stream_response:
                        if stream_response.status_code == 429:
                            retry_after = int(
                                stream_response.headers.get("retry-after", str(_RETRY_BASE_DELAY)),
                            )
                            delay = min(retry_after, 30)
                            logger.warning(
                                "Rate limited on stream (attempt %d/%d). Retrying in %ds...",
                                attempt + 1,
                                _MAX_RETRIES,
                                delay,
                            )
                            await asyncio.sleep(delay)
                            continue

                        if stream_response.status_code != 200:
                            body = await stream_response.aread()
                            raise LLMProviderError(
                                "openrouter",
                                f"HTTP {stream_response.status_code}: {body.decode()}",
                            )

                        async for line in stream_response.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
                        return

                except httpx.TimeoutException as exc:
                    raise LLMProviderError("openrouter", f"Request timed out: {exc}") from exc
                except httpx.ConnectError as exc:
                    raise LLMProviderError("openrouter", f"Connection failed: {exc}") from exc

        raise LLMProviderError("openrouter", "Max retries exceeded on stream")

    async def chat(
        self,
        messages: list[Message],
        system_prompt: str = "",
    ) -> str:
        if not self._api_key:
            raise LLMProviderError("openrouter", "API key not configured")

        payload = {
            "model": self._model,
            "messages": self._build_messages(messages, system_prompt),
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await self._request_with_retry(client, payload)
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.TimeoutException as exc:
                raise LLMProviderError("openrouter", f"Request timed out: {exc}") from exc
