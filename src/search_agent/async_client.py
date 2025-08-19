"""Async Google API client wrapper for improved performance."""

from typing import Any, Dict, Optional

from google.genai import Client
from google.genai.types import GenerateContentResponse


class AsyncGoogleClient:
    """Async wrapper for Google GenAI client to improve performance."""

    def __init__(self, api_key: str):
        """Initialize the async client wrapper.

        Args:
            api_key: Google API key for authentication
        """
        self._client = Client(api_key=api_key)
        self._aio_models = self._client.aio.models
        self._session = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the client and cleanup resources."""
        # Note: Google GenAI client doesn't have an explicit close method
        # This is here for future compatibility
        pass

    async def generate_content(
        self,
        model: str,
        contents: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> GenerateContentResponse:
        """Generate content asynchronously.

        Args:
            model: Model name to use
            contents: Content to generate from
            config: Configuration dictionary

        Returns:
            GenerateContentResponse: The generated response
        """
        if config is None:
            config = {}

        # 直接调用官方SDK的aio异步接口
        return await self._aio_models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )


# Global async client instance
_async_client: Optional[AsyncGoogleClient] = None


def get_async_client(api_key: str) -> AsyncGoogleClient:
    """Get or create the global async client instance.

    Args:
        api_key: Google API key for authentication

    Returns:
        AsyncGoogleClient: The async client instance
    """
    global _async_client
    if _async_client is None:
        _async_client = AsyncGoogleClient(api_key)
    return _async_client


async def close_async_client():
    """Close the global async client instance."""
    global _async_client
    if _async_client is not None:
        await _async_client.close()
        _async_client = None
