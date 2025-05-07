import asyncio
import json
import logging
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from types import SimpleNamespace as Obj
from typing import Any, AsyncGenerator, Optional

import httpx

from ..utils.time import to_seconds

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ollama_client")


@dataclass
class AiResponse:
    model: str
    response: str
    done: bool


@dataclass
class AiModel:
    name: str
    modified_at: str
    size: int
    digest: str
    details: dict[str, Any]


class AiClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: int = to_seconds(days=1),
    ):
        self.base_url = base_url
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    @asynccontextmanager
    async def client(
        self, base_url: Optional[str] = None, timeout: Optional[int] = None
    ) -> AsyncGenerator["AiClient", None]:
        client = AiClient(base_url or self.base_url, timeout or self.timeout)
        try:
            yield client
        finally:
            await client.close()

    def run_sync(self, func_name: str, *args, **kwargs) -> Any:
        method = getattr(self, func_name, None)
        if not callable(method):
            raise ValueError(f"Method {func_name} not found")
        return asyncio.run(method(*args, **kwargs))

    async def close(self) -> None:
        await self._client.aclose()
        logger.debug("HTTP client closed")

    async def _handle_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> Any:
        headers = headers or {"Content-Type": "application/json"}
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self._client.request(
                method, url, headers=headers, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error at {url}: {e}")
            raise RuntimeError(f"Request error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error at {url}: {e}")
            raise RuntimeError(f"Unexpected error: {e}") from e

    async def _stream_response(
        self, endpoint: str, payload: dict[str, Any], embedding: bool = False
    ) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}{endpoint}"
        try:
            async with self._client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line := line.strip():
                        try:
                            data = json.loads(line)
                            if embedding:
                                yield data.get("embedding", "")
                            else:
                                yield data.get(
                                    "response",
                                    data.get("message", {}).get("content", ""),
                                )
                        except json.JSONDecodeError:
                            logger.warning(f"Malformed JSON: {line}")
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"Error: {e}"

    async def _request_or_stream(
        self,
        endpoint: str,
        payload: dict[str, Any],
        stream: bool,
        extract: Callable[[dict], str],
        embedding: bool = False,
    ) -> AsyncGenerator[str, None] | str:
        if stream:
            async for chunk in self._stream_response(endpoint, payload, embedding):
                yield chunk
        else:
            try:
                data = await self._handle_request("POST", endpoint, json=payload)
                yield extract(data)
            except Exception as e:
                yield f"Error: {e}"

    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system_prompt:
            payload["system"] = system_prompt

        return self._request_or_stream(
            "/api/generate",
            payload,
            stream,
            extract=lambda d: d.get("response", "No response generated"),
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        stream: bool = False,
    ) -> AsyncGenerator[str, None]:
        payload = {"model": model, "messages": messages, "stream": stream}
        return self._request_or_stream(
            "/api/chat",
            payload,
            stream,
            extract=lambda d: d.get("message", {}).get("content", ""),
        )

    async def embeddings(
        self, prompt: str, model: str = "nomic-embed-text:latest", stream: bool = False
    ) -> AsyncGenerator[str, None]:
        payload = {"model": model, "prompt": prompt, "stream": stream}
        return self._request_or_stream(
            "/api/embeddings",
            payload,
            stream,
            extract=lambda d: d.get("embedding", ""),
            embedding=True,
        )

    async def list_models(self) -> list[Obj]:
        data = await self._handle_request("GET", "/api/tags")
        return [Obj(**m) for m in data.get("models", [])]

    async def pull_model(self, model_name: str) -> dict[str, Any]:
        return await self._handle_request(
            "POST", "/api/pull", json={"name": model_name}
        )

    async def delete_model(self, model_name: str) -> dict[str, Any]:
        return await self._handle_request(
            "DELETE", "/api/delete", json={"name": model_name}
        )

    async def __aenter__(self) -> "AiClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
